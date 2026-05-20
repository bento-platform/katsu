import uuid

from bento_lib.auth.resources import build_resource
from bento_lib.discovery import DiscoveryConfig
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from rest_framework.request import Request as DrfRequest

from chord_metadata_service.chord import models as cm

from .exceptions import DiscoveryScopeException

__all__ = [
    "ValidatedDiscoveryScope",
    "get_discovery_scope",
    "get_request_discovery_scope",
    "INSTANCE_SCOPE",
]


class ValidatedDiscoveryScope:
    """
    Contains discovery scope information (i.e., project and dataset), as well as helper methods for accessing the
    scope's discovery configuration, Bento authorization resource representation, and IDs.

    Projects and datasets are passed into the constructor rather than IDs to allow discovery calculations *and* ensure
    the project/dataset actually exist before scope object creation, thus the name - the project and dataset's
    existences are pre-validated. Of course, a project/dataset could be deleted asynchronously elsewhere, which could
    result in this becoming invalid.
    """

    def __init__(self, project: cm.Project | None, dataset: cm.Dataset | cm.DatasetV2 | None):
        """
        Constructor for an already-validated discovery scope - i.e., since we are getting fed project/dataset instances
        rather than just string IDs, we know these objects exist at the time of construction.
        """

        self._project = project
        self._dataset = dataset

        # Additional validation
        if self._dataset:
            if not self._project:
                # - make sure we have project set if dataset is set
                raise DiscoveryScopeException(dataset_id=str(self._dataset.identifier))
            elif (project_id := self._project.identifier) != self._dataset.project_id:
                # - make sure the specified project ID matches the dataset's project ID
                raise DiscoveryScopeException(dataset_id=str(self._dataset.identifier), project_id=str(project_id))

        # We can cache the discovery property after the first call to the getter defined below, since instances of this
        # class MUST NOT be mutated.
        self._discovery: DiscoveryConfig | None = None  # If None, not cached yet

    def __eq__(self, other) -> bool:
        return isinstance(other, ValidatedDiscoveryScope) and all((
            (self.project_id is None and other.project_id is None) or self.project_id == other.project_id,
            (self.dataset_id is None and other.dataset_id is None) or self.dataset_id == other.dataset_id,
        ))

    @property
    def project_id(self) -> str | None:
        """
        String representation of the scope project's ID, if set.
        """
        return str(self._project.identifier) if self._project else None

    @property
    def dataset_id(self) -> str | None:
        """
        String representation of the scope dataset's ID, if set.
        """
        return str(self._dataset.identifier) if self._dataset else None

    def __repr__(self):
        return f"<ValidatedDiscoveryScope project={self.project_id} dataset={self.dataset_id}>"

    def __hash__(self):
        return hash(f"{self.project_id or ''}|{self.dataset_id or ''}")

    def _get_project_discovery_or_fallback(self) -> DiscoveryConfig:
        if self._project and (d := self._project.discovery):
            return d
        # fallback on global discovery config if project is not set or has None as discovery
        return settings.CONFIG_PUBLIC

    def _get_dataset_discovery_or_fallback(self) -> DiscoveryConfig:
        """
        Gets the dataset discovery configuration dictionary, or falls back to the project (and eventually instance) one.
        """
        if self._dataset and (d := self._dataset.discovery):
            return d
        # fallback on project discovery config (which in turn may fall back on instance / global discovery config)
        return self._get_project_discovery_or_fallback()

    @property
    def discovery(self) -> DiscoveryConfig:
        """
        Get the discovery configuration dictionary for this scope, properly handling falling back
        (dataset -> project -> instance) as required.
        """
        if self._discovery is not None:
            return self._discovery
        else:
            d = self._get_dataset_discovery_or_fallback()
            self._discovery = d
            return d

    def as_authz_resource(self, data_type: str | None = None) -> dict:
        """
        Build a Bento authorization system-compatible resource dictionary from this discovery scope.
        Optionally, a data type can be passed to narrow the resource to a specific data type.
        """
        return build_resource(self.project_id, self.dataset_id, data_type=data_type)


def _get_project_id_and_dataset_id_from_request(request: DrfRequest | HttpRequest) -> tuple[str | None, str | None]:
    return request.GET.get("project") or None, request.GET.get("dataset") or None


async def _get_project_by_id(project_id: str) -> cm.Project:
    return await cm.Project.objects.filter(identifier=project_id).aget()


async def get_discovery_scope(project_id: str | None, dataset_id: str | None) -> ValidatedDiscoveryScope:
    project: cm.Project | None = None
    dataset: cm.DatasetV2 | None = None

    try:
        if project_id:
            uuid.UUID(project_id)
        if dataset_id:
            uuid.UUID(dataset_id)
    except ValueError:
        # We don't want to facilitate log injection, so replace the true values with placeholders
        raise DiscoveryScopeException("<not UUID>", "<not UUID>")

    try:
        if dataset_id:
            qs = cm.DatasetV2.objects.filter(identifier=dataset_id)
            if project_id:
                # check if the dataset exists and belongs to the specified project if project ID is specified;
                # otherwise, infer the project from the dataset.
                qs = qs.filter(project_id=project_id)

            dataset = await qs.aget()
            project = await _get_project_by_id(dataset.project_id)

        elif project_id:
            project = await _get_project_by_id(project_id)

    except ObjectDoesNotExist:
        # We've already checked these are UUIDs, so they're fine to log
        raise DiscoveryScopeException(dataset_id, project_id)

    return ValidatedDiscoveryScope(project=project, dataset=dataset)


async def get_request_discovery_scope(request: DrfRequest) -> ValidatedDiscoveryScope:
    if (existing_scope := getattr(request, "discovery_scope", None)) is not None:
        return existing_scope  # already cached by a previous call to this function

    project_id, dataset_id = _get_project_id_and_dataset_id_from_request(request)
    scope = await get_discovery_scope(project_id, dataset_id)

    # hack: cache discovery scope for this request on the object itself as an arbitrary property for future calls to
    # this function, to avoid database request spam.
    request.discovery_scope = scope

    return scope


INSTANCE_SCOPE = ValidatedDiscoveryScope(None, None)  # re-usable singleton for instance-wide scope
