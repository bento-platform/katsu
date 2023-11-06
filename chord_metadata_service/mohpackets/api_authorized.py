import os
from typing import List, Optional
from uuid import UUID, uuid4

import orjson
from django.apps import apps
from django.db.models import Count, Model, Prefetch, Q
from django.http import HttpResponse
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)
from ninja import Field, FilterSchema, ModelSchema, NinjaAPI, Query, Router, Schema
from ninja.pagination import PageNumberPagination, paginate
from ninja.parser import Parser
from ninja.renderers import BaseRenderer
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from chord_metadata_service.mohpackets.api_base import (
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
    SmallResultsSetPagination,
    StandardResultsSetPagination,
)
from chord_metadata_service.mohpackets.schema import (
    DonorFilterSchema,
    DonorSchema,
    DonorWithClinicalDataSchema,
)
from chord_metadata_service.mohpackets.serializers_nested import (
    DonorWithClinicalDataSerializer,
)

# class ORJSONRenderer(BaseRenderer):
#     media_type = "application/json"

#     def render(self, request, data, *, response_status):
#         return orjson.dumps(data)


# class ORJSONParser(Parser):
#     def parse_body(self, request):
#         return orjson.loads(request.body)


# api = NinjaAPI(renderer=ORJSONRenderer(), parser=ORJSONParser())

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

    # queryset = Donor.objects.all()


# from typing import List


# class ExposureSchema(ModelSchema):
#     class Config:
#         model = Exposure
#         model_fields = "__all__"


# class ComorbiditySchema(ModelSchema):
#     class Config:
#         model = Comorbidity
#         model_fields = "__all__"


# class SampleRegistrationSchema(ModelSchema):
#     class Config:
#         model = SampleRegistration
#         model_fields = "__all__"


# class SpecimenSchema(ModelSchema):
#     samplesregistrations: List[SampleRegistrationSchema] = Field(
#         ..., alias="sampleregistration_set"
#     )

#     class Config:
#         model = Specimen
#         model_fields = "__all__"


# class ChemotherapySchema(ModelSchema):
#     class Config:
#         model = Chemotherapy
#         model_fields = "__all__"


# class ImmunotherapySchema(ModelSchema):
#     class Config:
#         model = Immunotherapy
#         model_fields = "__all__"


# class HormoneTherapySchema(ModelSchema):
#     class Config:
#         model = HormoneTherapy
#         model_fields = "__all__"


# class RadiationSchema(ModelSchema):
#     class Config:
#         model = Radiation
#         model_fields = "__all__"


# class SurgerySchema(ModelSchema):
#     class Config:
#         model = Surgery
#         model_fields = "__all__"


# class FollowUpSchema(Schema):
#     class Config:
#         model = FollowUp
#         model_fields = "__all__"


# class TreatmentSchema(ModelSchema):
#     chemotherapies: List[ChemotherapySchema] = Field(..., alias="chemotherapy_set")
#     immunotherapies: List[ImmunotherapySchema] = Field(..., alias="immunotherapy_set")
#     hormonetherapies: List[HormoneTherapySchema] = Field(
#         ..., alias="hormonetherapy_set"
#     )
#     radiations: List[RadiationSchema] = Field(..., alias="radiation_set")
#     surgeries: List[SurgerySchema] = Field(..., alias="surgery_set")
#     followups: List[FollowUpSchema] = Field(..., alias="followup_set")

#     class Config:
#         model = Treatment
#         model_fields = "__all__"


# class PrimaryDiagnosisSchema(ModelSchema):
#     specimens: List[SpecimenSchema] = Field(..., alias="specimen_set")
#     treatments: List[TreatmentSchema] = Field(..., alias="treatment_set")
#     followups: List[FollowUpSchema] = Field(..., alias="followup_set")

#     class Config:
#         model = PrimaryDiagnosis
#         model_fields = "__all__"


# class BiomarkerSchema(ModelSchema):
#     class Config:
#         model = Biomarker
#         model_fields = "__all__"


# class DonorSchema(ModelSchema):
#     comorbidities: List[ComorbiditySchema] = Field(..., alias="comorbidity_set")
#     exposures: List[ExposureSchema] = Field(..., alias="exposure_set")
#     biomarkers: List[BiomarkerSchema] = Field(..., alias="biomarker_set")
#     primarydiagnosis: List[PrimaryDiagnosisSchema] = Field(
#         ..., alias="primarydiagnosis_set"
#     )
#     followups: List[FollowUpSchema] = Field(..., alias="followup_set")

#     class Config:
#         model = Donor
#         model_fields = "__all__"


# @api.get("/ninja_donors", response=List[DonorSchema])
# @paginate(PageNumberPagination, page_size=10)
# def tasks(request):
#     # queryset = Donor.objects.all()

#     donor_followups_prefetch = Prefetch(
#         "followup_set",
#         queryset=FollowUp.objects.filter(
#             submitter_primary_diagnosis_id__isnull=True,
#             submitter_treatment_id__isnull=True,
#         ),
#     )

#     primary_diagnosis_followups_prefetch = Prefetch(
#         "primarydiagnosis_set__followup_set",
#         queryset=FollowUp.objects.filter(
#             submitter_primary_diagnosis_id__isnull=False,
#             submitter_treatment_id__isnull=True,
#         ),
#     )
#     queryset = Donor.objects.prefetch_related(
#         donor_followups_prefetch,
#         primary_diagnosis_followups_prefetch,
#         "biomarker_set",
#         "comorbidity_set",
#         "exposure_set",
#         "primarydiagnosis_set__treatment_set__chemotherapy_set",
#         "primarydiagnosis_set__treatment_set__hormonetherapy_set",
#         "primarydiagnosis_set__treatment_set__immunotherapy_set",
#         "primarydiagnosis_set__treatment_set__radiation_set",
#         "primarydiagnosis_set__treatment_set__surgery_set",
#         "primarydiagnosis_set__treatment_set__followup_set",
#         "primarydiagnosis_set__specimen_set__sampleregistration_set",
#     ).all()
#     return list(queryset)


# =============================================================================
router = Router()


@router.get("/ninja_donors", response=List[DonorWithClinicalDataSchema])
@paginate(PageNumberPagination, page_size=10)
def tasks(request):
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
    return list(queryset)


@router.get(
    "/donors/",
    response=List[DonorSchema],
)
def list_donors(request, filters: DonorFilterSchema = Query(...)):
    authorized_datasets = request.authorized_datasets
    q = Q(program_id__in=authorized_datasets)
    q &= filters.get_filter_expression()
    return Donor.objects.filter(q)
