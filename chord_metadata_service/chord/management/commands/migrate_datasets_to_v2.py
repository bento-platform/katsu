"""
Management command to migrate legacy Dataset records into the DatasetV2 table.

The DatasetV2 table stores a full ProjectScopedDatasetModel payload split across
dedicated columns (identifier, project, title, release_date, last_modified) and
a JSONB `data` column for the remaining fields. Records are always created as the
English (default) canonical entry. Translations can be added via the API.

Old Dataset fields are DATS-style; this command performs a best-effort mapping
to the new Pydantic schema. Required Pydantic fields that cannot be derived
from the old record will cause that dataset to be skipped (with a logged
warning) unless --force-placeholder is supplied.

Usage:
    python manage.py migrate_datasets_to_v2
    python manage.py migrate_datasets_to_v2 --dry-run
    python manage.py migrate_datasets_to_v2 --skip-existing
    python manage.py migrate_datasets_to_v2 --force-placeholder
"""

import logging
from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from pydantic import ValidationError

from bento_lib.provenance.dataset import ProjectScopedDatasetModel
from chord_metadata_service.chord.models import Dataset, DatasetV2

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# DATS → new-schema helpers
# ---------------------------------------------------------------------------

_FALLBACK_ROLE = "Data Provider"


def _map_creators_to_stakeholders(creators: list) -> list[dict]:
    """Convert DATS-style creator objects to PersonOrOrganization dicts."""
    stakeholders = []
    for c in creators:
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or c.get("fullName") or "").strip()
        if not name:
            continue

        roles = [_FALLBACK_ROLE]

        stakeholders.append({
            "type": "organization",
            "name": name,
            "roles": roles,
        })
    return stakeholders


def _contact_from_text(contact_info: str) -> dict | None:
    """Build a minimal Organization from a free-text contact_info string."""
    text = (contact_info or "").strip()
    if not text:
        return None
    return {
        "type": "organization",
        "name": "Dataset Contact",
        "contact": {"address": text},
        "roles": [_FALLBACK_ROLE],
    }


def _extract_dates(dates_field: list) -> tuple[date | None, date | None]:
    """
    Try to pull release_date and last_modified from the DATS `dates` array.

    DATS date entry shape: {"date": "YYYY-MM-DD", "type": {"value": "..."}}
    """
    release_date: date | None = None
    last_modified: date | None = None

    for entry in (dates_field or []):
        if not isinstance(entry, dict):
            continue
        raw_date = entry.get("date")
        if not raw_date:
            continue
        type_value = ""
        if isinstance(entry.get("type"), dict):
            type_value = entry["type"].get("value", "").lower()
        elif isinstance(entry.get("type"), str):
            type_value = entry["type"].lower()

        try:
            parsed = date.fromisoformat(str(raw_date)[:10])
        except ValueError:
            continue

        if any(k in type_value for k in ("creat", "start", "release", "issued")):
            release_date = parsed
        elif any(k in type_value for k in ("modif", "updat", "revision")):
            last_modified = parsed

    return release_date, last_modified


def _map_publications(pubs: list) -> list[dict] | None:
    """Convert DATS primary_publications to Publication dicts (best-effort)."""
    result = []
    for pub in (pubs or []):
        if not isinstance(pub, dict):
            continue
        title = (pub.get("title") or "").strip()
        # DATS puts the URL in identifier.identifier or a top-level url field
        url = pub.get("url") or ""
        if not url and isinstance(pub.get("identifier"), dict):
            url = pub["identifier"].get("identifier", "")
        url = url.strip()
        if not title or not url:
            continue
        result.append({
            "title": title,
            "url": url,
            "publication_type": "Journal Article",
        })
    return result or None


def _map_keywords(keywords_field: list) -> list[str] | None:
    """Flatten DATS keywords (string or {value: ...} dicts) to plain strings."""
    result = []
    for kw in (keywords_field or []):
        if isinstance(kw, str):
            result.append(kw)
        elif isinstance(kw, dict):
            val = kw.get("value") or kw.get("label") or ""
            if val:
                result.append(str(val))
    return result or None


def _map_spatial_coverage(sc_field: object) -> object | None:
    """Return spatial_coverage in a form the new schema accepts (str or GeoJSON Feature)."""
    if sc_field is None:
        return None
    if isinstance(sc_field, list):
        sc_field = sc_field[0] if sc_field else None
    if sc_field is None:
        return None
    if isinstance(sc_field, str):
        return sc_field
    if isinstance(sc_field, dict):
        # If it looks like a GeoJSON Feature, pass it through; otherwise stringify name
        if sc_field.get("type") == "Feature":
            return sc_field
        name = sc_field.get("name") or sc_field.get("value") or ""
        return name if name else None
    return None


def build_v2_payload(dataset: Dataset, force_placeholder: bool) -> dict:
    """
    Build a dict suitable for ProjectScopedDatasetModel.model_validate().

    Raises ValueError if required fields cannot be satisfied and
    force_placeholder is False.
    """
    # --- stakeholders & primary_contact ---
    stakeholders = _map_creators_to_stakeholders(dataset.creators or [])

    if not stakeholders:
        contact_org = _contact_from_text(dataset.contact_info)
        if contact_org:
            stakeholders = [contact_org]
        elif force_placeholder:
            stakeholders = [{"type": "organization", "name": "placeholder (fill this)", "roles": [_FALLBACK_ROLE]}]
        else:
            raise ValueError(
                "No stakeholders could be derived (no creators, no contact_info). "
                "Use --force-placeholder to insert a synthetic entry."
            )

    primary_contact = stakeholders[0]

    # --- description ---
    description = (dataset.description or "").strip() or dataset.title

    # --- dates ---
    release_date, last_modified = _extract_dates(dataset.dates)
    if release_date is None:
        release_date = dataset.created.date() if dataset.created else date.today()
    if last_modified is None:
        last_modified = dataset.updated.date() if dataset.updated else date.today()

    # --- assemble payload ---
    payload: dict = {
        "schema_version": "1.0",
        "identifier": str(dataset.identifier),
        "project": str(dataset.project_id),
        "title": dataset.title,
        "description": description,
        "stakeholders": stakeholders,
        "primary_contact": primary_contact,
        "release_date": str(release_date),
        "last_modified": str(last_modified),
    }

    # Optional field mappings
    keywords = _map_keywords(dataset.keywords)
    if keywords:
        payload["keywords"] = keywords

    if dataset.privacy:
        payload["privacy"] = dataset.privacy

    version = (dataset.version or "").strip()
    if version:
        payload["version"] = version

    spatial_coverage = _map_spatial_coverage(dataset.spatial_coverage)
    if spatial_coverage:
        payload["spatial_coverage"] = spatial_coverage

    publications = _map_publications(dataset.primary_publications)
    if publications:
        payload["publications"] = publications

    # extra_properties: new schema requires dict[str, str|int|float|bool|None]
    # Filter out any values that are not scalar to avoid Pydantic errors.
    if dataset.extra_properties and isinstance(dataset.extra_properties, dict):
        scalar_types = (str, int, float, bool, type(None))
        filtered_ep = {
            k: v for k, v in dataset.extra_properties.items()
            if isinstance(v, scalar_types)
        }
        if filtered_ep:
            payload["extra_properties"] = filtered_ep

    return payload


# ---------------------------------------------------------------------------
# Management command
# ---------------------------------------------------------------------------

class Command(BaseCommand):
    help = (
        "Migrate legacy Dataset records to DatasetV2 using the ProjectScopedDatasetModel schema. "
        "Performs a best-effort mapping of DATS-style fields to the new schema."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Validate and print what would be created without writing to the DB.",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            default=False,
            help="Skip Dataset records that already have a matching DatasetV2 entry.",
        )
        parser.add_argument(
            "--force-placeholder",
            action="store_true",
            default=False,
            help=(
                "If required Pydantic fields (stakeholders, primary_contact) cannot be "
                "derived from old data, insert synthetic placeholder values so the record "
                "can still be migrated."
            ),
        )
        parser.add_argument(
            "--dataset-id",
            default=None,
            help="Migrate only the Dataset with this identifier (UUID). Useful for testing.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        skip_existing: bool = options["skip_existing"]
        force_placeholder: bool = options["force_placeholder"]
        dataset_id: str | None = options["dataset_id"]

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no records will be written."))

        qs = Dataset.objects.select_related("project").order_by("created")
        if dataset_id:
            qs = qs.filter(identifier=dataset_id)

        if skip_existing:
            existing_ids = set(
                DatasetV2.objects.values_list("identifier", flat=True)
            )
        else:
            existing_ids = set()

        total = qs.count()
        self.stdout.write(f"Found {total} Dataset record(s) to process.")

        created_count = 0
        skipped_count = 0
        error_count = 0

        for dataset in qs:
            identifier = str(dataset.identifier)

            if identifier in existing_ids:
                self.stdout.write(f"  SKIP  {identifier} — already exists in DatasetV2")
                skipped_count += 1
                continue

            # Build and validate Pydantic model
            try:
                payload = build_v2_payload(dataset, force_placeholder=force_placeholder)
                schema = ProjectScopedDatasetModel.model_validate(payload)
            except (ValueError, ValidationError) as exc:
                self.stderr.write(
                    self.style.ERROR(f"  ERROR {identifier} ({dataset.title!r}): {exc}")
                )
                error_count += 1
                continue

            if dry_run:
                self.stdout.write(
                    self.style.SUCCESS(f"  OK    {identifier} ({dataset.title!r}) → would create DatasetV2")
                )
                created_count += 1
                continue

            try:
                with transaction.atomic():
                    instance = DatasetV2.from_schema(schema)
                    instance.save()
                self.stdout.write(
                    self.style.SUCCESS(f"  OK    {identifier} ({dataset.title!r}) → DatasetV2 created")
                )
                created_count += 1
            except Exception as exc:
                self.stderr.write(
                    self.style.ERROR(f"  ERROR {identifier} ({dataset.title!r}): DB save failed: {exc}")
                )
                error_count += 1

        # Summary
        self.stdout.write("")
        action = "would be created" if dry_run else "created"
        self.stdout.write(f"Done. {created_count} {action}, {skipped_count} skipped, {error_count} errors.")
