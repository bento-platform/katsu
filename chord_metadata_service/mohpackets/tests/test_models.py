from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from chord_metadata_service.mohpackets.models import (
    Program,
    Donor,
    PrimaryDiagnosis
)

from chord_metadata_service.mohpackets.serializers import (
    ProgramSerializer,
    DonorSerializer,
    SpecimenSerializer,
    SampleRegistrationSerializer,
    PrimaryDiagnosisSerializer
)

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

    def test_invalid_program_id(self):
        # TODO: not sure why 42 is invalid
        values = ["f" * 62, 42, "", "SYNTHETIC"]
        for value in values:
            with self.subTest(value=value):
                self.program_id = value
                self.serializer = ProgramSerializer(instance=self.program, data=self.program_id)
                self.assertFalse(self.serializer.is_valid())
    

class DonorTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor_values = {
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
        self.donor = Donor.objects.create(**self.donor_values)
        self.serializer = DonorSerializer(instance=self.donor)

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
            self.program = Donor.objects.create(**self.donor_values)

    def test_invalid_id(self):
        values = ["f" * 65, ""]
        for value in values:
            with self.subTest(value=value):
                self.donor_values["submitter_donor_id"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_is_deceased(self):
        self.donor.is_deceased = "foo"
        with self.assertRaises(ValidationError):
            self.donor.save()

    def test_invalid_cause_of_death(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.donor_values["cause_of_death"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_date_of_death(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.donor_values["date_of_death"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
                self.assertFalse(self.serializer.is_valid())
        
    def test_invalid_date_of_birth(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.donor_values["date_of_birth"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_primary_site(self):
        values = ["foo", ["foo"]]
        for value in values:
            with self.subTest(value=value):
                self.donor_values["primary_site"] = value
                self.serializer = DonorSerializer(instance=self.donor, data=self.donor_values)
                self.assertFalse(self.serializer.is_valid())


class PrimaryDiagnosisTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(submitter_donor_id="DONOR_1", 
                                          program_id=self.program,
                                          primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis_values = {
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
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(**self.primary_diagnosis_values)
        self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis)
    
    def test_primary_diagnosis_creation(self):
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
            self.program = PrimaryDiagnosis.objects.create(**self.primary_diagnosis_values)

    def test_invalid_id(self):
        values = ["f" * 65, ""]
        for value in values:
            self.primary_diagnosis_values["submitter_primary_diagnosis_id"] = value
            self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
            self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_date_of_diagnosis(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["date_of_diagnosis"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())

    # TODO: write regex for testing
    # def test_invalid_cancer_type_code(self):
    #     self.primary_diagnosis_values["cancer_type_code"] = "foo"
    #     self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
    #     self.assertFalse(self.serializer.is_valid())

    def test_invalid_basis_of_diagnosis(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["basis_of_diagnosis"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_lymph_nodes_examined_status(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["lymph_nodes_examined_status"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_number_lymph_nodes_positive(self):
        self.primary_diagnosis.number_lymph_nodes_positive = "foo"
        with self.assertRaises(ValueError):
            self.primary_diagnosis.save()
    
    def test_invalid_clinical_tumour_staging_system(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["clinical_tumour_staging_system"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_t_category(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["clinical_t_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_n_category(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["clinical_n_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_m_category(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["clinical_m_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_clinical_stage_group(self):
        values = ["foo", 1]
        for value in values:
            with self.subTest(value=value):
                self.primary_diagnosis_values["clinical_stage_group"] = value
                self.serializer = PrimaryDiagnosisSerializer(instance=self.primary_diagnosis, data=self.primary_diagnosis_values)
                self.assertFalse(self.serializer.is_valid())