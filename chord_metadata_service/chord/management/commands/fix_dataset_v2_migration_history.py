"""
Management command to fix InconsistentMigrationHistory on systems where
experiments.0017 and phenopackets.0019 were applied before chord.0013 existed.

Run this before `python manage.py migrate` on affected systems.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone


_MIGRATION_0013 = ("chord", "0013_migrate_datasets_to_v2")
_MIGRATION_0017 = ("experiments", "0017_experiment_dataset_v2")
_MIGRATION_0019 = ("phenopackets", "0019_phenopacket_dataset_v2")


def _is_applied(cursor, app, name):
    cursor.execute(
        "SELECT 1 FROM django_migrations WHERE app=%s AND name=%s",
        [app, name],
    )
    return cursor.fetchone() is not None


class Command(BaseCommand):
    help = (
        "Fix InconsistentMigrationHistory caused by chord.0013 being added after "
        "experiments.0017 and phenopackets.0019 were already applied manually."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print what would be done without making changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        with connection.cursor() as cursor:
            applied_0013 = _is_applied(cursor, *_MIGRATION_0013)
            applied_0017 = _is_applied(cursor, *_MIGRATION_0017)
            applied_0019 = _is_applied(cursor, *_MIGRATION_0019)

        if applied_0013:
            self.stdout.write("chord.0013 already in migration history. Nothing to do.")
            return

        if not applied_0017 and not applied_0019:
            self.stdout.write("0017/0019 not applied yet. Run migrate normally.")
            return

        self.stdout.write(
            "Detected: 0017/0019 applied, 0013 missing. Fixing migration history..."
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — no changes will be made."))
            if applied_0017:
                self.stdout.write("  Would delete experiments.0017 from django_migrations")
            if applied_0019:
                self.stdout.write("  Would delete phenopackets.0019 from django_migrations")
            self.stdout.write("  Would insert chord.0013 into django_migrations")
            if applied_0017:
                self.stdout.write("  Would fake-apply experiments.0017")
            if applied_0019:
                self.stdout.write("  Would fake-apply phenopackets.0019")
            return

        with connection.cursor() as cursor:
            if applied_0017:
                cursor.execute(
                    "DELETE FROM django_migrations WHERE app=%s AND name=%s",
                    list(_MIGRATION_0017),
                )
                self.stdout.write(f"  Removed experiments.0017 from django_migrations")

            if applied_0019:
                cursor.execute(
                    "DELETE FROM django_migrations WHERE app=%s AND name=%s",
                    list(_MIGRATION_0019),
                )
                self.stdout.write(f"  Removed phenopackets.0019 from django_migrations")

            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                [_MIGRATION_0013[0], _MIGRATION_0013[1], timezone.now()],
            )
            self.stdout.write(f"  Inserted chord.0013 into django_migrations")

        if applied_0017:
            call_command("migrate", "experiments", "0017_experiment_dataset_v2", fake=True, verbosity=0)
            self.stdout.write("  Faked experiments.0017")

        if applied_0019:
            call_command("migrate", "phenopackets", "0019_phenopacket_dataset_v2", fake=True, verbosity=0)
            self.stdout.write("  Faked phenopackets.0019")

        self.stdout.write(self.style.SUCCESS("Done. Run `python manage.py migrate` now."))
