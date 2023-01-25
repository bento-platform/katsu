from rest_framework import serializers

import chord_metadata_service.mohpackets.validators as val

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
        validators=[val.ID]
    )
    name = serializers.CharField(
        max_length=255, 
        validators=[val.ID]
        )
    created = serializers.DateTimeField(validators=[val.DATE])  # TODO: ask Son (date format)
    updated = serializers.DateTimeField(validators=[val.DATE])  # TODO: ask Son

    class Meta:
        model = Program
        fields = "__all__"


class DonorSerializer(serializers.ModelSerializer):
    submitter_donor_id = serializers.CharField(
        max_length=64,
        validators=[val.ID],
    )
    is_deceased = serializers.BooleanField(
        validators=[val.BOOLEAN])
    cause_of_death = serializers.CharField(
        max_length=255,
        validators=[val.CAUSE_OF_DEATH]
    )
    date_of_birth = serializers.CharField(
        max_length=32,
        validators=[val.DATE]
    )
    date_of_death = serializers.CharField(
        max_length=32,
        validators=[val.DATE]
    )
    primary_site = serializers.CharField(
        max_length=255,
        validators=[val.PRIMARY_SITE]
    )

    class Meta:
        model = Donor
        fields = "__all__"


class SpecimenSerializer(serializers.ModelSerializer):
    submitter_specimen_id = serializers.CharField(  # TODO: confirm regex
        max_length=64,
        validators=[val.ID]
    )
    pathological_tumour_staging_system = serializers.CharField(
        max_length=255,
        validators=[val.TUMOUR_STAGING_SYSTEM]
    )
    pathological_t_category = serializers.CharField(
        max_length=255,
        validators=[val.T_CATEGORY]
    )
    pathological_n_category = serializers.CharField(
        max_length=64,
        validators=[val.N_CATEGORY]
    )
    pathological_m_category = serializers.CharField(
        max_length=64,
        validators=[val.M_CATEGORY]
    )
    pathological_stage_group = serializers.CharField(
        max_length=64,
        validators=[val.STAGE_GROUP]
    )
    specimen_collection_date = serializers.CharField(
        max_length=32,
        validators=[val.DATE]
    )
    specimen_storage = serializers.CharField(
        max_length=64,
        validators=[val.STORAGE]
    )
    # tumour_histological_type = serializers.CharField(validators=[val.MORPHOLOGY])  # TODO: Write validator
    specimen_anatomic_location = serializers.CharField(validators=[val.TOPOGRAPHY])
    reference_pathology_confirmed_diagnosis = serializers.CharField(
        max_length=32,
        validators=[val.CONFIRMED_DIAGNOSIS_TUMOUR]
    )
    reference_pathology_confirmed_tumour_presence = serializers.CharField(
        max_length=32,
        validators=[val.CONFIRMED_DIAGNOSIS_TUMOUR]
    )
    tumour_grading_system = serializers.CharField(
        max_length=128,
        validators=[val.TUMOUR_GRADING_SYSTEM]
    )
    tumour_grade = serializers.CharField(
        max_length=64,
        validators=[val.TUMOUR_GRADE]
    )
    percent_tumour_cells_range = serializers.CharField(
        max_length=64,
        validators=[val.PERCENT_CELLS_RANGE]
    )
    percent_tumour_cells_measurement_method = serializers.CharField(
        max_length=64,
        validators=[val.CELLS_MEASUREMENT_METHOD]
    )

    class Meta:
        model = Specimen
        fields = "__all__"


class SampleRegistrationSerializer(serializers.ModelSerializer):
    submitter_sample_id = serializers.CharField(
        max_length=64,
        validators=[val.ID]
    )  # TODO: check regex
    gender = serializers.CharField(
        max_length=32,
        validators=[val.GENDER])
    sex_at_birth = serializers.CharField(
        max_length=32,
        validators=[val.SEX_AT_BIRTH])
    specimen_tissue_source = serializers.CharField(
        max_length=255,
        validators=[val.SPECIMEN_TISSUE_SOURCE]
    )
    tumour_normal_designation = serializers.CharField(
        max_length=32,
        validators=[val.TUMOUR_DESIGNATION]
    )
    specimen_type = serializers.CharField(
        max_length=255,
        validators=[val.SPECIMEN_TYPE])
    sample_type = serializers.CharField(
        max_length=128,
        validators=[val.SAMPLE_TYPE])

    class Meta:
        model = SampleRegistration
        fields = "__all__"


class PrimaryDiagnosisSerializer(serializers.ModelSerializer):
    submitter_primary_diagnosis_id = serializers.CharField(
        max_length=64,
        validators=[val.ID]
    )  # TODO: check regex
    date_of_diagnosis = serializers.CharField(
        max_length=32,
        validators=[val.DATE]
    )
    # cancer_type_code = serializers.CharField()  # TODO: write validator
    basis_of_diagnosis = serializers.CharField(
        max_length=128,
        validators=[val.BASIS_OF_DIAGNOSIS]
    )
    lymph_nodes_examined_status = serializers.CharField(
        max_length=128,
        validators=[val.LYMPH_NODE_STATUS]
    )
    lymph_nodes_examined_method = serializers.CharField(
        max_length=64,
        validators=[val.LYMPH_NODE_METHOD]
    )
    number_lymph_nodes_positive = serializers.IntegerField(
        validators=[val.validate_positive_int]
    )
    clinical_tumour_staging_system = serializers.CharField(
        max_length=128,
        validators=[val.TUMOUR_STAGING_SYSTEM]
    )
    clinical_t_category = serializers.CharField(
        max_length=64,
        validators=[val.T_CATEGORY]
    )
    clinical_n_category = serializers.CharField(
        max_length=64,
        validators=[val.N_CATEGORY]
    )
    clinical_m_category = serializers.CharField(
        max_length=64,
        validators=[val.M_CATEGORY]
    )
    clinical_stage_group = serializers.CharField(
        max_length=64,
        validators=[val.STAGE_GROUP]
    )

    class Meta:
        model = PrimaryDiagnosis
        fields = "__all__"


class TreatmentSerializer(serializers.ModelSerializer):
    submitter_treatment_id = serializers.CharField(
        max_length=64,
        validators=[val.ID]
    )
    treatment_type = serializers.CharField(
        max_length=255,
        validators=[val.TRE]
    )
    is_primary_treatment = serializers.CharField(
        max_length=32
    )
    treatment_start_date = serializers.CharField(
        max_length=32
    )
    treatment_end_date = serializers.CharField(
        max_length=32
    )
    treatment_setting = serializers.CharField(
        max_length=128
    )
    treatment_intent = serializers.CharField(
        max_length=128
    )
    days_per_cycle = serializers.IntegerField(

    )
    number_of_cycles = serializers.IntegerField(blank=True, null=True)
    response_to_treatment_criteria_method = serializers.CharField(
        max_length=255, null=False, blank=False
    )
    response_to_treatment = serializers.CharField(max_length=255, null=False, blank=False)

    class Meta:
        model = Treatment
        fields = "__all__"


class ChemotherapySerializer(serializers.ModelSerializer):
    class Meta:
        model = Chemotherapy
        fields = "__all__"


class HormoneTherapySerializer(serializers.ModelSerializer):
    class Meta:
        model = HormoneTherapy
        fields = "__all__"


class RadiationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Radiation
        fields = "__all__"


class ImmunotherapySerializer(serializers.ModelSerializer):
    class Meta:
        model = Immunotherapy
        fields = "__all__"


class SurgerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Surgery
        fields = "__all__"


class FollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = "__all__"


class BiomarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biomarker
        fields = "__all__"


class ComorbiditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidity
        fields = "__all__"
