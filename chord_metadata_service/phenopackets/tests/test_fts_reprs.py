from django.test import TestCase

from chord_metadata_service.discovery.full_text_search import FTSHelpersMixin
from chord_metadata_service.phenopackets.models import GeneDescriptor
from .constants import VALID_GENE_DESCRIPTOR_1


class PhenopacketFTSReprsTest(TestCase):

    def test_gene_descriptor(self):
        gd = GeneDescriptor.objects.create(**VALID_GENE_DESCRIPTOR_1)
        self.assertEqual(
            FTSHelpersMixin.fts_repr_values_to_str(gd.fts_repr_values()),
            "HGNC:347 ETF1 ensembl:ENSRNOG00000019450 ncbigene:307503 comment test data",
        )
