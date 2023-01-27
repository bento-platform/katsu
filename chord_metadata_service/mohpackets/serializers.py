from rest_framework import serializers

import chord_metadata_service.mohpackets.permissible_values as val

from .validators import (
    positive_int,
    ChoicesValidator,
    ID,
    DATE,
    TOPOGRAPHY,
)

from .models import (
    Program,
    Donor,
    Specimen,
    SampleRegistration,
    PrimaryDiagnosis,
    Treatment,
    Chemotherapy,
    HormoneTherapy,
    Radiation,
    Immunotherapy,
    Surgery,
    FollowUp,
    Biomarker,
    Comorbidity,
)


"""
    This module contains the SERIALIZERS for the models in the mohpackets app.
    It converting Python objects or Django model instances into a JSON string,
    and back again for API transmissions.

    We use the ModelSerializer class, which provides a way to create a Serializer
    directly from a Django model. All that needs to be done to create a ModelSerializer
    is to specify a model on its Meta attribute. For reference, see:
    https://www.django-rest-framework.org/api-guide/serializers/#modelserializer

    NOTES: There is no validation in the serializers yet. Currently, it will be
    handled by the ingest process. Additional validations can be added here if needed.
"""


class ProgramSerializer(serializers.ModelSerializer):
    program_id = serializers.CharField(
        max_length=64, 
        validators=[ID]
    )
    name = serializers.CharField(
        max_length=255, 
        validators=[ID]
        )
    created = serializers.DateTimeField(validators=[DATE])  # TODO: ask Son (date format)
    updated = serializers.DateTimeField(validators=[DATE])  # TODO: ask Son

    class Meta:
        model = Program
        fields = "__all__"


class DonorSerializer(serializers.ModelSerializer):
    submitter_donor_id = serializers.CharField(
        max_length=64,
        validators=[ID],
    )
    is_deceased = serializers.BooleanField(
        validators=[ChoicesValidator(["Yes", "No"])])
    cause_of_death = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(choices=val.CAUSE_OF_DEATH)]
    )
    date_of_birth = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    date_of_death = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    primary_site = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.PRIMARY_SITE)]
    )

    class Meta:
        model = Donor
        fields = "__all__"


class SpecimenSerializer(serializers.ModelSerializer):
    submitter_specimen_id = serializers.CharField(  # TODO: confirm regex
        max_length=64,
        validators=[ID]
    )
    pathological_tumour_staging_system = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.TUMOUR_STAGING_SYSTEM)]
    )
    pathological_t_category = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.T_CATEGORY)]
    )
    pathological_n_category = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.N_CATEGORY)]
    )
    pathological_m_category = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.M_CATEGORY)]
    )
    pathological_stage_group = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.STAGE_GROUP)]
    )
    specimen_collection_date = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    specimen_storage = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.STORAGE)]
    )
    # tumour_histological_type = serializers.CharField(validators=[val.MORPHOLOGY])  # TODO: Write validator
    specimen_anatomic_location = serializers.CharField(validators=[TOPOGRAPHY])
    reference_pathology_confirmed_diagnosis = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(val.CONFIRMED_DIAGNOSIS_TUMOUR)]
    )
    reference_pathology_confirmed_tumour_presence = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(val.CONFIRMED_DIAGNOSIS_TUMOUR)]
    )
    tumour_grading_system = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.TUMOUR_GRADING_SYSTEM)]
    )
    tumour_grade = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.TUMOUR_GRADE)]
    )
    percent_tumour_cells_range = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.PERCENT_CELLS_RANGE)]
    )
    percent_tumour_cells_measurement_method = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.CELLS_MEASURE_METHOD)]
    )

    class Meta:
        model = Specimen
        fields = "__all__"


class SampleRegistrationSerializer(serializers.ModelSerializer):
    submitter_sample_id = serializers.CharField(
        max_length=64,
        validators=[ID]
    )  # TODO: check regex
    gender = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(val.GENDER)]
    )
    sex_at_birth = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(val.SEX_AT_BIRTH)]
    )
    specimen_tissue_source = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.SPECIMEN_TISSUE_SOURCE)]
    )
    tumour_normal_designation = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(["Normal", "Tumour"])]
    )
    specimen_type = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.SPECIMEN_TYPE)]
    )
    sample_type = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.SAMPLE_TYPE)]
    )

    class Meta:
        model = SampleRegistration
        fields = "__all__"


class PrimaryDiagnosisSerializer(serializers.ModelSerializer):
    submitter_primary_diagnosis_id = serializers.CharField(
        max_length=64,
        validators=[ID]
    )  # TODO: check regex
    date_of_diagnosis = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    # cancer_type_code = serializers.CharField()  # TODO: write validator
    basis_of_diagnosis = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.BASIS_OF_DIAGNOSIS)]
    )
    lymph_nodes_examined_status = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.LYMPH_NODE_STATUS)]
    )
    lymph_nodes_examined_method = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.LYMPH_NODE_METHOD)]
    )
    number_lymph_nodes_positive = serializers.IntegerField(
        validators=[positive_int]
    )
    clinical_tumour_staging_system = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.TUMOUR_STAGING_SYSTEM)]
    )
    clinical_t_category = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.T_CATEGORY)]
    )
    clinical_n_category = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.N_CATEGORY)]
    )
    clinical_m_category = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.M_CATEGORY)]
    )
    clinical_stage_group = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.STAGE_GROUP)]
    )

    class Meta:
        model = PrimaryDiagnosis
        fields = "__all__"


class TreatmentSerializer(serializers.ModelSerializer):
    submitter_treatment_id = serializers.CharField(
        max_length=64,
        validators=[ID]
    )
    treatment_type = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.TREATMENT_TYPE)]
    )
    is_primary_treatment = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(["Yes", "No", "Unknown"])]
    )
    treatment_start_date = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    treatment_end_date = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    treatment_setting = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.TREATMENT_SETTING)]
    )
    treatment_intent = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(["Curative", "Palliative"])]
    )
    days_per_cycle = serializers.IntegerField(
        validators=[positive_int]        
    )
    number_of_cycles = serializers.IntegerField(
        validators=[positive_int]
    )
    response_to_treatment_criteria_method = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.TREATMENT_RESPONSE_METHOD)]
    )
    response_to_treatment = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.TREATMENT_RESPONSE)]
    )

    class Meta:
        model = Treatment
        fields = "__all__"


class ChemotherapySerializer(serializers.ModelSerializer):
    # drug_name =  serializers.Charfield(
    #     max_length=255,
    #     validators=[ChoicesValidator]
    # )
    # drug_rxnormcui =  serializers.Charfield(
    #     max_length=64,
    #     validators=[ChoicesValidator]
    # )
    chemotherapy_dosage_units = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.DOSAGE_UNITS)]
    )
    cumulative_drug_dosage_prescribed = serializers.IntegerField(
        validators=[positive_int]
    )
    cumulative_drug_dosage_actual = serializers.IntegerField(
        validators=[positive_int]
    )
    class Meta:
        model = Chemotherapy
        fields = "__all__"


class HormoneTherapySerializer(serializers.ModelSerializer):
    # drug_name =  serializers.Charfield(
    #     max_length=255,
    #     validators=[ChoicesValidator]
    # )
    # drug_rxnormcui =  serializers.Charfield(
    #     max_length=64,
    #     validators=[ChoicesValidator]
    # )
    chemotherapy_dosage_units = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.DOSAGE_UNITS)]
    )
    cumulative_drug_dosage_prescribed = serializers.IntegerField(
        validators=[positive_int]
    )
    cumulative_drug_dosage_actual = serializers.IntegerField(
        validators=[positive_int]
    )
    class Meta:
        model = HormoneTherapy
        fields = "__all__"


class RadiationSerializer(serializers.ModelSerializer):
    radiation_therapy_modality = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.RADIATION_THERAPY_MODALITY)]
    )
    radiation_therapy_type = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(["External", "Internal"])]
    )
    radiation_therapy_fractions = serializers.IntegerField(
        validators=[positive_int]
    )
    radiation_therapy_dosage = serializers.IntegerField(
        validators=[positive_int]
    )
    anatomical_site_irradiated = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.RADIATION_ANATOMICAL_SITE)]
    )
    radiation_boost = serializers.BooleanField(
        validators=[ChoicesValidator(["Yes", "No"])]
    )
    reference_radiation_treatment_id = serializers.CharField(
        max_length=64
    )
    class Meta:
        model = Radiation
        fields = "__all__"


class ImmunotherapySerializer(serializers.ModelSerializer):
    immunotherapy_type = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.IMMUNOTHERAPY_TYPE)]
    )
    # drug_name =  serializers.Charfield(
    #     max_length=255,
    #     validators=[ChoicesValidator]
    # )
    # drug_rxnormcui =  serializers.Charfield(
    #     max_length=64,
    #     validators=[ChoicesValidator]
    # )
    class Meta:
        model = Immunotherapy
        fields = "__all__"


class SurgerySerializer(serializers.ModelSerializer):
    surgery_type = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.SURGERY_TYPE)]
    )
    surgery_site = serializers.CharField(
        max_length=255,
        validators=[TOPOGRAPHY]
    )
    surgery_location = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.SURGERY_LOCATION)]
    )
    tumour_length = serializers.IntegerField(
        validators=[positive_int]
    )
    tumour_width = serializers.IntegerField(
        validators=[positive_int]
    )
    greatest_dimension_tumour = serializers.IntegerField(
        validators=[positive_int]
    )
    tumour_focality = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.TUMOUR_FOCALITY)]
    )
    residual_tumour_classification = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.TUMOUR_CLASSIFICATION)]
    )
    margin_types_involved = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.MARGIN_TYPES)]
    )
    margin_types_not_involved = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.MARGIN_TYPES)]
    )
    margin_types_not_assessed = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.MARGIN_TYPES)]
    )
    lymphovascular_invasion = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.LYMPHOVACULAR_INVASION)]
    )
    perineural_invasion = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.PERINEURAL_INVASION)]
    )
    
    class Meta:
        model = Surgery
        fields = "__all__"


class FollowUpSerializer(serializers.ModelSerializer):
    date_of_followup = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    lost_to_followup = serializers.BooleanField(
        validators=[ChoicesValidator(["Yes", "No"])]
    )
    lost_to_followup_reason = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.LOST_FOLLOW_UP_REASON)]
    )
    disease_status_at_followup = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.DISEASE_STATUS_FOLLOWUP)]
    )
    relapse_type = serializers.CharField(
        max_length=128,
        validators=[ChoicesValidator(val.RELAPSE_TYPE)]
    )    
    date_of_relapse = serializers.CharField(
        max_length=32,
        validators=[DATE]
    )
    method_of_progression_status = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.PROGRESSION_STATUS_METHOD)]
    )
    anatomic_site_progression_or_recurrence = serializers.CharField(
        max_length=255,
        validators=[TOPOGRAPHY]
    )
    recurrence_tumour_staging_system = serializers.CharField(
        max_length=255,
        validators=[ChoicesValidator(val.TUMOUR_STAGING_SYSTEM)]
    )
    recurrence_t_category = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(val.T_CATEGORY)]
    )
    recurrence_n_category = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(val.N_CATEGORY)]
    )
    recurrence_m_category = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(val.M_CATEGORY)]
    )
    recurrence_stage_group = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.STAGE_GROUP)]
    )
    class Meta:
        model = FollowUp
        fields = "__all__"


class BiomarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biomarker
        fields = "__all__"


class ComorbiditySerializer(serializers.ModelSerializer):
    prior_malignancy = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(["Yes", "No", "Unknown"])]
    )
    laterality_of_prior_malignancy = serializers.CharField(
        max_length=64,
        validators=[ChoicesValidator(val.MALIGNANCY_LATERALITY)]
    )
    comorbidity_type_code = serializers.CharField(
        max_length=64
        # validators=  # TODO: write regex
    )
    comorbidity_treatment_status = serializers.CharField(
        max_length=32,
        validators=[ChoicesValidator(["Yes", "No", "Unknown"])]
    )
    comorbidity_treatment = serializers.CharField(
        max_length=255
    )
    class Meta:
        model = Comorbidity
        fields = "__all__"
