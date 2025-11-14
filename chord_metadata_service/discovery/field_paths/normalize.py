from bento_lib.discovery import DiscoveryEntity

__all__ = ["normalize_field_path_true_model"]


def normalize_field_path_true_model(
    entity_name: DiscoveryEntity, field_path: tuple[str, ...]
) -> tuple[DiscoveryEntity, tuple[str, ...]]:
    """
    Normalizes a discovery entity/field access to its simplest form, letting us know which discovery entity is truly
    being filtered. This also lets us correctly check any permissions for data types later...
    (which itself is quite a janky system).
    """

    match (entity_name, field_path):
        # We employ some recursion to progressively further normalize to a simpler form until we cannot anymore.
        case ("individual", ("phenopackets", *rest)):
            return normalize_field_path_true_model("phenopacket", tuple(rest))
        case ("individual", ("biosamples", *rest)):
            # NOTE: this is a non-standard access pattern, but still works as of the time of writing (2025-09-03)
            # because of the way the Django relationships are set up.
            return normalize_field_path_true_model("biosample", tuple(rest))
        case ("phenopacket", ("subject", *rest)):
            return normalize_field_path_true_model("individual", tuple(rest))
        case ("phenopacket", ("biosamples", *rest)):
            return normalize_field_path_true_model("biosample", tuple(rest))
        case ("biosample", ("phenopackets", *rest)):
            return normalize_field_path_true_model("phenopacket", tuple(rest))
        case ("biosample", ("individual", *rest)):
            return normalize_field_path_true_model("individual", tuple(rest))
        # TODO: remove old experiment path in a future version:
        case ("biosample", ("experiment" | "experiments", *rest)):  # "experiment" is old name, "experiments" is new
            return normalize_field_path_true_model("experiment", tuple(rest))
        case ("experiment", ("biosamples", *rest)):
            return normalize_field_path_true_model("biosample", tuple(rest))
        case ("experiment", ("experiment_results", *rest)):
            return normalize_field_path_true_model("experiment_result", tuple(rest))
        case ("experiment_result", ("experiments", *rest)):
            return normalize_field_path_true_model("experiment", tuple(rest))
        case _:  # base case; nothing to do
            return entity_name, field_path
