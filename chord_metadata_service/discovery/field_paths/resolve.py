from bento_lib.discovery import DiscoveryEntity
from ..exceptions import DiscoveryFilterRewriteException
from .normalize import normalize_field_path_true_model
from .utils import field_path_to_django_mapping

__all__ = [
    "resolve_queryset_entity_path_from_field_path",
    "resolve_filter_mapping_to_queryset_model",
]


def _resolve_filter_mapping_to_queryset_model_inner_2(
    queryset_entity: DiscoveryEntity,
    field_entity: DiscoveryEntity,
    field_path: tuple[str, ...],
    force_through_phenopackets: bool,
) -> tuple[str, ...]:
    """
    Given a goal (queryset) model name and a current (field) model name, rewrite a path to a field from the field model
    name to the goal queryset model name.
    Currently, this is used as an inner function for resolve_filter_mapping_to_queryset_model, but may have more broad
    use for rewriting field paths without converting them to Django form.
    The force_through_phenopackets param forces relationships that have "shortcuts" (individuals<->biosamples, mostly)
    to be related THROUGH phenopackets.
    """

    if queryset_entity == field_entity:
        norm_entity, norm_path = normalize_field_path_true_model(field_entity, field_path)
        if norm_entity != field_entity:
            # We normalized to a different entity, so we need to do further resolving to get the simplest lookup
            # TODO: verify this cannot infinite loop with, e.g., force_through_phenopackets.
            return _resolve_filter_mapping_to_queryset_model_inner_2(
                queryset_entity, norm_entity, norm_path, force_through_phenopackets
            )
        return norm_path

    exc = DiscoveryFilterRewriteException(f"cannot map field model {field_entity} to filtering model {queryset_entity}")

    match (queryset_entity, field_entity):
        #  - Phenopackets <-> Individuals
        case ("individual", "phenopacket"):  # re-writing the latter to the former
            if field_path[:1] == ("subject",):  # also conveniently handles the falsey case of field_path == ()
                return field_path[1:]
            if field_path[:1] == ("biosamples",) and not force_through_phenopackets:
                # we have biosamples related managers on both individuals and phenopackets
                # NOTE: this is a bit janky - we don't necessarily have individuals for all phenopackets, so this can
                # return something different. We're relying on a later join.
                return field_path
            return "phenopackets", *field_path
        case ("phenopacket", "individual"):
            if field_path[:1] == ("phenopackets",):  # also conveniently handles the falsey case of field_path == ()
                return field_path[1:]
            # If we have field_path[0] == biosamples, this one is subtle because not all phenopackets have individuals.
            # So we leave this as off of subject, although perhaps we could rely on joins to clear this up downstream...
            return "subject", *field_path
        #  - Phenopackets -> nested
        case ("phenopacket", "biosample"):  # re-writing the latter to the former
            return "biosamples", *field_path
        case ("phenopacket", "experiment"):
            return "biosamples", "experiments", *field_path
        case ("phenopacket", "experiment_result"):
            return "biosamples", "experiments", "experiment_results", *field_path
        #  - Individuals -> nested
        case ("individual", "biosample"):  # re-writing the latter to the former
            if force_through_phenopackets:
                return "phenopackets", "biosamples", *field_path
            return "biosamples", *field_path
        case ("individual", "experiment"):
            if force_through_phenopackets:
                return "phenopackets", "biosamples", "experiments", *field_path
            return "biosamples", "experiments", *field_path
        case ("individual", "experiment_result"):
            b = ("biosamples", "experiments", "experiment_results", *field_path)
            if force_through_phenopackets:
                return "phenopackets", *b
            return b
        #  - Biosamples -> nested
        case ("biosample", "experiment"):  # re-writing the latter to the former
            return "experiments", *field_path
        case ("biosample", "experiment_result"):
            return "experiments", "experiment_results", *field_path
        #  - Experiments -> nested
        case ("experiment", "experiment_result"):
            return "experiment_results", *field_path
        # --------------------------------------------------------------------------------------------------------------
        case ("biosample", "phenopacket"):  # re-writing the latter to the former
            # If we are accessing a biosample field through a phenopacket path, we can remap it to a biosample queryset
            # model. Otherwise, we go "backwards" out to phenopackets.
            if field_path[:1] == ("biosamples",):
                return field_path[1:]
            if field_path[:1] == ("subject",):
                if force_through_phenopackets:
                    return "phenopackets", *field_path
                else:
                    return "individual", *field_path[1:]
            return "phenopackets", *field_path
        case ("biosample", "individual"):  # re-writing the latter to the former
            if field_path[:2] == ("phenopackets", "biosamples"):
                return field_path[2:]
            elif field_path[:1] == ("biosamples",):
                return field_path[1:]
            if force_through_phenopackets:
                return "phenopackets", "subject", *field_path
            return "individual", *field_path
        case ("experiment", "biosample"):  # also handles (experiment, phenopacket) via recursion below
            # experiment: old path, prior to related_name; experiments: after
            if field_path[:1] in (
                ("experiment",),  # TODO: remove in future version
                ("experiments",),
            ):  # use slice to handle field_path == ()
                return field_path[1:]
            return "biosample", *field_path
        case ("experiment", "phenopacket"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:2] in {
                ("biosamples", "experiment"),  # TODO: remove in future version
                ("biosamples", "experiments"),
            }:
                return field_path[2:]
            if (not force_through_phenopackets) and field_path[:1] == ("subject",):
                # We can skip a hop if:
                #   a) we're not forced through phenopackets, and
                #   b) we're mapping to experiment --> ... --> individual:
                return "biosample", "individual", *field_path[1:]
            if field_path[:1] == ("biosamples",):
                return "biosample", *field_path[1:]
            return "biosample", "phenopackets", *field_path
        case ("experiment", "individual"):  # re-writing the latter to the former
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:3] in {
                ("phenopackets", "biosamples", "experiment"),  # TODO: remove in future version
                ("phenopackets", "biosamples", "experiments"),
            }:
                return field_path[3:]
            # Alternate path which skips phenopackets
            if field_path[:2] in {
                ("biosamples", "experiment"),  # TODO: remove in future version
                ("biosamples", "experiments"),
            }:
                return field_path[2:]
            if force_through_phenopackets:
                return "biosample", "phenopackets", "subject", *field_path
            # Shorter path than going through phenopackets, although this might lead to wacky results if not all
            # individuals are part of phenopackets.
            return "biosample", "individual", *field_path
        case ("experiment_result", "phenopacket"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:3] in {
                ("biosamples", "experiment", "experiment_results"),  # TODO: remove in future version
                ("biosamples", "experiments", "experiment_results"),
            }:
                return field_path[3:]
            if (not force_through_phenopackets) and field_path[:1] == ("subject",):
                return "experiments", "biosample", "individual", *field_path[1:]
            return "experiments", "biosample", "phenopackets", *field_path
        case ("experiment_result", "individual"):
            # biosamples__experiment: old path, prior to related_name; biosamples__experiments: after
            if field_path[:4] in {
                ("phenopackets", "biosamples", "experiment", "experiment_results"),  # TODO: remove in future version
                ("phenopackets", "biosamples", "experiments", "experiment_results"),
            }:
                return field_path[4:]
            # Alternate path which skips phenopackets
            if not force_through_phenopackets and field_path[:3] in {
                ("biosamples", "experiment", "experiment_results"),  # TODO: remove in future version
                ("biosamples", "experiments", "experiment_results"),
            }:
                return field_path[3:]
            if force_through_phenopackets:
                return "experiments", "biosample", "phenopackets", "subject", *field_path
            return "experiments", "biosample", "individual", *field_path
        case ("experiment_result", "biosample"):
            # experiment: old path, prior to related_name; experiments: after
            if field_path[:2] in {
                ("experiment", "experiment_results"),  # TODO: remove in future version
                ("experiments", "experiment_results"),
            }:
                return field_path[2:]
            return "experiments", "biosample", *field_path
        case ("experiment_result", "experiment"):
            if field_path[:1] == ("experiment_results",):
                return field_path[1:]
            return "experiments", *field_path
        # --------------------------------------------------------------------------------------------------------------
        case _:
            raise exc


def resolve_queryset_entity_path_from_field_path(
    queryset_entity: DiscoveryEntity,
    field_entity: DiscoveryEntity,
    field_path: tuple[str, ...],
    force_through_phenopackets: bool,
) -> tuple[str, ...]:
    """
    Small wrapper around _resolve_filter_mapping_to_queryset_model_inner_2, to basically repeatedly simplify the
    resolved path until we have the smallest form we can achieve (useful only for edge cases where we might go, e.g.,
    from phenopackets -> biosamples -> phenopackets -> biosamples -> sampled_tissue
    to phenopackets -> biosamples -> sampled_tissue.)
    """
    res = _resolve_filter_mapping_to_queryset_model_inner_2(
        queryset_entity, field_entity, field_path, force_through_phenopackets
    )

    # While our resolved path is still getting shorter, keep running the inner function to simplify it. This should
    # usually just run 0-1 times.
    while len(res) > len(
        res2 := _resolve_filter_mapping_to_queryset_model_inner_2(
            queryset_entity, queryset_entity, res, force_through_phenopackets
        )
    ):
        res = res2

    return res


def resolve_filter_mapping_to_queryset_model(
    queryset_entity: DiscoveryEntity,
    field_entity: DiscoveryEntity,
    field_path: tuple[str, ...],
    force_through_phenopackets: bool = False,
) -> str:
    """
    Given a goal (queryset) model name and a current (field) model name, rewrite a path to a field from the field model
    name to the goal queryset model name and convert it to a Django-query-form field path.
    IMPORTANT NOTE: This hard-codes model relationships, e.g., experiments inside biosamples inside phenopackets.
                    The "hard-coded" data model here is equivalent of the old "linked field set" concept, which was very
                    over-generalized.
    """
    return field_path_to_django_mapping(
        resolve_queryset_entity_path_from_field_path(
            queryset_entity, field_entity, field_path, force_through_phenopackets
        )
    )
