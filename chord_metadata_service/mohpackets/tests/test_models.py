from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from chord_metadata_service.mohpackets.models import (
    Program,
    Donor,
    PrimaryDiagnosis,
    Specimen,
    SampleRegistration,
    Treatment,
    Chemotherapy,
    HormoneTherapy,
    Radiation,
    Immunotherapy,
    Surgery,
    FollowUp,
    Biomarker,
    Comorbidity
)

from chord_metadata_service.mohpackets.serializers import (
    ProgramSerializer,
    DonorSerializer,
    PrimaryDiagnosisSerializer,
    SpecimenSerializer,
    SampleRegistrationSerializer,
    TreatmentSerializer,
    ChemotherapySerializer,
    HormoneTherapySerializer,
    RadiationSerializer,
    ImmunotherapySerializer,
    SurgerySerializer,
    FollowUpSerializer,
    BiomarkerSerializer,
    ComorbiditySerializer
)


def get_invalid_ids():
    """Returns the invalid values to test in ID fields."""
    return ["f" * 65, ""]


def get_invalid_choices():
    """Returns the invalid values to test in choice fields."""
    return ["foo", 1, True]


def get_invalid_dates():
    """Returns the invalid values to test in date fields."""
    return ["foo", "03", "114", "443-12", "Feb-1995", 1, True]


def create_model(model):
    """Returns a reusable 'placeholder' model to set up foreign key fields in test instances."""
    if model == "program":
        return Program.objects.create(program_id="SYNTHETIC")
    elif model == "donor":
        return Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=create_model("program"),
            primary_site=["Adrenal gland"]
        )
    elif model == "primary_diagnosis":
        return PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=create_model("program"),
            submitter_donor_id=create_model("donor")
        )
    elif model == "treatment":
        return Treatment.objects.create(
            submitter_treatment_id="TREATMENT_1",
            program_id=create_model("program"),
            submitter_donor_id=create_model("donor"),
            submitter_primary_diagnosis_id=create_model("primary_diagnosis")
        )


class ProgramTest(TestCase):
    def setUp(self):
        self.program_id = "SYNTHETIC"
        self.program = Program.objects.create(program_id=self.program_id)

    def test_program_creation(self):
        self.assertIsInstance(self.program, Program)

    def test_program_fields(self):
        self.assertEqual(self.program.program_id, self.program_id)
        self.assertIsNotNone(self.program.created)
        self.assertIsNotNone(self.program.updated)

    def test_unique_id(self):
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

    def test_donor_fields(self):
        self.assertIsInstance(self.donor, Donor)
        self.assertEqual(self.donor.submitter_donor_id, "DONOR_1")
        self.assertEqual(self.donor.program_id, self.program)
        self.assertTrue(self.donor.is_deceased)
        self.assertEqual(self.donor.cause_of_death, "Died of cancer")
        self.assertEqual(self.donor.date_of_birth, "1975-08")
        self.assertEqual(self.donor.date_of_death, "2009-08")
        self.assertCountEqual(self.donor.primary_site, [
            "Adrenal gland",
            "Other and ill-defined sites in lip, oral cavity and pharynx"
        ])

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.donor = Donor.objects.create(**self.valid_values)

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
            self.donor.full_clean()

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

    def test_primary_diagnosis_fields(self):
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
            self.primary_diagnosis = PrimaryDiagnosis.objects.create(**self.valid_values)

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
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor
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

    def test_specimen_fields(self):
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
            self.specimen = Specimen.objects.create(**self.valid_values)

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


class TestSampleRegistration(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor
        )
        self.specimen = Specimen.objects.create(
            program_id=self.program,
            submitter_donor_id=self.donor,
            submitter_primary_diagnosis_id=self.primary_diagnosis

        )
        self.valid_values = {
            "submitter_sample_id": "SAMPLE_REGISTRATION_1",
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_specimen_id": self.specimen,
            "gender": "Man",
            "sex_at_birth": "Male",
            "specimen_tissue_source": "Blood venous",
            "tumour_normal_designation": "Normal",
            "specimen_type": "Primary tumour - adjacent to normal",
            "sample_type": "Other DNA enrichments"
        }
        self.sample_registration = SampleRegistration.objects.create(**self.valid_values)

    def test_sample_registration_creation(self):
        self.assertIsInstance(self.sample_registration, SampleRegistration)

    def test_model_fields(self):
        self.assertEqual(self.sample_registration.submitter_sample_id, "SAMPLE_REGISTRATION_1")
        self.assertEqual(self.sample_registration.program_id, self.program)
        self.assertEqual(self.sample_registration.submitter_donor_id, self.donor)
        self.assertEqual(self.sample_registration.submitter_specimen_id, self.specimen)
        self.assertEqual(self.sample_registration.gender, "Man")
        self.assertEqual(self.sample_registration.sex_at_birth, "Male")
        self.assertEqual(self.sample_registration.specimen_tissue_source, "Blood venous")
        self.assertEqual(self.sample_registration.tumour_normal_designation, "Normal")
        self.assertEqual(self.sample_registration.specimen_type, "Primary tumour - adjacent to normal")
        self.assertEqual(self.sample_registration.sample_type, "Other DNA enrichments")

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.sample_registration = SampleRegistration.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_sample_id"] = value
            self.serializer = SampleRegistrationSerializer(instance=self.sample_registration, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_gender(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["gender"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_sex_at_birth(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["sex_at_birth"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_tissue_source(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_tissue_source"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_tumour_normal_designation(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["tumour_normal_designation"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_type"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_sample_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["sample_type"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values)
                self.assertFalse(self.serializer.is_valid())


class TestTreatment(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor
        )
        self.valid_values = {
            "submitter_treatment_id": "TREATMENT_1",
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_primary_diagnosis_id": self.primary_diagnosis,
            "treatment_type": [
                "Endoscopic therapy",
                "Photodynamic therapy"
            ],
            "is_primary_treatment": "Yes",
            "treatment_start_date": "2021-02",
            "treatment_end_date": "2022-09",
            "treatment_setting": "Neoadjuvant",
            "treatment_intent": "Palliative",
            "days_per_cycle": 1,
            "number_of_cycles": 3,
            "response_to_treatment_criteria_method": "Cheson CLL 2012 Oncology Response Criteria",
            "response_to_treatment": "Stable disease"
        }
        self.treatment = Treatment.objects.create(**self.valid_values)

    def test_treatment_creation(self):
        self.assertIsInstance(self.treatment, Treatment)

    def test_treatment_fields(self):
        self.assertEqual(self.treatment.submitter_treatment_id, "TREATMENT_1")
        self.assertEqual(self.treatment.program_id, self.program)
        self.assertEqual(self.treatment.submitter_donor_id, self.donor)
        self.assertEqual(self.treatment.submitter_primary_diagnosis_id, self.primary_diagnosis)
        self.assertCountEqual(self.treatment.treatment_type, ["Endoscopic therapy", "Photodynamic therapy"])
        self.assertEqual(self.treatment.is_primary_treatment, "Yes")
        self.assertEqual(self.treatment.treatment_start_date, "2021-02")
        self.assertEqual(self.treatment.treatment_end_date, "2022-09")
        self.assertEqual(self.treatment.treatment_setting, "Neoadjuvant")
        self.assertEqual(self.treatment.treatment_intent, "Palliative")
        self.assertEqual(self.treatment.days_per_cycle, 1)
        self.assertEqual(self.treatment.number_of_cycles, 3)
        self.assertEqual(self.treatment.response_to_treatment_criteria_method,
                         "Cheson CLL 2012 Oncology Response Criteria")
        self.assertEqual(self.treatment.response_to_treatment, "Stable disease")

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.treatment = Treatment.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_treatment_id"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_treatment_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_type"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_is_primary_treatment(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["is_primary_treatment"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_treatment_start_date(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_start_date"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_treatment_end_date(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_end_date"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_treatment_setting(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_setting"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_treatment_intent(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_intent"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_response_to_treatment_criteria_method(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["response_to_treatment_criteria_method"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_response_to_treatment(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["response_to_treatment"] = value
            self.serializer = TreatmentSerializer(instance=self.treatment, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())


class TestChemotherapy(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor
        )
        self.treatment = Treatment.objects.create(
            submitter_treatment_id="TREATMENT_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
            submitter_primary_diagnosis_id=self.primary_diagnosis,
        )
        self.valid_values = {
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_treatment_id": self.treatment,
            "drug_name": "FLUOROURACIL",
            "drug_rxnormcui": "6534648",
            "chemotherapy_dosage_units": "mg/m2",
            "cumulative_drug_dosage_prescribed": "320",
            "cumulative_drug_dosage_actual": "111"
        }
        self.chemotherapy = Chemotherapy.objects.create(**self.valid_values)

    def test_chemotherapy_creation(self):
        self.assertIsInstance(self.chemotherapy, Chemotherapy)

    def test_chemotherapy_fields(self):
        self.assertEqual(self.chemotherapy.program_id, self.program)
        self.assertEqual(self.chemotherapy.submitter_donor_id, self.donor)
        self.assertEqual(self.chemotherapy.submitter_treatment_id, self.treatment)
        self.assertEqual(self.chemotherapy.drug_name, "FLUOROURACIL")
        self.assertEqual(self.chemotherapy.drug_rxnormcui, "6534648")
        self.assertEqual(self.chemotherapy.chemotherapy_dosage_units, "mg/m2")
        self.assertEqual(self.chemotherapy.cumulative_drug_dosage_prescribed, "320")
        self.assertEqual(self.chemotherapy.cumulative_drug_dosage_actual, "111")

    def test_drug_name_max_length(self):
        self.chemotherapy.drug_name = "f" * 256
        with self.assertRaises(ValidationError):
            self.chemotherapy.full_clean()

    def test_drug_rxnormcui_max_length(self):
        self.chemotherapy.drug_rxnormcui = "f" * 65
        with self.assertRaises(ValidationError):
            self.chemotherapy.full_clean()

    def test_invalid_chemotherapy_dosage_units(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["chemotherapy_dosage_units"] = value
            self.serializer = ChemotherapySerializer(instance=self.chemotherapy, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def chemotherapy_dosage_units(self):
        self.chemotherapy.drug_rxnormcui = "f" * 65
        with self.assertRaises(ValidationError):
            self.chemotherapy.full_clean()


class TestHormoneTherapy(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor
        )
        self.treatment = Treatment.objects.create(
            submitter_treatment_id="TREATMENT_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
            submitter_primary_diagnosis_id=self.primary_diagnosis,
        )
        self.valid_values = {
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_treatment_id": self.treatment,
            "drug_name": "exemestane",
            "drug_rxnormcui": "345678",
            "hormone_drug_dosage_units": "mg/m2",
            "cumulative_drug_dosage_prescribed": "200",
            "cumulative_drug_dosage_actual": "200"
        }
        self.hormone_therapy = HormoneTherapy.objects.create(**self.valid_values)

    def hormone_therapy_creation(self):
        self.assertIsInstance(self.hormone_therapy, HormoneTherapy)

    def test_hormone_therapy_fields(self):
        self.assertEqual(self.hormone_therapy.program_id, self.program)
        self.assertEqual(self.hormone_therapy.submitter_donor_id, self.donor)
        self.assertEqual(self.hormone_therapy.submitter_treatment_id, self.treatment)
        self.assertEqual(self.hormone_therapy.drug_name, "exemestane")
        self.assertEqual(self.hormone_therapy.drug_rxnormcui, "345678")
        self.assertEqual(self.hormone_therapy.hormone_drug_dosage_units, "mg/m2")
        self.assertEqual(self.hormone_therapy.cumulative_drug_dosage_prescribed, "200")
        self.assertEqual(self.hormone_therapy.cumulative_drug_dosage_actual, "200")

    def test_drug_name(self):
        self.hormone_therapy.drug_name = "f" * 256
        with self.assertRaises(ValidationError):
            self.hormone_therapy.full_clean()

    def test_drug_rxnormcui(self):
        self.hormone_therapy.drug_rxnormcui = "f" * 65
        with self.assertRaises(ValidationError):
            self.hormone_therapy.full_clean()

    def test_invalid_hormone_therapy_dosage_units(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["hormone_drug_dosage_units"] = value
            self.serializer = HormoneTherapySerializer(instance=self.hormone_therapy, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def chemotherapy_dosage_units(self):
        self.hormone_therapy.drug_rxnormcui = "f" * 65
        with self.assertRaises(ValidationError):
            self.hormone_therapy.full_clean()


class TestRadiation(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor
        )
        self.treatment = Treatment.objects.create(
            submitter_treatment_id="TREATMENT_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
            submitter_primary_diagnosis_id=self.primary_diagnosis,
        )
        self.valid_values = {
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_treatment_id": self.treatment,
            "radiation_therapy_modality": "Brachytherapy (procedure)",
            "radiation_therapy_type": "Internal",
            "radiation_therapy_fractions": "30",
            "radiation_therapy_dosage": "66",
            "anatomical_site_irradiated": "Chest wall structure",
            "radiation_boost": True,
            "reference_radiation_treatment_id": "REFERENCE_RADIATION_TREATMENT_1"
        }
        self.radiation = Radiation.objects.create(**self.valid_values)

    def test_radiation_creation(self):
        self.assertIsInstance(self.radiation, Radiation)

    def test_radiation_fields(self):
        self.assertEqual(self.radiation.program_id, self.program)
        self.assertEqual(self.radiation.submitter_donor_id, self.donor)
        self.assertEqual(self.radiation.submitter_treatment_id, self.treatment)
        self.assertEqual(self.radiation.radiation_therapy_modality, "Brachytherapy (procedure)")
        self.assertEqual(self.radiation.radiation_therapy_type, "Internal")
        self.assertEqual(self.radiation.radiation_therapy_fractions, "30")
        self.assertEqual(self.radiation.radiation_therapy_dosage, "66")
        self.assertEqual(self.radiation.anatomical_site_irradiated, "Chest wall structure")
        self.assertTrue(self.radiation.radiation_boost)
        self.assertEqual(self.radiation.reference_radiation_treatment_id, "REFERENCE_RADIATION_TREATMENT_1")

    def test_invalid_radiation_therapy_modality(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["radiation_therapy_modality"] = value
            self.serializer = RadiationSerializer(instance=self.radiation, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())
    
    def test_invalid_radiation_therapy_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["radiation_therapy_type"] = value
            self.serializer = RadiationSerializer(instance=self.radiation, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_anatomical_site_irradiated(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["anatomical_site_irradiated"] = value
            self.serializer = RadiationSerializer(instance=self.radiation, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_radiation_boost(self):
        self.donor.radiation_boost = "foo"
        with self.assertRaises(ValidationError):
            self.donor.full_clean()

    def test_reference_radiation_treatment_id_max_length(self):
        self.radiation.reference_radiation_treatment_id = "f" * 65
        with self.assertRaises(ValidationError):
            self.radiation.full_clean()


class TestImmunotherapy(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"]
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor
        )
        self.treatment = Treatment.objects.create(
            submitter_treatment_id="TREATMENT_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
            submitter_primary_diagnosis_id=self.primary_diagnosis,
        )
        self.valid_values = {
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_treatment_id": self.treatment,
            "immunotherapy_type": "Cell-based",
            "drug_name": "Necitumumab",
            "drug_rxnormcui": "8756456"
        }
        self.immunotherapy = Immunotherapy.objects.create(**self.valid_values)
    
    def test_immunotherapy_creation(self):
        self.assertIsInstance(self.immunotherapy, Immunotherapy)

    def test_immunotherapy_fields(self):
        self.assertEqual(self.immunotherapy.program_id, self.program)
        self.assertEqual(self.immunotherapy.submitter_donor_id, self.donor)
        self.assertEqual(self.immunotherapy.submitter_treatment_id, self.treatment)
        self.assertEqual(self.immunotherapy.immunotherapy_type, "Cell-based")
        self.assertEqual(self.immunotherapy.drug_name, "Necitumumab")
        self.assertEqual(self.immunotherapy.drug_rxnormcui, "8756456")
    
    def test_invalid_immunotherapy_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["immunotherapy_type"] = value
            self.serializer = ImmunotherapySerializer(instance=self.immunotherapy, data=self.valid_values)
            self.assertFalse(self.serializer.is_valid())
    
    def test_drug_name(self):
        self.immunotherapy.drug_name = "f" * 256
        with self.assertRaises(ValidationError):
            self.immunotherapy.full_clean()

    def test_drug_rxnormcui(self):
        self.immunotherapy.drug_rxnormcui = "f" * 65
        with self.assertRaises(ValidationError):
            self.immunotherapy.full_clean()