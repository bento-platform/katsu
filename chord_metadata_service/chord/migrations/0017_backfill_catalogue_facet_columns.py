from django.db import migrations


def _label(item):
    return item.get("label") if isinstance(item, dict) else item


def backfill_catalogue_facet_columns(apps, schema_editor):
    # Historical models don't carry the real Dataset.save() override, so the derivation logic
    # for taxa_labels/keyword_labels/license_label is duplicated here rather than relying on it.
    #
    # Note: this leaves program_name/privacy/study_status/study_context/domain duplicated in the
    # `data` JSONB blob for existing rows, since only a schema-driven save (from_schema/
    # update_from_schema) strips COLUMN_FIELDS keys out of it. Harmless, and self-cleans on the
    # next write to each dataset.
    Dataset = apps.get_model("chord", "Dataset")
    for ds in Dataset.objects.all().iterator():
        raw = ds.data or {}
        ds.program_name = raw.get("program_name")
        ds.privacy = raw.get("privacy")
        ds.study_status = raw.get("study_status")
        ds.study_context = raw.get("study_context")
        # None rather than [] for "no value": the pydantic schema requires domain/taxa/keywords to be
        # either None or non-empty (min_length=1).
        ds.domain = raw.get("domain") or None
        ds.taxa_labels = [_label(t) for t in (raw.get("taxa") or [])] or None
        ds.keyword_labels = [_label(k) for k in (raw.get("keywords") or [])] or None
        license_ = raw.get("license")
        ds.license_label = license_.get("label") if isinstance(license_, dict) else None
        ds.save(
            update_fields=[
                "program_name",
                "privacy",
                "study_status",
                "study_context",
                "domain",
                "taxa_labels",
                "keyword_labels",
                "license_label",
            ]
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("chord", "0016_add_catalogue_facet_columns"),
    ]

    operations = [
        migrations.RunPython(backfill_catalogue_facet_columns, noop_reverse),
    ]
