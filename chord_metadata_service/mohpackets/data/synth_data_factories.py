import random
import math
import factory
import chord_metadata_service.mohpackets.permissible_values as PERM_VAL
import synth_data_values as SYNTH_VAL

from chord_metadata_service.mohpackets.tests.factories import (
    BiomarkerFactory,
    ComorbidityFactory,
    DonorFactory,
    ExposureFactory,
    FollowUpFactory,
    PrimaryDiagnosisFactory,
    RadiationFactory,
    SampleRegistrationFactory,
    SpecimenFactory,
    SurgeryFactory,
    SystemicTherapyFactory,
    TreatmentFactory,
    ProgramFactory,
    days_to_months,
)

"""
    This file contains factory classes for generating synthetic data.

    They inherit from factories used for code testing at chord_metadata_service.mohpackets.tests.factories but
    override some variables to make them more suitable for synthetic data testing.

    They are primarily used in the `data_factory.py` script to create a set of programs with linked MoHCCN data for
    ingest into the CanDIG platform.

    NullSynth*Factories have all nullable fields nulled
    AllSynthFactories have no null fields (within model constraints, e.g. if a donor has is_deceased False, there will
    not be a cause_of_death)

    Example Usage:

        # This will create a Donor instance and a Program instance
        donor = SynthDonorFactory()

    Note:
        These factories use the Factory Boy library (https://factoryboy.readthedocs.io/)
        to generate test data.
        Some business logic is not strictly enforced.

    Author: Marion Shadbolt
"""


###############
#  Factories  #
###############


class SynthProgramFactory(ProgramFactory):
    class Meta:
        django_get_or_create = ("program_id",)

    # default values
    program_id = factory.Sequence(lambda n: f"SYNTH_{str(n).zfill(2)}")


class SynthDonorFactory(DonorFactory):
    class Meta:
        django_get_or_create = ("submitter_donor_id",)
        exclude = ("fill_dob", "null_percent", "is_deceased_bool",)

    submitter_donor_id = factory.Sequence(lambda n: f"DONOR_{str(n).zfill(4)}")
    gender = factory.Faker("random_element", elements=SYNTH_VAL.GENDER)
    sex_at_birth = factory.Faker("random_element", elements=SYNTH_VAL.SEX_AT_BIRTH)
    fill_dob = factory.Faker("pybool", truth_probability=80)
    date_of_birth = factory.Maybe(
        "fill_dob",
        yes_declaration=factory.LazyFunction(
            lambda: {
                "day_interval": random.randint(-21900, -12775),
            }
        ),
        no_declaration=None,
    )


class NullSynthDonorFactory(SynthDonorFactory):
    submitter_donor_id = factory.Sequence(lambda n: f"DONOR_NULL_{str(n).zfill(4)}")
    gender = None
    sex_at_birth = None
    is_deceased = None
    lost_to_followup_reason = None
    lost_to_followup_after_clinical_event_identifier = None
    date_alive_after_lost_to_followup = None
    date_resolution = "day"
    cause_of_death = None
    date_of_birth = None
    date_of_death = None


class AllSynthDonorFactory(DonorFactory):
    class Meta:
        django_get_or_create = ("submitter_donor_id",)

    submitter_donor_id = factory.Sequence(lambda n: f"DONOR_ALL_{str(n).zfill(4)}")
    is_deceased = factory.Iterator(PERM_VAL.UBOOLEAN)
    gender = factory.Faker("random_element", elements=SYNTH_VAL.ALL_GENDER)
    sex_at_birth = factory.Faker("random_element", elements=SYNTH_VAL.ALL_SEX_AT_BIRTH)

    @factory.post_generation
    def set_sex_at_birth(self, create, extracted, **kwargs):
        """This shouldn't be necessary but was finding null values sometimes"""
        if not self.sex_at_birth:
            self.sex_at_birth = random.choice(["Male", "Female", "Other"])


class SynthPrimaryDiagnosisFactory(PrimaryDiagnosisFactory):
    class Meta:
        django_get_or_create = ("submitter_primary_diagnosis_id",)
        exclude = "fill_dod"

    submitter_primary_diagnosis_id = factory.Sequence(
        lambda n: f"DIAG_{str(n).zfill(4)}"
    )
    fill_dod = factory.Faker("pybool", truth_probability=80)
    date_of_diagnosis = factory.Maybe(
        "fill_dod",
        yes_declaration={"month_interval": 0, "day_interval": 0},
        no_declaration=None,
    )
    cancer_type_code = factory.Faker("random_element", elements=SYNTH_VAL.CANCER_CODES)
    basis_of_diagnosis = factory.Faker(
        "random_element", elements=SYNTH_VAL.BASIS_OF_DIAGNOSIS
    )
    laterality = factory.Faker(
        "random_element", elements=SYNTH_VAL.PRIMARY_DIAGNOSIS_LATERALITY
    )
    clinical_tumour_staging_system = factory.Faker(
        "random_element", elements=SYNTH_VAL.TUMOUR_STAGING_SYSTEM
    )
    clinical_t_category = None
    clinical_n_category = None
    clinical_m_category = None
    clinical_stage_group = factory.Faker(
        "random_element", elements=SYNTH_VAL.STAGE_GROUP
    )
    pathological_tumour_staging_system = factory.Faker(
        "random_element", elements=SYNTH_VAL.TUMOUR_STAGING_SYSTEM
    )
    pathological_t_category = None
    pathological_n_category = None
    pathological_m_category = None
    pathological_stage_group = factory.Faker(
        "random_element", elements=SYNTH_VAL.STAGE_GROUP
    )
    primary_site = factory.Iterator(SYNTH_VAL.PRIMARY_SITE)

    @factory.post_generation
    def set_clinical_event_identifier(self, create, extracted, **kwargs):
        """If Donor isn't deceased, 85% of the time, fill out the 'lost_to_followup' fields on the linked donor"""
        if random.random() < 0.15:
            pass
        else:
            donor = self.donor_uuid
            if donor.is_deceased == "No":
                donor.lost_to_followup_after_clinical_event_identifier = (
                    self.submitter_primary_diagnosis_id
                )
                donor.lost_to_followup_reason = random.choice(
                    PERM_VAL.LOST_TO_FOLLOWUP_REASON
                )
                donor.date_alive_after_lost_to_followup = {
                    "day_interval": random.randint(3650, 4380),
                }
                donor.date_alive_after_lost_to_followup["month_interval"] = (
                    days_to_months(
                        donor.date_alive_after_lost_to_followup["day_interval"]
                    )
                )
                donor.save()

    @factory.post_generation
    def consistent_stages(self, create, extracted, **kwargs):
        if (
            self.clinical_tumour_staging_system is None
            and self.pathological_tumour_staging_system is None
        ):
            self.clinical_tumour_staging_system = random.choice(
                PERM_VAL.TUMOUR_STAGING_SYSTEM
            )
        if (
            self.clinical_tumour_staging_system
            and self.clinical_tumour_staging_system.startswith("AJCC")
        ):
            self.clinical_t_category = random.choice(PERM_VAL.T_CATEGORY)
            self.clinical_m_category = random.choice(PERM_VAL.M_CATEGORY)
            self.clinical_n_category = random.choice(PERM_VAL.N_CATEGORY)
        if (
            self.pathological_tumour_staging_system
            and self.pathological_tumour_staging_system.startswith("AJCC")
        ):
            self.pathological_t_category = random.choice(PERM_VAL.T_CATEGORY)
            self.pathological_m_category = random.choice(PERM_VAL.M_CATEGORY)
            self.pathological_n_category = random.choice(PERM_VAL.N_CATEGORY)
        if (
            self.clinical_tumour_staging_system
            and self.clinical_tumour_staging_system in SYNTH_VAL.STAGE_GROUP_KEY.keys()
        ):
            self.clinical_stage_group = random.choice(
                SYNTH_VAL.STAGE_GROUP_KEY[self.clinical_tumour_staging_system]
            )
        if (
            self.pathological_tumour_staging_system
            and self.pathological_tumour_staging_system
            in SYNTH_VAL.STAGE_GROUP_KEY.keys()
        ):
            self.pathological_stage_group = random.choice(
                SYNTH_VAL.STAGE_GROUP_KEY[self.pathological_tumour_staging_system]
            )


class NullSynthPrimaryDiagnosisFactory(PrimaryDiagnosisFactory):
    submitter_primary_diagnosis_id = factory.Sequence(
        lambda n: f"DIAG_NULL_{str(n).zfill(4)}"
    )

    date_of_diagnosis = None
    cancer_type_code = None
    basis_of_diagnosis = None
    laterality = None
    clinical_tumour_staging_system = None
    clinical_t_category = None
    clinical_n_category = None
    clinical_m_category = None
    clinical_stage_group = None
    pathological_tumour_staging_system = None
    pathological_t_category = None
    pathological_n_category = None
    pathological_m_category = None
    pathological_stage_group = None
    primary_site = None

    @factory.post_generation
    def set_clinical_event_identifier(self, create, extracted, **kwargs):
        pass


class AllSynthPrimaryDiagnosisFactory(PrimaryDiagnosisFactory):
    class Meta:
        django_get_or_create = ("submitter_primary_diagnosis_id",)

    submitter_primary_diagnosis_id = factory.Sequence(
        lambda n: f"DIAG_ALL_{str(n).zfill(4)}"
    )
    cancer_type_code = "C06.9"
    primary_site = "Floor of mouth"
    basis_of_diagnosis = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_BASIS_OF_DIAGNOSIS
    )
    laterality = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_PRIMARY_DIAGNOSIS_LATERALITY
    )
    clinical_tumour_staging_system = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TUMOUR_STAGING_SYSTEM
    )
    clinical_stage_group = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_STAGE_GROUP
    )
    pathological_tumour_staging_system = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TUMOUR_STAGING_SYSTEM
    )

    @factory.post_generation
    def set_clinical_event_identifier(self, create, extracted, **kwargs):
        """If donor is not deceased, fill out lost to followup info."""
        donor = self.donor_uuid
        if donor.is_deceased == "No":
            donor.lost_to_followup_after_clinical_event_identifier = (
                self.submitter_primary_diagnosis_id
            )
            donor.lost_to_followup_reason = random.choice(
                PERM_VAL.LOST_TO_FOLLOWUP_REASON
            )
            donor.date_alive_after_lost_to_followup = {
                "day_interval": random.randint(3650, 4380),
            }
            donor.date_alive_after_lost_to_followup["month_interval"] = (
                days_to_months(
                    donor.date_alive_after_lost_to_followup["day_interval"]
                )
            )
            donor.cause_of_death = None
            donor.date_of_death = None
            donor.save()
        elif donor.is_deceased == "Yes":
            donor.cause_of_death = random.choice(SYNTH_VAL.ALL_CAUSE_OF_DEATH)
            donor.date_of_death = {"day_interval": random.randint(3650, 16425)}
            donor.date_of_death["month_interval"] = days_to_months(donor.date_of_death["day_interval"])

    @factory.post_generation
    def all_staging_filled(self, create, extracted, **kwargs):
        if self.clinical_tumour_staging_system is None:
            self.clinical_tumour_staging_system = random.choice(SYNTH_VAL.ALL_TUMOUR_STAGING_SYSTEM)
        if self.clinical_stage_group is None:
            self.clinical_stage_group = random.choice(SYNTH_VAL.ALL_STAGE_GROUP)
        if self.clinical_n_category is None:
            self.clinical_n_category = random.choice(PERM_VAL.N_CATEGORY)
        if self.clinical_m_category is None:
            self.clinical_m_category = random.choice(PERM_VAL.M_CATEGORY)
        if self.clinical_t_category is None:
            self.clinical_t_category = random.choice(PERM_VAL.T_CATEGORY)
        if self.pathological_tumour_staging_system is None:
            self.pathological_tumour_staging_system = random.choice(SYNTH_VAL.ALL_TUMOUR_STAGING_SYSTEM)
        if self.pathological_stage_group is None:
            self.pathological_stage_group = random.choice(SYNTH_VAL.ALL_STAGE_GROUP)
        if self.pathological_n_category is None:
            self.pathological_n_category = random.choice(PERM_VAL.N_CATEGORY)
        if self.pathological_m_category is None:
            self.pathological_m_category = random.choice(PERM_VAL.M_CATEGORY)
        if self.pathological_t_category is None:
            self.pathological_t_category = random.choice(PERM_VAL.T_CATEGORY)


class SynthSpecimenFactory(SpecimenFactory):
    class Meta:
        django_get_or_create = ("submitter_specimen_id",)

    submitter_specimen_id = factory.Sequence(lambda n: f"SPECIMEN_{str(n).zfill(4)}")
    specimen_storage = factory.Faker("random_element", elements=SYNTH_VAL.STORAGE)
    specimen_processing = factory.Faker(
        "random_element", elements=SYNTH_VAL.SPECIMEN_PROCESSING
    )
    tumour_histological_type = None
    specimen_anatomic_location = factory.Faker(
        "random_element", elements=SYNTH_VAL.TOPOGRAPHY_CODES
    )
    specimen_laterality = factory.Faker(
        "random_element", elements=SYNTH_VAL.SPECIMEN_LATERALITY
    )
    reference_pathology_confirmed_diagnosis = factory.Faker(
        "random_element", elements=SYNTH_VAL.CONFIRMED_DIAGNOSIS_TUMOUR
    )
    reference_pathology_confirmed_tumour_presence = factory.Faker(
        "random_element", elements=SYNTH_VAL.CONFIRMED_DIAGNOSIS_TUMOUR
    )
    tumour_grading_system = factory.Faker(
        "random_element", elements=SYNTH_VAL.TUMOUR_GRADING_SYSTEM
    )
    tumour_grade = factory.Faker("random_element", elements=SYNTH_VAL.TUMOUR_GRADE)
    percent_tumour_cells_range = factory.Faker(
        "random_element", elements=SYNTH_VAL.PERCENT_CELLS_RANGE
    )
    percent_tumour_cells_measurement_method = factory.Faker(
        "random_element", elements=SYNTH_VAL.CELLS_MEASURE_METHOD
    )

    @factory.post_generation
    def set_date(self, create, extracted, **kwargs):
        """85% of the time, set a specimen collection date."""
        if random.random() < 0.15:
            self.specimen_collection_date = None
        else:
            self.specimen_collection_date = {"day_interval": random.randint(0, 90)}
            self.specimen_collection_date["month_interval"] = days_to_months(
                self.specimen_collection_date["day_interval"]
            )

    @factory.post_generation
    def generate_histology_code(self, create, extracted, **kwargs):
        if random.random() < 0.15:
            self.tumour_histological_type = None
        else:
            one = str(random.randint(8, 9))
            two = str(random.randint(0, 999)).rjust(3, "0")
            code = one + two + "/3"
            self.tumour_histological_type = code


class NullSynthSpecimenFactory(SpecimenFactory):
    submitter_specimen_id = factory.Sequence(
        lambda n: f"SPECIMEN_NULL_{str(n).zfill(4)}"
    )

    specimen_collection_date = None
    specimen_storage = None
    specimen_processing = None
    tumour_histological_type = None
    specimen_anatomic_location = None
    specimen_laterality = None
    reference_pathology_confirmed_diagnosis = None
    reference_pathology_confirmed_tumour_presence = None
    tumour_grading_system = None
    tumour_grade = None
    percent_tumour_cells_measurement_method = None

    @factory.post_generation
    def set_months(self, create, extracted, **kwargs):
        """override method to keep null values"""
        pass

    @factory.post_generation
    def generate_histology_code(self, create, extracted, **kwargs):
        """override method to keep null values"""
        pass


class AllSynthSpecimenFactory(SpecimenFactory):
    class Meta:
        django_get_or_create = ("submitter_specimen_id",)

    submitter_specimen_id = factory.Sequence(
        lambda n: f"SPECIMEN_ALL_{str(n).zfill(4)}"
    )
    specimen_storage = factory.Faker("random_element", elements=SYNTH_VAL.ALL_STORAGE)
    specimen_processing = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_SPECIMEN_PROCESSING
    )
    tumour_histological_type = None
    specimen_anatomic_location = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TOPOGRAPHY_CODES
    )
    specimen_laterality = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_SPECIMEN_LATERALITY
    )
    reference_pathology_confirmed_diagnosis = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_CONFIRMED_DIAGNOSIS_TUMOUR
    )
    reference_pathology_confirmed_tumour_presence = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_CONFIRMED_DIAGNOSIS_TUMOUR
    )
    tumour_grading_system = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TUMOUR_GRADING_SYSTEM
    )
    tumour_grade = factory.Faker("random_element", elements=SYNTH_VAL.ALL_TUMOUR_GRADE)
    percent_tumour_cells_range = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_PERCENT_CELLS_RANGE
    )
    percent_tumour_cells_measurement_method = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_CELLS_MEASURE_METHOD
    )

    @factory.post_generation
    def generate_histology_code(self, create, extracted, **kwargs):
        """override method to remove 15% nulls"""
        one = str(random.randint(8, 9))
        two = str(random.randint(0, 999)).rjust(3, "0")
        code = one + two + "/3"
        self.tumour_histological_type = code


class SynthSampleRegistrationFactory(SampleRegistrationFactory):
    class Meta:
        django_get_or_create = ("submitter_sample_id",)

    submitter_sample_id = factory.Sequence(lambda n: f"SAMPLE_{str(n).zfill(4)}")
    specimen_tissue_source = factory.Faker(
        "random_element", elements=SYNTH_VAL.SPECIMEN_TISSUE_SOURCE
    )
    tumour_normal_designation = factory.Iterator(SYNTH_VAL.TUMOUR_DESIGNATION)
    specimen_type = factory.Faker("random_element", elements=SYNTH_VAL.SPECIMEN_TYPE)
    sample_type = factory.Faker("random_element", elements=SYNTH_VAL.SAMPLE_TYPE)


class NullSynthSampleRegistrationFactory(SampleRegistrationFactory):
    submitter_sample_id = factory.Sequence(lambda n: f"SAMPLE_NULL_{str(n).zfill(4)}")

    specimen_tissue_source = None
    tumour_normal_designation = None
    specimen_type = None
    sample_type = None


class AllSynthSampleRegistrationFactory(SampleRegistrationFactory):
    class Meta:
        django_get_or_create = ("submitter_sample_id",)

    submitter_sample_id = factory.Sequence(lambda n: f"SAMPLE_ALL_{str(n).zfill(4)}")
    specimen_tissue_source = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_SPECIMEN_TISSUE_SOURCE
    )
    specimen_type = factory.Faker("random_element", elements=SYNTH_VAL.ALL_SPECIMEN_TYPE)
    sample_type = factory.Faker("random_element", elements=SYNTH_VAL.ALL_SAMPLE_TYPE)


class SynthTreatmentFactory(TreatmentFactory):
    class Meta:
        django_get_or_create = ("submitter_treatment_id",)

    submitter_treatment_id = factory.Sequence(lambda n: f"TREATMENT_{str(n).zfill(4)}")
    treatment_type = factory.Faker(
        "random_elements",
        elements=SYNTH_VAL.TREATMENT_TYPE,
        length=random.randint(1, 3),
        unique=True,
    )
    treatment_intent = factory.Faker(
        "random_element", elements=SYNTH_VAL.TREATMENT_INTENT
    )
    response_to_treatment_criteria_method = factory.Faker(
        "random_element", elements=SYNTH_VAL.TREATMENT_RESPONSE_METHOD
    )
    response_to_treatment = factory.Faker(
        "random_element", elements=SYNTH_VAL.TREATMENT_RESPONSE
    )
    status_of_treatment = factory.Faker(
        "random_element", elements=SYNTH_VAL.TREATMENT_STATUS
    )

    @factory.post_generation
    def set_treatment_dates(self, create, extracted, **kwargs):
        treatment = self
        if random.random() < 0.15:
            treatment.treatment_start_date = None
        else:
            day_int = random.randint(5, 180)
            treatment.treatment_start_date = {
                "day_interval": day_int,
                "month_interval": days_to_months(day_int),
            }
        if random.random() < 0.15:
            treatment.treatment_end_date = None
        else:
            if treatment.treatment_start_date:
                min_start = treatment.treatment_start_date["day_interval"] + 30
            else:
                min_start = 5
            min_end = min_start + 365
            day_int = random.randint(min_start, min_end)
            treatment.treatment_end_date = {
                "day_interval": day_int,
                "month_interval": days_to_months(day_int),
            }
        treatment.save()

    @factory.post_generation
    def correct_treatment_type(self, create, extracted, **kwargs):
        if random.random() < 0.15:
            self.treatment_type = []
        elif self.treatment_type and "No treatment" in self.treatment_type:
            self.treatment_type = ["No treatment"]
        self.treatment_type = [x for x in self.treatment_type if x is not None]


class NullSynthTreatmentFactory(TreatmentFactory):
    submitter_treatment_id = factory.Sequence(
        lambda n: f"TREATMENT_NULL_{str(n).zfill(4)}"
    )
    treatment_type = None
    is_primary_treatment = None
    treatment_start_date = None
    treatment_end_date = None
    treatment_intent = None
    response_to_treatment_criteria_method = None
    response_to_treatment = None
    status_of_treatment = None

    @factory.post_generation
    def set_treatment_dates(self, create, extracted, **kwargs):
        """override method to keep null values"""
        pass

    @factory.post_generation
    def correct_treatment_type(self, create, extracted, **kwargs):
        """override method to keep null values"""
        pass


class AllSynthTreatmentFactory(TreatmentFactory):
    class Meta:
        django_get_or_create = ("submitter_treatment_id",)

    submitter_treatment_id = factory.Sequence(
        lambda n: f"TREATMENT_ALL_{str(n).zfill(4)}"
    )
    is_primary_treatment = factory.Faker("random_element", elements=["Yes", "No"])
    treatment_type = factory.Faker(
        "random_elements",
        elements=SYNTH_VAL.TREATMENT_TYPE_FOR_ALL,
        unique=True,
        length=random.randint(1, 3),
    )
    treatment_intent = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TREATMENT_INTENT
    )
    response_to_treatment_criteria_method = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TREATMENT_RESPONSE_METHOD
    )
    response_to_treatment = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TREATMENT_RESPONSE
    )
    status_of_treatment = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TREATMENT_STATUS
    )

    @factory.post_generation
    def set_treatment_dates(self, create, extracted, **kwargs):
        """override method to prevent 15% nulls"""
        day_int = random.randint(5, 180)
        self.treatment_start_date = {
            "day_interval": day_int,
            "month_interval": days_to_months(day_int),
        }
        min_start = self.treatment_start_date["day_interval"] + 30
        min_end = min_start + 365
        day_int = random.randint(self.treatment_start_date["day_interval"], min_end)
        self.treatment_end_date = {
            "day_interval": day_int,
            "month_interval": days_to_months(day_int),
        }

    @factory.post_generation
    def correct_treatment_type(self, create, extracted, **kwargs):
        """override method to prevent 15% nulls"""
        if self.treatment_type and "No treatment" in self.treatment_type:
            self.treatment_type = ["No treatment"]


class SynthSystemicTherapyFactory(SystemicTherapyFactory):

    days_per_cycle_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    days_per_cycle = factory.Maybe(
        "days_per_cycle_not_available",
        None,
        factory.Faker("random_int", min=1, max=30)
    )
    number_of_cycles_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    number_of_cycles = factory.Maybe(
        "number_of_cycles_not_available",
        None,
        factory.Faker("random_int", min=1, max=10)
    )
    drug_name = None
    drug_reference_database = None
    drug_reference_identifier = None
    drug_dose_units = factory.Faker("random_element", elements=SYNTH_VAL.DOSAGE_UNITS)
    prescribed_cumulative_drug_dose_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    prescribed_cumulative_drug_dose = factory.Maybe(
        "prescribed_cumulative_drug_dose_not_available",
        None,
        factory.Faker(
            "pyfloat",
            left_digits=2,
            right_digits=1,
            positive=True,
            min_value=20,
            max_value=50,
        ),
    )
    actual_cumulative_drug_dose_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    actual_cumulative_drug_dose = factory.Maybe(
        "actual_cumulative_drug_dose_not_available",
        None,
        factory.Faker(
            "pyfloat",
            left_digits=2,
            right_digits=1,
            positive=True,
            min_value=51,
            max_value=100,
        ),
    )

    @factory.post_generation
    def add_dates(self, create, extracted, **kwargs):
        if random.random() < 0.15:
            pass
        else:
            treatment = self.treatment_uuid
            if treatment.treatment_start_date and treatment.treatment_end_date:
                self.start_date = {
                    "day_interval": random.randint(
                        treatment.treatment_start_date["day_interval"],
                        treatment.treatment_end_date["day_interval"],
                    )
                }
                self.start_date["month_interval"] = days_to_months(
                    self.start_date["day_interval"]
                )
                self.end_date = {
                    "day_interval": random.randint(
                        self.start_date["day_interval"],
                        treatment.treatment_end_date["day_interval"],
                    )
                }
                self.end_date["month_interval"] = days_to_months(
                    self.end_date["day_interval"]
                )
            elif treatment.treatment_start_date:
                self.start_date = {
                    "day_interval": random.randint(
                        treatment.treatment_start_date["day_interval"],
                        treatment.treatment_start_date["day_interval"] + 100,
                    )
                }
                self.end_date = {
                    "day_interval": random.randint(
                        self.start_date["day_interval"],
                        self.start_date["day_interval"] + 100,
                    )
                }
                self.end_date["month_interval"] = days_to_months(
                    self.end_date["day_interval"]
                )
            elif treatment.treatment_end_date:
                day_int = random.randint(
                    max([0, (treatment.treatment_end_date["day_interval"] - 100)]),
                    treatment.treatment_end_date["day_interval"],
                )
                self.start_date = {"day_interval": day_int}
                self.start_date["month_interval"] = days_to_months(
                    self.start_date["day_interval"]
                )
                day_int = random.randint(
                    self.start_date["day_interval"],
                    treatment.treatment_end_date["day_interval"],
                )
                self.end_date = {"day_interval": day_int}
                self.end_date["month_interval"] = days_to_months(
                    self.end_date["day_interval"]
                )

    @factory.post_generation
    def add_systemic_therapy_treatment_type(self, create, extracted, **kwargs):
        treatment = self.treatment_uuid
        if treatment.treatment_type == [None] or treatment.treatment_type is None:
            treatment.treatment_type = ["Systemic therapy"]
        elif "Systemic therapy" not in treatment.treatment_type:
            treatment.treatment_type.append("Systemic therapy")
        if "No treatment" in treatment.treatment_type:
            treatment.treatment_type.remove("No treatment")
        treatment.treatment_type = [
            x for x in treatment.treatment_type if x is not None
        ]

    @factory.post_generation
    def add_drug_info(self, create, extracted, **kwargs):
        if random.random() < 0.15:
            self.drug_name = None
            self.drug_reference_database = None
            self.drug_reference_identifier = None
        else:
            self.drug_reference_database = random.choice(PERM_VAL.DRUG_REFERENCE_DB)
            if self.drug_reference_database:
                if self.systemic_therapy_type == "Chemotherapy":
                    self.drug_name = random.choice(list(SYNTH_VAL.CHEMO_DRUGS.keys()))
                    if self.drug_name:
                        self.drug_reference_identifier = SYNTH_VAL.CHEMO_DRUGS[
                            self.drug_name
                        ][self.drug_reference_database]
                elif self.systemic_therapy_type == "Hormone therapy":
                    self.drug_name = random.choice(list(SYNTH_VAL.HORMONE_DRUGS.keys()))
                    if self.drug_name:
                        self.drug_reference_identifier = SYNTH_VAL.HORMONE_DRUGS[
                            self.drug_name
                        ][self.drug_reference_database]
                elif self.systemic_therapy_type == "Immunotherapy":
                    self.drug_name = random.choice(list(SYNTH_VAL.IMMUNO_DRUGS.keys()))
                    if self.drug_name:
                        self.drug_reference_identifier = SYNTH_VAL.IMMUNO_DRUGS[
                            self.drug_name
                        ][self.drug_reference_database]


class NullSynthSystemicTherapyFactory(SystemicTherapyFactory):
    drug_dose_units = None
    prescribed_cumulative_drug_dose = None
    actual_cumulative_drug_dose = None

    @factory.post_generation
    def add_dates(self, create, extracted, **kwargs):
        """Override method to keep null values."""
        pass

    @factory.post_generation
    def remove_drug_info(self, create, extracted, **kwargs):
        self.drug_name = None
        self.drug_reference_database = None
        self.drug_reference_identifier = None


class AllSynthSystemicTherapyFactory(SynthSystemicTherapyFactory):
    drug_reference_database = factory.Faker(
        "random_element", elements=PERM_VAL.DRUG_REFERENCE_DB
    )

    @factory.post_generation
    def add_drug_info(self, create, extracted, **kwargs):
        if not self.systemic_therapy_type:
            self.systemic_therapy_type = random.choice(PERM_VAL.SYSTEMIC_THERAPY_TYPE)
        if self.systemic_therapy_type == "Chemotherapy":
            self.drug_name = random.choice(list(SYNTH_VAL.CHEMO_DRUGS.keys()))
            if self.drug_name:
                self.drug_reference_identifier = SYNTH_VAL.CHEMO_DRUGS[self.drug_name][
                    self.drug_reference_database
                ]
        elif self.systemic_therapy_type == "Hormone therapy":
            self.drug_name = random.choice(list(SYNTH_VAL.HORMONE_DRUGS.keys()))
            if self.drug_name:
                self.drug_reference_identifier = SYNTH_VAL.HORMONE_DRUGS[
                    self.drug_name
                ][self.drug_reference_database]
        elif self.systemic_therapy_type == "Immunotherapy":
            self.drug_name = random.choice(list(SYNTH_VAL.IMMUNO_DRUGS.keys()))
            if self.drug_name:
                self.drug_reference_identifier = SYNTH_VAL.IMMUNO_DRUGS[self.drug_name][
                    self.drug_reference_database
                ]
        # I don't know why but it is sometimes null but I don't want any nulls so catching it here
        if self.drug_name is None:
            self.drug_name = "Nivolumab"
            self.drug_reference_identifier = "1597876"
            self.drug_reference_database = "RxNorm"
        if self.drug_dose_units is None:
            self.drug_dose_units = "mg/kg"

    @factory.post_generation
    def add_dates(self, create, extracted, **kwargs):
        """Override function so no nulls"""
        treatment = self.treatment_uuid
        if treatment.treatment_start_date and treatment.treatment_end_date:
            self.start_date = {
                "day_interval": random.randint(
                    treatment.treatment_start_date["day_interval"],
                    treatment.treatment_end_date["day_interval"],
                )
            }
            self.start_date["month_interval"] = days_to_months(
                self.start_date["day_interval"]
            )
            self.end_date = {
                "day_interval": random.randint(
                    self.start_date["day_interval"],
                    treatment.treatment_end_date["day_interval"],
                )
            }
            self.end_date["month_interval"] = days_to_months(
                self.end_date["day_interval"]
            )
        elif treatment.treatment_start_date:
            self.start_date = {
                "day_interval": random.randint(
                    treatment.treatment_start_date["day_interval"],
                    treatment.treatment_start_date["day_interval"] + 50,
                )
            }
            self.start_date["month_interval"] = days_to_months(
                self.start_date["day_interval"]
            )
            self.end_date = {
                "day_interval": random.randint(
                    self.start_date["day_interval"],
                    self.start_date["day_interval"] + 50,
                )
            }
            self.end_date["month_interval"] = days_to_months(
                self.end_date["day_interval"]
            )
        elif treatment.treatment_end_date:
            self.start_date = {
                "day_interval": random.randint(
                    treatment.treatment_end_date["day_interval"] - 50,
                    treatment.treatment_end_date["day_interval"],
                )
            }
            self.start_date["month_interval"] = days_to_months(
                self.start_date["day_interval"]
            )
            self.end_date = {
                "day_interval": random.randint(
                    self.start_date["day_interval"],
                    treatment.treatment_end_date["day_interval"],
                )
            }
            self.end_date["month_interval"] = days_to_months(
                self.end_date["day_interval"]
            )


class SynthRadiationFactory(RadiationFactory):
    class Meta:
        exclude = ("fill_dosage_fraction",)

    radiation_therapy_modality = factory.Faker(
        "random_element", elements=SYNTH_VAL.RADIATION_THERAPY_MODALITY
    )
    radiation_therapy_type = factory.Faker(
        "random_element", elements=SYNTH_VAL.THERAPY_TYPE
    )
    anatomical_site_irradiated = factory.Faker(
        "random_element", elements=SYNTH_VAL.RADIATION_ANATOMICAL_SITE
    )

    radiation_therapy_fractions_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    radiation_therapy_fractions = factory.Maybe(
        "radiation_therapy_fractions_not_available", factory.Faker("random_int", min=1, max=30), None
    )
    radiation_therapy_dosage_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    radiation_therapy_dosage = factory.Maybe(
        "radiation_therapy_dosage_not_available", factory.Faker("random_int", min=1, max=100), None
    )
    radiation_boost = "No"
    reference_radiation_treatment_id = None


class NullSynthRadiationFactory(RadiationFactory):
    radiation_therapy_modality = None
    radiation_therapy_type = None
    radiation_therapy_fractions = None
    radiation_therapy_dosage = None
    anatomical_site_irradiated = None
    radiation_boost = None


class AllSynthRadiationFactory(SynthRadiationFactory):
    fill_dosage_fraction = True
    radiation_therapy_modality = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_RADIATION_THERAPY_MODALITY
    )
    radiation_therapy_type = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_THERAPY_TYPE
    )
    anatomical_site_irradiated = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_RADIATION_ANATOMICAL_SITE
    )
    radiation_therapy_fractions = factory.Faker("random_int", min=1, max=30)
    radiation_therapy_dosage = factory.Faker("random_int", min=1, max=100)


class SynthSurgeryFactory(SurgeryFactory):
    class Meta:
        exclude = ("null_margin_types",)

    surgery_site = factory.Faker("random_element", elements=SYNTH_VAL.TOPOGRAPHY_CODES)
    surgery_location = factory.Faker(
        "random_element", elements=SYNTH_VAL.SURGERY_LOCATION
    )
    tumour_length_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    tumour_length = factory.Maybe(
        "tumour_length_not_available", None, factory.Faker("random_int", min=1, max=10)
    )
    tumour_width_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    tumour_width = factory.Maybe(
        "tumour_width_not_available", None, factory.Faker("random_int", min=1, max=10)
    )
    greatest_dimension_tumour_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    greatest_dimension_tumour = factory.Maybe(
        "greatest_dimension_tumour_not_available", None, factory.Faker("random_int", min=1, max=10)
    )
    tumour_focality = factory.Faker(
        "random_element", elements=SYNTH_VAL.TUMOUR_FOCALITY
    )
    residual_tumour_classification = factory.Faker(
        "random_element", elements=SYNTH_VAL.TUMOUR_CLASSIFICATION
    )
    null_margin_types = factory.LazyFunction(lambda: random.random() < 0.15)
    margin_types_involved = factory.Maybe(
        "null_margin_type",
        None,
        factory.Faker(
            "random_elements",
            elements=SYNTH_VAL.MARGIN_TYPES,
            length=random.randint(1, 3),
            unique=True,
        ),
    )
    margin_types_not_involved = factory.Maybe(
        "null_margin_type",
        None,
        factory.Faker(
            "random_elements",
            elements=SYNTH_VAL.MARGIN_TYPES,
            length=random.randint(1, 3),
            unique=True,
        ),
    )
    margin_types_not_assessed = factory.Maybe(
        "null_margin_type",
        None,
        factory.Faker(
            "random_elements",
            elements=SYNTH_VAL.MARGIN_TYPES,
            length=random.randint(1, 3),
            unique=True,
        ),
    )

    @factory.post_generation
    def add_surgery_type(self, create, extracted, **kwargs):
        if random.random() < 0.15:
            pass
        else:
            self.surgery_type = random.choice(list(SYNTH_VAL.SURGERY_TYPE.keys()))
            if self.surgery_type:
                self.surgery_reference_database = random.choice(
                    list(SYNTH_VAL.SURGERY_TYPE[self.surgery_type].keys())
                )
                if self.surgery_reference_database:
                    self.surgery_reference_identifier = SYNTH_VAL.SURGERY_TYPE[
                        self.surgery_type
                    ][self.surgery_reference_database]


class NullSynthSurgeryFactory(SurgeryFactory):
    surgery_site = None
    surgery_location = None
    tumour_length = None
    tumour_width = None
    greatest_dimension_tumour = None
    tumour_focality = None
    residual_tumour_classification = None
    margin_types_involved = None
    margin_types_not_involved = None
    margin_types_not_assessed = None
    lymphovascular_invasion = None
    perineural_invasion = None

    @factory.post_generation
    def add_surgery_type(self, create, extracted, **kwargs):
        """Override method to keep null values."""
        pass


class AllSynthSurgeryFactory(SurgeryFactory):
    surgery_site = factory.Faker("random_element", elements=SYNTH_VAL.ALL_TOPOGRAPHY_CODES)
    surgery_location = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_SURGERY_LOCATION
    )
    tumour_length = factory.Faker("random_int", min=1, max=10)
    tumour_length_not_available = False
    tumour_width = factory.Faker("random_int", min=1, max=10)
    tumour_width_not_available = False
    greatest_dimension_tumour = factory.Faker("random_int", min=1, max=10)
    greatest_dimension_tumour_not_available = False
    tumour_focality = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TUMOUR_FOCALITY
    )
    residual_tumour_classification = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_TUMOUR_CLASSIFICATION
    )
    margin_types_involved = factory.Faker(
            "random_elements",
            elements=SYNTH_VAL.ALL_MARGIN_TYPES,
            length=random.randint(1, 3),
            unique=True,
        )
    margin_types_not_involved = factory.Faker(
            "random_elements",
            elements=SYNTH_VAL.ALL_MARGIN_TYPES,
            length=random.randint(1, 3),
            unique=True,
        )
    margin_types_not_assessed = factory.Faker(
            "random_elements",
            elements=SYNTH_VAL.MARGIN_TYPES,
            length=random.randint(1, 3),
            unique=True,
        )

    @factory.post_generation
    def add_surgery_type(self, create, extracted, **kwargs):
        self.surgery_type = random.choice(list(SYNTH_VAL.SURGERY_TYPE.keys()))
        if self.surgery_type:
            self.surgery_reference_database = random.choice(
                list(SYNTH_VAL.SURGERY_TYPE[self.surgery_type].keys())
            )
            if self.surgery_reference_database:
                self.surgery_reference_identifier = SYNTH_VAL.SURGERY_TYPE[
                    self.surgery_type
                ][self.surgery_reference_database]


class SynthBiomarkerFactory(BiomarkerFactory):
    class Meta:
        exclude = (
            "null_hpv_strain",
            "fill_specimen",
            "fill_pd",
            "fill_treatment",
            "fill_followup",
            "specimen_uuid",
            "pd_uuid",
            "treatment_uuid",
            "followup_uuid",
        )

    er_status = factory.Faker("random_element", elements=SYNTH_VAL.ER_PR_HPV_STATUS)
    pr_status = factory.Faker("random_element", elements=SYNTH_VAL.ER_PR_HPV_STATUS)
    her2_ihc_status = factory.Faker("random_element", elements=SYNTH_VAL.HER2_STATUS)
    her2_ish_status = factory.Faker("random_element", elements=SYNTH_VAL.HER2_STATUS)
    psa_level_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    psa_level = factory.Maybe("psa_level_not_available",
                              None,
                              factory.Faker("pyint", min_value=0, max_value=100))
    ca125_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    ca125 = factory.Maybe("ca125_not_available",
                          None,
                          factory.Faker("pyint", min_value=0, max_value=100))
    cea_not_available = factory.LazyFunction(lambda: random.random() < 0.15)
    cea = factory.Maybe("cea_not_available",
                        None,
                        factory.Faker("pyint", min_value=0, max_value=100))

    null_hpv_strain = factory.LazyFunction(lambda: random.random() < 0.15)
    hpv_strain = factory.Maybe(
        "null_hpv_strain",
        None,
        factory.Faker(
            "random_elements",
            elements=PERM_VAL.HPV_STRAIN,
            length=random.randint(1, 5),
            unique=True,
        ),
    )
    # Alternate between linking biomarker to Donor, specimen, pd, treatment and followup
    fill_specimen = factory.Iterator([False, True, False, False, False])
    fill_pd = factory.Iterator([False, False, True, False, False])
    fill_treatment = factory.Iterator([False, False, False, True, False])
    fill_followup = factory.Iterator([False, False, False, False, True])
    submitter_specimen_id = factory.Maybe(
        "fill_specimen",
        factory.SelfAttribute("specimen_uuid.submitter_specimen_id"),
        None,
    )
    submitter_primary_diagnosis_id = factory.Maybe(
        "fill_pd", factory.SelfAttribute("pd_uuid.submitter_primary_diagnosis_id"), None
    )
    submitter_treatment_id = factory.Maybe(
        "fill_treatment",
        factory.SelfAttribute("treatment_uuid.submitter_treatment_id"),
        None,
    )
    submitter_follow_up_id = factory.Maybe(
        "fill_followup",
        factory.SelfAttribute("followup_uuid.submitter_follow_up_id"),
        None,
    )

    @factory.post_generation
    def set_date(self, create, extracted, **kwargs):
        """Set dates after object generation to ensure consistency with death and birth dates of the donor.
        Date generated will not necessarily be consistent with other linked objects if linked to a diagnosis, treatment,
        followup or specimen.
        """
        donor = self.donor_uuid
        if random.random() < 0.15:
            self.test_date = None
        elif donor.date_of_death and donor.date_of_birth:
            test_day_int = random.randint(
                donor.date_of_birth["day_interval"], donor.date_of_death["day_interval"]
            )
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }
        elif donor.date_of_birth:
            test_day_int = random.randint(donor.date_of_birth["day_interval"], 3650)
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }
        else:
            test_day_int = random.randint(-3650, 3650)
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }

    @factory.post_generation
    def set_percents(self, create, extracted, **kwargs):
        if self.er_status in [
            "Cannot be determined",
            "Negative",
            "Not applicable",
            "Unknown",
        ]:
            self.er_percent_positive = None
        else:
            self.er_percent_positive = round(random.random() * 100, 2)
        if self.pr_status in [
            "Cannot be determined",
            "Negative",
            "Not applicable",
            "Unknown",
        ]:
            self.pr_percent_positive = None
        else:
            self.pr_percent_positive = round(random.random() * 100, 2)


class NullSynthBiomarkerFactory(SynthBiomarkerFactory):
    class Meta:
        exclude = (
            "null_hpv_strain",
            "fill_specimen",
            "fill_pd",
            "fill_treatment",
            "fill_followup",
            "specimen_uuid",
            "pd_uuid",
            "treatment_uuid",
            "followup_uuid",
        )

    psa_level = None
    ca125 = None
    cea = None
    er_status = None
    er_percent_positive = None
    pr_status = None
    pr_percent_positive = None
    her2_ihc_status = None
    her2_ish_status = None
    hpv_ihc_status = None
    hpv_pcr_status = None
    hpv_strain = None

    @factory.post_generation
    def set_date(self, create, extracted, **kwargs):
        """Override method to keep null values."""
        pass

    @factory.post_generation
    def set_percents(self, create, extracted, **kwargs):
        """Override method to keep null values."""
        pass


class AllSynthBiomarkerFactory(SynthBiomarkerFactory):
    class Meta:
        exclude = (
            "null_hpv_strain",
            "fill_specimen",
            "fill_pd",
            "fill_treatment",
            "fill_followup",
            "specimen_uuid",
            "pd_uuid",
            "treatment_uuid",
            "followup_uuid",
        )

    er_status = factory.Faker("random_element", elements=SYNTH_VAL.ALL_ER_PR_HPV_STATUS)
    pr_status = factory.Faker("random_element", elements=SYNTH_VAL.ALL_ER_PR_HPV_STATUS)
    her2_ihc_status = factory.Faker("random_element", elements=SYNTH_VAL.ALL_HER2_STATUS)
    her2_ish_status = factory.Faker("random_element", elements=SYNTH_VAL.ALL_HER2_STATUS)
    psa_level_not_available = False
    psa_level = factory.Faker("pyint", min_value=0, max_value=100)
    ca125_not_available = False
    ca125 = factory.Faker("pyint", min_value=0, max_value=100)
    cea_not_available = False
    cea = factory.Faker("pyint", min_value=0, max_value=100)
    hpv_strain = factory.Faker(
        "random_elements",
        elements=PERM_VAL.HPV_STRAIN,
        length=random.randint(1, 5),
        unique=True,
    )

    @factory.post_generation
    def set_date(self, create, extracted, **kwargs):
        donor = self.donor_uuid
        if donor.date_of_death and donor.date_of_birth:
            test_day_int = random.randint(
                donor.date_of_birth["day_interval"], donor.date_of_death["day_interval"]
            )
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }
        elif donor.date_of_birth:
            test_day_int = random.randint(donor.date_of_birth["day_interval"], 10950)
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }
        else:
            test_day_int = random.randint(7500, 10950)
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }

    @factory.post_generation
    def set_percents(self, create, extracted, **kwargs):
        if self.er_status in [
            "Cannot be determined",
            "Negative",
            "Not applicable",
            "Unknown",
        ]:
            self.er_percent_positive = None
        else:
            self.er_percent_positive = round(random.random() * 100, 2)
        if self.pr_status in [
            "Cannot be determined",
            "Negative",
            "Not applicable",
            "Unknown",
        ]:
            self.pr_percent_positive = None
        else:
            self.pr_percent_positive = round(random.random() * 100, 2)


class SynthComorbidityFactory(ComorbidityFactory):
    prior_malignancy = factory.Faker("random_element", elements=SYNTH_VAL.UBOOLEAN)
    laterality_of_prior_malignancy = None
    comorbidity_type_code = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_CODES
    )
    age_at_comorbidity_diagnosis_not_available = factory.LazyFunction(lambda: random.random() < 0.15)

    @factory.post_generation
    def set_priors(self, create, extracted, **kwargs):
        comorbidity = self
        donor = self.donor_uuid
        cancer_treatments = [
            "Chemotherapy",
            "Hormone therapy",
            "Immunotherapy",
            "Radiation",
        ]
        if donor.date_of_birth:
            age_at_diagnosis = math.floor(donor.date_of_birth["month_interval"] / -12)
        if comorbidity.comorbidity_type_code in SYNTH_VAL.CANCER_CODES:
            comorbidity.laterality_of_prior_malignancy = random.choice(
                PERM_VAL.MALIGNANCY_LATERALITY
            )
            if donor.date_of_birth:
                if not comorbidity.age_at_comorbidity_diagnosis_not_available:
                    comorbidity.age_at_comorbidity_diagnosis = random.randint(
                        10, age_at_diagnosis
                    )
            comorbidity.prior_malignancy = "Yes"
            comorbidity.comorbidity_treatment_status = random.choice(PERM_VAL.UBOOLEAN)
            if comorbidity.comorbidity_treatment_status == "Yes":
                comorbidity.comorbidity_treatment = random.choice(cancer_treatments)
        elif comorbidity.comorbidity_type_code:
            comorbidity.comorbidity_treatment_status = random.choice(PERM_VAL.UBOOLEAN)
            if donor.date_of_birth:
                if not comorbidity.age_at_comorbidity_diagnosis_not_available:
                    comorbidity.age_at_comorbidity_diagnosis = random.randint(
                        10, age_at_diagnosis
                    )
        comorbidity.save()


class NullSynthComorbidityFactory(ComorbidityFactory):
    prior_malignancy = None
    laterality_of_prior_malignancy = None
    age_at_comorbidity_diagnosis = None
    comorbidity_type_code = None
    comorbidity_treatment_status = None
    comorbidity_treatment = None

    @factory.post_generation
    def set_priors(self, create, extracted, **kwargs):
        """Override method to keep null values."""
        pass


class AllSynthComorbidityFactory(SynthComorbidityFactory):
    class Meta:
        exclude = ("is_prior_malignancy", )

    is_prior_malignancy = factory.Faker("pybool")
    prior_malignancy = factory.Maybe("is_prior_malignancy",
                                     "Yes",
                                     "No")
    laterality_of_prior_malignancy = (
        factory.Maybe("is_prior_malignancy",
                      factory.Faker("random_element", elements=SYNTH_VAL.ALL_MALIGNANCY_LATERALITY),
                      None))
    comorbidity_type_code = factory.Maybe("is_prior_malignancy",
                                          "C18.6",
                                          "F00")
    comorbidity_treatment_status = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_UBOOLEAN
    )
    comorbidity_treatment = factory.Maybe("is_prior_malignancy",
                                          "Treated with surgery and chemotherapy (Oxaliplatin).",
                                          "Treated with Donepezil (Aricept).")


class SynthFollowUpFactory(FollowUpFactory):
    class Meta:
        django_get_or_create = ("submitter_follow_up_id",)
        exclude = ("fill_pd", "fill_treatment")

    submitter_follow_up_id = factory.Sequence(lambda n: f"FOLLOW_UP_{str(n).zfill(4)}")
    disease_status_at_followup = factory.Faker(
        "random_element", elements=PERM_VAL.DISEASE_STATUS_FOLLOWUP
    )
    method_of_progression_status = factory.Faker(
        "random_elements",
        elements=PERM_VAL.PROGRESSION_STATUS_METHOD,
        length=random.randint(1, 5),
        unique=True,
    )
    fill_pd = factory.Iterator([True, False, False])
    primary_diagnosis_uuid = factory.Maybe(
        "fill_pd",
        yes_declaration=factory.SubFactory(PrimaryDiagnosisFactory),
        no_declaration=None,
    )
    submitter_primary_diagnosis_id = factory.Maybe(
        "fill_pd",
        yes_declaration=factory.SelfAttribute(
            "primary_diagnosis_uuid.submitter_primary_diagnosis_id"
        ),
        no_declaration=None,
    )
    fill_treatment = factory.Iterator([False, True, False])
    submitter_treatment_id = factory.Maybe(
        "fill_treatment",
        yes_declaration=factory.SelfAttribute("treatment_uuid.submitter_treatment_id"),
        no_declaration=None,
    )
    treatment_uuid = factory.Maybe(
        "fill_treatment",
        yes_declaration=factory.SubFactory(TreatmentFactory),
        no_declaration=None,
    )

    @factory.post_generation
    def set_followup_date(self, create, extracted, **kwargs):
        if random.random() < 0.15:
            pass
        else:
            if self.submitter_treatment_id:
                treatment = self.treatment_uuid
                if treatment.treatment_start_date:
                    day_int = random.randint(
                        treatment.treatment_start_date["day_interval"] + 365,
                        treatment.treatment_start_date["day_interval"] + 1000,
                    )
                    self.date_of_followup = {
                        "day_interval": day_int,
                        "month_interval": days_to_months(day_int),
                    }
            else:
                if self.donor_uuid.date_of_death:
                    day_int = random.randint(
                        400, self.donor_uuid.date_of_death["day_interval"]
                    )
                elif self.donor_uuid.date_alive_after_lost_to_followup:
                    day_int = random.randint(
                        400,
                        self.donor_uuid.date_alive_after_lost_to_followup[
                            "day_interval"
                        ],
                    )
                else:
                    day_int = random.randint(400, 2000)
                self.date_of_followup = {
                    "day_interval": day_int,
                    "month_interval": days_to_months(day_int),
                }

    @factory.post_generation
    def set_relapse_type_date(self, create, extracted, **kwargs):
        if random.random() < 0.15:
            pass
        elif self.disease_status_at_followup in [
            "Distant progression",
            "Loco-regional progression",
            "Progression not otherwise specified",
        ]:
            # donor = self.donor_uuid
            self.relapse_type = random.choice(PERM_VAL.RELAPSE_TYPE)
            if self.date_of_followup:
                relapse_day_int = random.randint(
                    0, self.date_of_followup["day_interval"]
                )
                relapse_month_int = days_to_months(relapse_day_int)
                self.date_of_relapse = {
                    "day_interval": relapse_day_int,
                    "month_interval": relapse_month_int,
                }
            else:
                relapse_day_int = random.randint(0, 500)
                relapse_month_int = days_to_months(relapse_day_int)
                self.date_of_relapse = {
                    "day_interval": relapse_day_int,
                    "month_interval": relapse_month_int,
                }


class NullSynthFollowUpFactory(SynthFollowUpFactory):
    submitter_follow_up_id = factory.Sequence(
        lambda n: f"FOLLOW_UP_NULL_{str(n).zfill(4)}"
    )
    date_of_followup = None
    disease_status_at_followup = None
    relapse_type = None
    date_of_relapse = None
    method_of_progression_status = None
    anatomic_site_progression_or_recurrence = None

    @factory.post_generation
    def set_relapse_type_date(self, create, extracted, **kwargs):
        """Override method to keep null values."""
        pass


class AllSynthFollowUpFactory(SynthFollowUpFactory):
    submitter_follow_up_id = factory.Sequence(
        lambda n: f"FOLLOW_UP_ALL_{str(n).zfill(4)}"
    )
    disease_status_at_followup = factory.Faker(
        "random_element", elements=SYNTH_VAL.ALL_DISEASE_STATUS_FOLLOWUP
    )
    method_of_progression_status = factory.Faker(
        "random_elements",
        elements=SYNTH_VAL.ALL_PROGRESSION_STATUS_METHOD,
        length=random.randint(1, 5),
        unique=True,
    )

    @factory.post_generation
    def set_followup_date(self, create, extracted, **kwargs):
        if self.submitter_treatment_id:
            treatment = self.treatment_uuid
            if treatment.treatment_start_date:
                day_int = random.randint(
                    treatment.treatment_start_date["day_interval"] + 365,
                    treatment.treatment_start_date["day_interval"] + 1000,
                )
                self.date_of_followup = {
                    "day_interval": day_int,
                    "month_interval": days_to_months(day_int),
                }
        else:
            if self.donor_uuid.date_of_death:
                day_int = random.randint(
                    400, self.donor_uuid.date_of_death["day_interval"]
                )
            elif self.donor_uuid.date_alive_after_lost_to_followup:
                day_int = random.randint(
                    400,
                    self.donor_uuid.date_alive_after_lost_to_followup[
                        "day_interval"
                    ],
                )
            else:
                day_int = random.randint(400, 2000)
            self.date_of_followup = {
                "day_interval": day_int,
                "month_interval": days_to_months(day_int),
            }

    @factory.post_generation
    def set_relapse_type_date(self, create, extracted, **kwargs):
        """Override method to remove 15% nulls."""
        if self.disease_status_at_followup in [
            "Distant progression",
            "Loco-regional progression",
            "Progression not otherwise specified",
            "Relapse or recurrence"
        ]:
            donor = self.donor_uuid
            self.relapse_type = random.choice(PERM_VAL.RELAPSE_TYPE)
            self.anatomic_site_progression_or_recurrence = random.choices(SYNTH_VAL.TOPOGRAPHY_CODES,
                                                                          k=random.randint(1, 3))
            if donor.date_of_death:
                relapse_day_int = random.randint(0, donor.date_of_death["day_interval"])
                relapse_month_int = days_to_months(relapse_day_int)
                self.date_of_relapse = {
                    "day_interval": relapse_day_int,
                    "month_interval": relapse_month_int,
                }
            else:
                relapse_day_int = random.randint(0, 3650)
                relapse_month_int = days_to_months(relapse_day_int)
                self.date_of_relapse = {
                    "day_interval": relapse_day_int,
                    "month_interval": relapse_month_int,
                }
            if self.method_of_progression_status is None:
                self.method_of_progression_status = random.choices(PERM_VAL.PROGRESSION_STATUS_METHOD,
                                                                   k=random.randint(1, 5))


class SynthExposureFactory(ExposureFactory):
    class Meta:
        exclude = ("fill_status",)

    fill_status = factory.LazyFunction(lambda: random.random() > 0.15)
    tobacco_smoking_status = factory.Maybe(
        "fill_status",
        factory.Faker("random_element", elements=PERM_VAL.SMOKING_STATUS),
        None,
    )
    tobacco_type = None
    pack_years_smoked = None

    @factory.post_generation
    def set_smoking_information(self, create, extracted, **kwargs):
        if self.tobacco_smoking_status:
            if self.tobacco_smoking_status not in [
                "Not applicable",
                "Not available",
                "Lifelong non-smoker (<100 cigarettes smoked in lifetime)",
            ]:
                self.tobacco_type = random.sample(
                    SYNTH_VAL.SMOKER_TOBACCO_TYPE, k=random.randint(1, 3)
                )
                if len(self.tobacco_type) > 1 and "Unknown" in self.tobacco_type:
                    self.tobacco_type.remove("Unknown")
                if (
                    self.tobacco_smoking_status
                    == "Current reformed smoker, duration not specified"
                ):
                    self.pack_years_smoked = None
                else:
                    self.pack_years_smoked_not_available = random.choice([True, False])
                    if not self.pack_years_smoked_not_available:
                        self.pack_years_smoked = random.randint(5, 70)


class AllSynthExposureFactory(SynthExposureFactory):
    tobacco_smoking_status = factory.Faker("random_element", elements=SYNTH_VAL.ALL_SMOKING_STATUS)

    @factory.post_generation
    def set_smoking_information(self, create, extracted, **kwargs):
        if self.tobacco_smoking_status:
            if self.tobacco_smoking_status not in [
                "Not applicable",
                "Not available",
                "Lifelong non-smoker (<100 cigarettes smoked in lifetime)",
            ]:
                self.tobacco_type = random.sample(
                    SYNTH_VAL.SMOKER_TOBACCO_TYPE, k=random.randint(1, 3)
                )
                if len(self.tobacco_type) > 1 and "Unknown" in self.tobacco_type:
                    self.tobacco_type.remove("Unknown")
                    self.pack_years_smoked_not_available = False
                    self.pack_years_smoked = random.randint(5, 70)


class NullSynthExposureFactory(ExposureFactory):
    tobacco_smoking_status = None
    tobacco_type = None
    pack_years_smoked = None
