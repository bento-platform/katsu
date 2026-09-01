from typing import Type

from bento_lib.discovery import DiscoveryEntity
from dataclasses import dataclass
from django.db.models import QuerySet, ManyToManyField, ManyToOneRel

from ..model_lookups import DISCOVERY_ENTITY_NAMES_TO_MODEL
from ..scopeable_model import BaseScopeableModel
from ..types import AnyFieldDefinition
from .normalize import normalize_field_path_true_model
from .resolve import resolve_queryset_entity_path_from_field_path
from .utils import field_path_to_django_mapping

__all__ = [
    "DiscoveryFieldSubquery",
    "get_field_django_mapping_and_queried_entity",
    "get_field_django_mapping",
]


@dataclass
class DiscoveryFieldSubquery:
    """
    Data class representing a spec for executing an Exists(...) subquery across a many-to-many or many-to-one Django
    relation boundary.
    """
    queryset: QuerySet  # queryset for inner Exists
    inner_field: str  # queried field, rewritten for the inner queryset
    related_field: str


def get_field_django_mapping_and_queried_entity(
    queryset_entity: DiscoveryEntity,
    field_props: AnyFieldDefinition,
    force_through_phenopackets: bool = False,
    resolve_ontology_class: bool = False,
) -> tuple[str, DiscoveryFieldSubquery | None, DiscoveryEntity]:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns a tuple of (
        the Django string representation of the field for this object relative to the queryset entity,
        a specification for executing an Exists(...) subquery IF crossing a many-to-many or many-to-one boundary,
        the queried entity name,
    )
    Can raise django.core.exceptions.FieldDoesNotExist if the field mapping does not correspond to a real model field.
    """

    entity_name, field_path = normalize_field_path_true_model(*field_props.get_entity_and_field_path())

    model: Type[BaseScopeableModel] | None = DISCOVERY_ENTITY_NAMES_TO_MODEL.get(entity_name)
    if model is None:
        msg = f"Accessing field on model {entity_name} not implemented"
        raise NotImplementedError(msg)

    resolved_field_path = resolve_queryset_entity_path_from_field_path(
        queryset_entity, entity_name, field_path, force_through_phenopackets
    ) + (("id",) if field_props.datatype == "ontology-class" and resolve_ontology_class else ())

    subquery: DiscoveryFieldSubquery | None = None

    if field_path:
        field_obj = DISCOVERY_ENTITY_NAMES_TO_MODEL[queryset_entity]._meta.get_field(resolved_field_path[0])
        # If we have a many-to-many field or a many-to-one (from a foreign key) relationship, we need to do filtering
        # based on an Exists subquery rather than an inner join, since the latter prevents us from getting correct
        # counts/stats (Django executes an inner join even when we don't want one, basically).
        # For example, instead of getting the counts for ALL diseases with phenopackets that have "breast cancer" as a
        # disease (i.e., a distribution with the *other* diseases breast cancer patients may have as well), we ONLY get
        # inner-joined records for matching Disease models if we do this naively, when instead we want what was
        # described: all disease counts for phenopackets with breast cancer.
        # To solve this, we do an Exists subquery to check if we have at least one matching object from the other side
        # of the m2m/many-to-one relation which matches the field query (which as been rewritten to be valid for
        # the model referred to in the relation rather than the queryset model.)
        if isinstance(field_obj, ManyToManyField | ManyToOneRel):
            if isinstance(field_obj, ManyToManyField):
                rel = field_obj.remote_field.accessor_name
            else:  # isinstance(field_obj, ManyToOneRel)
                rel = field_obj.field.name
            subquery = DiscoveryFieldSubquery(
                queryset=field_obj.related_model.objects.all(),
                inner_field=field_path_to_django_mapping(resolved_field_path[1:]),
                related_field=rel,
            )

    return field_path_to_django_mapping(resolved_field_path), subquery, entity_name


def get_field_django_mapping(
    queryset_entity: DiscoveryEntity, field_props: AnyFieldDefinition, resolve_ontology_class: bool = False
) -> str:
    """
    Parses a path-like string representing an ORM such as "individual/extra_properties/date_of_consent"
    where the first crumb represents the object in the DB model, and the next ones
    are the field with their possible joins through tables relations.
    Returns the Django string representation of the field for this object.
    """
    return get_field_django_mapping_and_queried_entity(queryset_entity, field_props, resolve_ontology_class)[0]
