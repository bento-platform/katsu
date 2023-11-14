import os
from functools import wraps
from http import HTTPStatus
from typing import Dict, List

from django.apps import apps
from django.db.models import Prefetch, Q
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from ninja import Query, Router
from ninja.pagination import PageNumberPagination, RouterPaginated, paginate
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from chord_metadata_service.mohpackets.api.api_base import (
    BaseBiomarkerViewSet,
    BaseChemotherapyViewSet,
    BaseComorbidityViewSet,
    BaseDonorViewSet,
    BaseExposureViewSet,
    BaseFollowUpViewSet,
    BaseHormoneTherapyViewSet,
    BaseImmunotherapyViewSet,
    BasePrimaryDiagnosisViewSet,
    BaseProgramViewSet,
    BaseRadiationViewSet,
    BaseSampleRegistrationViewSet,
    BaseSpecimenViewSet,
    BaseSurgeryViewSet,
    BaseTreatmentViewSet,
)
from chord_metadata_service.mohpackets.authentication import (
    LocalAuthentication,
    TokenAuthentication,
)
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
from chord_metadata_service.mohpackets.pagination import (
    CustomPagination,
    CustomRouterPaginated,
    SmallResultsSetPagination,
    StandardResultsSetPagination,
)
from chord_metadata_service.mohpackets.schema.schema import (
    BiomarkerFilterSchema,
    BiomarkerModelSchema,
    ChemotherapyFilterSchema,
    ChemotherapyModelSchema,
    ComorbidityFilterSchema,
    ComorbidityModelSchema,
    DonorFilterSchema,
    DonorModelSchema,
    DonorWithClinicalDataFilterSchema,
    DonorWithClinicalDataSchema,
    ExposureFilterSchema,
    ExposureModelSchema,
    FollowUpFilterSchema,
    FollowUpModelSchema,
    HormoneTherapyFilterSchema,
    HormoneTherapyModelSchema,
    ImmunotherapyFilterSchema,
    ImmunotherapyModelSchema,
    PrimaryDiagnosisFilterSchema,
    PrimaryDiagnosisModelSchema,
    ProgramFilterSchema,
    ProgramModelSchema,
    RadiationFilterSchema,
    RadiationModelSchema,
    SampleRegistrationFilterSchema,
    SampleRegistrationModelSchema,
    SpecimenFilterSchema,
    SpecimenModelSchema,
    SurgeryFilterSchema,
    SurgeryModelSchema,
    TreatmentFilterSchema,
    TreatmentModelSchema,
)
from chord_metadata_service.mohpackets.serializers_nested import (
    DonorWithClinicalDataSerializer,
)

"""
    This module inheriting from the base views and adding the authorized mixin,
    which returns the objects related to the datasets that the user is authorized to see.
"""


##########################################
#                                        #
#           HELPER FUNCTIONS             #
#                                        #
##########################################


class AuthorizedMixin:
    """
    This mixin should be used for viewsets that need to restrict access.

    The authentication classes are set based on the `DJANGO_SETTINGS_MODULE`.
    If the env is "dev" or "prod", the `TokenAuthentication` class is
    used. Otherwise, the `LocalAuthentication` class is used.

    Methods
    -------
    get_queryset()
        Returns a filtered queryset that includes only the objects that the user is
        authorized to see based on their permissions.
    """

    pagination_class = StandardResultsSetPagination
    settings_module = os.environ.get("DJANGO_SETTINGS_MODULE")
    auth_methods = []
    # Use jwt token auth in prod/dev environment
    if "dev" in settings_module or "prod" in settings_module:
        auth_methods.append(TokenAuthentication)
    else:
        auth_methods.append(LocalAuthentication)
    authentication_classes = auth_methods

    def get_queryset(self):
        authorized_datasets = self.request.authorized_datasets
        filtered_queryset = (
            super().get_queryset().filter(program_id__in=authorized_datasets)
        )
        return filtered_queryset


##############################################
#                                            #
#           AUTHORIZED API VIEWS             #
#                                            #
##############################################


class AuthorizedProgramViewSet(
    AuthorizedMixin, BaseProgramViewSet, mixins.DestroyModelMixin
):
    def destroy(self, request, pk=None):
        """
        Delete a program, must be an admin that can access all programs
        """
        self.queryset = Program.objects.all()
        try:
            dataset = Program.objects.get(pk=pk)
            dataset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Program.DoesNotExist:
            return Response(
                {"detail": "Program matching query does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )


class AuthorizedDonorViewSet(AuthorizedMixin, BaseDonorViewSet):
    """
    Retrieves a list of authorized donors.
    """

    pass


class AuthorizedSpecimenViewSet(AuthorizedMixin, BaseSpecimenViewSet):
    """
    Retrieves a list of authorized specimens.
    """

    pass


class AuthorizedSampleRegistrationViewSet(
    AuthorizedMixin, BaseSampleRegistrationViewSet
):
    """
    Retrieves a list of authorized sample registrations.
    """

    pass


class AuthorizedPrimaryDiagnosisViewSet(AuthorizedMixin, BasePrimaryDiagnosisViewSet):
    """
    Retrieves a list of authorized primary diagnosises.
    """

    pass


class AuthorizedTreatmentViewSet(AuthorizedMixin, BaseTreatmentViewSet):
    """
    Retrieves a list of authorized treatments.
    """

    pass


class AuthorizedChemotherapyViewSet(AuthorizedMixin, BaseChemotherapyViewSet):
    """
    Retrieves a list of authorized chemotherapies.
    """

    pass


class AuthorizedHormoneTherapyViewSet(AuthorizedMixin, BaseHormoneTherapyViewSet):
    """
    Retrieves a list of authorized hormone therapies.
    """

    pass


class AuthorizedRadiationViewSet(AuthorizedMixin, BaseRadiationViewSet):
    """
    Retrieves a list of authorized radiations.
    """

    pass


class AuthorizedImmunotherapyViewSet(AuthorizedMixin, BaseImmunotherapyViewSet):
    """
    Retrieves a list of authorized immuno therapies.
    """

    pass


class AuthorizedSurgeryViewSet(AuthorizedMixin, BaseSurgeryViewSet):
    """
    Retrieves a list of authorized surgeries.
    """

    pass


class AuthorizedFollowUpViewSet(AuthorizedMixin, BaseFollowUpViewSet):
    """
    Retrieves a list of authorized follow ups.
    """

    pass


class AuthorizedBiomarkerViewSet(AuthorizedMixin, BaseBiomarkerViewSet):
    """
    Retrieves a list of authorized biomarkers.
    """

    pass


class AuthorizedComorbidityViewSet(AuthorizedMixin, BaseComorbidityViewSet):
    """
    Retrieves a list of authorized comorbidities.
    """

    pass


class AuthorizedExposureViewSet(AuthorizedMixin, BaseExposureViewSet):
    """
    Retrieves a list of authorized exposures.
    """

    pass


###############################################
#                                             #
#           CUSTOM API ENDPOINTS              #
#                                             #
###############################################


class OnDemandViewSet(AuthorizedMixin, viewsets.ViewSet):
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="model",
                description="Model name",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="include_fields",
                description="Comma-separated list of included fields",
                required=True,
                type=str,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={201: OpenApiTypes.STR},
    )
    def list(self, request):
        model_name = request.query_params.get("model")
        include_fields = request.query_params.getlist("include_fields")

        try:
            model = apps.get_model("mohpackets", model_name)
        except LookupError:
            return Response(
                {"error": f"Model '{model_name}' not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = model.objects.values(*include_fields)

        return Response(queryset)


@extend_schema_view(
    list=extend_schema(
        description="Retrieves a list of authorized Donor with clinical data."
    )
)
class AuthorizedDonorWithClinicalDataViewSet(AuthorizedMixin, BaseDonorViewSet):
    """
    This viewset provides access to Donor model and its related clinical data.
    It uses the DonorWithClinicalDataSerializer for serialization.

    The viewset pre-fetches related objects using the `prefetch_related` method
    to minimize database queries. This ensures that all the related objects are
    available in a single database query, improving the performance of the viewset.
    """

    serializer_class = DonorWithClinicalDataSerializer
    pagination_class = SmallResultsSetPagination

    donor_followups_prefetch = Prefetch(
        "followup_set",
        queryset=FollowUp.objects.filter(
            submitter_primary_diagnosis_id__isnull=True,
            submitter_treatment_id__isnull=True,
        ),
    )

    primary_diagnosis_followups_prefetch = Prefetch(
        "primarydiagnosis_set__followup_set",
        queryset=FollowUp.objects.filter(
            submitter_primary_diagnosis_id__isnull=False,
            submitter_treatment_id__isnull=True,
        ),
    )

    queryset = Donor.objects.prefetch_related(
        donor_followups_prefetch,
        primary_diagnosis_followups_prefetch,
        "biomarker_set",
        "comorbidity_set",
        "exposure_set",
        "primarydiagnosis_set__treatment_set__chemotherapy_set",
        "primarydiagnosis_set__treatment_set__hormonetherapy_set",
        "primarydiagnosis_set__treatment_set__immunotherapy_set",
        "primarydiagnosis_set__treatment_set__radiation_set",
        "primarydiagnosis_set__treatment_set__surgery_set",
        "primarydiagnosis_set__treatment_set__followup_set",
        "primarydiagnosis_set__specimen_set__sampleregistration_set",
    ).all()


# =============================================================================
router = CustomRouterPaginated()


# ==============================================================================
# Helper tools
# ==============================================================================
def require_program_donor_together(func):
    @wraps(func)
    def wrapper(request, filters):
        if (filters.program_id and not filters.submitter_donor_id) or (
            filters.submitter_donor_id and not filters.program_id
        ):
            error_message = {
                "error": "Either both program_id and submitter_donor_id are required, or none"
            }
            return HTTPStatus.BAD_REQUEST, error_message

        return func(request, filters)

    return wrapper


# ==============================================================================
# Delete
# ==============================================================================
@router.delete(
    "/program/{program_id}",
    response={204: None, 404: Dict[str, str]},
)
def delete_program(request, program_id: str):
    try:
        dataset = Program.objects.get(pk=program_id)
        dataset.delete()
        return HTTPStatus.NO_CONTENT, None
    except Program.DoesNotExist:
        return HTTPStatus.NOT_FOUND, {"error": "Program matching query does not exist"}


# ==============================================================================
# Donor with clinical data
# ==============================================================================
@router.get(
    "/donor_with_clinical_data/",
    response={200: DonorWithClinicalDataSchema, 404: Dict[str, str]},
)
def get_donor_with_clinical_data(
    request, filters: Query[DonorWithClinicalDataFilterSchema]
):
    donor_followups_prefetch = Prefetch(
        "followup_set",
        queryset=FollowUp.objects.filter(
            submitter_primary_diagnosis_id__isnull=True,
            submitter_treatment_id__isnull=True,
        ),
    )

    primary_diagnosis_followups_prefetch = Prefetch(
        "primarydiagnosis_set__followup_set",
        queryset=FollowUp.objects.filter(
            submitter_primary_diagnosis_id__isnull=False,
            submitter_treatment_id__isnull=True,
        ),
    )
    queryset = Donor.objects.prefetch_related(
        donor_followups_prefetch,
        primary_diagnosis_followups_prefetch,
        "biomarker_set",
        "comorbidity_set",
        "exposure_set",
        "primarydiagnosis_set__treatment_set__chemotherapy_set",
        "primarydiagnosis_set__treatment_set__hormonetherapy_set",
        "primarydiagnosis_set__treatment_set__immunotherapy_set",
        "primarydiagnosis_set__treatment_set__radiation_set",
        "primarydiagnosis_set__treatment_set__surgery_set",
        "primarydiagnosis_set__treatment_set__followup_set",
        "primarydiagnosis_set__specimen_set__sampleregistration_set",
    ).all()
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q = filters.get_filter_expression()
    result = queryset.filter(q).first()
    if result:
        return result
    else:
        return HTTPStatus.NOT_FOUND, {
            "error": "Donor matching query does not exist or inaccessible"
        }


# ==============================================================================
# Authorized
# ==============================================================================
@router.get(
    "/programs/",
    response=List[ProgramModelSchema],
)
def list_programs(request, filters: Query[ProgramFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Program.objects.filter(q)


@router.get(
    "/donors/",
    response=List[DonorModelSchema],
)
@require_program_donor_together
def list_donors(request, filters: Query[DonorFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Donor.objects.filter(q)


@router.get(
    "/primary_diagnoses/",
    response=List[PrimaryDiagnosisModelSchema],
)
@require_program_donor_together
def list_primary_diagnoses(request, filters: Query[PrimaryDiagnosisFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return PrimaryDiagnosis.objects.filter(q)


@router.get(
    "/biomarkers/",
    response=List[BiomarkerModelSchema],
)
@require_program_donor_together
def list_biomarkers(request, filters: Query[BiomarkerFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Biomarker.objects.filter(q)


@router.get(
    "/chemotherapies/",
    response=List[ChemotherapyModelSchema],
)
@require_program_donor_together
def list_chemotherapies(request, filters: Query[ChemotherapyFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Chemotherapy.objects.filter(q)


@router.get(
    "/comorbidities/",
    response=List[ComorbidityModelSchema],
)
@require_program_donor_together
def list_comorbidities(request, filters: Query[ComorbidityFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Comorbidity.objects.filter(q)


@router.get(
    "/exposures/",
    response={200: List[ExposureModelSchema], 400: Dict[str, str]},
)
@require_program_donor_together
def list_exposures(request, filters: Query[ExposureFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Exposure.objects.filter(q)


@router.get(
    "/followups/",
    response=List[FollowUpModelSchema],
)
@require_program_donor_together
def list_followups(request, filters: Query[FollowUpFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return FollowUp.objects.filter(q)


@router.get(
    "/hormone_therapies/",
    response=List[HormoneTherapyModelSchema],
)
@require_program_donor_together
def list_hormone_therapies(request, filters: Query[HormoneTherapyFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return HormoneTherapy.objects.filter(q)


@router.get(
    "/immunotherapies/",
    response=List[ImmunotherapyModelSchema],
)
@require_program_donor_together
def list_immunotherapies(request, filters: Query[ImmunotherapyFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Immunotherapy.objects.filter(q)


@router.get(
    "/radiations/",
    response=List[RadiationModelSchema],
)
@require_program_donor_together
def list_radiations(request, filters: Query[RadiationFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Radiation.objects.filter(q)


@router.get(
    "/sample_registrations/",
    response=List[SampleRegistrationModelSchema],
)
@require_program_donor_together
def list_sample_registrations(request, filters: Query[SampleRegistrationFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return SampleRegistration.objects.filter(q)


@router.get(
    "/specimens/",
    response=List[SpecimenModelSchema],
)
@require_program_donor_together
def list_specimens(request, filters: Query[SpecimenFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Specimen.objects.filter(q)


@router.get(
    "/surgeries/",
    response=List[SurgeryModelSchema],
)
@require_program_donor_together
def list_surgeries(request, filters: Query[SurgeryFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Surgery.objects.filter(q)


@router.get(
    "/treatments/",
    response=List[TreatmentModelSchema],
)
@require_program_donor_together
def list_treatments(request, filters: Query[TreatmentFilterSchema]):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Treatment.objects.filter(q)
