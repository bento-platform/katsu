from django.core.exceptions import ValidationError
from django.db.models import Q
from django.test import TestCase

from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.discovery.full_text_search import FTSHelpersMixin
from chord_metadata_service.geo.models import GeoLocation
from chord_metadata_service.geo.tests.constants import GEO_LOCATION_1
from chord_metadata_service.resources.tests.constants import VALID_RESOURCE_1, VALID_RESOURCE_2
from chord_metadata_service.phenopackets.filters import (
    filter_ontology,
    filter_extra_properties_datatype,
    PhenopacketFilter,
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
        self.assertEqual(biosample_one.id, 'katsu.biosample_id:1')
        self.assertEqual(biosample_one.schema_type, SchemaType.BIOSAMPLE)
        self.assertEqual(biosample_one.get_project_id(), self.project.identifier)

        # does not belong to a phenopacket => has no project
        self.assertIsNone(self.biosample_3.get_project_id())

    def test_biosample_with_location_collected(self):
        geo = GeoLocation.objects.create(**GEO_LOCATION_1)
        bs = c.valid_biosample_1(self.individual)
        bs["id"] = "katsu.biosample_id:4"
        bs["location_collected"] = geo
        b = m.Biosample.objects.create(**bs)

        self.assertEqual(str(b.location_collected), "Kingston (44.2380626, -76.512335)")

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
        result = filter_extra_properties_datatype(m.PhenotypicFeature.objects.all(), "extra_properties", "complication")
        self.assertEqual(len(result), 0)
        result = filter_extra_properties_datatype(m.PhenotypicFeature.objects.all(), "extra_properties", "symptom")
        self.assertEqual(len(result), 2)


class GeneDescriptorTest(TestCase):
    def setUp(self):
        self.gene_descriptor = m.GeneDescriptor.objects.create(**c.VALID_GENE_DESCRIPTOR_1)

    def test_gene_descriptor_fts_repr(self):
        self.assertEqual(
            FTSHelpersMixin.fts_repr_values_to_str(self.gene_descriptor.fts_repr_values()),
            "HGNC:347 ETF1 ensembl:ENSRNOG00000019450 ncbigene:307503 comment test data",
        )


class GenomicInterpretationTest(TestCase):
    """ Test module for GenomicInterpretation model. """

    def setUp(self):
        self.maxDiff = None  # for seeing long string diffs

        self.gene_descriptor = m.GeneDescriptor.objects.create(**c.VALID_GENE_DESCRIPTOR_1)
        self.variant_descriptor = m.VariationDescriptor.objects.create(**c.VALID_VARIANT_DESCRIPTOR)
        self.variant_interpretation = m.VariantInterpretation.objects.create(
            **c.valid_variant_interpretation(self.variant_descriptor)
        )
        self.genomic_interpretation = m.GenomicInterpretation.objects.create(
            **c.valid_genomic_interpretation(self.gene_descriptor, self.variant_interpretation)
        )

    def test_genomic_interpretation(self):
        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_validation_gene_or_variant(self):
        with self.assertRaises(ValidationError):
            m.GenomicInterpretation.objects.create(**c.valid_genomic_interpretation()).clean()

    def test_variant_descriptor_repr(self):
        self.assertEqual(
            FTSHelpersMixin.fts_repr_values_to_str(self.variant_descriptor),
            "clinvar:13294 syntax hgvs value NM_001848.2:c.877G\u003eA GENO:0000135 heterozygous",
        )

    def test_genomic_interpretation_str(self):
        self.assertEqual(str(self.genomic_interpretation), str(self.genomic_interpretation.id))

    def test_genomic_interpretation_fts_repr(self):
        self.assertEqual(
            FTSHelpersMixin.fts_repr_values_to_str(self.genomic_interpretation),
            (
                "CANDIDATE HGNC:347 ETF1 ensembl:ENSRNOG00000019450 ncbigene:307503 comment test data NOT_PROVIDED"
                " UNKNOWN_ACTIONABILITY clinvar:13294 syntax hgvs value NM_001848.2:c.877G\u003eA GENO:0000135 "
                "heterozygous comment test data"
            ),
        )


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
        self._test_disease_filter(Q(disease__id__icontains="omim"), 1)
        self._test_disease_filter(Q(disease__id__icontains="Omim:1644"), 1)
        self._test_disease_filter(Q(disease__id__icontains="should_not_match"), 0)

        self._test_disease_filter(Q(disease__label__icontains="Spinocerebellar ataxia 1"), 1)
        self._test_disease_filter(Q(disease__label__icontains="should_not_match"), 0)

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

    def test_interpretation_str(self):
        self.assertEqual(str(self.interpretation), str(self.interpretation.id))


class MetaDataTest(TestCase):
    """ Test module for MetaData model. """

    def setUp(self):
        self.resource_1 = m.Resource.objects.create(**VALID_RESOURCE_1)
        self.resource_2 = m.Resource.objects.create(**VALID_RESOURCE_2)
        self.metadata = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.metadata.resources.set([self.resource_1, self.resource_2])

    def test_metadata(self):
        metadata = m.MetaData.objects.get(created_by__icontains="victor")
        self.assertEqual(metadata.submitted_by, c.VALID_META_DATA_2["submitted_by"])
        self.assertEqual(metadata.resources.count(), 2)
        self.assertTupleEqual(
            metadata.fts_repr_values(),
            (
                c.VALID_META_DATA_2["created_by"],
                c.VALID_META_DATA_2["submitted_by"],
                c.VALID_META_DATA_2["updates"],
                c.VALID_META_DATA_2["external_references"],
                None,
            )
        )

    def test_metadata_str(self):
        self.assertEqual(str(self.metadata), str(self.metadata.id))


class PhenopacketTest(ProjectTestCase):
    """ Test module for Phenopacket model """

    def setUp(self):
        self.maxDiff = None

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

        # force back-populate FTS representations
        self.phenopacket.save()

    def test_phenopacket_without_individual(self):
        obj = m.Phenopacket.objects.create(
            id="phenopacket_id:2",
            meta_data=self.meta_data,
            dataset=self.dataset,
        )

        # should be populated with metadata stuff
        self.assertEqual(obj.fts_extra, "David Lougheed David Lougheed")

    def test_phenopacket(self):
        phenopacket = m.Phenopacket.objects.filter(id="phenopacket_id:1")
        self.assertEqual(len(phenopacket), 1)
        self.assertEqual(len(phenopacket.values("phenotypic_features")), 2)
        self.assertEqual(len(phenopacket.values("diseases")), 1)
        instance = phenopacket.get()
        self.assertEqual(instance.schema_type, SchemaType.PHENOPACKET)
        self.assertEqual(instance.get_project_id(), self.project.identifier)
        self.assertEqual(
            instance.fts_extra,
            (
                "interpretation:1 IN_PROGRESS interpretation:1 OMIM:164400 Spinocerebellar ataxia 1 comment test data "
                "Test interpretation comment test data OMIM:164400 Spinocerebellar ataxia 1 P25Y3M2D P28Y3M2D "
                "NCIT:C48233 Cancer TNM Finding by Site NCIT:C28091 Gleason Score 7 comment test data This is a test "
                "phenotypic feature HP:0000520 Proptosis excluded HP:0012825 Mild HP:0012825 Mild HP:0012826 Moderate "
                "Congenital onset (HP:0003577) reference PMID:30962759 Recurrent Erythema Nodosum in a Child with a "
                "SHOC2 Gene Mutation evidence_code ECO:0006017 Author statement from published clinical study used in "
                "manual assertion comment test data datatype symptom This is a test phenotypic feature HP:0000520 "
                "Proptosis excluded HP:0012825 Mild HP:0012825 Mild HP:0012826 Moderate Congenital onset (HP:0003577) "
                "reference PMID:30962759 Recurrent Erythema Nodosum in a Child with a SHOC2 Gene Mutation evidence_code"
                " ECO:0006017 Author statement from published clinical study used in manual assertion comment test data"
                " datatype symptom David Lougheed David Lougheed"
            ),
        )  # should be populated with interpretations + diseases + phenotypic features + metadata stuff

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
