from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

import chord_metadata_service.mohpackets.permissible_values as val
from chord_metadata_service.mohpackets.permissible_values import REGEX_PATTERNS as regex

from .models import (
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

"""
    This module contains the SERIALIZERS for the models in the mohpackets app.
    It converting Python objects or Django model instances into a JSON string,
    and back again for API transmissions.

    We use the ModelSerializer class, which provides a way to create a Serializer
    directly from a Django model. All that needs to be done to create a ModelSerializer
    is to specify a model on its Meta attribute. For reference, see:
    https://www.django-rest-framework.org/api-guide/serializers/#modelserializer

"""


class CustomChoiceField(serializers.ChoiceField):
    """Custom ChoiceField that prints permissible choices when an exception is raised."""

    default_error_messages = {
        "invalid_choice": _(
            '"{input}" is not a valid choice. The valid choices are: [{choices}]'
        )
    }

    def to_internal_value(self, data):
        if data == "" and self.allow_blank:
            return ""

        try:
            return self.choice_strings_to_values[str(data)]
        except KeyError:
            choices = [c for c in self.choices]
            self.fail("invalid_choice", input=data, choices=choices)


##########################################
#                                        #
#           MODEL SERIALIZERS            #
#                                        #
##########################################


class ProgramSerializer(serializers.ModelSerializer):
    program_id = serializers.RegexField(
        regex=regex["ID"],
        max_length=64,
        validators=[UniqueValidator(queryset=Program.objects.all())],
    )

    class Meta:
        model = Program
        fields = "__all__"


class DonorSerializer(serializers.ModelSerializer):
    submitter_donor_id = serializers.RegexField(
        regex=regex["ID"],
        max_length=64,
        validators=[UniqueValidator(queryset=Donor.objects.all())],
    )
    cause_of_death = CustomChoiceField(
        choices=val.CAUSE_OF_DEATH, allow_blank=True, allow_null=True, required=False
    )
    date_of_birth = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    date_of_death = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    primary_site = serializers.ListField(
        required=False,
        allow_null=True,
        allow_empty=True,
        child=CustomChoiceField(
            choices=val.PRIMARY_SITE, allow_blank=True, allow_null=True, required=False
        ),
    )
    gender = CustomChoiceField(
        choices=val.GENDER, allow_blank=True, allow_null=True, required=False
    )
    sex_at_birth = CustomChoiceField(
        choices=val.SEX_AT_BIRTH, allow_blank=True, allow_null=True, required=False
    )
    lost_to_followup_reason = CustomChoiceField(
        choices=val.LOST_TO_FOLLOWUP_REASON,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    date_alive_after_lost_to_followup = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Donor
        fields = "__all__"


class SpecimenSerializer(serializers.ModelSerializer):
    submitter_specimen_id = serializers.RegexField(
        regex=regex["ID"],
        max_length=64,
        validators=[UniqueValidator(queryset=Specimen.objects.all())],
    )
    pathological_tumour_staging_system = CustomChoiceField(
        choices=val.TUMOUR_STAGING_SYSTEM,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    pathological_t_category = CustomChoiceField(
        choices=val.T_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    pathological_n_category = CustomChoiceField(
        choices=val.N_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    pathological_m_category = CustomChoiceField(
        choices=val.M_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    pathological_stage_group = CustomChoiceField(
        choices=val.STAGE_GROUP, allow_blank=True, allow_null=True, required=False
    )
    specimen_collection_date = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    specimen_storage = CustomChoiceField(
        choices=val.STORAGE, allow_blank=True, allow_null=True, required=False
    )
    tumour_histological_type = serializers.RegexField(
        max_length=128,
        regex=regex["MORPHOLOGY"],
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    specimen_anatomic_location = serializers.RegexField(
        max_length=32,
        regex=regex["TOPOGRAPHY"],
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    reference_pathology_confirmed_diagnosis = CustomChoiceField(
        choices=val.CONFIRMED_DIAGNOSIS_TUMOUR,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    reference_pathology_confirmed_tumour_presence = CustomChoiceField(
        choices=val.CONFIRMED_DIAGNOSIS_TUMOUR,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    tumour_grading_system = CustomChoiceField(
        choices=val.TUMOUR_GRADING_SYSTEM,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    tumour_grade = CustomChoiceField(
        choices=val.TUMOUR_GRADE, allow_blank=True, allow_null=True, required=False
    )
    percent_tumour_cells_range = CustomChoiceField(
        choices=val.PERCENT_CELLS_RANGE,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    percent_tumour_cells_measurement_method = CustomChoiceField(
        choices=val.CELLS_MEASURE_METHOD,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    specimen_processing = CustomChoiceField(
        choices=val.SPECIMEN_PROCESSING,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    specimen_laterality = CustomChoiceField(
        choices=val.SPECIMEN_LATERALITY,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Specimen
        fields = "__all__"


class SampleRegistrationSerializer(serializers.ModelSerializer):
    submitter_sample_id = serializers.RegexField(
        regex=regex["ID"],
        max_length=64,
        validators=[UniqueValidator(queryset=SampleRegistration.objects.all())],
    )
    specimen_tissue_source = CustomChoiceField(
        choices=val.SPECIMEN_TISSUE_SOURCE,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    tumour_normal_designation = CustomChoiceField(
        choices=["Normal", "Tumour"], allow_blank=True, allow_null=True, required=False
    )
    specimen_type = CustomChoiceField(
        choices=val.SPECIMEN_TYPE, allow_blank=True, allow_null=True, required=False
    )
    sample_type = CustomChoiceField(
        choices=val.SAMPLE_TYPE, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = SampleRegistration
        fields = "__all__"


class PrimaryDiagnosisSerializer(serializers.ModelSerializer):
    submitter_primary_diagnosis_id = serializers.RegexField(
        regex=regex["ID"], max_length=64
    )
    date_of_diagnosis = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    # cancer_type_code = serializers.CharField()  # TODO: write regex
    basis_of_diagnosis = CustomChoiceField(
        choices=val.BASIS_OF_DIAGNOSIS,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    lymph_nodes_examined_status = CustomChoiceField(
        choices=val.LYMPH_NODE_STATUS, allow_blank=True, allow_null=True, required=False
    )
    lymph_nodes_examined_method = CustomChoiceField(
        choices=val.LYMPH_NODE_METHOD, allow_blank=True, allow_null=True, required=False
    )
    clinical_tumour_staging_system = CustomChoiceField(
        choices=val.TUMOUR_STAGING_SYSTEM,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    clinical_t_category = CustomChoiceField(
        choices=val.T_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    clinical_n_category = CustomChoiceField(
        choices=val.N_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    clinical_m_category = CustomChoiceField(
        choices=val.M_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    clinical_stage_group = CustomChoiceField(
        choices=val.STAGE_GROUP, allow_blank=True, allow_null=True, required=False
    )
    laterality = CustomChoiceField(
        choices=val.PRIMARY_DIAGNOSIS_LATERALITY,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = PrimaryDiagnosis
        fields = "__all__"


class TreatmentSerializer(serializers.ModelSerializer):
    submitter_treatment_id = serializers.RegexField(regex=regex["ID"], max_length=64)
    treatment_type = serializers.ListField(
        allow_null=True,
        allow_empty=True,
        required=False,
        child=CustomChoiceField(
            choices=val.TREATMENT_TYPE,
            allow_blank=True,
            allow_null=True,
            required=False,
        ),
    )
    is_primary_treatment = CustomChoiceField(
        choices=val.UBOOLEAN, allow_blank=True, allow_null=True, required=False
    )
    treatment_start_date = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    treatment_end_date = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    treatment_setting = CustomChoiceField(
        choices=val.TREATMENT_SETTING, allow_blank=True, allow_null=True, required=False
    )
    treatment_intent = CustomChoiceField(
        choices=val.TREATMENT_INTENT, allow_blank=True, allow_null=True, required=False
    )
    response_to_treatment_criteria_method = CustomChoiceField(
        choices=val.TREATMENT_RESPONSE_METHOD,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    response_to_treatment = CustomChoiceField(
        choices=val.TREATMENT_RESPONSE,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    status_of_treatment = CustomChoiceField(
        choices=val.TREATMENT_STATUS, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = Treatment
        fields = "__all__"


class ChemotherapySerializer(serializers.ModelSerializer):
    chemotherapy_drug_dose_units = CustomChoiceField(
        choices=val.DOSAGE_UNITS, allow_blank=True, allow_null=True, required=False
    )
    drug_reference_database = CustomChoiceField(
        choices=val.DRUG_REFERENCE_DB, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = Chemotherapy
        fields = "__all__"


class HormoneTherapySerializer(serializers.ModelSerializer):
    hormone_drug_dose_units = CustomChoiceField(
        choices=val.DOSAGE_UNITS, allow_blank=True, allow_null=True, required=False
    )
    drug_reference_database = CustomChoiceField(
        choices=val.DRUG_REFERENCE_DB, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = HormoneTherapy
        fields = "__all__"


class RadiationSerializer(serializers.ModelSerializer):
    radiation_therapy_modality = CustomChoiceField(
        choices=val.RADIATION_THERAPY_MODALITY,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    radiation_therapy_type = CustomChoiceField(
        choices=["External", "Internal"],
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    anatomical_site_irradiated = CustomChoiceField(
        choices=val.RADIATION_ANATOMICAL_SITE,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Radiation
        fields = "__all__"


class ImmunotherapySerializer(serializers.ModelSerializer):
    immunotherapy_type = CustomChoiceField(
        choices=val.IMMUNOTHERAPY_TYPE,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    drug_reference_database = CustomChoiceField(
        choices=val.DRUG_REFERENCE_DB, allow_blank=True, allow_null=True, required=False
    )
    immunotherapy_drug_dose_units = CustomChoiceField(
        choices=val.DOSAGE_UNITS, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = Immunotherapy
        fields = "__all__"


class SurgerySerializer(serializers.ModelSerializer):
    surgery_type = CustomChoiceField(
        choices=val.SURGERY_TYPE, allow_blank=True, allow_null=True, required=False
    )
    surgery_site = serializers.RegexField(
        regex=regex["TOPOGRAPHY"],
        max_length=255,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    surgery_location = CustomChoiceField(
        choices=val.SURGERY_LOCATION, allow_blank=True, allow_null=True, required=False
    )
    tumour_focality = CustomChoiceField(
        choices=val.TUMOUR_FOCALITY, allow_blank=True, allow_null=True, required=False
    )
    residual_tumour_classification = CustomChoiceField(
        choices=val.TUMOUR_CLASSIFICATION,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    margin_types_involved = serializers.ListField(
        allow_null=True,
        allow_empty=True,
        required=False,
        child=CustomChoiceField(
            choices=val.MARGIN_TYPES, allow_blank=True, allow_null=True, required=False
        ),
    )
    margin_types_not_involved = serializers.ListField(
        allow_null=True,
        allow_empty=True,
        required=False,
        child=CustomChoiceField(
            choices=val.MARGIN_TYPES, allow_blank=True, allow_null=True, required=False
        ),
    )
    margin_types_not_assessed = serializers.ListField(
        allow_null=True,
        allow_empty=True,
        required=False,
        child=CustomChoiceField(
            choices=val.MARGIN_TYPES, allow_blank=True, allow_null=True, required=False
        ),
    )
    lymphovascular_invasion = CustomChoiceField(
        choices=val.LYMPHOVACULAR_INVASION,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    perineural_invasion = CustomChoiceField(
        choices=val.PERINEURAL_INVASION,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Surgery
        fields = "__all__"


class FollowUpSerializer(serializers.ModelSerializer):
    disease_status_at_followup = CustomChoiceField(
        choices=val.DISEASE_STATUS_FOLLOWUP,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    relapse_type = CustomChoiceField(
        choices=val.RELAPSE_TYPE, allow_blank=True, allow_null=True, required=False
    )
    date_of_relapse = serializers.RegexField(
        regex=regex["DATE"],
        max_length=32,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    method_of_progression_status = serializers.ListField(
        allow_null=True,
        allow_empty=True,
        required=False,
        child=CustomChoiceField(
            choices=val.PROGRESSION_STATUS_METHOD,
            allow_blank=True,
            allow_null=True,
            required=False,
        ),
    )
    anatomic_site_progression_or_recurrence = serializers.RegexField(
        max_length=32,
        regex=regex["TOPOGRAPHY"],
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    recurrence_tumour_staging_system = CustomChoiceField(
        choices=val.TUMOUR_STAGING_SYSTEM,
        allow_blank=True,
        allow_null=True,
        required=False,
    )

    recurrence_t_category = CustomChoiceField(
        choices=val.T_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    recurrence_n_category = CustomChoiceField(
        choices=val.N_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    recurrence_m_category = CustomChoiceField(
        choices=val.M_CATEGORY, allow_blank=True, allow_null=True, required=False
    )
    recurrence_stage_group = CustomChoiceField(
        choices=val.STAGE_GROUP, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = FollowUp
        fields = "__all__"


class BiomarkerSerializer(serializers.ModelSerializer):
    er_status = CustomChoiceField(
        choices=val.ER_PR_HPV_STATUS, allow_blank=True, allow_null=True, required=False
    )
    pr_status = CustomChoiceField(
        choices=val.ER_PR_HPV_STATUS, allow_blank=True, allow_null=True, required=False
    )
    her2_ihc_status = CustomChoiceField(
        choices=val.HER2_STATUS, allow_blank=True, allow_null=True, required=False
    )
    her2_ish_status = CustomChoiceField(
        choices=val.HER2_STATUS, allow_blank=True, allow_null=True, required=False
    )
    hpv_ihc_status = CustomChoiceField(
        choices=val.ER_PR_HPV_STATUS, allow_blank=True, allow_null=True, required=False
    )
    hpv_pcr_status = CustomChoiceField(
        choices=val.ER_PR_HPV_STATUS, allow_blank=True, allow_null=True, required=False
    )
    hpv_strain = serializers.ListField(
        allow_null=True,
        allow_empty=True,
        required=False,
        child=CustomChoiceField(
            choices=val.HPV_STRAIN, allow_blank=True, allow_null=True, required=False
        ),
    )

    class Meta:
        model = Biomarker
        fields = "__all__"


class ComorbiditySerializer(serializers.ModelSerializer):
    prior_malignancy = CustomChoiceField(
        choices=val.UBOOLEAN, allow_blank=True, allow_null=True, required=False
    )
    laterality_of_prior_malignancy = CustomChoiceField(
        choices=val.MALIGNANCY_LATERALITY,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    comorbidity_type_code = serializers.RegexField(
        regex=regex["COMORBIDITY"],
        max_length=64,
        allow_blank=True,
        allow_null=True,
        required=False,
    )
    comorbidity_treatment_status = CustomChoiceField(
        choices=val.UBOOLEAN, allow_blank=True, allow_null=True, required=False
    )
    comorbidity_treatment = serializers.CharField(
        max_length=255, allow_blank=True, allow_null=True, required=False
    )

    class Meta:
        model = Comorbidity
        fields = "__all__"


class ExposureSerializer(serializers.ModelSerializer):
    tobacco_smoking_status = CustomChoiceField(
        choices=val.SMOKING_STATUS, allow_blank=True, allow_null=True, required=False
    )
    tobacco_type = serializers.ListField(
        allow_null=True,
        allow_empty=True,
        required=False,
        child=CustomChoiceField(
            choices=val.TOBACCO_TYPE, allow_blank=True, allow_null=True, required=False
        ),
    )

    class Meta:
        model = Exposure
        fields = "__all__"


##########################################
#                                        #
#           CUSTOM SERIALIZERS           #
#                                        #
##########################################
class IngestRequestSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.JSONField())
