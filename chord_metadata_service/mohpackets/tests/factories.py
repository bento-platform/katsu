import random
import uuid
import math

import factory

import chord_metadata_service.mohpackets.permissible_values as PERM_VAL
from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    PrimaryDiagnosis,
    Program,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    SystemicTherapy,
    Treatment,
)

"""
    This file contains factory classes for generating test data.

    These factories make it easy to create mock instances of various models
    with customizable attributes, which simplifies the process of setting up
    test data for unit and integration tests.

    Example Usage:
        # This will create a Program instance with the specified program_id.
        program = ProgramFactory(program_id='CUSTOM_PROGRAM')

        # This will create a Donor instance and a Program instance
        donor = DonorFactory()

    Note:
        These factories use the Factory Boy library (https://factoryboy.readthedocs.io/)
        to generate test data.
        Some business logic is not strictly enforced. For example,
        date_of_birth could have mismatched month_interval and day_interval.

    Author: Son Chau & Marion Shadbolt
"""


def days_to_months(day_interval):
    """Convert a day interval to a month interval."""
    return int(math.floor(day_interval * 0.032855))


class ProgramFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Program

    # default values
    program_id = factory.Sequence(lambda n: "PROGRAM_%d" % n)


class DonorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Donor
        exclude = ("is_deceased_bool",)

    # default values
    submitter_donor_id = factory.Sequence(lambda n: "DONOR_%d" % n)
    gender = factory.Faker("random_element", elements=PERM_VAL.GENDER)
    sex_at_birth = factory.Faker("random_element", elements=PERM_VAL.SEX_AT_BIRTH)
    is_deceased_bool = factory.Faker("pybool")
    is_deceased = factory.Maybe("is_deceased_bool",
                                "Yes",
                                factory.Faker("random_element", elements=["No", "Not available"]))
    lost_to_followup_reason = None
    lost_to_followup_after_clinical_event_identifier = None
    date_alive_after_lost_to_followup = None
    date_resolution = "day"

    cause_of_death = factory.Maybe(
        "is_deceased_bool",
        yes_declaration=factory.Faker(
            "random_element", elements=PERM_VAL.CAUSE_OF_DEATH
        ),
        no_declaration=None,
    )
    date_of_birth = factory.LazyFunction(
        lambda: {"day_interval": random.randint(-21900, -18220)}
    )
    date_of_death = factory.Maybe(
        "is_deceased_bool",
        yes_declaration=factory.LazyFunction(
            lambda: {"day_interval": random.randint(3650, 16425)}
        ),
        no_declaration=None,
    )

    # set foreign key
    program_id = factory.SubFactory(ProgramFactory)

    @factory.post_generation
    def consistent_dates(self, create, extracted, **kwargs):
        "Calculate a month interval after the object is created so that the day and month intervals are consistent."
        if self.date_of_birth:
            try:
                self.date_of_birth["month_interval"] = days_to_months(
                    self.date_of_birth["day_interval"]
                )
            except KeyError:
                self.date_of_birth = {"day_interval": random.randint(-21900, -18220)}
                self.date_of_birth["month_interval"] = days_to_months(
                    self.date_of_birth["day_interval"]
                )
        if self.date_of_death:
            self.date_of_death["month_interval"] = days_to_months(
                self.date_of_death["day_interval"]
            )


class PrimaryDiagnosisFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = PrimaryDiagnosis

    # Default values
    submitter_primary_diagnosis_id = factory.Sequence(lambda n: "DIAG_%d" % n)
    date_of_diagnosis = {"month_interval": 0, "day_interval": 0}
    cancer_type_code = factory.Faker("uuid4")
    basis_of_diagnosis = factory.Faker(
        "random_element", elements=PERM_VAL.BASIS_OF_DIAGNOSIS
    )
    laterality = factory.Faker(
        "random_element", elements=PERM_VAL.PRIMARY_DIAGNOSIS_LATERALITY
    )
    clinical_tumour_staging_system = factory.Faker(
        "random_element", elements=PERM_VAL.TUMOUR_STAGING_SYSTEM
    )
    clinical_t_category = factory.Faker("random_element", elements=PERM_VAL.T_CATEGORY)
    clinical_n_category = factory.Faker("random_element", elements=PERM_VAL.N_CATEGORY)
    clinical_m_category = factory.Faker("random_element", elements=PERM_VAL.M_CATEGORY)
    clinical_stage_group = factory.Faker(
        "random_element", elements=PERM_VAL.STAGE_GROUP
    )
    primary_site = factory.Faker(
        "random_element",
        elements=PERM_VAL.PRIMARY_SITE,
    )
    pathological_tumour_staging_system = factory.Faker(
        "random_element", elements=PERM_VAL.TUMOUR_STAGING_SYSTEM
    )
    pathological_t_category = factory.Faker(
        "random_element", elements=PERM_VAL.T_CATEGORY
    )
    pathological_n_category = factory.Faker(
        "random_element", elements=PERM_VAL.N_CATEGORY
    )
    pathological_m_category = factory.Faker(
        "random_element", elements=PERM_VAL.M_CATEGORY
    )
    pathological_stage_group = factory.Faker(
        "random_element", elements=PERM_VAL.STAGE_GROUP
    )

    # Set the foreign keys
    program_id = factory.SelfAttribute("donor_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("donor_uuid.submitter_donor_id")
    donor_uuid = factory.SubFactory(DonorFactory)

    @factory.post_generation
    def set_clinical_event_identifier(self, create, extracted, **kwargs):
        donor = self.donor_uuid
        if donor.is_deceased == "No":
            donor.lost_to_followup_after_clinical_event_identifier = (
                self.submitter_primary_diagnosis_id
            )
            donor.lost_to_followup_reason = random.choice(
                PERM_VAL.LOST_TO_FOLLOWUP_REASON
            )
            donor.date_alive_after_lost_to_followup = {
                "day_interval": random.randint(25551, 32850),
            }
            donor.date_alive_after_lost_to_followup["month_interval"] = days_to_months(
                donor.date_alive_after_lost_to_followup["day_interval"]
            )
            donor.save()


class SpecimenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Specimen

    # default values
    submitter_specimen_id = factory.Sequence(lambda n: "SPECIMEN_%d" % n)

    specimen_collection_date = factory.LazyFunction(
        lambda: {"day_interval": random.randint(0, 90)}
    )
    specimen_storage = factory.Faker("random_element", elements=PERM_VAL.STORAGE)
    specimen_processing = factory.Faker(
        "random_element", elements=PERM_VAL.SPECIMEN_PROCESSING
    )
    tumour_histological_type = None
    specimen_anatomic_location = factory.Faker(
        "random_element",
        elements=[
            "C00.6",
            "C00.8",
            "C01.9",
            "C02.0",
            "C02.1",
            "C02.2",
            "C02.3",
            "C02.4",
            "C02.8",
            "C02.9",
            "C03.0",
            "C03.1",
        ],
    )
    specimen_laterality = factory.Faker(
        "random_element", elements=PERM_VAL.SPECIMEN_LATERALITY
    )
    reference_pathology_confirmed_diagnosis = factory.Faker(
        "random_element", elements=PERM_VAL.CONFIRMED_DIAGNOSIS_TUMOUR
    )
    reference_pathology_confirmed_tumour_presence = factory.Faker(
        "random_element", elements=PERM_VAL.CONFIRMED_DIAGNOSIS_TUMOUR
    )
    tumour_grading_system = factory.Faker(
        "random_element", elements=PERM_VAL.TUMOUR_GRADING_SYSTEM
    )
    tumour_grade = factory.Faker("random_element", elements=PERM_VAL.TUMOUR_GRADE)
    percent_tumour_cells_range = factory.Faker(
        "random_element", elements=PERM_VAL.PERCENT_CELLS_RANGE
    )
    percent_tumour_cells_measurement_method = factory.Faker(
        "random_element", elements=PERM_VAL.CELLS_MEASURE_METHOD
    )

    # set foreign keys
    program_id = factory.SelfAttribute("primary_diagnosis_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute(
        "primary_diagnosis_uuid.submitter_donor_id"
    )
    donor_uuid = factory.SelfAttribute("primary_diagnosis_uuid.donor_uuid")
    submitter_primary_diagnosis_id = factory.SelfAttribute(
        "primary_diagnosis_uuid.submitter_primary_diagnosis_id"
    )
    primary_diagnosis_uuid = factory.SubFactory(PrimaryDiagnosisFactory)
    submitter_treatment_id = None

    @factory.post_generation
    def set_months(self, create, extracted, **kwargs):
        if self.specimen_collection_date:
            self.specimen_collection_date["month_interval"] = days_to_months(
                self.specimen_collection_date["day_interval"]
            )

    @factory.post_generation
    def generate_histology_code(self, create, extracted, **kwargs):
        one = str(random.randint(8, 9))
        two = str(random.randint(0, 999)).rjust(3, "0")
        code = one + two + "/3"
        self.tumour_histological_type = code


class SampleRegistrationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SampleRegistration

    # default values
    submitter_sample_id = factory.Sequence(lambda n: "SAMPLE_%d" % n)
    specimen_tissue_source = factory.Faker(
        "random_element", elements=PERM_VAL.SPECIMEN_TISSUE_SOURCE
    )
    tumour_normal_designation = factory.Iterator(PERM_VAL.TUMOUR_DESIGNATION)
    specimen_type = factory.Faker("random_element", elements=PERM_VAL.SPECIMEN_TYPE)
    sample_type = factory.Faker("random_element", elements=PERM_VAL.SAMPLE_TYPE)

    # set foreign keys
    program_id = factory.SelfAttribute("specimen_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("specimen_uuid.submitter_donor_id")
    donor_uuid = factory.SelfAttribute("specimen_uuid.donor_uuid")
    submitter_specimen_id = factory.SelfAttribute("specimen_uuid.submitter_specimen_id")
    specimen_uuid = factory.SubFactory(SpecimenFactory)


class TreatmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Treatment

    # default values
    submitter_treatment_id = factory.Sequence(lambda n: "TREATMENT_%d" % n)
    treatment_type = factory.Faker(
        "random_elements",
        elements=PERM_VAL.TREATMENT_TYPE,
        length=random.randint(1, 5),
        unique=True,
    )
    is_primary_treatment = factory.Faker("random_element", elements=["Yes", "No"])
    treatment_start_date = factory.LazyFunction(
        lambda: {"day_interval": random.randint(5, 180)}
    )
    treatment_end_date = None
    treatment_intent = factory.Faker(
        "random_element", elements=PERM_VAL.TREATMENT_INTENT
    )
    response_to_treatment_criteria_method = factory.Faker(
        "random_element", elements=PERM_VAL.TREATMENT_RESPONSE_METHOD
    )
    response_to_treatment = factory.Faker(
        "random_element", elements=PERM_VAL.TREATMENT_RESPONSE
    )
    status_of_treatment = factory.Faker(
        "random_element", elements=PERM_VAL.TREATMENT_STATUS
    )

    # set foreign keys
    program_id = factory.SelfAttribute("primary_diagnosis_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute(
        "primary_diagnosis_uuid.submitter_donor_id"
    )
    donor_uuid = factory.SelfAttribute("primary_diagnosis_uuid.donor_uuid")
    submitter_primary_diagnosis_id = factory.SelfAttribute(
        "primary_diagnosis_uuid.submitter_primary_diagnosis_id"
    )
    primary_diagnosis_uuid = factory.SubFactory(PrimaryDiagnosisFactory)

    @factory.post_generation
    def set_treatment_dates(self, create, extracted, **kwargs):
        if not self.treatment_start_date:
            self.treatment_start_date["day_interval"] = random.randint(5, 180)
        self.treatment_start_date["month_interval"] = days_to_months(
            self.treatment_start_date["day_interval"]
        )
        min_start = self.treatment_start_date["day_interval"] + 3
        min_end = min_start + 365
        day_int = random.randint(min_start, min_end)
        self.treatment_end_date = {
            "day_interval": day_int,
            "month_interval": days_to_months(day_int),
        }

    @factory.post_generation
    def correct_treatment_type(self, create, extracted, **kwargs):
        if self.treatment_type and "No treatment" in self.treatment_type:
            self.treatment_type = ["No treatment"]
        self.treatment_type = [x for x in self.treatment_type if x is not None]


class SystemicTherapyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SystemicTherapy

    # default values
    uuid = factory.LazyFunction(uuid.uuid4)
    systemic_therapy_type = factory.Faker(
        "random_element", elements=PERM_VAL.SYSTEMIC_THERAPY_TYPE
    )
    days_per_cycle = factory.Faker("random_int", min=1, max=30)
    number_of_cycles = factory.Faker("random_int", min=1, max=10)
    start_date = None
    end_date = None
    drug_reference_database = factory.Faker(
        "random_element", elements=PERM_VAL.DRUG_REFERENCE_DB
    )
    drug_name = factory.Faker("pystr", min_chars=10, max_chars=30)
    drug_reference_identifier = factory.Faker("pystr", min_chars=10, max_chars=30)
    drug_dose_units = factory.Faker("random_element", elements=PERM_VAL.DOSAGE_UNITS)
    prescribed_cumulative_drug_dose = factory.Faker(
        "pyfloat",
        left_digits=2,
        right_digits=1,
        positive=True,
        min_value=20,
        max_value=50,
    )
    actual_cumulative_drug_dose = factory.Faker(
        "pyfloat",
        left_digits=2,
        right_digits=1,
        positive=True,
        min_value=51,
        max_value=100,
    )

    # set foregin keys
    program_id = factory.SelfAttribute("treatment_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("treatment_uuid.submitter_donor_id")
    donor_uuid = factory.SelfAttribute("treatment_uuid.donor_uuid")
    submitter_treatment_id = factory.SelfAttribute(
        "treatment_uuid.submitter_treatment_id"
    )
    treatment_uuid = factory.SubFactory(TreatmentFactory)

    @factory.post_generation
    def add_dates(self, create, extracted, **kwargs):
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
            self.start_date["month_interval"] = days_to_months(
                self.start_date["day_interval"]
            )
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


class RadiationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Radiation

    # default values
    uuid = factory.LazyFunction(uuid.uuid4)
    radiation_therapy_modality = factory.Faker(
        "random_element", elements=PERM_VAL.RADIATION_THERAPY_MODALITY
    )
    radiation_therapy_type = factory.Faker(
        "random_element", elements=PERM_VAL.THERAPY_TYPE
    )
    radiation_therapy_fractions = factory.Faker("random_int", min=1, max=30)
    radiation_therapy_dosage = factory.Faker("random_int", min=1, max=100)
    anatomical_site_irradiated = factory.Faker(
        "random_element", elements=PERM_VAL.RADIATION_ANATOMICAL_SITE
    )
    radiation_boost = factory.Faker("random_element", elements=PERM_VAL.UBOOLEAN)
    reference_radiation_treatment_id = factory.Faker("word")

    # set foreign keys
    program_id = factory.SelfAttribute("treatment_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("treatment_uuid.submitter_donor_id")
    donor_uuid = factory.SelfAttribute("treatment_uuid.donor_uuid")
    submitter_treatment_id = factory.SelfAttribute(
        "treatment_uuid.submitter_treatment_id"
    )
    treatment_uuid = factory.SubFactory(TreatmentFactory)

    @factory.post_generation
    def add_radiation_treatment_type(self, create, extracted, **kwargs):
        treatment = self.treatment_uuid
        if not treatment.treatment_type:
            treatment.treatment_type = []
        if treatment.treatment_type:
            if "Radiation therapy" not in treatment.treatment_type:
                treatment.treatment_type.append("Radiation therapy")
            if "No treatment" in treatment.treatment_type:
                treatment.treatment_type.remove("No treatment")
        treatment.treatment_type = [
            x for x in treatment.treatment_type if x is not None
        ]


class SurgeryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Surgery

    # default values
    uuid = factory.LazyFunction(uuid.uuid4)
    surgery_type = factory.Faker("pystr", min_chars=10, max_chars=64)
    surgery_site = factory.Faker(
        "random_element",
        elements=[
            "C00.0",
            "C00.1",
            "C00.2",
            "C00.3",
            "C00.4",
            "C00.5",
            "C00.6",
            "C02.3",
            "C02.4",
            "C02.8",
            "C02.9",
            "C03.0",
            "C03.1",
        ],
    )
    surgery_location = factory.Faker(
        "random_element", elements=PERM_VAL.SURGERY_LOCATION
    )
    tumour_length = factory.Faker("random_int", min=1, max=10)
    tumour_width = factory.Faker("random_int", min=1, max=10)
    greatest_dimension_tumour = factory.Faker("random_int", min=1, max=10)
    tumour_focality = factory.Faker("random_element", elements=PERM_VAL.TUMOUR_FOCALITY)
    residual_tumour_classification = factory.Faker(
        "random_element", elements=PERM_VAL.TUMOUR_CLASSIFICATION
    )
    margin_types_involved = factory.Faker(
        "random_elements",
        elements=PERM_VAL.MARGIN_TYPES,
        length=random.randint(1, 5),
        unique=True,
    )
    margin_types_not_involved = factory.Faker(
        "random_elements",
        elements=PERM_VAL.MARGIN_TYPES,
        length=random.randint(1, 5),
        unique=True,
    )
    margin_types_not_assessed = factory.Faker(
        "random_elements",
        elements=PERM_VAL.MARGIN_TYPES,
        length=random.randint(1, 5),
        unique=True,
    )
    lymphovascular_invasion = factory.Faker(
        "random_element", elements=PERM_VAL.LYMPHOVACULAR_INVASION
    )
    perineural_invasion = factory.Faker(
        "random_element", elements=PERM_VAL.PERINEURAL_INVASION
    )
    surgery_reference_database = factory.Faker(
        "random_element", elements=PERM_VAL.SURGERY_REFERENCE_DATABASE
    )
    surgery_reference_identifier = None

    # set foreign keys
    program_id = factory.SelfAttribute("treatment_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("treatment_uuid.submitter_donor_id")
    donor_uuid = factory.SelfAttribute("treatment_uuid.donor_uuid")
    submitter_treatment_id = factory.SelfAttribute(
        "treatment_uuid.submitter_treatment_id"
    )
    treatment_uuid = factory.SubFactory(TreatmentFactory)

    @factory.post_generation
    def clean_margin_nulls(self, create, extracted, **kwargs):
        if self.margin_types_involved:
            self.margin_types_involved = [
                x for x in self.margin_types_involved if x is not None
            ]
        if self.margin_types_not_involved:
            self.margin_types_not_involved = [
                x for x in self.margin_types_not_involved if x is not None
            ]
        if self.margin_types_not_assessed:
            self.margin_types_not_assessed = [
                x for x in self.margin_types_not_assessed if x is not None
            ]

    @factory.post_generation
    def add_surgery_treatment_type(self, create, extracted, **kwargs):
        treatment = self.treatment_uuid
        if not treatment.treatment_type:
            treatment.treatment_type = []
        if "Surgery" not in treatment.treatment_type:
            treatment.treatment_type.append("Surgery")
        if "No treatment" in treatment.treatment_type:
            treatment.treatment_type.remove("No treatment")
        treatment.treatment_type = [
            x for x in treatment.treatment_type if x is not None
        ]


class FollowUpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FollowUp

    # default values
    submitter_follow_up_id = factory.Sequence(lambda n: "FOLLOW_UP_%d" % n)
    date_of_followup = None
    disease_status_at_followup = factory.Faker(
        "random_element", elements=PERM_VAL.DISEASE_STATUS_FOLLOWUP
    )
    relapse_type = factory.Faker("random_element", elements=PERM_VAL.RELAPSE_TYPE)
    date_of_relapse = None
    method_of_progression_status = factory.Faker(
        "random_elements",
        elements=PERM_VAL.PROGRESSION_STATUS_METHOD,
        length=random.randint(1, 5),
        unique=True,
    )
    anatomic_site_progression_or_recurrence = None

    # set foreign keys
    program_id = factory.SelfAttribute("treatment_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("treatment_uuid.submitter_donor_id")
    donor_uuid = factory.SelfAttribute("treatment_uuid.donor_uuid")
    submitter_primary_diagnosis_id = factory.SelfAttribute(
        "treatment_uuid.submitter_primary_diagnosis_id"
    )
    primary_diagnosis_uuid = factory.SelfAttribute(
        "treatment_uuid.primary_diagnosis_uuid"
    )
    submitter_treatment_id = factory.SelfAttribute(
        "treatment_uuid.submitter_treatment_id"
    )
    treatment_uuid = factory.SubFactory(TreatmentFactory)

    @factory.post_generation
    def clean_nulls_method(self, create, extracted, **kwargs):
        if self.method_of_progression_status:
            self.method_of_progression_status = [
                x for x in self.method_of_progression_status if x is not None
            ]


class BiomarkerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Biomarker

    # default values
    uuid = factory.LazyFunction(uuid.uuid4)
    test_date = factory.LazyFunction(
        lambda: {
            "month_interval": random.randint(0, 1000),
            "day_interval": random.randint(0, 3000),
        }
    )
    psa_level = factory.Faker("pyint", min_value=0, max_value=100)
    ca125 = factory.Faker("pyint", min_value=0, max_value=100)
    cea = factory.Faker("pyint", min_value=0, max_value=100)
    er_status = factory.Faker("random_element", elements=PERM_VAL.ER_PR_HPV_STATUS)
    er_percent_positive = factory.Faker(
        "pyfloat", positive=True, left_digits=2, right_digits=1
    )
    pr_status = factory.Faker("random_element", elements=PERM_VAL.ER_PR_HPV_STATUS)
    pr_percent_positive = factory.Faker(
        "pyfloat", positive=True, left_digits=2, right_digits=1
    )
    her2_ihc_status = factory.Faker("random_element", elements=PERM_VAL.HER2_STATUS)
    her2_ish_status = factory.Faker("random_element", elements=PERM_VAL.HER2_STATUS)
    hpv_ihc_status = factory.Faker("random_element", elements=PERM_VAL.ER_PR_HPV_STATUS)
    hpv_pcr_status = factory.Faker("random_element", elements=PERM_VAL.ER_PR_HPV_STATUS)
    hpv_strain = factory.Faker(
        "random_elements",
        elements=PERM_VAL.HPV_STRAIN,
        length=random.randint(1, 5),
        unique=True,
    )
    submitter_specimen_id = None
    submitter_primary_diagnosis_id = None
    submitter_treatment_id = None
    submitter_follow_up_id = None

    # set foreign keys
    program_id = factory.SelfAttribute("donor_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("donor_uuid.submitter_donor_id")
    donor_uuid = factory.SubFactory(DonorFactory)

    @factory.post_generation
    def set_date(self, create, extracted, **kwargs):
        """Set dates after object generation to ensure consistency with death and birth dates of the donor.
        Date generated will not necessarily be consistent with other linked objects if linked to a diagnosis, treatment,
        followup or specimen.
        """
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
            test_day_int = random.randint(donor.date_of_birth["day_interval"], 32850)
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }
        else:
            test_day_int = random.randint(7500, 32850)
            test_month_int = days_to_months(test_day_int)
            self.test_date = {
                "day_interval": test_day_int,
                "month_interval": test_month_int,
            }

    # @factory.post_generation
    # def set_linkage(self, create, extracted, **kwargs):
    #     linked_event = random.choice(['specimen', 'primary_diagnosis', 'treatment', None])
    #     biomarker = self
    #     # if biomarker.submitter_treatment_id:
    #     #     treatment = biomarker.submitter_treatment_id
    #     #     biomarker.submitter_treatment_id = treatment.submitter_treatment_id
    #     # if biomarker.submitter_primary_diagnosis_id:
    #     #     pd = biomarker.submitter_primary_diagnosis_id
    #     #     biomarker.submitter_primary_diagnosis_id = pd.submitter_treatment_id
    #     if linked_event == "specimen":
    #         specimen = self.specimen_uuid
    #         biomarker.submitter_specimen_id = specimen.submitter_specimen_id
    #     biomarker.save()


class ComorbidityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comorbidity

    # default values
    uuid = factory.LazyFunction(uuid.uuid4)
    prior_malignancy = factory.Faker("random_element", elements=PERM_VAL.UBOOLEAN)
    laterality_of_prior_malignancy = factory.Faker(
        "random_element", elements=PERM_VAL.MALIGNANCY_LATERALITY
    )
    age_at_comorbidity_diagnosis = factory.Faker("pyint", min_value=20, max_value=80)
    comorbidity_type_code = "Not available"
    comorbidity_treatment_status = factory.Faker(
        "random_element", elements=PERM_VAL.UBOOLEAN
    )
    comorbidity_treatment = factory.Faker("word")

    # set foreign keys
    program_id = factory.SelfAttribute("donor_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("donor_uuid.submitter_donor_id")
    donor_uuid = factory.SubFactory(DonorFactory)


class ExposureFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Exposure

    # default values
    uuid = factory.LazyFunction(uuid.uuid4)
    tobacco_smoking_status = factory.Faker(
        "random_element", elements=PERM_VAL.SMOKING_STATUS
    )
    tobacco_type = factory.Faker("random_elements", elements=PERM_VAL.TOBACCO_TYPE)
    pack_years_smoked = factory.Faker(
        "pyfloat",
        left_digits=2,
        right_digits=1,
        positive=True,
        min_value=1,
        max_value=100,
    )

    # set foreign keys
    program_id = factory.SelfAttribute("donor_uuid.program_id")
    submitter_donor_id = factory.SelfAttribute("donor_uuid.submitter_donor_id")
    donor_uuid = factory.SubFactory(DonorFactory)
