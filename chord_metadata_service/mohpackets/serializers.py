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
    program_id = serializers.PrimaryKeyRelatedField(
        queryset=Program.objects.all(), validators=[val.ID]
    )
    name=serializers.CharField(validators=[val.ID])
    created = serializers.DateTimeField(validators=[val.DATE]) # TODO: ask Son
    updated = serializers.DateTimeField(validators=[val.DATE]) # TODO: ask Son

    class Meta:
        model = Program
        fields = "__all__"


class DonorSerializer(serializers.ModelSerializer):
    submitter_donor_id = serializers.PrimaryKeyRelatedField( # TODO: ask Son
        queryset=Donor.objects.all(), validators=[val.ID]
    )
    is_deceased = serializers.BooleanField(validators=[val.BOOLEAN])
    cause_of_death = serializers.CharField(validators=[val.CAUSE_OF_DEATH])
    date_of_birth = serializers.CharField(validators=[val.DATE])
    date_of_death = serializers.CharField(validators=[val.DATE])
    primary_site = serializers.CharField(validators=[val.PRIMARY_SITE])
    
    class Meta:
        model = Donor
        fields = "__all__"


class SpecimenSerializer(serializers.ModelSerializer):
    submitter_specimen_id = serializers.PrimaryKeyRelatedField( # TODO: ask Son
        queryset=Specimen.objects.all(), validators=[val.ID]
    )
    pathological_tumour_staging_system = serializers.CharField(
        validators=[val.TUMOUR_STAGING_SYSTEM]
    )
    pathological_t_category = serializers.CharField(validators=[val.T_CATEGORY])
    pathological_n_category = serializers.CharField(validators=[val.N_CATEGORY])
    pathological_m_category = serializers.CharField(validators=[val.M_CATEGORY])
    pathological_stage_group = serializers.CharField(validators=[val.STAGE_GROUP])
    specimen_collection_date = serializers.CharField(validators=[val.DATE])
    specimen_storage = serializers.CharField(validators=[val.STORAGE])
    # tumour_histological_type = serializers.CharField(validators=[val.MORPHOLOGY]) # TODO: Write validator
    specimen_anatomic_location = serializers.CharField(validators=[val.TOPOGRAPHY])
    reference_pathology_confirmed_diagnosis = serializers.CharField(
        validators=[val.CONFIRMED_DIAGNOSIS_TUMOUR]
    )
    reference_pathology_confirmed_tumour_presence = serializers.CharField(
        validators=[val.CONFIRMED_DIAGNOSIS_TUMOUR]
    )
    tumour_grading_system = serializers.CharField(
        validators=[val.TUMOUR_GRADING_SYSTEM]
    )
    tumour_grade = serializers.CharField(
        validators=[val.TUMOUR_GRADE]
    )
    percent_tumour_cells_range = serializers.CharField(
        validators=[val.PERCENT_CELLS_RANGE]
    )
    percent_tumour_cells_measurement_method = serializers.CharField(
        validators=[val.CELLS_MEASUREMENT_METHOD]
    )

    class Meta:
        model = Specimen
        fields = "__all__"


class SampleRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleRegistration
        fields = "__all__"


class PrimaryDiagnosisSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimaryDiagnosis
        fields = "__all__"


class TreatmentSerializer(serializers.ModelSerializer):
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
