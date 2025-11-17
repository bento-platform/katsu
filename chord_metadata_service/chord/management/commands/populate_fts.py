from django.core.management.base import BaseCommand
from chord_metadata_service.discovery.model_lookups import DISCOVERY_ENTITY_NAMES_TO_MODEL


class Command(BaseCommand):
    help = """
        Populates fts_extra fields for all discovery entity models.
    """

    def handle(self, *args, **options):
        for e, m in DISCOVERY_ENTITY_NAMES_TO_MODEL.items():
            self.stdout.write(f"Working on entity {e}\n")

            qs = m.objects.all()
            if e == "biosample":
                qs = qs.prefetch_related("phenotypic_features").select_related("location_collected")
            elif e == "phenopacket":
                qs = (
                    qs.prefetch_related("interpretations", "diseases", "phenotypic_features").select_related("meta_data")
                )
            elif e == "experiment":
                qs = qs.select_related("instrument")
            elif e == "individual":
                qs = qs.select_related("vital_status")

            for obj in qs:
                obj.save()
