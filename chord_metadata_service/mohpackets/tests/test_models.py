from django.core.exceptions import ValidationError
from django.db.utils import DataError, IntegrityError
from django.test import TestCase

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Chemotherapy,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    HormoneTherapy,
    Immunotherapy,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)
from chord_metadata_service.mohpackets.serializers import (
    ChemotherapySerializer,
    ComorbiditySerializer,
    DonorSerializer,
    FollowUpSerializer,
    HormoneTherapySerializer,
    ImmunotherapySerializer,
    PrimaryDiagnosisSerializer,
    ProgramSerializer,
    RadiationSerializer,
    SampleRegistrationSerializer,
    SpecimenSerializer,
    SurgerySerializer,
    TreatmentSerializer,
)


def get_optional_fields(excluded_fields, model_fields):
    """
    Get a list of optional field names based on the excluded fields and the given fields.

    Args:
        excluded_fields (list): List of field names to be excluded.
        model_fields (list): List of field objects to check against the excluded fields.

    Returns:
        list: List of optional field names.
    """
    optional_fields = [
        field.name for field in model_fields if field.name not in excluded_fields
    ]
    return optional_fields


def get_invalid_ids():
    """
    Returns the invalid values to test in ID fields. ID fields must be strings
    with 64 characters or less and must not be blank nor empty.
    """
    return ["f" * 65, "", None, True]


def get_invalid_choices():
    """
    Returns the invalid values to test in choice fields. ChoiceFields values
    must be strings and among the permissible values defined for that field
    in serializers.py or permissible_values.py
    """
    return ["foo", 1, True]


def get_invalid_dates():
    """
    Returns the invalid values to test in date fields. Dates must be strings
    in one of the following formats: YYYY, YYYY-MM, YYYY-MM-DD
    """
    return ["foo", "03", "114", "443-12", "Feb-1995", 1, True]


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
                self.serializer = ProgramSerializer(
                    instance=self.program, data=self.program_id
                )
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
            ],
            "gender": "Woman",
            "sex_at_birth": "Unknown",
            "lost_to_followup_after_clinical_event_identifier": "",
            "lost_to_followup_reason": "Not applicable",
            "date_alive_after_lost_to_followup": "2022-02",
        }
        self.donor = Donor.objects.create(**self.valid_values)

    def test_donor_creation(self):
        self.assertIsInstance(self.donor, Donor)

    def test_donor_fields(self):
        self.assertEqual(self.donor.submitter_donor_id, "DONOR_1")
        self.assertEqual(self.donor.program_id, self.program)
        self.assertTrue(self.donor.is_deceased)
        self.assertEqual(self.donor.cause_of_death, "Died of cancer")
        self.assertEqual(self.donor.date_of_birth, "1975-08")
        self.assertEqual(self.donor.date_of_death, "2009-08")
        self.assertEqual(self.donor.gender, "Woman")
        self.assertEqual(self.donor.sex_at_birth, "Unknown")
        self.assertEqual(
            self.donor.lost_to_followup_after_clinical_event_identifier, ""
        )
        self.assertEqual(self.donor.lost_to_followup_reason, "Not applicable")
        self.assertEqual(self.donor.date_alive_after_lost_to_followup, "2022-02")
        self.assertCountEqual(
            self.donor.primary_site,
            [
                "Adrenal gland",
                "Other and ill-defined sites in lip, oral cavity and pharynx",
            ],
        )

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=["submitter_donor_id", "program_id"],
            model_fields=self.donor._meta.fields,
        )
        for field in optional_fields:
            setattr(self.donor, field, None)
            self.donor.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=["submitter_donor_id", "program_id"],
            model_fields=self.donor._meta.fields,
        )
        for field in optional_fields:
            setattr(self.donor, field, "")
            self.donor.full_clean()

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.donor = Donor.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["submitter_donor_id"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_program_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["program_id"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
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
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_date_of_death(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_death"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_date_of_birth(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_birth"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_primary_site(self):
        invalid_values = ["foo", ["foo"]]
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["primary_site"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_gender(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["gender"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_sex_at_birth(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["sex_at_birth"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_lost_to_followup_reason(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["lost_to_followup_reason"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_date_alive_after_lost_to_followup(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_alive_after_lost_to_followup"] = value
                self.serializer = DonorSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())


class PrimaryDiagnosisTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
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
            "clinical_stage_group": "Stage IA3",
            "laterality": "Right",
        }
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(**self.valid_values)

    def test_primary_diagnosis_creation(self):
        self.assertIsInstance(self.primary_diagnosis, PrimaryDiagnosis)

    def test_primary_diagnosis_fields(self):
        self.assertEqual(
            self.primary_diagnosis.submitter_primary_diagnosis_id, "PRIMARY_DIAGNOSIS_1"
        )
        self.assertEqual(self.primary_diagnosis.program_id, self.program)
        self.assertEqual(self.primary_diagnosis.submitter_donor_id, self.donor)
        self.assertEqual(self.primary_diagnosis.date_of_diagnosis, "2019-11")
        self.assertEqual(self.primary_diagnosis.cancer_type_code, "C02.1")
        self.assertEqual(self.primary_diagnosis.basis_of_diagnosis, "Unknown")
        self.assertEqual(
            self.primary_diagnosis.lymph_nodes_examined_status, "Not applicable"
        )
        self.assertEqual(
            self.primary_diagnosis.lymph_nodes_examined_method,
            "Physical palpation of patient",
        )
        self.assertEqual(self.primary_diagnosis.number_lymph_nodes_positive, 15)
        self.assertEqual(
            self.primary_diagnosis.clinical_tumour_staging_system,
            "Lugano staging system",
        )
        self.assertEqual(self.primary_diagnosis.clinical_t_category, "T2a1")
        self.assertEqual(self.primary_diagnosis.clinical_n_category, "N2mi")
        self.assertEqual(self.primary_diagnosis.clinical_m_category, "M1b(0)")
        self.assertEqual(self.primary_diagnosis.clinical_stage_group, "Stage IA3")
        self.assertEqual(self.primary_diagnosis.laterality, "Right")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_primary_diagnosis_id",
            ],
            model_fields=self.primary_diagnosis._meta.fields,
        )
        for field in optional_fields:
            setattr(self.primary_diagnosis, field, None)
            self.primary_diagnosis.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_primary_diagnosis_id",
            ],
            model_fields=self.primary_diagnosis._meta.fields,
        )
        for field in optional_fields:
            setattr(self.primary_diagnosis, field, "")
            self.primary_diagnosis.full_clean()

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.primary_diagnosis = PrimaryDiagnosis.objects.create(
                **self.valid_values
            )

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_primary_diagnosis_id"] = value
            self.serializer = PrimaryDiagnosisSerializer(
                instance=self.primary_diagnosis, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_program_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_primary_diagnosis_id"] = value
            self.serializer = PrimaryDiagnosisSerializer(
                instance=self.primary_diagnosis, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_date_of_diagnosis(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_diagnosis"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
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
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_lymph_nodes_examined_status(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["lymph_nodes_examined_status"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_clinical_tumour_staging_system(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_tumour_staging_system"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_clinical_t_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_t_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_clinical_n_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_n_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_clinical_m_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_m_category"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_clinical_stage_group(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["clinical_stage_group"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_laterality(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["laterality"] = value
                self.serializer = PrimaryDiagnosisSerializer(
                    instance=self.primary_diagnosis, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())


class SpecimenTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
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
            "percent_tumour_cells_measurement_method": "Image analysis",
            "specimen_processing": "Formalin fixed - unbuffered",
            "specimen_laterality": "Left",
        }
        self.specimen = Specimen.objects.create(**self.valid_values)

    def test_specimen_creation(self):
        self.assertIsInstance(self.specimen, Specimen)

    def test_specimen_fields(self):
        self.assertEqual(self.specimen.submitter_specimen_id, "SPECIMEN_1")
        self.assertEqual(self.specimen.program_id, self.program)
        self.assertEqual(self.specimen.submitter_donor_id, self.donor)
        self.assertEqual(
            self.specimen.submitter_primary_diagnosis_id, self.primary_diagnosis
        )
        self.assertEqual(
            self.specimen.pathological_tumour_staging_system, "AJCC 6th edition"
        )
        self.assertEqual(self.specimen.pathological_t_category, "Tis")
        self.assertEqual(self.specimen.pathological_n_category, "N0b")
        self.assertEqual(self.specimen.pathological_m_category, "M1a")
        self.assertEqual(self.specimen.pathological_stage_group, "Stage IAS")
        self.assertEqual(self.specimen.specimen_collection_date, "2021-06-25")
        self.assertEqual(self.specimen.specimen_storage, "Cut slide")
        self.assertEqual(self.specimen.tumour_histological_type, "8209/3")
        self.assertEqual(self.specimen.specimen_anatomic_location, "C43.9")
        self.assertEqual(
            self.specimen.reference_pathology_confirmed_diagnosis, "Not done"
        )
        self.assertEqual(
            self.specimen.reference_pathology_confirmed_tumour_presence, "Yes"
        )
        self.assertEqual(self.specimen.tumour_grading_system, "ISUP grading system")
        self.assertEqual(self.specimen.tumour_grade, "G2")
        self.assertEqual(self.specimen.percent_tumour_cells_range, "51-100%")
        self.assertEqual(
            self.specimen.percent_tumour_cells_measurement_method, "Image analysis"
        )
        self.assertEqual(
            self.specimen.specimen_processing, "Formalin fixed - unbuffered"
        )
        self.assertEqual(self.specimen.specimen_laterality, "Left")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_primary_diagnosis_id",
                "submitter_specimen_id",
            ],
            model_fields=self.specimen._meta.fields,
        )
        for field in optional_fields:
            setattr(self.specimen, field, None)
            self.specimen.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_primary_diagnosis_id",
                "submitter_specimen_id",
            ],
            model_fields=self.specimen._meta.fields,
        )
        for field in optional_fields:
            setattr(self.specimen, field, "")
            self.specimen.full_clean()

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.specimen = Specimen.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_specimen_id"] = value
            self.serializer = SpecimenSerializer(
                instance=self.specimen, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_pathological_tumour_staging_system(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_tumour_staging_system"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_pathological_t_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_t_category"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_pathological_n_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_n_category"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_pathological_m_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_m_category"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_pathological_stage_group(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["pathological_stage_group"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_collection_date(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_collection_date"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_storage(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_storage"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
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

    def test_invalid_reference_pathology_confirmed_diagnosis(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["reference_pathology_confirmed_diagnosis"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_reference_pathology_confirmed_tumour_presence(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values[
                    "reference_pathology_confirmed_tumour_presence"
                ] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_tumour_grading_system(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["tumour_grading_system"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_tumour_grade(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["tumour_grade"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_percent_tumour_cells_range(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["percent_tumour_cells_range"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_percent_tumour_cells_measurement_method(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["percent_tumour_cells_measurement_method"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_processing(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_processing"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_laterality(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_laterality"] = value
                self.serializer = SpecimenSerializer(
                    instance=self.specimen, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())


class SampleRegistrationTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
        )
        self.specimen = Specimen.objects.create(
            submitter_specimen_id="SPECIMEN-1",
            program_id=self.program,
            submitter_donor_id=self.donor,
            submitter_primary_diagnosis_id=self.primary_diagnosis,
        )
        self.valid_values = {
            "submitter_sample_id": "SAMPLE_REGISTRATION_1",
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_specimen_id": self.specimen,
            "specimen_tissue_source": "Blood venous",
            "tumour_normal_designation": "Normal",
            "specimen_type": "Primary tumour - adjacent to normal",
            "sample_type": "Other DNA enrichments",
        }
        self.sample_registration = SampleRegistration.objects.create(
            **self.valid_values
        )

    def test_sample_registration_creation(self):
        self.assertIsInstance(self.sample_registration, SampleRegistration)

    def test_model_fields(self):
        self.assertEqual(
            self.sample_registration.submitter_sample_id, "SAMPLE_REGISTRATION_1"
        )
        self.assertEqual(self.sample_registration.program_id, self.program)
        self.assertEqual(self.sample_registration.submitter_donor_id, self.donor)
        self.assertEqual(self.sample_registration.submitter_specimen_id, self.specimen)
        self.assertEqual(
            self.sample_registration.specimen_tissue_source, "Blood venous"
        )
        self.assertEqual(self.sample_registration.tumour_normal_designation, "Normal")
        self.assertEqual(
            self.sample_registration.specimen_type,
            "Primary tumour - adjacent to normal",
        )
        self.assertEqual(self.sample_registration.sample_type, "Other DNA enrichments")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_specimen_id",
                "submitter_sample_id",
            ],
            model_fields=self.sample_registration._meta.fields,
        )
        for field in optional_fields:
            setattr(self.sample_registration, field, None)
            self.sample_registration.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_specimen_id",
                "submitter_sample_id",
            ],
            model_fields=self.sample_registration._meta.fields,
        )
        for field in optional_fields:
            setattr(self.sample_registration, field, "")
            self.sample_registration.full_clean()

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.sample_registration = SampleRegistration.objects.create(
                **self.valid_values
            )

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_sample_id"] = value
            self.serializer = SampleRegistrationSerializer(
                instance=self.sample_registration, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_gender(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["gender"] = value
                self.sample_registration.full_clean()

    def test_invalid_sex_at_birth(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["sex_at_birth"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_tissue_source(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_tissue_source"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_tumour_normal_designation(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["tumour_normal_designation"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_specimen_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["specimen_type"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_sample_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["sample_type"] = value
                self.serializer = SampleRegistrationSerializer(
                    instance=self.sample_registration, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())


class TreatmentTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
        )
        self.valid_values = {
            "submitter_treatment_id": "TREATMENT_1",
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_primary_diagnosis_id": self.primary_diagnosis,
            "treatment_type": ["Endoscopic therapy", "Photodynamic therapy"],
            "is_primary_treatment": "Yes",
            "treatment_start_date": "2021-02",
            "treatment_end_date": "2022-09",
            "treatment_setting": "Neoadjuvant",
            "treatment_intent": "Palliative",
            "days_per_cycle": 1,
            "number_of_cycles": 3,
            "response_to_treatment_criteria_method": "Cheson CLL 2012 Oncology Response Criteria",
            "response_to_treatment": "Stable disease",
            "line_of_treatment": 5,
            "status_of_treatment": "Other",
        }
        self.treatment = Treatment.objects.create(**self.valid_values)

    def test_treatment_creation(self):
        self.assertIsInstance(self.treatment, Treatment)

    def test_treatment_fields(self):
        self.assertEqual(self.treatment.submitter_treatment_id, "TREATMENT_1")
        self.assertEqual(self.treatment.program_id, self.program)
        self.assertEqual(self.treatment.submitter_donor_id, self.donor)
        self.assertEqual(
            self.treatment.submitter_primary_diagnosis_id, self.primary_diagnosis
        )
        self.assertCountEqual(
            self.treatment.treatment_type,
            ["Endoscopic therapy", "Photodynamic therapy"],
        )
        self.assertEqual(self.treatment.is_primary_treatment, "Yes")
        self.assertEqual(self.treatment.treatment_start_date, "2021-02")
        self.assertEqual(self.treatment.treatment_end_date, "2022-09")
        self.assertEqual(self.treatment.treatment_setting, "Neoadjuvant")
        self.assertEqual(self.treatment.treatment_intent, "Palliative")
        self.assertEqual(self.treatment.days_per_cycle, 1)
        self.assertEqual(self.treatment.number_of_cycles, 3)
        self.assertEqual(
            self.treatment.response_to_treatment_criteria_method,
            "Cheson CLL 2012 Oncology Response Criteria",
        )
        self.assertEqual(self.treatment.response_to_treatment, "Stable disease")
        self.assertEqual(self.treatment.line_of_treatment, 5)
        self.assertEqual(self.treatment.status_of_treatment, "Other")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
                "submitter_primary_diagnosis_id",
            ],
            model_fields=self.treatment._meta.fields,
        )
        for field in optional_fields:
            setattr(self.treatment, field, None)
            self.treatment.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
                "submitter_primary_diagnosis_id",
            ],
            model_fields=self.treatment._meta.fields,
        )
        for field in optional_fields:
            setattr(self.treatment, field, "")
            self.treatment.full_clean()

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.treatment = Treatment.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_treatment_id"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_treatment_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_type"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_is_primary_treatment(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["is_primary_treatment"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_treatment_start_date(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_start_date"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_treatment_end_date(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_end_date"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_treatment_setting(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_setting"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_treatment_intent(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["treatment_intent"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_response_to_treatment_criteria_method(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["response_to_treatment_criteria_method"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_response_to_treatment(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["response_to_treatment"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_status_of_treatment(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["status_of_treatment"] = value
            self.serializer = TreatmentSerializer(
                instance=self.treatment, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())


class ChemotherapyTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
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
            "drug_reference_identifier": "87354",
            "chemotherapy_drug_dose_units": "mg/m2",
            "prescribed_cumulative_drug_dose": "320",
            "actual_cumulative_drug_dose": "111",
            "drug_reference_database": "PubChem",
        }
        self.chemotherapy = Chemotherapy.objects.create(**self.valid_values)

    def test_chemotherapy_creation(self):
        self.assertIsInstance(self.chemotherapy, Chemotherapy)

    def test_chemotherapy_fields(self):
        self.assertEqual(self.chemotherapy.program_id, self.program)
        self.assertEqual(self.chemotherapy.submitter_donor_id, self.donor)
        self.assertEqual(self.chemotherapy.submitter_treatment_id, self.treatment)
        self.assertEqual(self.chemotherapy.drug_name, "FLUOROURACIL")
        self.assertEqual(self.chemotherapy.drug_reference_identifier, "87354")
        self.assertEqual(self.chemotherapy.chemotherapy_drug_dose_units, "mg/m2")
        self.assertEqual(self.chemotherapy.prescribed_cumulative_drug_dose, "320")
        self.assertEqual(self.chemotherapy.actual_cumulative_drug_dose, "111")
        self.assertEqual(self.chemotherapy.drug_reference_database, "PubChem")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.chemotherapy._meta.fields,
        )
        for field in optional_fields:
            setattr(self.chemotherapy, field, None)
            self.chemotherapy.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.chemotherapy._meta.fields,
        )
        for field in optional_fields:
            setattr(self.chemotherapy, field, "")
            self.chemotherapy.full_clean()

    def test_drug_name_max_length(self):
        self.chemotherapy.drug_name = "f" * 256
        with self.assertRaises(DataError):
            self.chemotherapy.save()

    def test_drug_reference_identifier_max_length(self):
        self.chemotherapy.drug_reference_identifier = "f" * 65
        with self.assertRaises(DataError):
            self.chemotherapy.save()

    def test_invalid_chemotherapy_drug_dose_units(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["chemotherapy_drug_dose_units"] = value
            self.serializer = ChemotherapySerializer(
                instance=self.chemotherapy, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_drug_reference_database(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["drug_reference_database"] = value
            self.serializer = ChemotherapySerializer(
                instance=self.chemotherapy, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())


class HormoneTherapyTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
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
            "drug_reference_identifier": "345678",
            "hormone_drug_dose_units": "mg/m2",
            "prescribed_cumulative_drug_dose": "200",
            "actual_cumulative_drug_dose": "200",
        }
        self.hormone_therapy = HormoneTherapy.objects.create(**self.valid_values)

    def hormone_therapy_creation(self):
        self.assertIsInstance(self.hormone_therapy, HormoneTherapy)

    def test_hormone_therapy_fields(self):
        self.assertEqual(self.hormone_therapy.program_id, self.program)
        self.assertEqual(self.hormone_therapy.submitter_donor_id, self.donor)
        self.assertEqual(self.hormone_therapy.submitter_treatment_id, self.treatment)
        self.assertEqual(self.hormone_therapy.drug_name, "exemestane")
        self.assertEqual(self.hormone_therapy.drug_reference_identifier, "345678")
        self.assertEqual(self.hormone_therapy.hormone_drug_dose_units, "mg/m2")
        self.assertEqual(self.hormone_therapy.prescribed_cumulative_drug_dose, "200")
        self.assertEqual(self.hormone_therapy.actual_cumulative_drug_dose, "200")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.hormone_therapy._meta.fields,
        )
        for field in optional_fields:
            setattr(self.hormone_therapy, field, None)
            self.hormone_therapy.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.hormone_therapy._meta.fields,
        )
        for field in optional_fields:
            setattr(self.hormone_therapy, field, "")
            self.hormone_therapy.full_clean()

    def test_drug_name_max_length(self):
        self.hormone_therapy.drug_name = "f" * 256
        with self.assertRaises(DataError):
            self.hormone_therapy.save()

    def test_drug_reference_identifier_max_length(self):
        self.hormone_therapy.drug_reference_identifier = "f" * 65
        with self.assertRaises(DataError):
            self.hormone_therapy.save()

    def test_invalid_hormone_drug_dose_units(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["hormone_drug_dose_units"] = value
            self.serializer = HormoneTherapySerializer(
                instance=self.hormone_therapy, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_drug_reference_database(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["drug_reference_database"] = value
            self.serializer = ChemotherapySerializer(
                instance=self.hormone_therapy, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())


class RadiationTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
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
            "reference_radiation_treatment_id": "REFERENCE_RADIATION_TREATMENT_1",
        }
        self.radiation = Radiation.objects.create(**self.valid_values)

    def test_radiation_creation(self):
        self.assertIsInstance(self.radiation, Radiation)

    def test_radiation_fields(self):
        self.assertEqual(self.radiation.program_id, self.program)
        self.assertEqual(self.radiation.submitter_donor_id, self.donor)
        self.assertEqual(self.radiation.submitter_treatment_id, self.treatment)
        self.assertEqual(
            self.radiation.radiation_therapy_modality, "Brachytherapy (procedure)"
        )
        self.assertEqual(self.radiation.radiation_therapy_type, "Internal")
        self.assertEqual(self.radiation.radiation_therapy_fractions, "30")
        self.assertEqual(self.radiation.radiation_therapy_dosage, "66")
        self.assertEqual(
            self.radiation.anatomical_site_irradiated, "Chest wall structure"
        )
        self.assertTrue(self.radiation.radiation_boost)
        self.assertEqual(
            self.radiation.reference_radiation_treatment_id,
            "REFERENCE_RADIATION_TREATMENT_1",
        )

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.radiation._meta.fields,
        )
        for field in optional_fields:
            setattr(self.radiation, field, None)
            self.radiation.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.radiation._meta.fields,
        )
        for field in optional_fields:
            setattr(self.radiation, field, "")
            self.radiation.full_clean()

    def test_invalid_radiation_therapy_modality(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["radiation_therapy_modality"] = value
            self.serializer = RadiationSerializer(
                instance=self.radiation, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_radiation_therapy_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["radiation_therapy_type"] = value
            self.serializer = RadiationSerializer(
                instance=self.radiation, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_anatomical_site_irradiated(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["anatomical_site_irradiated"] = value
            self.serializer = RadiationSerializer(
                instance=self.radiation, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_radiation_boost(self):
        self.radiation.radiation_boost = "foo"
        with self.assertRaises(ValidationError):
            self.radiation.save()

    def test_reference_radiation_treatment_id_max_length(self):
        self.radiation.reference_radiation_treatment_id = "f" * 65
        with self.assertRaises(DataError):
            self.radiation.save()


class ImmunotherapyTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
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
            "drug_reference_identifier": "8756456",
            "immunotherapy_drug_dose_units": "mg/m2",
            "prescribed_cumulative_drug_dose": "200",
            "actual_cumulative_drug_dose": "200",
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
        self.assertEqual(self.immunotherapy.drug_reference_identifier, "8756456")
        self.assertEqual(self.immunotherapy.immunotherapy_drug_dose_units, "mg/m2")
        self.assertEqual(self.immunotherapy.prescribed_cumulative_drug_dose, "200")
        self.assertEqual(self.immunotherapy.actual_cumulative_drug_dose, "200")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.immunotherapy._meta.fields,
        )
        for field in optional_fields:
            setattr(self.immunotherapy, field, None)
            self.immunotherapy.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
            ],
            model_fields=self.immunotherapy._meta.fields,
        )
        for field in optional_fields:
            setattr(self.immunotherapy, field, "")
            self.immunotherapy.full_clean()

    def test_invalid_immunotherapy_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["immunotherapy_type"] = value
            self.serializer = ImmunotherapySerializer(
                instance=self.immunotherapy, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_drug_name_max_length(self):
        self.immunotherapy.drug_name = "f" * 256
        with self.assertRaises(DataError):
            self.immunotherapy.save()

    def test_drug_reference_identifier_max_length(self):
        self.immunotherapy.drug_reference_identifier = "f" * 65
        with self.assertRaises(DataError):
            self.immunotherapy.save()


class SurgeryTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
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
            "surgery_type": "Drainage of abscess",
            "surgery_site": "C06",
            "surgery_location": "Primary",
            "tumour_length": "5",
            "tumour_width": "7",
            "greatest_dimension_tumour": "4",
            "tumour_focality": "Cannot be assessed",
            "residual_tumour_classification": "R2",
            "margin_types_involved": ["Proximal margin", "Not applicable"],
            "margin_types_not_involved": ["Unknown"],
            "lymphovascular_invasion": "Absent",
            "margin_types_not_assessed": ["Common bile duct margin", "Not applicable"],
            "perineural_invasion": "Not applicable",
        }
        self.surgery = Surgery.objects.create(**self.valid_values)

    def test_immunotherapy_creation(self):
        self.assertIsInstance(self.surgery, Surgery)

    def test_surgery_fields(self):
        self.assertEqual(self.surgery.program_id, self.program)
        self.assertEqual(self.surgery.submitter_donor_id, self.donor)
        self.assertEqual(self.surgery.submitter_treatment_id, self.treatment)
        self.assertEqual(self.surgery.surgery_type, "Drainage of abscess")
        self.assertEqual(self.surgery.surgery_site, "C06")
        self.assertEqual(self.surgery.surgery_location, "Primary")
        self.assertEqual(self.surgery.tumour_length, "5")
        self.assertEqual(self.surgery.tumour_width, "7")
        self.assertEqual(self.surgery.greatest_dimension_tumour, "4")
        self.assertEqual(self.surgery.tumour_focality, "Cannot be assessed")
        self.assertEqual(self.surgery.residual_tumour_classification, "R2")
        self.assertCountEqual(
            self.surgery.margin_types_involved, ["Proximal margin", "Not applicable"]
        )
        self.assertCountEqual(self.surgery.margin_types_not_involved, ["Unknown"])
        self.assertEqual(self.surgery.lymphovascular_invasion, "Absent")
        self.assertCountEqual(
            self.surgery.margin_types_not_assessed,
            ["Common bile duct margin", "Not applicable"],
        )
        self.assertEqual(self.surgery.perineural_invasion, "Not applicable")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
                "submitter_specimen_id",
                "margin_types_involved",
                "margin_types_not_involved",
                "margin_types_not_assessed",
            ],
            model_fields=self.surgery._meta.fields,
        )
        for field in optional_fields:
            setattr(self.surgery, field, None)
            self.surgery.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
                "submitter_specimen_id",
                "margin_types_involved",
                "margin_types_not_involved",
                "margin_types_not_assessed",
            ],
            model_fields=self.surgery._meta.fields,
        )
        for field in optional_fields:
            setattr(self.surgery, field, "")
            self.surgery.full_clean()

    def test_invalid_surgery_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["surgery_type"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    # TODO: fix regular expression
    # def test_specimen_surgery_site(self):
    #     invalid_values = ["8260/3", 1]
    #     for value in invalid_values:
    #         with self.subTest(value=value):
    #             self.valid_values["specimen_anatomic_location"] = value
    #             self.serializer = SpecimenSerializer(instance=self.donor, data=self.valid_values)
    #             self.assertFalse(self.serializer.is_valid())

    def test_invalid_surgery_location(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["surgery_location"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_tumour_focality(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["tumour_focality"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_residual_tumour_classification(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["residual_tumour_classification"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_margin_types_involved(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["margin_types_involved"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_margin_types_not_involved(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["margin_types_not_involved"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_margin_types_not_assessed(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["margin_types_not_assessed"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_lymphovascular_invasion(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["lymphovascular_invasion"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_perineural_invasion(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["perineural_invasion"] = value
            self.serializer = SurgerySerializer(
                instance=self.surgery, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())


class FollowUpTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.primary_diagnosis = PrimaryDiagnosis.objects.create(
            submitter_primary_diagnosis_id="PRIMARY_DIAGNOSIS_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
        )
        self.treatment = Treatment.objects.create(
            submitter_treatment_id="TREATMENT_1",
            program_id=self.program,
            submitter_donor_id=self.donor,
            submitter_primary_diagnosis_id=self.primary_diagnosis,
        )
        self.valid_values = {
            "submitter_follow_up_id": "FOLLOW_UP_1",
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "submitter_primary_diagnosis_id": self.primary_diagnosis,
            "submitter_treatment_id": self.treatment,
            "date_of_followup": "2022-10",
            "disease_status_at_followup": "Loco-regional progression",
            "relapse_type": "Progression (liquid tumours)",
            "date_of_relapse": "2022-07",
            "method_of_progression_status": [
                "Imaging (procedure)",
                "Laboratory data interpretation (procedure)",
            ],
            "anatomic_site_progression_or_recurrence": ["C18"],
            "recurrence_tumour_staging_system": "Lugano staging system",
            "recurrence_t_category": "T2a",
            "recurrence_n_category": "N0a (biopsy)",
            "recurrence_m_category": "M0(i+)",
            "recurrence_stage_group": "Stage IBS",
        }
        self.followup = FollowUp.objects.create(**self.valid_values)

    def test_followup_creation(self):
        self.assertIsInstance(self.followup, FollowUp)

    def test_followup_fields(self):
        self.assertEqual(self.followup.submitter_follow_up_id, "FOLLOW_UP_1")
        self.assertEqual(self.followup.program_id, self.program)
        self.assertEqual(self.followup.submitter_donor_id, self.donor)
        self.assertEqual(
            self.followup.submitter_primary_diagnosis_id, self.primary_diagnosis
        )
        self.assertEqual(self.followup.submitter_treatment_id, self.treatment)
        self.assertEqual(self.followup.date_of_followup, "2022-10")
        self.assertEqual(
            self.followup.disease_status_at_followup, "Loco-regional progression"
        )
        self.assertEqual(self.followup.relapse_type, "Progression (liquid tumours)")
        self.assertEqual(self.followup.date_of_relapse, "2022-07")
        self.assertEqual(
            self.followup.method_of_progression_status,
            ["Imaging (procedure)", "Laboratory data interpretation (procedure)"],
        )
        self.assertEqual(self.followup.anatomic_site_progression_or_recurrence, ["C18"])
        self.assertEqual(
            self.followup.recurrence_tumour_staging_system,
            "Lugano staging system",
        )
        self.assertEqual(self.followup.recurrence_t_category, "T2a")
        self.assertEqual(self.followup.recurrence_n_category, "N0a (biopsy)")
        self.assertEqual(self.followup.recurrence_m_category, "M0(i+)")
        self.assertEqual(self.followup.recurrence_stage_group, "Stage IBS")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_follow_up_id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
                "submitter_primary_diagnosis_id",
            ],
            model_fields=self.followup._meta.fields,
        )
        for field in optional_fields:
            setattr(self.followup, field, None)
            self.followup.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "submitter_follow_up_id",
                "submitter_donor_id",
                "program_id",
                "submitter_treatment_id",
                "submitter_primary_diagnosis_id",
            ],
            model_fields=self.followup._meta.fields,
        )
        for field in optional_fields:
            setattr(self.followup, field, "")
            self.followup.full_clean()

    def test_unique_id(self):
        with self.assertRaises(IntegrityError):
            self.followup = FollowUp.objects.create(**self.valid_values)

    def test_invalid_id(self):
        invalid_values = get_invalid_ids()
        for value in invalid_values:
            self.valid_values["submitter_follow_up_id"] = value
            self.serializer = FollowUpSerializer(
                instance=self.followup, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_date_of_followup(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_followup"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_disease_status_at_followup(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["disease_status_at_followup"] = value
            self.serializer = FollowUpSerializer(
                instance=self.followup, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_relapse_type(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["relapse_type"] = value
            self.serializer = FollowUpSerializer(
                instance=self.followup, data=self.valid_values
            )
            self.assertFalse(self.serializer.is_valid())

    def test_invalid_date_of_relapse(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["date_of_relapse"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_method_of_progression_status(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["method_of_progression_status"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    # TODO: fix regular expression
    # def test_anatomic_site_progression_or_recurrence(self):
    #     invalid_values = ["8260/3", 1]
    #     for value in invalid_values:
    #         with self.subTest(value=value):
    #             self.valid_values["sanatomic_site_progression_or_recurrence"] = value
    #             self.serializer = FollowUpSerializer(instance=self.followup, data=self.valid_values)
    #             self.assertFalse(self.serializer.is_valid())

    def test_invalid_recurrence_tumour_staging_system(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["recurrence_tumour_staging_system"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.followup, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_recurrence_t_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["recurrence_t_category"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.followup, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_recurrence_n_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["recurrence_n_category"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.followup, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_recurrence_m_category(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["recurrence_m_category"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.followup, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_recurrence_stage_group(self):
        invalid_values = get_invalid_dates()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["recurrence_stage_group"] = value
                self.serializer = FollowUpSerializer(
                    instance=self.donor, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())


class BiomarkerTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.valid_values = {
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "test_date": "8",
            "psa_level": 230,
            "ca125": 29,
            "cea": 11,
            "er_status": "Cannot be determined",
            "er_percent_positive": 18.3,
            "pr_status": "Unknown",
            "pr_percent_positive": 65.2,
            "her2_ihc_status": "Equivocal",
            "her2_ish_status": "Negative",
            "hpv_ihc_status": "Not applicable",
            "hpv_pcr_status": "Negative",
            "hpv_strain": ["HPV35"],
        }
        self.biomarker = Biomarker.objects.create(**self.valid_values)

    def test_biomarker_creation(self):
        self.assertIsInstance(self.biomarker, Biomarker)

    def test_biomarker_fields(self):
        self.assertEqual(self.biomarker.program_id, self.program)
        self.assertEqual(self.biomarker.submitter_donor_id, self.donor)
        self.assertEqual(self.biomarker.test_date, "8")
        self.assertEqual(self.biomarker.psa_level, 230)
        self.assertEqual(self.biomarker.ca125, 29)
        self.assertEqual(self.biomarker.cea, 11)
        self.assertEqual(self.biomarker.er_status, "Cannot be determined")
        self.assertEqual(self.biomarker.er_percent_positive, 18.3)
        self.assertEqual(self.biomarker.pr_status, "Unknown")
        self.assertEqual(self.biomarker.pr_percent_positive, 65.2)
        self.assertEqual(self.biomarker.her2_ihc_status, "Equivocal")
        self.assertEqual(self.biomarker.her2_ish_status, "Negative")
        self.assertEqual(self.biomarker.hpv_ihc_status, "Not applicable")
        self.assertEqual(self.biomarker.hpv_pcr_status, "Negative")
        self.assertEqual(self.biomarker.hpv_strain, ["HPV35"])

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
            ],
            model_fields=self.biomarker._meta.fields,
        )
        for field in optional_fields:
            setattr(self.biomarker, field, None)
            self.biomarker.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
                "submitter_specimen_id",
                "submitter_primary_diagnosis_id",
                "submitter_treatment_id",
                "submitter_follow_up_id",
            ],
            model_fields=self.biomarker._meta.fields,
        )
        for field in optional_fields:
            setattr(self.biomarker, field, "")
            self.biomarker.full_clean()


class ComorbidityTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.valid_values = {
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "prior_malignancy": "Yes",
            "laterality_of_prior_malignancy": "Not applicable",
            "age_at_comorbidity_diagnosis": 35,
            "comorbidity_type_code": "C04.0",
            "comorbidity_treatment_status": "No",
            "comorbidity_treatment": "Surgery",
        }
        self.comorbidity = Comorbidity.objects.create(**self.valid_values)

    def test_comorbidity_creation(self):
        self.assertIsInstance(self.comorbidity, Comorbidity)

    def test_comorbitidy_fields(self):
        self.assertEqual(self.comorbidity.program_id, self.program)
        self.assertEqual(self.comorbidity.submitter_donor_id, self.donor)
        self.assertEqual(self.comorbidity.prior_malignancy, "Yes")
        self.assertEqual(
            self.comorbidity.laterality_of_prior_malignancy, "Not applicable"
        )
        self.assertEqual(self.comorbidity.age_at_comorbidity_diagnosis, 35)
        self.assertEqual(self.comorbidity.comorbidity_type_code, "C04.0")
        self.assertEqual(self.comorbidity.comorbidity_treatment_status, "No")
        self.assertEqual(self.comorbidity.comorbidity_treatment, "Surgery")

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
            ],
            model_fields=self.comorbidity._meta.fields,
        )
        for field in optional_fields:
            setattr(self.comorbidity, field, None)
            self.comorbidity.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
            ],
            model_fields=self.comorbidity._meta.fields,
        )
        for field in optional_fields:
            setattr(self.comorbidity, field, "")
            self.comorbidity.full_clean()

    def test_invalid_prior_malignancy(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["prior_malignancy"] = value
                self.serializer = ComorbiditySerializer(
                    instance=self.comorbidity, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_invalid_laterality_of_prior_malignancy(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["laterality_of_prior_malignancy"] = value
                self.serializer = ComorbiditySerializer(
                    instance=self.comorbidity, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    # TODO: fix regular expression
    # def test_comorbidity_type_code(self):
    #     invalid_values = ["8260/3", 1]
    #     for value in invalid_values:
    #         with self.subTest(value=value):
    #             self.valid_values["comorbidity_type_code"] = value
    #             self.serializer = ComorbiditySerializer(instance=self.followup, data=self.valid_values)
    #             self.assertFalse(self.serializer.is_valid())

    def test_invalid_comorbidity_treatment_status(self):
        invalid_values = get_invalid_choices()
        for value in invalid_values:
            with self.subTest(value=value):
                self.valid_values["comorbidity_treatment_status"] = value
                self.serializer = ComorbiditySerializer(
                    instance=self.comorbidity, data=self.valid_values
                )
                self.assertFalse(self.serializer.is_valid())

    def test_comorbidity_treatment_max_length(self):
        self.comorbidity.comorbidity_treatment = "f" * 256
        with self.assertRaises(DataError):
            self.comorbidity.save()


class ExposureTest(TestCase):
    def setUp(self):
        self.program = Program.objects.create(program_id="SYNTHETIC")
        self.donor = Donor.objects.create(
            submitter_donor_id="DONOR_1",
            program_id=self.program,
            primary_site=["Adrenal gland"],
        )
        self.valid_values = {
            "program_id": self.program,
            "submitter_donor_id": self.donor,
            "tobacco_smoking_status": "Current smoker",
            "tobacco_type": ["Unknown", "Electronic cigarettes", "Not applicable"],
            "pack_years_smoked": 280,
        }
        self.exposure = Exposure.objects.create(**self.valid_values)

    def test_exposure_creation(self):
        self.assertIsInstance(self.exposure, Exposure)

    def test_exposure_fields(self):
        self.assertEqual(self.exposure.program_id, self.program)
        self.assertEqual(self.exposure.submitter_donor_id, self.donor)
        self.assertEqual(self.exposure.tobacco_smoking_status, "Current smoker")
        self.assertEqual(
            self.exposure.tobacco_type,
            ["Unknown", "Electronic cigarettes", "Not applicable"],
        )
        self.assertEqual(self.exposure.pack_years_smoked, 280)

    def test_null_optional_fields(self):
        """Tests no exceptions are raised when saving null values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
            ],
            model_fields=self.exposure._meta.fields,
        )
        for field in optional_fields:
            setattr(self.exposure, field, None)
            self.exposure.full_clean()

    def test_blank_optional_fields(self):
        """Tests no exceptions are raised when saving blank values in optional fields."""
        optional_fields = get_optional_fields(
            excluded_fields=[
                "id",
                "submitter_donor_id",
                "program_id",
            ],
            model_fields=self.exposure._meta.fields,
        )
        for field in optional_fields:
            setattr(self.exposure, field, "")
            self.exposure.full_clean()
