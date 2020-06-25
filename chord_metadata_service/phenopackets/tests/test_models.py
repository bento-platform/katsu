from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from chord_metadata_service.resources.tests.constants import VALID_RESOURCE_1, VALID_RESOURCE_2
from . import constants as c
from .. import models as m


class BiosampleTest(TestCase):
    """ Test module for Biosample model """

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.procedure = m.Procedure.objects.create(**c.VALID_PROCEDURE_1)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(self.individual, self.procedure))
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(None, self.procedure))
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)

        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
        )
        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

    def test_biosample(self):
        biosample_one = m.Biosample.objects.get(
            tumor_progression__label='Primary Malignant Neoplasm',
            sampled_tissue__label__icontains='urinary bladder'
            )
        self.assertEqual(biosample_one.id, 'biosample_id:1')

    def test_string_representations(self):
        # Test __str__
        self.assertEqual(str(self.individual), str(self.individual.pk))
        self.assertEqual(str(self.procedure), str(self.procedure.pk))
        self.assertEqual(str(self.biosample_1), str(self.biosample_1.pk))
        self.assertEqual(str(self.meta_data), str(self.meta_data.pk))
        self.assertEqual(str(self.phenopacket), str(self.phenopacket.pk))


class PhenotypicFeatureTest(TestCase):
    """ Test module for PhenotypicFeature model. """

    def setUp(self):
        self.individual_1 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.individual_2 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_2)
        self.procedure = m.Procedure.objects.create(**c.VALID_PROCEDURE_1)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(
            self.individual_1, self.procedure)
        )
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(
            self.individual_2, self.procedure)
        )
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.phenopacket = m.Phenopacket.objects.create(
            id='phenopacket_id:1',
            subject=self.individual_2,
            meta_data=self.meta_data,
        )
        self.phenotypic_feature_1 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(biosample=self.biosample_1))
        self.phenotypic_feature_2 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(biosample=self.biosample_2, phenopacket=self.phenopacket))

    def test_phenotypic_feature(self):
        phenotypic_feature_query = m.PhenotypicFeature.objects.filter(
            severity__label='Mild',
            pftype__label='Proptosis'
        )
        phenotypic_feature_2 = m.PhenotypicFeature.objects.filter(phenopacket__id='phenopacket_id:1')
        self.assertEqual(m.PhenotypicFeature.objects.count(), 2)
        self.assertEqual(phenotypic_feature_query.count(), 2)
        self.assertEqual(phenotypic_feature_2.count(), 1)

    def test_phenotypic_feature_str(self):
        self.assertEqual(str(self.phenotypic_feature_1), str(self.phenotypic_feature_1.id))


class ProcedureTest(TestCase):
    def setUp(self):
        self.procedure_1 = m.Procedure.objects.create(**c.VALID_PROCEDURE_1)
        self.procedure_2 = m.Procedure.objects.create(**c.VALID_PROCEDURE_2)

    def test_procedure(self):
        procedure_query_1 = m.Procedure.objects.filter(
            body_site__label__icontains='arm'
            )
        procedure_query_2 = m.Procedure.objects.filter(code__id='NCIT:C28743')
        self.assertEqual(procedure_query_1.count(), 2)
        self.assertEqual(procedure_query_2.count(), 2)


class HtsFileTest(TestCase):
    def setUp(self):
        self.hts_file = m.HtsFile.objects.create(**c.VALID_HTS_FILE)

    def test_hts_file(self):
        hts_file = m.HtsFile.objects.get(genome_assembly='GRCh38')
        self.assertEqual(hts_file.uri, 'https://data.example/genomes/germline_wgs.vcf.gz')

    def test_hts_file_str(self):
        self.assertEqual(str(self.hts_file), 'https://data.example/genomes/germline_wgs.vcf.gz')


class GeneTest(TestCase):
    def setUp(self):
        self.gene_1 = m.Gene.objects.create(**c.VALID_GENE_1)

    def test_gene(self):
        gene_1 = m.Gene.objects.get(id='HGNC:347')
        self.assertEqual(gene_1.symbol, 'ETF1')
        with self.assertRaises(IntegrityError):
            m.Gene.objects.create(**c.DUPLICATE_GENE_2)

    def test_gene_str(self):
        self.assertEqual(str(self.gene_1), "HGNC:347")


class VariantTest(TestCase):
    def setUp(self):
        self.variant = m.Variant.objects.create(**c.VALID_VARIANT_1)

    def test_variant(self):
        variant_query = m.Variant.objects.filter(zygosity__id='NCBITaxon:9606')
        self.assertEqual(variant_query.count(), 1)

    def test_variant_str(self):
        self.assertEqual(str(self.variant), str(self.variant.id))


class DiseaseTest(TestCase):
    def setUp(self):
        self.disease_1 = m.Disease.objects.create(**c.VALID_DISEASE_1)

    def test_disease(self):
        disease_query = m.Disease.objects.filter(term__id='OMIM:164400')
        self.assertEqual(disease_query.count(), 1)

    def test_disease_str(self):
        self.assertEqual(str(self.disease_1), str(self.disease_1.id))


class GenomicInterpretationTest(TestCase):
    def setUp(self):
        self.gene = m.Gene.objects.create(**c.VALID_GENE_1)
        self.variant = m.Variant.objects.create(**c.VALID_VARIANT_1)
        self.genomic_interpretation = m.GenomicInterpretation.objects.create(
            **c.valid_genomic_interpretation(self.gene, self.variant)
            )

    def test_genomic_interpretation(self):
        genomic_interpretation_query = m.GenomicInterpretation.objects.filter(
            gene='HGNC:347')
        self.assertEqual(genomic_interpretation_query.count(), 1)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_validation_gene_or_variant(self):
        with self.assertRaises(ValidationError):
            m.GenomicInterpretation.objects.create(**c.valid_genomic_interpretation()).clean()

    def test_genomic_interpretation_str(self):
        self.assertEqual(str(self.genomic_interpretation), str(self.genomic_interpretation.id))


class DiagnosisTest(TestCase):
    def setUp(self):
        self.disease = m.Disease.objects.create(**c.VALID_DISEASE_1)

        self.gene = m.Gene.objects.create(**c.VALID_GENE_1)
        self.variant = m.Variant.objects.create(**c.VALID_VARIANT_1)
        self.genomic_interpretation_1 = m.GenomicInterpretation.objects.create(
            **c.valid_genomic_interpretation(self.gene, self.variant)
            )
        self.genomic_interpretation_2 = m.GenomicInterpretation.objects.create(
            **c.valid_genomic_interpretation(self.gene)
            )
        self.diagnosis = m.Diagnosis.objects.create(**c.valid_diagnosis(
            self.disease))
        self.diagnosis.genomic_interpretations.set([
            self.genomic_interpretation_1,
            self.genomic_interpretation_2
        ])

    def test_diagnosis(self):
        diagnosis = m.Diagnosis.objects.filter(disease__term__id='OMIM:164400')
        self.assertEqual(diagnosis.count(), 1)

    def test_diagnosis_str(self):
        self.assertEqual(str(self.diagnosis), str(self.diagnosis.id))


class InterpretationTest(TestCase):
    def setUp(self):
        self.disease = m.Disease.objects.create(**c.VALID_DISEASE_1)
        self.diagnosis = m.Diagnosis.objects.create(**c.valid_diagnosis(
            self.disease))
        self.meta_data_phenopacket = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.meta_data_interpretation = m.MetaData.objects.create(**c.VALID_META_DATA_2)

        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data_phenopacket,
        )
        self.interpretation = m.Interpretation.objects.create(**c.valid_interpretation(
            phenopacket=self.phenopacket,
            meta_data=self.meta_data_interpretation
            ))
        self.interpretation.diagnosis.set([self.diagnosis])

    def test_interpretation(self):
        interpretation_query = m.Interpretation.objects.filter(
            resolution_status='IN_PROGRESS'
            )
        self.assertEqual(interpretation_query.count(), 1)

    def test_interpretation_str(self):
        self.assertEqual(str(self.interpretation), str(self.interpretation.id))


class MetaDataTest(TestCase):
    def setUp(self):
        self.resource_1 = m.Resource.objects.create(**VALID_RESOURCE_1)
        self.resource_2 = m.Resource.objects.create(**VALID_RESOURCE_2)
        self.metadata = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.metadata.resources.set([self.resource_1, self.resource_2])

    def test_metadata(self):
        metadata = m.MetaData.objects.get(created_by__icontains='ksenia')
        self.assertEqual(metadata.submitted_by, 'Ksenia Zaytseva')
        self.assertEqual(metadata.resources.count(), 2)

    def test_metadata_str(self):
        self.assertEqual(str(self.metadata), str(self.metadata.id))
