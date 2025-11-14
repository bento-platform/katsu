from bento_lib.discovery import DiscoveryEntity
from django.contrib.postgres.search import SearchVector
from django.db.models import BooleanField, Field, TextField
from django.db.models.functions import Cast
from typing import Type, TypeAlias

from chord_metadata_service.discovery.field_paths.resolve import resolve_filter_mapping_to_queryset_model

__all__ = [
    "FULL_TEXT_SEARCH_FIELDS",
    "full_text_search_vector",
]


GENOMIC_INTERPRETATION_PATH = ("interpretations", "diagnosis", "genomic_interpretations")
GENE_DESCRIPTOR_PATH = (*GENOMIC_INTERPRETATION_PATH, "gene_descriptor")
VARIANT_INTERPRETATION_PATH = (*GENOMIC_INTERPRETATION_PATH, "variant_interpretation")
VARIATION_DESCRIPTOR_PATH = (*VARIANT_INTERPRETATION_PATH, "variation_descriptor")

# TODO: maybe we can get this automatically
ENTITY_M2M_FIELDS: dict[DiscoveryEntity, tuple[str, ...]] = {
    "phenopacket": ("phenotypic_features", "interpretations", "diseases"),
}

FTSFieldDescriptor: TypeAlias = list[str] | tuple[list[str], Type[Field]]

PHENOTYPIC_FEATURE_FTS_FIELDS: tuple[FTSFieldDescriptor, ...] = (
    ["description"],
    (["pftype"], TextField),
    (["severity"], TextField),
    (["modifiers"], TextField),
    (["onset"], TextField),
    (["evidence"], TextField),
    (["extra_properties"], TextField),
)

DISEASE_FTS_FIELDS: tuple[FTSFieldDescriptor, ...] = (
    (["diseases", "term"], TextField),
    (["diseases", "excluded"], BooleanField),
    (["diseases", "onset"], TextField),
    (["diseases", "resolution"], TextField),
    (["diseases", "disease_stage"], TextField),
    (["diseases", "clinical_tnm_finding"], TextField),
    (["diseases", "primary_site"], TextField),
    (["diseases", "laterality"], TextField),
    (["diseases", "extra_properties"], TextField),
)


def _prefix_fts_field_descriptor(prefix: tuple[str, ...], f: FTSFieldDescriptor) -> FTSFieldDescriptor:
    return [*prefix, *f] if isinstance(f, list) else ([*prefix, *f], f[1])


FULL_TEXT_SEARCH_FIELDS: dict[DiscoveryEntity, tuple[FTSFieldDescriptor, ...]] = {
    "phenopacket": (
        ["id"],
        # Phenotypic features field
        *(_prefix_fts_field_descriptor(("phenotypic_features",), ff) for ff in PHENOTYPIC_FEATURE_FTS_FIELDS),
        # Interpretations
        ["interpretations", "progress_status"],
        ["interpretations", "summary"],
        (["interpretations", "extra_properties"], TextField),
        #  - Interpretations -> Diagnosis
        (["interpretations", "diagnosis", "disease"], TextField),
        (["interpretations", "diagnosis", "extra_properties"], TextField),
        #  - Interpretations -> Diagnosis -> GenomicInterpretation
        [*GENOMIC_INTERPRETATION_PATH, "subject", "id"],
        [*GENOMIC_INTERPRETATION_PATH, "biosample", "id"],
        [*GENOMIC_INTERPRETATION_PATH, "interpretation_status"],
        ([*GENOMIC_INTERPRETATION_PATH, "extra_properties"], TextField),
        #  - Interpretations -> Diagnosis -> GenomicInterpretation -> VariantInterpretation
        ([*VARIANT_INTERPRETATION_PATH, "acmg_pathogenicity_classification"], TextField),
        ([*VARIANT_INTERPRETATION_PATH, "therapeutic_actionability"], TextField),
        #  - Interpretations -> Diagnosis -> GenomicInterpretation -> VariantInterpretation -> VariationDescriptor
        [*VARIATION_DESCRIPTOR_PATH, "id"],
        [*VARIATION_DESCRIPTOR_PATH, "label"],
        [*VARIATION_DESCRIPTOR_PATH, "description"],
        [*VARIATION_DESCRIPTOR_PATH, "molecule_context"],
        [*VARIATION_DESCRIPTOR_PATH, "vrs_ref_allele_seq"],
        ([*VARIATION_DESCRIPTOR_PATH, "variation"], TextField),
        ([*VARIATION_DESCRIPTOR_PATH, "expressions"], TextField),
        ([*VARIATION_DESCRIPTOR_PATH, "vcf_record"], TextField),
        ([*VARIATION_DESCRIPTOR_PATH, "xrefs"], TextField),
        ([*VARIATION_DESCRIPTOR_PATH, "alternate_labels"], TextField),
        ([*VARIATION_DESCRIPTOR_PATH, "extensions"], TextField),
        ([*VARIATION_DESCRIPTOR_PATH, "structural_type"], TextField),
        ([*VARIATION_DESCRIPTOR_PATH, "allelic_state"], TextField),
        #  - Interpretations -> Diagnosis -> GenomicInterpretation -> GeneDescriptor
        [*GENE_DESCRIPTOR_PATH, "value_id"],
        [*GENE_DESCRIPTOR_PATH, "symbol"],
        [*GENE_DESCRIPTOR_PATH, "description"],
        ([*GENE_DESCRIPTOR_PATH, "alternate_ids"], TextField),
        ([*GENE_DESCRIPTOR_PATH, "xrefs"], TextField),
        ([*GENE_DESCRIPTOR_PATH, "alternate_symbols"], TextField),
        ([*GENE_DESCRIPTOR_PATH, "extra_properties"], TextField),
        # Disease
        *(_prefix_fts_field_descriptor(("diseases",), ff) for ff in DISEASE_FTS_FIELDS),
    ),
    "individual": (
        ["id"],
        ["alternate_ids"],
        ["date_of_birth"],
        ["sex"],
        ["karyotypic_sex"],
        (["gender"], TextField),
        (["taxonomy"], TextField),
        (["time_at_last_encounter"], TextField),
        (["time_at_last_encounter", "age"], TextField),
        (["time_at_last_encounter", "age_range"], TextField),
        (["vital_status", "status"], TextField),
        (["vital_status", "time_of_death"], TextField),
        (["vital_status", "cause_of_death"], TextField),
        (["vital_status", "survival_time_in_days"], TextField),
        (["extra_properties"], TextField),
    ),
    "biosample": (
        ["id"],
        ["description"],
        (["sampled_tissue"], TextField),
        (["taxonomy"], TextField),
        (["time_of_collection"], TextField),
        (["histological_diagnosis"], TextField),
        (["tumor_progression"], TextField),
        (["tumor_grade"], TextField),
        (["diagnostic_markers"], TextField),
        (["extra_properties"], TextField),
        # Biosample -> Procedure
        (["procedure", "code"], TextField),
        (["procedure", "body_site"], TextField),
        (["procedure", "extra_properties"], TextField),
    ),
    "experiment": (
        # Experiment fields
        ["study_type"],
        ["experiment_type"],
        (["experiment_ontology"], TextField),
        ["molecule"],
        (["molecule_ontology"], TextField),
        ["library_strategy"],
        ["library_source"],
        ["library_selection"],
        ["library_layout"],
        ["extraction_protocol"],
        ["reference_registry_id"],
        (["extra_properties"], TextField),
        # Instrument fields
        ["instrument", "device"],
        ["instrument", "description"],
        (["instrument", "extra_properties"], TextField),
    ),
    "experiment_result": (
        ["description"],
        ["filename"],
        ["file_format"],
        ["genome_assembly_id"],
        ["data_output_type"],
        ["usage"],
        ["creation_date"],
        ["created_by"],
        (["extra_properties"], TextField),
    ),
}


def full_text_search_vector(queryset_entity: DiscoveryEntity, include_m2m: bool = False) -> SearchVector:
    """
    Given a queryset entity (most likely phenopacket or individual, since they're more "top-level"), generate a Postgres
    SearchVector object for full-text search across the entity/linked entities.
    TODO: right now (and historically) in Katsu this is very slow. Need to figure out a way to improve performance!
    """

    args = []

    def _add_args(fe: DiscoveryEntity):
        fields = FULL_TEXT_SEARCH_FIELDS[fe]
        for f in fields:
            field: list[str]
            fc: Type[Field] | None

            # Our fields listed in FULL_TEXT_SEARCH_FIELDS[entity] come in two forms:
            #  list[str]: a straight-up field path; doesn't need any casting for searching
            #  tuple[list[str], Type[Field]]: a field-path that must be cast to a specific type of field for searching
            if isinstance(f, list):
                field = f
                fc = None
            else:
                field = f[0]
                fc = f[-1]

            # TODO: explain
            if not include_m2m and field[0] in ENTITY_M2M_FIELDS.get(fe, ()):
                continue  # skip m2m field if we're not including them

            # re-write the field from a list[str] to a Django path, resolved to the current entity being queried.
            #  e.g, individual [sex] would be rewritten to "subject__sex" for a phenopacket queryset entity.
            resolved_field = resolve_filter_mapping_to_queryset_model(queryset_entity, fe, tuple(field))
            args.append(Cast(resolved_field, fc()) if fc is not None else resolved_field)

    if include_m2m:
        for field_entity, fts_fields in FULL_TEXT_SEARCH_FIELDS.items():
            _add_args(field_entity)
    else:
        # TODO: explain
        _add_args(queryset_entity)

        # TODO: explain
        if queryset_entity == "phenopacket":
            _add_args("individual")

    return SearchVector(*args)
