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

    NOTES: There is no validation in the serializers yet. Currently, it will be
    handled by the ingest process. Additional validations can be added here if needed.
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
    cause_of_death = CustomChoiceField(choices=val.CAUSE_OF_DEATH, allow_blank=True)
    date_of_birth = serializers.RegexField(regex=regex["DATE"], max_length=32)
    date_of_death = serializers.RegexField(
        regex=regex["DATE"], max_length=32, allow_blank=True
    )
    primary_site = serializers.ListField(
        allow_empty=False, child=CustomChoiceField(choices=val.PRIMARY_SITE)
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
        choices=val.TUMOUR_STAGING_SYSTEM, allow_blank=True
    )
    pathological_t_category = CustomChoiceField(
        choices=val.T_CATEGORY, allow_blank=True
    )
    pathological_n_category = CustomChoiceField(
        choices=val.N_CATEGORY, allow_blank=True
    )
    pathological_m_category = CustomChoiceField(
        choices=val.M_CATEGORY, allow_blank=True
    )
    pathological_stage_group = CustomChoiceField(
        choices=val.STAGE_GROUP, allow_blank=True
    )
    specimen_collection_date = serializers.RegexField(
        regex=regex["DATE"], max_length=32
    )
    specimen_storage = CustomChoiceField(choices=val.STORAGE)
    tumour_histological_type = serializers.RegexField(
        max_length=128, regex=regex["MORPHOLOGY"], allow_blank=True
    )
    specimen_anatomic_location = serializers.RegexField(
        max_length=32, regex=regex["TOPOGRAPHY"], allow_blank=True
    )
    reference_pathology_confirmed_diagnosis = CustomChoiceField(
        choices=val.CONFIRMED_DIAGNOSIS_TUMOUR, allow_blank=True
    )
    reference_pathology_confirmed_tumour_presence = CustomChoiceField(
        choices=val.CONFIRMED_DIAGNOSIS_TUMOUR, allow_blank=True
    )
    tumour_grading_system = CustomChoiceField(
        choices=val.TUMOUR_GRADING_SYSTEM, allow_blank=True
    )
    tumour_grade = CustomChoiceField(choices=val.TUMOUR_GRADE, allow_blank=True)
    percent_tumour_cells_range = CustomChoiceField(
        choices=val.PERCENT_CELLS_RANGE, allow_blank=True
    )
    percent_tumour_cells_measurement_method = CustomChoiceField(
        choices=val.CELLS_MEASURE_METHOD, allow_blank=True
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
    gender = CustomChoiceField(choices=val.GENDER)
    sex_at_birth = CustomChoiceField(choices=val.SEX_AT_BIRTH)
    specimen_tissue_source = CustomChoiceField(choices=val.SPECIMEN_TISSUE_SOURCE)
    tumour_normal_designation = CustomChoiceField(choices=["Normal", "Tumour"])
    specimen_type = CustomChoiceField(choices=val.SPECIMEN_TYPE)
    sample_type = CustomChoiceField(choices=val.SAMPLE_TYPE)

    class Meta:
        model = SampleRegistration
        fields = "__all__"


class PrimaryDiagnosisSerializer(serializers.ModelSerializer):
    submitter_primary_diagnosis_id = serializers.RegexField(
        regex=regex["ID"], max_length=64
    )
    date_of_diagnosis = serializers.RegexField(regex=regex["DATE"], max_length=32)
    # cancer_type_code = serializers.CharField()  # TODO: write regex
    basis_of_diagnosis = CustomChoiceField(choices=val.BASIS_OF_DIAGNOSIS)
    lymph_nodes_examined_status = CustomChoiceField(choices=val.LYMPH_NODE_STATUS)
    lymph_nodes_examined_method = CustomChoiceField(choices=val.LYMPH_NODE_METHOD)
    clinical_tumour_staging_system = CustomChoiceField(
        choices=val.TUMOUR_STAGING_SYSTEM, allow_blank=True
    )
    clinical_t_category = CustomChoiceField(choices=val.T_CATEGORY, allow_blank=True)
    clinical_n_category = CustomChoiceField(choices=val.N_CATEGORY, allow_blank=True)
    clinical_m_category = CustomChoiceField(choices=val.M_CATEGORY, allow_blank=True)
    clinical_stage_group = CustomChoiceField(choices=val.STAGE_GROUP, allow_blank=True)

    class Meta:
        model = PrimaryDiagnosis
        fields = "__all__"


class TreatmentSerializer(serializers.ModelSerializer):
    submitter_treatment_id = serializers.RegexField(regex=regex["ID"], max_length=64)
    treatment_type = serializers.ListField(
        allow_empty=False, child=CustomChoiceField(choices=val.TREATMENT_TYPE)
    )
    is_primary_treatment = CustomChoiceField(choices=val.UBOOLEAN)
    treatment_start_date = serializers.RegexField(regex=regex["DATE"], max_length=32)
    treatment_end_date = serializers.RegexField(regex=regex["DATE"], max_length=32)
    treatment_setting = CustomChoiceField(choices=val.TREATMENT_SETTING)
    treatment_intent = CustomChoiceField(choices=["Curative", "Palliative"])
    response_to_treatment_criteria_method = CustomChoiceField(
        choices=val.TREATMENT_RESPONSE_METHOD
    )
    response_to_treatment = CustomChoiceField(choices=val.TREATMENT_RESPONSE)

    class Meta:
        model = Treatment
        fields = "__all__"


class ChemotherapySerializer(serializers.ModelSerializer):
    chemotherapy_dosage_units = CustomChoiceField(choices=val.DOSAGE_UNITS)

    class Meta:
        model = Chemotherapy
        fields = "__all__"


class HormoneTherapySerializer(serializers.ModelSerializer):
    hormone_drug_dosage_units = CustomChoiceField(choices=val.DOSAGE_UNITS)

    class Meta:
        model = HormoneTherapy
        fields = "__all__"


class RadiationSerializer(serializers.ModelSerializer):
    radiation_therapy_modality = CustomChoiceField(
        choices=val.RADIATION_THERAPY_MODALITY
    )
    radiation_therapy_type = CustomChoiceField(choices=["External", "Internal"])
    anatomical_site_irradiated = CustomChoiceField(
        choices=val.RADIATION_ANATOMICAL_SITE
    )

    class Meta:
        model = Radiation
        fields = "__all__"


class ImmunotherapySerializer(serializers.ModelSerializer):
    immunotherapy_type = CustomChoiceField(choices=val.IMMUNOTHERAPY_TYPE)

    class Meta:
        model = Immunotherapy
        fields = "__all__"


class SurgerySerializer(serializers.ModelSerializer):
    surgery_type = CustomChoiceField(choices=val.SURGERY_TYPE)
    surgery_site = serializers.RegexField(
        regex=regex["TOPOGRAPHY"], max_length=255, allow_blank=True
    )
    surgery_location = CustomChoiceField(choices=val.SURGERY_LOCATION, allow_blank=True)
    tumour_focality = CustomChoiceField(choices=val.TUMOUR_FOCALITY, allow_blank=True)
    residual_tumour_classification = CustomChoiceField(
        choices=val.TUMOUR_CLASSIFICATION, allow_blank=True
    )
    margin_types_involved = serializers.ListField(
        child=CustomChoiceField(choices=val.MARGIN_TYPES, allow_blank=True),
    )
    margin_types_not_involved = serializers.ListField(
        child=CustomChoiceField(choices=val.MARGIN_TYPES, allow_blank=True),
    )
    margin_types_not_assessed = serializers.ListField(
        child=CustomChoiceField(choices=val.MARGIN_TYPES, allow_blank=True),
    )
    lymphovascular_invasion = CustomChoiceField(
        choices=val.LYMPHOVACULAR_INVASION, allow_blank=True
    )
    perineural_invasion = CustomChoiceField(
        choices=val.PERINEURAL_INVASION, allow_blank=True
    )

    class Meta:
        model = Surgery
        fields = "__all__"


class FollowUpSerializer(serializers.ModelSerializer):
    date_of_followup = serializers.RegexField(regex=regex["DATE"], max_length=32)
    lost_to_followup_reason = CustomChoiceField(
        choices=val.LOST_FOLLOW_UP_REASON, allow_blank=True
    )
    disease_status_at_followup = CustomChoiceField(choices=val.DISEASE_STATUS_FOLLOWUP)
    relapse_type = CustomChoiceField(choices=val.RELAPSE_TYPE, allow_blank=True)
    date_of_relapse = serializers.RegexField(
        regex=regex["DATE"], max_length=32, allow_blank=True
    )
    method_of_progression_status = CustomChoiceField(
        choices=val.PROGRESSION_STATUS_METHOD, allow_blank=True
    )
    anatomic_site_progression_or_recurrence = serializers.RegexField(
        max_length=32, regex=regex["TOPOGRAPHY"], allow_blank=True
    )
    recurrence_tumour_staging_system = CustomChoiceField(
        choices=val.TUMOUR_STAGING_SYSTEM, allow_blank=True
    )
    recurrence_t_category = CustomChoiceField(choices=val.T_CATEGORY, allow_blank=True)
    recurrence_n_category = CustomChoiceField(choices=val.N_CATEGORY, allow_blank=True)
    recurrence_m_category = CustomChoiceField(choices=val.M_CATEGORY, allow_blank=True)
    recurrence_stage_group = CustomChoiceField(
        choices=val.STAGE_GROUP, allow_blank=True
    )

    class Meta:
        model = FollowUp
        fields = "__all__"


class BiomarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biomarker
        fields = "__all__"


class ComorbiditySerializer(serializers.ModelSerializer):
    prior_malignancy = CustomChoiceField(choices=val.UBOOLEAN)
    laterality_of_prior_malignancy = CustomChoiceField(
        choices=val.MALIGNANCY_LATERALITY, allow_blank=True
    )
    comorbidity_type_code = serializers.RegexField(
        regex=regex["COMORBIDITY"], max_length=64, allow_blank=True
    )
    comorbidity_treatment_status = CustomChoiceField(
        choices=val.UBOOLEAN, allow_blank=True
    )
    comorbidity_treatment = serializers.CharField(max_length=255, allow_blank=True)

    class Meta:
        model = Comorbidity
        fields = "__all__"


##########################################
#                                        #
#           CUSTOM SERIALIZERS           #
#                                        #
##########################################
class IngestRequestSerializer(serializers.Serializer):
    data = serializers.ListField(child=serializers.JSONField())


# ------------------------------


class DonorRelatedClinicalDataSerializer(serializers.ModelSerializer):
    primary_diagnoses = serializers.SerializerMethodField()
    comorbidities = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()

    def get_primary_diagnoses(self, obj):
        primary_diagnoses = obj.primarydiagnosis_set.all()
        return NestedPrimaryDiagnosisSerializer(primary_diagnoses, many=True).data

    def get_comorbidities(self, obj):
        comorbidities = obj.comorbidity_set.all()
        return NestedComorbiditySerializer(comorbidities, many=True).data

    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    class Meta:
        model = Donor
        fields = [
            "submitter_donor_id",
            "program_id",
            "is_deceased",
            "cause_of_death",
            "date_of_birth",
            "date_of_death",
            "primary_site",
            "primary_diagnoses",
            "comorbidities",
            "biomarkers",
        ]


class NestedPrimaryDiagnosisSerializer(serializers.ModelSerializer):
    specimens = serializers.SerializerMethodField()
    treatments = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()

    def get_specimens(self, obj):
        spicemen = obj.specimen_set.all()
        return NestedSpecimenSerializer(spicemen, many=True).data

    def get_treatments(self, obj):
        treatments = obj.treatment_set.all()
        return NestedTreatmentSerializer(treatments, many=True).data

    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    class Meta:
        model = PrimaryDiagnosis
        fields = [
            "submitter_primary_diagnosis_id",
            "date_of_diagnosis",
            "cancer_type_code",
            "basis_of_diagnosis",
            "lymph_nodes_examined_status",
            "lymph_nodes_examined_method",
            "number_lymph_nodes_positive",
            "clinical_tumour_staging_system",
            "clinical_t_category",
            "clinical_n_category",
            "clinical_m_category",
            "clinical_stage_group",
            "specimens",
            "treatments",
            "biomarkers",
        ]


class NestedSpecimenSerializer(serializers.ModelSerializer):
    sample_registrations = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()

    def get_sample_registrations(self, obj):
        sample_registrations = obj.sampleregistration_set.all()
        return NestedSampleRegistrationSerializer(sample_registrations, many=True).data

    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    class Meta:
        model = Specimen
        fields = [
            "pathological_tumour_staging_system",
            "pathological_t_category",
            "pathological_n_category",
            "pathological_m_category",
            "pathological_stage_group",
            "specimen_collection_date",
            "specimen_storage",
            "tumour_histological_type",
            "specimen_anatomic_location",
            "reference_pathology_confirmed_diagnosis",
            "reference_pathology_confirmed_tumour_presence",
            "tumour_grading_system",
            "tumour_grade",
            "percent_tumour_cells_range",
            "percent_tumour_cells_measurement_method",
            "sample_registrations",
            "biomarkers",
        ]


class NestedTreatmentSerializer(serializers.ModelSerializer):
    chemotherapies = serializers.SerializerMethodField()
    hormone_therapies = serializers.SerializerMethodField()
    immunotherapies = serializers.SerializerMethodField()
    radiation = serializers.SerializerMethodField()
    surgery = serializers.SerializerMethodField()
    followups = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()

    def get_chemotherapies(self, obj):
        chemotherapies = obj.chemotherapy_set.all()
        return NestedChemotherapySerializer(chemotherapies, many=True).data

    def get_hormone_therapies(self, obj):
        hormone_therapies = obj.hormonetherapy_set.all()
        return NestedHormoneTherapySerializer(hormone_therapies, many=True).data

    def get_immunotherapies(self, obj):
        immunotherapies = obj.immunotherapy_set.all()
        return NestedImmunotherapySerializer(immunotherapies, many=True).data

    def get_radiation(self, obj):
        try:
            radiation = obj.radiation
            return NestedRadiationSerializer(radiation).data
        except Radiation.DoesNotExist:
            return None

    def get_surgery(self, obj):
        try:
            surgery = obj.surgery
            return NestedSurgerySerializer(surgery).data
        except Surgery.DoesNotExist:
            return None

    def get_followups(self, obj):
        followups = obj.followup_set.all()
        return NestedFollowUpSerializer(followups, many=True).data

    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    class Meta:
        model = Treatment
        fields = [
            "submitter_treatment_id",
            "is_primary_treatment",
            "treatment_start_date",
            "treatment_end_date",
            "treatment_setting",
            "treatment_intent",
            "days_per_cycle",
            "number_of_cycles",
            "response_to_treatment_criteria_method",
            "chemotherapies",
            "hormone_therapies",
            "immunotherapies",
            "radiation",
            "surgery",
            "followups",
            "biomarkers",
        ]


class NestedComorbiditySerializer(serializers.ModelSerializer):
    class Meta:
        model = Comorbidity
        fields = [
            "prior_malignancy",
            "laterality_of_prior_malignancy",
            "age_at_comorbidity_diagnosis",
            "comorbidity_type_code",
            "comorbidity_treatment_status",
            "comorbidity_treatment",
        ]


class NestedSampleRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleRegistration
        fields = [
            "submitter_sample_id",
            "gender",
            "sex_at_birth",
            "specimen_tissue_source",
            "tumour_normal_designation",
            "specimen_type",
            "sample_type",
        ]


class NestedChemotherapySerializer(serializers.ModelSerializer):
    class Meta:
        model = Chemotherapy
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id"]


class NestedHormoneTherapySerializer(serializers.ModelSerializer):
    class Meta:
        model = HormoneTherapy
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id"]


class NestedImmunotherapySerializer(serializers.ModelSerializer):
    class Meta:
        model = Immunotherapy
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id"]


class NestedRadiationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Radiation
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id"]


class NestedSurgerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Surgery
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id"]


class NestedFollowUpSerializer(serializers.ModelSerializer):

    biomarkers = serializers.SerializerMethodField()

    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    class Meta:
        model = FollowUp
        fields = [
            "date_of_followup",
            "lost_to_followup",
            "lost_to_followup_reason",
            "disease_status_at_followup",
            "relapse_type",
            "date_of_relapse",
            "method_of_progression_status",
            "anatomic_site_progression_or_recurrence",
            "recurrence_tumour_staging_system",
            "recurrence_t_category",
            "recurrence_n_category",
            "recurrence_m_category",
            "recurrence_stage_group",
            "biomarkers",
        ]


class NestedBiomarkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Biomarker
        fields = [
            "id",
            "test_interval",
            "psa_level",
            "ca125",
            "cea",
        ]
