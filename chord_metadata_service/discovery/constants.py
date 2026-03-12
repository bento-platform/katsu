from bento_lib.discovery import DiscoveryEntity

# Python typing struggles with frozenset[Literal[...]] so this is a little hack to build one:
_DISCOVERY_ENTITIES_SET: set[DiscoveryEntity] = {
    "phenopacket", "individual", "biosample", "experiment", "experiment_result"
}
DISCOVERY_ENTITIES: frozenset[DiscoveryEntity] = frozenset(_DISCOVERY_ENTITIES_SET)

# From a Phenopackets-centric view, this is a mapping of a discovery entity to the entities nested inside.
# As a caveat, we can think of these entities as nested in any of the other ones, basically, but in Katsu we aim for
# this "Phenopackets-centric" PoV.
NESTED_ENTITIES: dict[DiscoveryEntity, tuple[DiscoveryEntity, ...]] = {
    "phenopacket": ("individual", "biosample", "experiment", "experiment_result"),
    "individual": (),
    "biosample": ("experiment", "experiment_result"),
    "experiment": ("experiment_result",),
    "experiment_result": (),
}

ENTITY_TO_DATASET_GROUP_BY = {
    "phenopacket": "dataset_id",
    "individual": "phenopackets__dataset_id",
    "biosample": "phenopackets__dataset_id",
    "experiment": "biosample__individual__phenopackets__dataset_id",
    "experiment_result": "experiments__biosample__individual__phenopackets__dataset_id",
}
