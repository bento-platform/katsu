from django.test import TestCase
from dateutil.parser import isoparse

from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.views_ingest import create_phenotypic_feature, ingest_phenopacket
from chord_metadata_service.phenopackets.models import PhenotypicFeature, Phenopacket

from .constants import VALID_DATA_USE_1
from .example_ingest import EXAMPLE_INGEST


class IngestTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)

    def test_create_pf(self):
        p1 = create_phenotypic_feature({
            "description": "test",
            "type": {
                "id": "HP:0000790",
                "label": "Hematuria"
            },
            "negated": False,
            "modifier": [],
            "evidence": []
        })

        p2 = PhenotypicFeature.objects.get(description="test")

        self.assertEqual(p1.pk, p2.pk)

    def test_ingesting_json(self):
        p = ingest_phenopacket(EXAMPLE_INGEST, self.d.identifier)
        self.assertEqual(p.id, Phenopacket.objects.get(id=p.id).id)

        self.assertEqual(p.subject.id, EXAMPLE_INGEST["subject"]["id"])
        self.assertEqual(p.subject.date_of_birth, isoparse(EXAMPLE_INGEST["subject"]["date_of_birth"]))
        self.assertEqual(p.subject.sex, EXAMPLE_INGEST["subject"]["sex"])
        self.assertEqual(p.subject.karyotypic_sex, EXAMPLE_INGEST["subject"]["karyotypic_sex"])

        pfs = list(p.phenotypic_features.all().order_by("pftype__id"))

        self.assertEqual(len(pfs), 2)
        self.assertEqual(pfs[0].description, EXAMPLE_INGEST["phenotypic_features"][0]["description"])
        self.assertEqual(pfs[0].pftype["id"], EXAMPLE_INGEST["phenotypic_features"][0]["type"]["id"])
        self.assertEqual(pfs[0].pftype["label"], EXAMPLE_INGEST["phenotypic_features"][0]["type"]["label"])
        self.assertEqual(pfs[0].negated, EXAMPLE_INGEST["phenotypic_features"][0]["negated"])
        # TODO: Test more properties

        diseases = list(p.diseases.all().order_by("term__id"))
        self.assertEqual(len(diseases), 1)
        # TODO: More

        # TODO: Test Metadata

        biosamples = list(p.biosamples.all().order_by("id"))
        self.assertEqual(len(biosamples), 5)
        # TODO: More
