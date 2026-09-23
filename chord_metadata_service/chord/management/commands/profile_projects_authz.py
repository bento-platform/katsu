import json
import logging
import time
from unittest.mock import patch

from django.core.management.base import BaseCommand
from django.db import connection
from django.test import Client
from tabulate import tabulate

from chord_metadata_service.authz.middleware import authz_middleware
from chord_metadata_service.chord import serializers as chord_serializers
from chord_metadata_service.discovery.api_views import QueryHelper

MODE_PER_OBJECT = "per-object authz (old)"
MODE_BATCHED = "batched matrix authz"


class Command(BaseCommand):
    help = """
        Profiles GET /api/projects (or another path) with discovery permissions resolved per project/dataset (the old
        behaviour: one authz request per object) vs. in one batched matrix request (the current behaviour), and reports
        authz calls, entity count query time, and the returned counts for each mode.
    """

    def add_arguments(self, parser):
        parser.add_argument("--path", default="/api/projects", help="Endpoint to profile (default: /api/projects)")
        parser.add_argument("--runs", type=int, default=3, help="Measured runs per mode; median is reported")
        parser.add_argument("--token", default=None, help="Bearer token to profile as a logged-in user")
        parser.add_argument("--language", default="en", help="Accept-Language header (default: en)")
        parser.add_argument("--verbose-logs", action="store_true", help="Don't silence katsu/SQL logging")

    def handle(self, *args, **options):
        if not options["verbose_logs"]:
            logging.disable(logging.CRITICAL)  # katsu debug logs (incl. every SQL query) would drown the report

        headers = {
            "HTTP_ACCEPT": "application/json",
            "HTTP_HOST": "localhost",
            "HTTP_ACCEPT_LANGUAGE": options["language"],
        }
        if options["token"]:
            headers["HTTP_AUTHORIZATION"] = f"Bearer {options['token']}"

        profiler = _Profiler(Client(**headers), options["path"], max(options["runs"], 1))

        # Disabling the bulk prefetch makes the serializers fall back to one authz request per project/dataset,
        # which is exactly the behaviour before batching was introduced.
        with patch.object(chord_serializers, "prefetch_discovery_permissions_for_serializer", lambda *_a, **_k: None):
            per_object = profiler.run()
        batched = profiler.run()

        self._print_timings(options, {MODE_PER_OBJECT: per_object, MODE_BATCHED: batched})
        self._print_counts(per_object["counts"], batched["counts"])

    def _print_timings(self, options, results: dict[str, dict]):
        self.stdout.write(
            f"\nGET {options['path']}  (median of {options['runs']} runs, "
            f"{'token' if options['token'] else 'anonymous'}, Accept-Language: {options['language']})\n"
        )
        rows = []
        for mode, r in results.items():
            rows.append(
                [
                    mode,
                    r["status"],
                    f"{r['total']:.3f}s",
                    f"{r['authz_n']} ({r['authz_t']:.3f}s)",
                    f"{r['counts_n']} ({r['counts_t']:.3f}s)",
                    f"{r['counts_sql_n']} ({r['counts_sql_t']:.3f}s)",
                    f"{r['other_sql_n']} ({r['other_sql_t']:.3f}s)",
                ]
            )
        self.stdout.write(
            tabulate(
                rows,
                headers=["mode", "status", "total", "authz calls", "entity counts", "count SQL", "other SQL"],
            )
        )

        old, new = results[MODE_PER_OBJECT]["total"], results[MODE_BATCHED]["total"]
        if new > 0:
            self.stdout.write(f"\nspeedup: {old / new:.1f}x ({old - new:.3f}s saved per request)")

    def _print_counts(self, per_object: dict, batched: dict):
        rows = []
        # keep response order (datasets listed under their project)
        for key in [*per_object, *(k for k in batched if k not in per_object)]:
            a, b = per_object.get(key), batched.get(key)
            rows.append([key, json.dumps(a, sort_keys=True), json.dumps(b, sort_keys=True), "yes" if a == b else "NO"])

        self.stdout.write("\nReturned counts:\n")
        self.stdout.write(tabulate(rows, headers=["object", MODE_PER_OBJECT, MODE_BATCHED, "identical"]))

        if per_object == batched:
            self.stdout.write(self.style.SUCCESS("\nCounts are identical in both modes."))
        else:
            self.stdout.write(self.style.ERROR("\nCounts DIFFER between modes!"))


class _Profiler:
    """
    Instruments authz calls, discovery entity counts, and SQL, then issues requests against an endpoint and returns the
    measurements of the median run.
    """

    def __init__(self, client: Client, path: str, runs: int):
        self._client = client
        self._path = path
        self._runs = runs
        self._reset()

    def _reset(self):
        self.authz_n, self.authz_t = 0, 0.0
        self.counts_n, self.counts_t = 0, 0.0
        self.counts_sql_n, self.counts_sql_t = 0, 0.0
        self.sql_n, self.sql_t = 0, 0.0
        self._in_counts = False

    def _instrumented_eval(self, orig):
        async def _eval(*args, **kwargs):
            t = time.perf_counter()
            try:
                return await orig(*args, **kwargs)
            finally:
                self.authz_n += 1
                self.authz_t += time.perf_counter() - t

        return _eval

    def _instrumented_counts(self, orig):
        profiler = self

        async def _counts(qh, *args, **kwargs):
            t = time.perf_counter()
            profiler._in_counts = True
            try:
                return await orig(qh, *args, **kwargs)
            finally:
                profiler._in_counts = False
                profiler.counts_n += 1
                profiler.counts_t += time.perf_counter() - t

        return _counts

    def _sql_wrapper(self, execute, sql, params, many, context):
        t = time.perf_counter()
        try:
            return execute(sql, params, many, context)
        finally:
            dt = time.perf_counter() - t
            self.sql_n += 1
            self.sql_t += dt
            if self._in_counts:
                self.counts_sql_n += 1
                self.counts_sql_t += dt

    def run(self) -> dict:
        with (
            patch.object(authz_middleware, "async_evaluate", self._instrumented_eval(authz_middleware.async_evaluate)),
            patch.object(
                QueryHelper,
                "get_censored_entity_counts",
                self._instrumented_counts(QueryHelper.get_censored_entity_counts),
            ),
        ):
            self._client.get(self._path)  # warm-up

            results = []
            for _ in range(self._runs):
                self._reset()
                with connection.execute_wrapper(self._sql_wrapper):
                    t = time.perf_counter()
                    r = self._client.get(self._path)
                    total = time.perf_counter() - t
                results.append(
                    {
                        "status": r.status_code,
                        "total": total,
                        "authz_n": self.authz_n,
                        "authz_t": self.authz_t,
                        "counts_n": self.counts_n,
                        "counts_t": self.counts_t,
                        "counts_sql_n": self.counts_sql_n,
                        "counts_sql_t": self.counts_sql_t,
                        "other_sql_n": self.sql_n - self.counts_sql_n,
                        "other_sql_t": max(self.sql_t - self.counts_sql_t, 0.0),
                        "counts": _extract_counts(r),
                    }
                )

        results.sort(key=lambda x: x["total"])
        return results[len(results) // 2]


def _extract_counts(response) -> dict:
    """Returns {"<project|dataset> <title> (<id>)": counts} for every project/dataset in a list response."""
    try:
        body = response.json()
    except ValueError:
        return {}

    items = body.get("results", body) if isinstance(body, dict) else body
    if isinstance(items, dict):  # retrieve endpoint
        items = [items]

    res = {}
    for item in items:
        if "counts" in item:  # project
            res[f"project {item.get('title')} ({item.get('identifier')})"] = item["counts"]
            for ds in item.get("datasets", []):
                res[f"  dataset {ds.get('title')} ({ds.get('identifier')})"] = ds.get("counts_by_entity")
        elif "counts_by_entity" in item:  # dataset
            res[f"dataset {item.get('title')} ({item.get('identifier')})"] = item["counts_by_entity"]
    return res
