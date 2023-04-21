from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from chord_metadata_service.mohpackets.models import (
    Program,
    Donor,
    PrimaryDiagnosis,
    Specimen,
)

from chord_metadata_service.mohpackets.serializers import (
    ProgramSerializer,
    DonorSerializer,
    PrimaryDiagnosisSerializer,
    SpecimenSerializer,
    SampleRegistrationSerializer,
)

def get_invalid_ids():
    """Returns the invalid values to test in ID fields."""
    return ["f" * 65, ""]

def get_invalid_choices():
    """Returns the invalid values to test in multiple choice fields."""
    return ["foo", 1, True]

def get_invalid_dates():
    """Returns the invalid values to test in Date fields."""
    return ["foo", "03", "114", "443-12", 1, True]


class ProgramTest(TestCase):
    def setUp(self):
        self.program_id = "SYNTHETIC"
        self.program = Program.objects.create(program_id=self.program_id)
        
    def test_program_creation(self):
        self.assertIsInstance(self.program, Program)
        self.assertEqual(self.program.program_id, self.program_id)
        self.assertIsNotNone(self.program.created)
        self.assertIsNotNone(self.program.updated)
    
    def test_unique_id (self):
        with self.assertRaises(IntegrityError):
            self.program = Program.objects.create(program_id=self.program_id)
    
    # TODO: This test passes with valid values too, the other ID fields don't
    def test_invalid_program_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            with self.subTest(value=value):
                self.program_id = value
                self.serializer = ProgramSerializer(instance=self.program, data=self.program_id)
                self.assertFalse(self.serializer.is_valid())
    

class DonorTest(TestCase):
    def setUp(self):
        self.model = "donor"
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.valid_values = {
            "submitter_donor_id": "DONOR_1",
            "program_id": self.program,
            "is_deceased": True,
            "cause_of_death": "Died of cancer",
            "date_of_birth": "1975-08",
            "date_of_death": "2009-08",
            "primary_site": [
                "Adrenal gland",
                "Other and ill-defined sites in lip, oral cavity and pharynx",
            ]
        }
        self.donor = Donor.objects.create(**self.valid_values)

    def test_donor_creation(self):
        self.assertIsInstance(self.donor, Donor)
        self.assertEqual(self.donor.submitter_donor_id, "DONOR_1")
        self.assertEqual(self.donor.program_id, self.program)
        self.assertTrue(self.donor.is_deceased)
        self.assertEqual(self.donor.cause_of_death, "Died of cancer")
        self.assertEqual(self.donor.date_of_birth, "1975-08")
        self.assertEqual(self.donor.date_of_death, "2009-08")
        self.assertEqual(self.donor.primary_site, [
            "Adrenal gland",
            "Other and ill-defined sites in lip, oral cavity and pharynx"
        ])
    
    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.program = Donor.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["submitter_donor_id"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_is_deceased(self):
        self.donor.is_deceased = "foo"
        with self.assertRaises(ValidationError):
            self.donor.save()

    def test_invalid_cause_of_death(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["cause_of_death"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_date_of_death(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_death"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
        
    def test_invalid_date_of_birth(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_birth"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_primary_site(self):
        invalid_values = ["foo", ["foo"]]
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["primary_site"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())


class PrimaryDiagnosisTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(submitter_donor_id="DONOR_1", 
                                          program_id=self.program,
                                          primary_site=["Adrenal gland"]
        )
        self.valid_values = {
            "submitter_primary_diagnosis_id": "PRIMARY_DIAGNOSIS_1",
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "date_of_diagnosis": "2019-11",
            "cancer_type_code": "C02.1",
            "basis_of_diagnosis": "Unknown",
            "lymph_nodes_examined_status": "Not applicable",
            "lymph_nodes_examined_method": "Physical palpation of patient",
            "number_lymph_nodes_positive": 15,
            "clinical_tumour_staging_system": "Lugano staging system",
            "clinical_t_category": "T2a1",
            "clinical_n_category": "N2mi",
            "clinical_m_category": "M1b(0)",
            "clinical_stage_group": "Stage IA3"
        }
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(**self.valid_values)
    
    def test_primary_diagnosis_creation(self):
        self.assertIsInstance(self.primary_diagnosis, PrimaryDiagnosis)
        self.assertEqual(self.primary_diagnosis.submitter_primary_diagnosis_id, "PRIMARY_DIAGNOSIS_1")
        self.assertEqual(self.primary_diagnosis.program_id, self.program)
        self.assertEqual(self.primary_diagnosis.submitter_donor_id, self.donor)
        self.assertEqual(self.primary_diagnosis.date_of_diagnosis, "2019-11")
        self.assertEqual(self.primary_diagnosis.cancer_type_code, "C02.1")
        self.assertEqual(self.primary_diagnosis.basis_of_diagnosis, "Unknown")
        self.assertEqual(self.primary_diagnosis.lymph_nodes_examined_status, "Not applicable")
        self.assertEqual(self.primary_diagnosis.lymph_nodes_examined_method, "Physical palpation of patient")
        self.assertEqual(self.primary_diagnosis.number_lymph_nodes_positive, 15)
        self.assertEqual(self.primary_diagnosis.clinical_tumour_staging_system, "Lugano staging system")
        self.assertEqual(self.primary_diagnosis.clinical_t_category, "T2a1")
        self.assertEqual(self.primary_diagnosis.clinical_n_category, "N2mi")
        self.assertEqual(self.primary_diagnosis.clinical_m_category, "M1b(0)")
        self.assertEqual(self.primary_diagnosis.clinical_stage_group, "Stage IA3")

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.program = PrimaryDiagnosis.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_primary_diagnosis_id"] = value
            self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_date_of_diagnosis(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_diagnosis"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    # TODO: write regex for testing
    # def test_invalid_cancer_type_code(self):
    #     self.valid_values["cancer_type_code"] = "foo"
    #     self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
    #     self.assertFalse(self.serializer.is_valid())

    def test_invalid_basis_of_diagnosis(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["basis_of_diagnosis"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_lymph_nodes_examined_status(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["lymph_nodes_examined_status"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_number_lymph_nodes_positive(self):
        self.primary_diagnosis.number_lymph_nodes_positive = "foo"
        with self.assertRaises(ValueError):
            self.primary_diagnosis.save()
    
    def test_invalid_clinical_tumour_staging_system(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_tumour_staging_system"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_t_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_t_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_n_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_n_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_m_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_m_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_stage_group(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_stage_group"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())


class TestSpecimen(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(submitter_donor_id="DONOR_1", 
                                          program_id=self.program,
                                          primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id = "PRIMARY_DIAGNOSIS_1",
            program_id = self.program,
            submitter_donor_id = self.donor
        )
        self.valid_values = {
            "submitter_specimen_id": "SPECIMEN_1",
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_primary_diagnosis_id": self.primary_diagnosis,
            "pathological_tumour_staging_system": "AJCC 6th edition",
            "pathological_t_category": "Tis",
            "pathological_n_category": "N0b",
            "pathological_m_category": "M1a",
            "pathological_stage_group": "Stage IAS",
            "specimen_collection_date": "2021-06-25",
            "specimen_storage": "Cut slide",
            "tumour_histological_type": "8209/3",
            "specimen_anatomic_location": "C43.9",
            "reference_pathology_confirmed_diagnosis": "Not done",
            "reference_pathology_confirmed_tumour_presence": "Yes",
            "tumour_grading_system": "ISUP grading system",
            "tumour_grade": "G2",
            "percent_tumour_cells_range": "51-100%",
            "percent_tumour_cells_measurement_method": "Image analysis"
        }
        self.specimen = Specimen.objects.create(**self.valid_values)
    
    def test_specimen_creation(self):
        self.assertIsInstance(self.specimen, Specimen)
        self.assertEqual(self.specimen.submitter_specimen_id, "SPECIMEN_1")
        self.assertEqual(self.specimen.program_id, self.program)
        self.assertEqual(self.specimen.submitter_donor_id, self.donor)
        self.assertEqual(self.specimen.submitter_primary_diagnosis_id, self.primary_diagnosis)
        self.assertEqual(self.specimen.pathological_tumour_staging_system, "AJCC 6th edition")
        self.assertEqual(self.specimen.pathological_t_category, "Tis")
        self.assertEqual(self.specimen.pathological_n_category, "N0b")
        self.assertEqual(self.specimen.pathological_m_category, "M1a")
        self.assertEqual(self.specimen.pathological_stage_group, "Stage IAS")
        self.assertEqual(self.specimen.specimen_collection_date, "2021-06-25")
        self.assertEqual(self.specimen.specimen_storage, "Cut slide")
        self.assertEqual(self.specimen.tumour_histological_type, "8209/3")
        self.assertEqual(self.specimen.specimen_anatomic_location, "C43.9")
        self.assertEqual(self.specimen.reference_pathology_confirmed_diagnosis, "Not done")
        self.assertEqual(self.specimen.reference_pathology_confirmed_tumour_presence, "Yes")
        self.assertEqual(self.specimen.tumour_grading_system, "ISUP grading system")
        self.assertEqual(self.specimen.tumour_grade, "G2")
        self.assertEqual(self.specimen.percent_tumour_cells_range, "51-100%")
        self.assertEqual(self.specimen.percent_tumour_cells_measurement_method, "Image analysis")

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.program = Specimen.objects.create(**self.valid_values)
    
    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_specimen_id"] = value
            self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_pathological_tumour_staging_system(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_tumour_staging_system"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_pathological_t_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_t_category"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_pathological_n_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_n_category"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_pathological_m_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_m_category"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_pathological_stage_group(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_stage_group"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_specimen_collection_date(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_collection_date"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_specimen_storage(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_storage"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    # TODO: fix regular expression    
    # def test_invalid_tumour_histological_type(self):
    #     invalid_values = ["8260/3", 1]
    #     for value in invalid_values:
    #         with self.subTest(value=value):
    #             self.valid_values["tumour_histological_type"] = value
    #             self.serializer = SpecimenSerializer(instance=self.donor, data=self.valid_values)
    #             self.assertFalse(self.serializer.is_valid())

    # TODO: fix regular expression 
    # def test_specimen_anatomic_location(self):
    #     invalid_values = ["8260/3", 1]
    #     for value in invalid_values:
    #         with self.subTest(value=value):
    #             self.valid_values["specimen_anatomic_location"] = value
    #             self.serializer = SpecimenSerializer(instance=self.donor, data=self.valid_values)
    #             self.assertFalse(self.serializer.is_valid())
    
    def test_reference_pathology_confirmed_diagnosis(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["reference_pathology_confirmed_diagnosis"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_reference_pathology_confirmed_tumour_presence(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["reference_pathology_confirmed_tumour_presence"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_tumour_grading_system(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["tumour_grading_system"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_tumour_grade(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["tumour_grade"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_percent_tumour_cells_range(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["percent_tumour_cells_range"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_percent_tumour_cells_measurement_method(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["percent_tumour_cells_measurement_method"] = value
                self.serializer = SpecimenSerializer(instance=self.specimen, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())