from django.test import TestCase

from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Gene
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_MCODE_JSON
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.restapi.tests.utils import load_local_json

from ..models import (
    MCodePacket, CancerCondition, MedicationStatement,
    CancerRelatedProcedure, GenomicsReport, GeneticSpecimen,
    CancerGeneticVariant, GenomicRegionStudied, TNMStaging,
)

EXAMPLE_INGEST_MCODE_JSON = load_local_json("example_mcode_json.json")


class IngestMcodeJsonTest(TestCase):

    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset",
                                        data_use=VALID_DATA_USE_1,
                                        project=p)

    def test_ingest_mcodepacket_json(self):
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_MCODE_JSON](EXAMPLE_INGEST_MCODE_JSON, self.d.identifier)
        self.assertEqual(len(MCodePacket.objects.all()), 1)
        self.assertEqual(len(Individual.objects.all()), 1)
        individual = Individual.objects.get(id="ind:HG00096")
        self.assertEqual(individual.sex, "FEMALE")
        self.assertIsNotNone(individual.date_of_birth)
        self.assertEqual(individual.karyotypic_sex, "XX")
        self.assertIsNotNone(individual.taxonomy)
        self.assertEqual(individual.active, True)
        self.assertEqual(individual.deceased, False)
        self.assertIsNotNone(individual.comorbid_condition)
        self.assertIsInstance(individual.comorbid_condition, dict)
        self.assertIn("clinical_status", individual.comorbid_condition.keys())
        self.assertIn("code", individual.comorbid_condition.keys())
        self.assertIsInstance(individual.ecog_performance_status, dict)
        self.assertEqual(individual.ecog_performance_status["label"], "Fully active")
        self.assertEqual(individual.ecog_performance_status["id"], "0")
        self.assertIsInstance(individual.karnofsky, dict)
        self.assertEqual(individual.karnofsky["label"], "Normal, no complaints; no evidence of disease")
        self.assertEqual(individual.karnofsky["id"], "100")
        self.assertEqual(individual.race, "Unknown")
        self.assertEqual(individual.ethnicity, "Unknown")
        # cancer condition
        self.assertEqual(len(CancerCondition.objects.all()), 1)
        cancer_condition = CancerCondition.objects.filter(condition_type="primary")[0]
        self.assertEqual("active", cancer_condition.clinical_status["label"])
        self.assertEqual("SNOMED:24028007", cancer_condition.laterality["id"])
        self.assertIsInstance(cancer_condition.body_site, list)
        self.assertEqual("SNOMED:253035009", cancer_condition.histology_morphology_behavior["id"])
        # cancer condition tnm staging
        self.assertEqual(len(TNMStaging.objects.all()), 2)
        for tnm_staging in TNMStaging.objects.all():
            self.assertIsNotNone(tnm_staging.tnm_type)
            for field in ["stage_group", "primary_tumor_category",
                          "regional_nodes_category", "distant_metastases_category"]:
                self.assertIsNotNone(tnm_staging.__dict__[field])
                self.assertIsInstance(tnm_staging.__dict__[field], dict)

        # mcodepacket
        self.assertEqual(len(MCodePacket.objects.all()), 1)
        mcodepacket = MCodePacket.objects.all()[0]
        self.assertEqual(mcodepacket.cancer_disease_status["label"], "Patient's condition improved")
        # medication statement
        self.assertEqual(len(MedicationStatement.objects.all()), 1)
        # tumor marker
        self.assertEqual(len(CancerRelatedProcedure.objects.all()), 1)
        # genomics report
        self.assertEqual(len(GenomicsReport.objects.all()), 1)
        genomics_report = GenomicsReport.objects.get(id="3000")
        self.assertIn("DNA double strand", genomics_report.code["label"])
        self.assertIn("Cancer Centre", genomics_report.performing_organization_name)
        self.assertIsNotNone(genomics_report.issued)
        # genetic specimen
        self.assertEqual(len(GeneticSpecimen.objects.all()), 3)
        # 1
        genetic_specimen_1 = GeneticSpecimen.objects.get(id="3000-0")
        self.assertEqual("SNOMED:2855004", genetic_specimen_1.collection_body["id"])
        self.assertIn("cephalic vein", genetic_specimen_1.collection_body["label"])
        self.assertEqual("BLD", genetic_specimen_1.specimen_type["id"])
        self.assertIn("blood", genetic_specimen_1.specimen_type["label"])
        self.assertEqual("SNOMED:24028007", genetic_specimen_1.laterality["id"])
        self.assertEqual("Right (qualifier value)", genetic_specimen_1.laterality["label"])
        # 2
        genetic_specimen_2 = GeneticSpecimen.objects.get(id="3000-1")
        self.assertEqual("SNOMED:9568000", genetic_specimen_2.collection_body["id"])
        self.assertIn("areola", genetic_specimen_2.collection_body["label"])
        self.assertEqual("TUMOR", genetic_specimen_2.specimen_type["id"])
        self.assertIn("Tumor", genetic_specimen_2.specimen_type["label"])
        # 3
        genetic_specimen_3 = GeneticSpecimen.objects.get(id="3000-2")
        self.assertEqual("SNOMED:9568000", genetic_specimen_3.collection_body["id"])
        self.assertIn("areola", genetic_specimen_3.collection_body["label"])
        self.assertEqual("TISS", genetic_specimen_3.specimen_type["id"])
        self.assertIn("Tissue", genetic_specimen_3.specimen_type["label"])
        # genetic variant
        self.assertEqual(len(CancerGeneticVariant.objects.all()), 1)
        genetic_variant = CancerGeneticVariant.objects.get(id="3000")
        self.assertIsInstance(genetic_variant.data_value, dict)
        self.assertEqual("LOINC:LA4489-6", genetic_variant.data_value["id"])
        self.assertEqual("Unknown", genetic_variant.data_value["label"])
        for field in ["method", "amino_acid_change", "amino_acid_change_type", "cytogenetic_location",
                      "cytogenetic_nomenclature", "genomic_dna_change", "genomic_source_class"]:
            self.assertEqual("SNOMED:261665006", genetic_variant.__dict__[field]["id"])
            self.assertEqual("Unknown", genetic_variant.__dict__[field]["label"])
        self.assertIsNotNone(genetic_variant.extra_properties)
        # gene studied in genetic variant
        self.assertEqual(len(Gene.objects.all()), 1)
        gene = Gene.objects.get(id="HGNC:7989")
        self.assertEqual(gene.symbol, "NRAS")
        # genomic region studied
        self.assertEqual(len(GenomicRegionStudied.objects.all()), 1)
        genomic_region_studied = GenomicRegionStudied.objects.get(id="3000")
        for field in ["genomic_reference_sequence_id", "genomic_region_coordinate_system"]:
            self.assertEqual("SNOMED:261665006", genomic_region_studied.__dict__[field]["id"])
            self.assertEqual("Unknown", genomic_region_studied.__dict__[field]["label"])
        self.assertIsNotNone(genomic_region_studied.extra_properties)
        self.assertIsInstance(genomic_region_studied.dna_region_description, list)
        self.assertEqual(len(genomic_region_studied.dna_ranges_examined), 1)
        # gene mutation in genomic region studied
        self.assertIsInstance(genomic_region_studied.gene_mutation, list)
        self.assertEqual(len(genomic_region_studied.gene_mutation), 1)
        self.assertEqual(genomic_region_studied.gene_mutation[0]["id"], "HGVS:40488")
        self.assertIn("NM_002834.5", genomic_region_studied.gene_mutation[0]["label"])
        # gene studied in genomic region studied
        self.assertIsInstance(genomic_region_studied.gene_studied, list)
        self.assertEqual(len(genomic_region_studied.gene_studied), 1)
        self.assertEqual(genomic_region_studied.gene_studied[0]["id"], "HGNC:7989")
        self.assertEqual("NRAS", genomic_region_studied.gene_studied[0]["label"])
