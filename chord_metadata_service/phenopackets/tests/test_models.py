from django.core.exceptions import ValidationError
from django.test import TestCase
from django.db.models import Q
from chord_metadata_service.chord.tests.helpers import ProjectTestCase

from chord_metadata_service.resources.tests.constants import VALID_RESOURCE_1, VALID_RESOURCE_2
from chord_metadata_service.phenopackets.filters import (
    InterpretationFilter,
    filter_ontology,
    filter_extra_properties_datatype,
    PhenotypicFeatureFilter,
    PhenopacketFilter,
    GenomicInterpretationFilter
)
from chord_metadata_service.restapi.models import SchemaType

from . import constants as c
from .. import models as m


class BiosampleTest(ProjectTestCase):
    """ Test module for Biosample model """

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(self.individual))
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(None))
        self.biosample_3 = m.Biosample.objects.create(**{
            **c.valid_biosample_2(None),
            "id": 'biosample_id:3'
        })
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)

        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
            dataset=self.dataset,
        )
        # biosample_3 is not added to the phenopacket
        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

    def test_biosample(self):
        biosample_one = m.Biosample.objects.get(
            tumor_progression__label='Primary Malignant Neoplasm',
            sampled_tissue__label__icontains='urinary bladder'
        )
        self.assertEqual(biosample_one.id, 'biosample_id:1')
        self.assertEqual(biosample_one.schema_type, SchemaType.BIOSAMPLE)
        self.assertEqual(biosample_one.get_project_id(), self.project.identifier)

        # does not belong to a phenopacket => has no project
        self.assertIsNone(self.biosample_3.get_project_id())

    def test_string_representations(self):
        # Test __str__
        self.assertEqual(str(self.individual), str(self.individual.pk))
        self.assertEqual(str(self.biosample_1), str(self.biosample_1.pk))
        self.assertEqual(str(self.meta_data), str(self.meta_data.pk))
        self.assertEqual(str(self.phenopacket), str(self.phenopacket.pk))


class PhenotypicFeatureTest(TestCase):
    """ Test module for PhenotypicFeature model. """

    def setUp(self):
        self.individual_1 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.individual_2 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_2)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(
            self.individual_1)
        )
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(
            self.individual_2)
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

    def test_filtering(self):
        result = filter_ontology(m.PhenotypicFeature.objects.all(), "severity", "mild")
        self.assertEqual(len(result), 2)
        result = filter_ontology(m.PhenotypicFeature.objects.all(), "pftype", "HP:0000520")
        self.assertEqual(len(result), 2)
        f = PhenotypicFeatureFilter()
        result = f.filter_evidence(m.PhenotypicFeature.objects.all(), "evidence__evidence_code", "ECO:0006017")
        self.assertEqual(len(result), 2)
        result = filter_extra_properties_datatype(m.PhenotypicFeature.objects.all(), "extra_properties", "complication")
        self.assertEqual(len(result), 0)
        result = filter_extra_properties_datatype(m.PhenotypicFeature.objects.all(), "extra_properties", "symptom")
        self.assertEqual(len(result), 2)
        f = PhenotypicFeatureFilter(queryset=m.PhenotypicFeature.objects.all(),
                                    data={"individual": "patient:2,patient:1"})
        result = f.qs
        self.assertEqual(len(result), 1)


# class GeneTest(TestCase):
#     """ Test module for Gene model. """
#
#     def setUp(self):
#         self.gene_1 = m.Gene.objects.create(**c.VALID_GENE_1)
#
#     def test_gene(self):
#         gene_1 = m.Gene.objects.get(id='HGNC:347')
#         self.assertEqual(gene_1.symbol, 'ETF1')
#         with self.assertRaises(IntegrityError):
#             m.Gene.objects.create(**c.DUPLICATE_GENE_2)
#
#     def test_gene_str(self):
#         self.assertEqual(str(self.gene_1), "HGNC:347")


# class VariantTest(TestCase):
#     """ Test module for Variant model. """
#
#     def setUp(self):
#         self.variant = m.Variant.objects.create(**c.VALID_VARIANT_1)
#
#     def test_variant(self):
#         variant_query = m.Variant.objects.filter(zygosity__id='NCBITaxon:9606')
#         self.assertEqual(variant_query.count(), 1)
#
#     def test_variant_str(self):
#         self.assertEqual(str(self.variant), str(self.variant.id))


class GenomicInterpretationTest(TestCase):
    """ Test module for GenomicInterpretation model. """

    def setUp(self):
        self.gene_descriptor = m.GeneDescriptor.objects.create(**c.VALID_GENE_DESCRIPTOR_1)
        self.variant_descriptor = m.VariationDescriptor.objects.create(**c.VALID_VARIANT_DESCRIPTOR)
        self.variant_interpretation = m.VariantInterpretation.objects.create(
            **c.valid_variant_interpretation(self.variant_descriptor)
        )
        self.genomic_interpretation = m.GenomicInterpretation.objects.create(
            **c.valid_genomic_interpretation(self.gene_descriptor, self.variant_interpretation)
        )

    def test_genomic_interpretation(self):
        self._test_gene_filter("hgnc", 1)
        self._test_gene_filter("ensembl", 1)
        self._test_gene_filter("ncbigene", 1)
        self._test_gene_filter("expect_0", 0)

        self._test_variant_filter("NOT_PROVIDED", 1)
        self._test_variant_filter("UNKNOWN_ACTIONABILITY", 1)
        self._test_variant_filter("clinvar:13294", 1)
        self._test_variant_filter("expect_0", 0)

        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_validation_gene_or_variant(self):
        with self.assertRaises(ValidationError):
            m.GenomicInterpretation.objects.create(**c.valid_genomic_interpretation()).clean()

    def test_genomic_interpretation_str(self):
        self.assertEqual(str(self.genomic_interpretation), str(self.genomic_interpretation.id))

    def _test_gene_filter(self, value, count: int):
        qs = GenomicInterpretationFilter().filter_gene(
            m.GenomicInterpretation.objects.all(),
            "gene_descriptor",
            value
        )
        self.assertEqual(qs.count(), count)

    def _test_variant_filter(self, value, count: int):
        qs = GenomicInterpretationFilter().filter_variant(
            m.GenomicInterpretation.objects.all(),
            "variant_interpretation",
            value
        )
        self.assertEqual(qs.count(), count)


class DiagnosisTest(TestCase):
    """ Test module for Diagnosis model. """

    def setUp(self):
        # With GeneDescriptor
        self.gene_descriptor = m.GeneDescriptor.objects.create(**c.VALID_GENE_DESCRIPTOR_1)

        # With VariantInterpretation
        self.variant_descriptor = m.VariationDescriptor.objects.create(
            **c.valid_variant_descriptor(self.gene_descriptor))
        self.variant_interpretation = m.VariantInterpretation.objects.create(**c.valid_variant_interpretation(
            variant_descriptor=self.variant_descriptor
        ))

        self.genomic_interpretation_1 = m.GenomicInterpretation.objects.create(
            **c.valid_genomic_interpretation(self.gene_descriptor, self.variant_interpretation)
        )
        self.genomic_interpretation_2 = m.GenomicInterpretation.objects.create(
            **c.valid_genomic_interpretation(self.gene_descriptor)
        )
        self.diagnosis = m.Diagnosis.objects.create(**c.valid_diagnosis(c.VALID_DISEASE_ONTOLOGY))
        self.diagnosis.genomic_interpretations.set([
            self.genomic_interpretation_1,
            self.genomic_interpretation_2
        ])

    def test_diagnosis(self):
        self._test_disease_filter(Q(disease_ontology__id__icontains="omim"), 1)
        self._test_disease_filter(Q(disease_ontology__id__icontains="Omim:1644"), 1)
        self._test_disease_filter(Q(disease_ontology__id__icontains="should_not_match"), 0)

        self._test_disease_filter(Q(disease_ontology__label__icontains="Spinocerebellar ataxia 1"), 1)
        self._test_disease_filter(Q(disease_ontology__label__icontains="should_not_match"), 0)

    def test_diagnosis_str(self):
        self.assertEqual(str(self.diagnosis), str(self.diagnosis.id))

    def _test_disease_filter(self, filter: Q, count: int):
        result = m.Diagnosis.objects.all().filter(filter)
        self.assertEqual(result.count(), count)


class InterpretationTest(TestCase):
    """ Test module for Interpretation model. """

    def setUp(self):
        self.disease_ontology = c.VALID_DISEASE_ONTOLOGY
        self.diagnosis = m.Diagnosis.objects.create(**c.valid_diagnosis(self.disease_ontology))
        self.meta_data_phenopacket = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.meta_data_interpretation = m.MetaData.objects.create(**c.VALID_META_DATA_2)

        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data_phenopacket,
        )
        self.interpretation = m.Interpretation.objects.create(**c.valid_interpretation(self.diagnosis))

    def test_interpretation(self):
        interpretation_qs = m.Interpretation.objects.filter(
            progress_status='IN_PROGRESS'
        )
        self.assertEqual(interpretation_qs.count(), 1)

        self._test_interpretation_filter(self.disease_ontology['id'], 1)
        self._test_interpretation_filter("MONDO:0005015", 0)

    def test_interpretation_str(self):
        self.assertEqual(str(self.interpretation), str(self.interpretation.id))

    def _test_interpretation_filter(self, value, count: int):
        qs = InterpretationFilter().filter_diagnosis(
            m.Interpretation.objects.all(),
            "diagnosis__disease_ontology__id",
            value,
        )
        self.assertEqual(qs.count(), count)


class MetaDataTest(TestCase):
    """ Test module for MetaData model. """

    def setUp(self):
        self.resource_1 = m.Resource.objects.create(**VALID_RESOURCE_1)
        self.resource_2 = m.Resource.objects.create(**VALID_RESOURCE_2)
        self.metadata = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.metadata.resources.set([self.resource_1, self.resource_2])

    def test_metadata(self):
        metadata = m.MetaData.objects.get(created_by__icontains='victor')
        self.assertEqual(metadata.submitted_by, c.VALID_META_DATA_2["submitted_by"])
        self.assertEqual(metadata.resources.count(), 2)

    def test_metadata_str(self):
        self.assertEqual(str(self.metadata), str(self.metadata.id))


class PhenopacketTest(ProjectTestCase):
    """ Test module for Phenopacket model """

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.disease = m.Disease.objects.create(**c.VALID_DISEASE_1)
        self.interpretation = m.Interpretation.objects.create(
            **c.valid_interpretation(
                diagnosis=m.Diagnosis.objects.create(
                    **c.valid_diagnosis(
                        disease=c.VALID_DISEASE_ONTOLOGY)
                )
            )
        )
        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
            measurements=[c.VALID_MEASUREMENT_1, c.VALID_MEASUREMENT_2],
            medical_actions=c.VALID_MEDICAL_ACTIONS,
            dataset=self.dataset,
        )
        self.phenopacket.diseases.set([self.disease])
        self.phenopacket.interpretations.set([self.interpretation])
        self.phenotypic_feature_1 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )
        self.phenotypic_feature_2 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )

    def test_phenopacket(self):
        phenopacket = m.Phenopacket.objects.filter(id="phenopacket_id:1")
        self.assertEqual(len(phenopacket), 1)
        self.assertEqual(len(phenopacket.values("phenotypic_features")), 2)
        self.assertEqual(len(phenopacket.values("diseases")), 1)
        instance = phenopacket.get()
        self.assertEqual(instance.schema_type, SchemaType.PHENOPACKET)
        self.assertEqual(instance.get_project_id(), self.project.identifier)

    def test_filtering(self):
        f = PhenopacketFilter()
        number_of_found_pf = len(m.Phenopacket.objects.filter(phenotypic_features__excluded=False))
        # all phenotypic feature constants have excluded=True
        result = f.filter_found_phenotypic_feature(m.Phenopacket.objects.all(), "phenotypic_features", "proptosis")
        self.assertEqual(len(result), 0)
        result = f.filter_found_phenotypic_feature(m.Phenopacket.objects.all(), "phenotypic_features", "HP:0000520")
        self.assertEqual(len(result), 0)
        self.assertEqual(len(result), number_of_found_pf)
        result_label = filter_ontology(m.Phenopacket.objects.all(), "diseases__term", "Spinocerebellar ataxia 1")
        self.assertEqual(len(result_label), 1)
        result_id = filter_ontology(m.Phenopacket.objects.all(), "diseases__term", "OMIM:164400")
        self.assertEqual(len(result_label), len(result_id))
