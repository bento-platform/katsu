from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.serializers import ListSerializer

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
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    Treatment,
)
from chord_metadata_service.mohpackets.serializers import (
    BiomarkerSerializer,
    ChemotherapySerializer,
    ComorbiditySerializer,
    DonorSerializer,
    ExposureSerializer,
    FollowUpSerializer,
    HormoneTherapySerializer,
    ImmunotherapySerializer,
    PrimaryDiagnosisSerializer,
    RadiationSerializer,
    SampleRegistrationSerializer,
    SpecimenSerializer,
    SurgerySerializer,
    TreatmentSerializer,
)

"""
    This module provides serializers for the Donor model and its related clinical data.
    All the other objects are nested under the Donor model, and foreign keys are
    replaced with nested objects. For instance, the DonorSerializer includes a
    nested PrimaryDiagnosisSerializer, which in turn includes a nested SpecimenSerializer, and so on.

    BioMarkers have unique relationships that require nesting at multiple levels.
"""


class NestedExposureSerializer(ExposureSerializer):
    class Meta:
        model = Exposure
        exclude = ["program_id", "submitter_donor_id", "id"]


class NestedComorbiditySerializer(ComorbiditySerializer):
    class Meta:
        model = Comorbidity
        exclude = ["program_id", "submitter_donor_id", "id"]


class NestedSampleRegistrationSerializer(SampleRegistrationSerializer):
    class Meta:
        model = SampleRegistration
        exclude = [
            "program_id",
            "submitter_donor_id",
            "submitter_specimen_id",
        ]


class NestedChemotherapySerializer(ChemotherapySerializer):
    class Meta:
        model = Chemotherapy
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id", "id"]


class NestedHormoneTherapySerializer(HormoneTherapySerializer):
    class Meta:
        model = HormoneTherapy
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id", "id"]


class NestedImmunotherapySerializer(ImmunotherapySerializer):
    class Meta:
        model = Immunotherapy
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id", "id"]


class NestedRadiationSerializer(RadiationSerializer):
    class Meta:
        model = Radiation
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id", "id"]


class NestedSurgerySerializer(SurgerySerializer):
    class Meta:
        model = Surgery
        exclude = ["program_id", "submitter_donor_id", "submitter_treatment_id", "id"]


class NestedBiomarkerSerializer(BiomarkerSerializer):
    class Meta:
        model = Biomarker
        exclude = [
            "program_id",
            "submitter_donor_id",
            "submitter_specimen_id",
            "submitter_primary_diagnosis_id",
            "submitter_treatment_id",
            "submitter_follow_up_id",
            "id"
        ]


class NestedFollowUpSerializer(FollowUpSerializer):
    biomarkers = serializers.SerializerMethodField()

    @extend_schema_field(ListSerializer(child=NestedBiomarkerSerializer()))
    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    class Meta:
        model = FollowUp
        fields = [
            "submitter_follow_up_id",
            "date_of_followup",
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
            "biomarkers",  # nested child
        ]


class NestedTreatmentSerializer(TreatmentSerializer):
    chemotherapies = serializers.SerializerMethodField()
    hormone_therapies = serializers.SerializerMethodField()
    immunotherapies = serializers.SerializerMethodField()
    radiation = serializers.SerializerMethodField()
    surgery = serializers.SerializerMethodField()
    followups = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()

    @extend_schema_field(ListSerializer(child=NestedChemotherapySerializer()))
    def get_chemotherapies(self, obj):
        chemotherapies = obj.chemotherapy_set.all()
        return NestedChemotherapySerializer(chemotherapies, many=True).data

    @extend_schema_field(ListSerializer(child=NestedHormoneTherapySerializer()))
    def get_hormone_therapies(self, obj):
        hormone_therapies = obj.hormonetherapy_set.all()
        return NestedHormoneTherapySerializer(hormone_therapies, many=True).data

    @extend_schema_field(ListSerializer(child=NestedImmunotherapySerializer()))
    def get_immunotherapies(self, obj):
        immunotherapies = obj.immunotherapy_set.all()
        return NestedImmunotherapySerializer(immunotherapies, many=True).data

    @extend_schema_field(NestedRadiationSerializer)
    def get_radiation(self, obj):
        try:
            radiation = obj.radiation
            return NestedRadiationSerializer(radiation).data
        except Radiation.DoesNotExist:
            return None

    @extend_schema_field(NestedSurgerySerializer)
    def get_surgery(self, obj):
        try:
            surgery = obj.surgery
            return NestedSurgerySerializer(surgery).data
        except Surgery.DoesNotExist:
            return None

    @extend_schema_field(ListSerializer(child=NestedFollowUpSerializer()))
    def get_followups(self, obj):
        followups = obj.followup_set.all()
        return NestedFollowUpSerializer(followups, many=True).data

    @extend_schema_field(ListSerializer(child=NestedBiomarkerSerializer()))
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
            "line_of_treatment",
            "status_of_treatment",
            "treatment_type",
            "response_to_treatment_criteria_method",
            "response_to_treatment",
            "chemotherapies",  # nested child
            "hormone_therapies",  # nested child
            "immunotherapies",  # nested child
            "radiation",  # nested child
            "surgery",  # nested child
            "followups",  # nested child
            "biomarkers",  # nested child
        ]


class NestedSpecimenSerializer(SpecimenSerializer):
    sample_registrations = serializers.SerializerMethodField()
    surgery = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()

    @extend_schema_field(ListSerializer(child=NestedSampleRegistrationSerializer()))
    def get_sample_registrations(self, obj):
        sample_registrations = obj.sampleregistration_set.all()
        return NestedSampleRegistrationSerializer(sample_registrations, many=True).data

    @extend_schema_field(NestedSurgerySerializer)
    def get_surgery(self, obj):
        try:
            surgery = obj.surgery
            return NestedSurgerySerializer(surgery).data
        except Surgery.DoesNotExist:
            return None

    @extend_schema_field(ListSerializer(child=NestedBiomarkerSerializer()))
    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    class Meta:
        model = Specimen
        fields = [
            "submitter_specimen_id",
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
            "specimen_processing",
            "specimen_laterality",
            "surgery",  # nested child
            "sample_registrations",  # nested child
            "biomarkers",  # nested child
        ]


class NestedPrimaryDiagnosisSerializer(PrimaryDiagnosisSerializer):
    specimens = serializers.SerializerMethodField()
    treatments = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()
    followups = serializers.SerializerMethodField()

    @extend_schema_field(ListSerializer(child=NestedSpecimenSerializer()))
    def get_specimens(self, obj):
        spicemen = obj.specimen_set.all()
        return NestedSpecimenSerializer(spicemen, many=True).data

    @extend_schema_field(ListSerializer(child=NestedTreatmentSerializer()))
    def get_treatments(self, obj):
        treatments = obj.treatment_set.all()
        return NestedTreatmentSerializer(treatments, many=True).data

    @extend_schema_field(ListSerializer(child=NestedBiomarkerSerializer()))
    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    @extend_schema_field(ListSerializer(child=NestedFollowUpSerializer()))
    def get_followups(self, obj):
        followups = obj.followup_set.all()
        return NestedFollowUpSerializer(followups, many=True).data

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
            "laterality",
            "specimens",  # nested child
            "treatments",  # nested child
            "biomarkers",  # nested child
            "followups",  # nested child
        ]


class DonorWithClinicalDataSerializer(DonorSerializer):
    primary_diagnoses = serializers.SerializerMethodField()
    comorbidities = serializers.SerializerMethodField()
    exposures = serializers.SerializerMethodField()
    biomarkers = serializers.SerializerMethodField()
    followups = serializers.SerializerMethodField()

    @extend_schema_field(ListSerializer(child=NestedPrimaryDiagnosisSerializer()))
    def get_primary_diagnoses(self, obj):
        primary_diagnoses = obj.primarydiagnosis_set.all()
        return NestedPrimaryDiagnosisSerializer(primary_diagnoses, many=True).data

    @extend_schema_field(ListSerializer(child=NestedComorbiditySerializer()))
    def get_comorbidities(self, obj):
        comorbidities = obj.comorbidity_set.all()
        return NestedComorbiditySerializer(comorbidities, many=True).data

    @extend_schema_field(ListSerializer(child=NestedExposureSerializer()))
    def get_exposures(self, obj):
        exposures = obj.exposure_set.all()
        return NestedExposureSerializer(exposures, many=True).data

    @extend_schema_field(ListSerializer(child=NestedBiomarkerSerializer()))
    def get_biomarkers(self, obj):
        biomarkers = obj.biomarker_set.all()
        return NestedBiomarkerSerializer(biomarkers, many=True).data

    @extend_schema_field(ListSerializer(child=NestedFollowUpSerializer()))
    def get_followups(self, obj):
        followups = obj.followup_set.all()
        return NestedFollowUpSerializer(followups, many=True).data

    class Meta:
        model = Donor
        fields = [
            "submitter_donor_id",
            "program_id",
            "lost_to_followup_after_clinical_event_identifier",
            "lost_to_followup_reason",
            "date_alive_after_lost_to_followup",
            "is_deceased",
            "cause_of_death",
            "date_of_birth",
            "date_of_death",
            "gender",
            "sex_at_birth",
            "primary_site",
            "primary_diagnoses",  # nested child
            "comorbidities",  # nested child
            "exposures",  # nested child
            "biomarkers",  # nested child
            "followups",  # nested child
        ]
