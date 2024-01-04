from __future__ import annotations

from humps import decamelize

from dateutil.parser import isoparse
from decimal import Decimal
from chord_metadata_service.chord.models import Project, ProjectJsonSchema, Dataset
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA, VRS_REF_REGISTRY
from chord_metadata_service.patients.values import KaryotypicSex
from chord_metadata_service.restapi.schema_utils import patch_project_schemas
from chord_metadata_service.restapi.types import ExtensionSchemaDict
from chord_metadata_service.restapi.utils import time_element_to_years

from .exceptions import IngestError
from .resources import ingest_resource
from .schema import schema_validation
from .utils import map_if_list, query_and_check_nulls
from .logger import logger
from typing import Any, Dict, Iterable, Optional, Union, Callable, TypeVar
from django.db.models import Model

# Generic TypeVar for django db models
T = TypeVar('T', bound=Model)


def _get_or_create_opt(key: str, data: dict, create_func: Callable[..., T]) -> Optional[T]:
    """
    Helper function to get or create DB objects if a key is in a dict
    """
    obj = None
    if key in data:
        obj = create_func(data[key])
    return obj


def get_or_create_phenotypic_feature(pf: dict) -> pm.PhenotypicFeature:
    # Below is code for if we want to re-use phenotypic features in the future
    # For now, the lack of a many-to-many relationship doesn't let us do that.
    #  - David Lougheed, Nov 11 2022
    # pf_query = {}
    # for k in ("severity", "onset", "evidence"):
    #     pf_query.update(query_and_check_nulls(pf, k))
    #
    # get_q = dict(
    #     description=pf.get("description", ""),
    #     pftype=pf["type"],
    #     negated=pf.get("negated", False),
    #     modifier=pf.get("modifier", []),  # TODO: Validate ontology term in schema...
    #     extra_properties=pf.get("extra_properties", {}),
    #     **pf_query,
    # )
    #
    # try:
    #     pf_obj, _ = pm.PhenotypicFeature.objects.get_or_create(**get_q)
    # except MultipleObjectsReturned:
    #     pf_obj = pm.PhenotypicFeature.objects.filter(**get_q).first()

    pf_obj = pm.PhenotypicFeature(
        description=pf.get("description", ""),
        pftype=pf["type"],
        excluded=pf.get("excluded", False),
        modifiers=pf.get("modifiers", []),  # TODO: Validate ontology term in schema...
        severity=pf.get("severity"),
        onset=pf.get("onset"),
        evidence=pf.get("evidence"),  # TODO: Separate class for evidence?
        extra_properties=pf.get("extra_properties", {}),
    )
    pf_obj.save()
    return pf_obj


def validate_phenopacket(phenopacket_data: dict[str, Any],
                         schema: dict = PHENOPACKET_SCHEMA,
                         idx: Optional[int] = None) -> None:
    # Validate phenopacket data against phenopackets schema.
    # validation = schema_validation(phenopacket_data, PHENOPACKET_SCHEMA)
    validation = schema_validation(phenopacket_data, schema, registry=VRS_REF_REGISTRY)
    if not validation:
        # TODO: Report more precise errors
        raise IngestError(
            f"Failed schema validation for phenopacket{(' ' + str(idx)) if idx is not None else ''} "
            f"(check Katsu logs for more information)")


def update_or_create_subject(subject: dict) -> pm.Individual:
    extra_properties: dict[str, Any] = subject.get("extra_properties", {})

    # Pre-process subject data:    ---------------------------------------------------------------------------------

    # - Be a bit flexible with the subject date_of_birth field for Signature; convert blank strings to None.
    subject["date_of_birth"] = subject.get("date_of_birth") or None
    subject_query = query_and_check_nulls(subject, "date_of_birth", transform=isoparse)
    for k in ("alternate_ids", "time_at_last_encounter", "sex", "taxonomy"):
        subject_query.update(query_and_check_nulls(subject, k))

    # --------------------------------------------------------------------------------------------------------------

    age_numeric_value: Optional[Decimal] = None
    age_unit_value: Optional[str] = None
    if "time_at_last_encounter" in subject:
        age_numeric_value, age_unit_value = time_element_to_years(subject["time_at_last_encounter"])

    # Check if subject already exists
    existing_extra_properties: dict[str, Any]
    try:
        existing_subject = pm.Individual.objects.get(id=subject["id"])
        existing_extra_properties = existing_subject.extra_properties
    except pm.Individual.DoesNotExist:
        existing_extra_properties = extra_properties
        pass

    # --------------------------------------------------------------------------------------------------------------

    subject_obj, subject_obj_created = pm.Individual.objects.get_or_create(
        id=subject["id"],
        # if left out/null, karyotypic_sex defaults to UNKNOWN_KARYOTYPE
        karyotypic_sex=subject.get("karyotypic_sex") or KaryotypicSex.UNKNOWN_KARYOTYPE,
        age_numeric=age_numeric_value,
        age_unit=age_unit_value if age_unit_value else "",
        extra_properties=existing_extra_properties,
        **subject_query
    )

    if not subject_obj_created:
        # Add any new extra properties to subject if they already exist
        subject_obj.extra_properties = extra_properties
        subject_obj.save()

    return subject_obj


def get_or_create_biosample(bs: dict) -> pm.Biosample:
    bs_query = query_and_check_nulls(bs, "individual_id", lambda i: pm.Individual.objects.get(id=i))
    for k in ("sampled_tissue", "taxonomy", "time_of_collection", "histological_diagnosis",
              "tumor_progression", "tumor_grade"):
        bs_query.update(query_and_check_nulls(bs, k))

    bs_obj, bs_created = pm.Biosample.objects.get_or_create(
        id=bs["id"],
        description=bs.get("description", ""),
        procedure=bs.get("procedure", {}),
        sample_type=bs.get("sample_type", {}),
        measurements=bs.get("measurements", []),
        pathological_stage=bs.get("pathological_stage", {}),
        is_control_sample=bs.get("is_control_sample", False),
        diagnostic_markers=bs.get("diagnostic_markers", []),
        extra_properties=bs.get("extra_properties", {}),
        **bs_query
    )

    if derived_from_id := bs.get("derived_from_id"):
        try:
            parent_biosample = pm.Biosample.objects.get(id=derived_from_id)
            parent_biosample.derived_biosamples.add(bs_obj)
            parent_biosample.save()
        except pm.Biosample.DoesNotExist:
            logger.warning(
                f"Biosample {bs['id']} refers to a non-existing 'derived_from_id' Biosample {derived_from_id}.")

    if bs_created:
        bs_pfs = [get_or_create_phenotypic_feature(pf) for pf in bs.get("phenotypic_features", [])]
        bs_obj.phenotypic_features.set(bs_pfs)

    # TODO: Update phenotypic features otherwise?

    return bs_obj


def get_or_create_gene_descriptor(gene_desc) -> pm.GeneDescriptor:
    gene_descriptor, _ = pm.GeneDescriptor.objects.get_or_create(
        value_id=gene_desc["value_id"],
        symbol=gene_desc["symbol"],
        description=gene_desc.get("description", ""),
        alternate_ids=gene_desc.get("alternate_ids", []),
        xrefs=gene_desc.get("xrefs", []),
        alternate_symbols=gene_desc.get("alternate_symbols", [])
    )
    return gene_descriptor


def get_or_create_variant_descriptor(var_desc: dict) -> pm.VariationDescriptor:
    gene_descriptor = _get_or_create_opt("gene_context", var_desc, get_or_create_gene_descriptor)
    variant_descriptor, _ = pm.VariationDescriptor.objects.get_or_create(
        id=var_desc["id"],
        variation=var_desc.get("variation", {}),
        label=var_desc.get("label", ""),
        description=var_desc.get("description", ""),
        gene_context=gene_descriptor,
        expressions=var_desc.get("expressions", []),
        vcf_record=var_desc.get("vcf_record", {}),
        xrefs=var_desc.get("xrefs", []),
        alternate_labels=var_desc.get("alternate_labels", []),
        extensions=var_desc.get("extensions", []),
        molecule_context=var_desc.get("molecule_context", "unspecified_molecule_context"),
        structural_type=var_desc.get("structural_type", {}),
        vrs_ref_allele_seq=var_desc.get("vrs_ref_allele_seq", ""),
        allelic_state=var_desc.get("allelic_state", {})
    )
    return variant_descriptor


def get_or_create_variant_interp(variant_interp_data: dict) -> pm.VariantInterpretation:
    variant_descriptor = get_or_create_variant_descriptor(variant_interp_data["variation_descriptor"])
    variant_interpretation, _ = pm.VariantInterpretation.objects.get_or_create(
        acmg_pathogenicity_classification=variant_interp_data["acmg_pathogenicity_classification"],
        therapeutic_actionability=variant_interp_data["therapeutic_actionability"],
        variation_descriptor=variant_descriptor
    )
    return variant_interpretation


def get_or_create_genomic_interpretation(gen_interp: dict) -> pm.GenomicInterpretation:
    # Check if a Biosample or Individual with subject_or_biosample_id exists
    subject_or_biosample_id = gen_interp["subject_or_biosample_id"]
    is_biosample = pm.Biosample.objects.filter(id=subject_or_biosample_id).exists()
    is_subject = pm.Individual.objects.filter(id=subject_or_biosample_id).exists()

    if is_biosample and is_subject:
        # Cannot be both
        raise IngestError(
            f"Ambiguous GenomicInterpretation.subject_or_biosample_id {subject_or_biosample_id} "
            "points to a Biosample AND a Subject. Must point to a Biosample or a Subject, not both.")
    elif is_biosample:
        # Get related Biosample
        related_obj = pm.Biosample.objects.get(id=subject_or_biosample_id)
    elif is_subject:
        # Get related Individual
        related_obj = pm.Individual.objects.get(id=subject_or_biosample_id)
    else:
        # Cannot be neither
        raise IngestError(
            f"GenomicInterpretation.subject_or_biosample_id {subject_or_biosample_id} "
            "has no matching Biosample or Individual.")

    gene_descriptor = _get_or_create_opt("gene_descriptor", gen_interp, get_or_create_gene_descriptor)
    variant_interpretation = _get_or_create_opt("variant_interpretation", gen_interp, get_or_create_variant_interp)

    gen_obj, _ = pm.GenomicInterpretation.objects.get_or_create(
        interpretation_status=gen_interp["interpretation_status"],
        gene_descriptor=gene_descriptor,
        variant_interpretation=variant_interpretation,
        extra_properties=gen_interp.get("extra_properties", {}),
    )

    if related_obj:
        # Set the link with Biosample/Individual
        related_obj.genomic_interpretations.add(gen_obj)
        related_obj.save()

    return gen_obj


def get_or_create_disease(disease) -> pm.Disease:
    d_obj, _ = pm.Disease.objects.get_or_create(
        term=disease["term"],
        disease_stage=disease.get("disease_stage", []),
        clinical_tnm_finding=disease.get("clinical_tnm_finding", []),
        extra_properties=disease.get("extra_properties", {}),
        **query_and_check_nulls(disease, "onset")
    )
    return d_obj


def get_or_create_interpretation_diagnosis(interpretation: dict) -> pm.Diagnosis | None:
    diagnosis = interpretation.get("diagnosis")

    if not diagnosis:
        # No diagnosis to create
        return

    # One-to-one relation between Interpretation and Diagnosis.
    # If an Interpretation has a Diagnosis, the created Diagnosis row uses the interpretation's ID as its PK
    # This ensures unique diagnoses if more than one share the same disease/extra_properties
    id = interpretation.get("id")
    diag_obj, created = pm.Diagnosis.objects.get_or_create(
        id=id,
        disease=diagnosis.get("disease", {}),
        extra_properties=diagnosis.get("extra_properties", {}),
    )

    if created:
        # Create GenomicInterpretation
        genomic_interpretations_data = diagnosis.get("genomic_interpretations", [])
        genomic_interpretations = [
            get_or_create_genomic_interpretation(gen_interp)
            for gen_interp
            in genomic_interpretations_data
        ]
        diag_obj.genomic_interpretations.set(genomic_interpretations)
    return diag_obj


def get_or_create_interpretation(interpretation: dict) -> pm.Interpretation:
    diagnosis = get_or_create_interpretation_diagnosis(interpretation)
    interp_obj, _ = pm.Interpretation.objects.get_or_create(
        id=interpretation["id"],
        diagnosis=diagnosis,
        progress_status=interpretation["progress_status"],
        summary=interpretation.get("summary", {}),
        extra_properties=interpretation.get("extra_properties", {})
    )

    return interp_obj


def ingest_phenopacket(phenopacket_data: dict[str, Any],
                       dataset_id: str,
                       json_schema: dict = PHENOPACKET_SCHEMA,
                       validate: bool = True,
                       idx: Optional[int] = None) -> pm.Phenopacket:
    """Ingests a single phenopacket."""

    if validate:
        # Validate phenopacket data against phenopackets schema prior to ingestion, if specified.
        # `validate` may be false if the phenopacket has already been validated.
        validate_phenopacket(phenopacket_data, json_schema, idx)

    # Rough phenopackets structure:
    #  id: ...
    #  subject: {...}
    #  phenotypic_features: [...]
    #  measurements: [...]
    #  biosamples: [...]
    #  interpretations: [...]
    #  diseases: [...]
    #  medical_actions: [...]
    #  meta_data: {..., resources: [...]}

    if phenopacket_data.get("files", []):
        logger.warning("Found files in phenopacket.files are not ingested by Katsu.")

    # Abort the ingestion if the phenopacket's ID exists in the DB
    phenopacket_id = phenopacket_data.get("id")
    if pm.Phenopacket.objects.filter(id=phenopacket_id).exists():
        error_msg = f"Cannot ingest Phenopacket with ID {phenopacket_id}, ID already exists in the database."
        logger.error(error_msg)
        raise IngestError(error_msg)

    subject = phenopacket_data.get("subject")

    phenotypic_features = phenopacket_data.get("phenotypic_features", [])

    # Pre-process biosamples; historically (<2.17.3) we were running into issues because a missing individual_id in
    # the biosample meant it would be left as None rather than properly associated with a specified subject.
    #   - Here, we tag the biosample with the subject's ID if a subject is specified, since the Phenopacket spec
    #     explicitly says of the biosamples field:
    #       "This field describes samples that have been derived from the patient who is the object of the Phenopacket"
    biosamples = [
        {**bs, "individual_id": subject["id"]} if "individual_id" not in bs and subject else bs
        for bs in phenopacket_data.get("biosamples", [])
    ]

    # Pull other fields out of the phenopacket input
    diseases = phenopacket_data.get("diseases", [])
    meta_data = phenopacket_data["meta_data"]  # required to be present, so no .get()
    resources = meta_data.get("resources", [])
    interpretations = phenopacket_data.get("interpretations", [])
    measurements = phenopacket_data.get("measurements", [])
    medical_actions = phenopacket_data.get("medical_actions", [])

    # If there's a subject attached to the phenopacket, create it
    # - or, if it already exists, *update* the extra properties if needed.
    #   This is one of the few cases of 'updating' something that exists in Katsu.
    subject_obj: Optional[pm.Individual] = None
    if subject:  # we have a dictionary of subject data in the phenopacket
        subject_obj = update_or_create_subject(subject)

    # Get or create all phenotypic features in the phenopacket
    phenotypic_features_db = [get_or_create_phenotypic_feature(pf) for pf in phenotypic_features]

    # Get or create all biosamples in the phenopacket
    biosamples_db = [get_or_create_biosample(bs) for bs in biosamples]

    # Get or create all resources (ontologies, etc.) in the phenopacket
    resources_db = [ingest_resource(rs) for rs in resources]

    interpretations_db = [get_or_create_interpretation(interp) for interp in interpretations]
    diseases_db = [get_or_create_disease(disease) for disease in diseases]

    # Create phenopacket metadata object
    meta_data_obj = pm.MetaData(
        created_by=meta_data["created_by"],
        submitted_by=meta_data.get("submitted_by"),
        phenopacket_schema_version=meta_data.get("phenopacket_schema_version"),
        external_references=meta_data.get("external_references", []),
        extra_properties=meta_data.get("extra_properties", {}),
    )
    meta_data_obj.save()

    # Attach resources to the metadata object
    meta_data_obj.resources.set(resources_db)

    # Create the phenopacket object...
    phenopacket = pm.Phenopacket(
        id=phenopacket_id,
        subject=subject_obj,
        measurements=measurements,
        medical_actions=medical_actions,
        meta_data=meta_data_obj,
        dataset=Dataset.objects.get(identifier=dataset_id),
    )

    #  ... save it to the database...
    phenopacket.save()

    # ... and attach all the other objects to it.
    phenopacket.phenotypic_features.set(phenotypic_features_db)
    phenopacket.interpretations.set(interpretations_db)
    phenopacket.biosamples.set(biosamples_db)
    phenopacket.diseases.set(diseases_db)

    return phenopacket


def ingest_phenopacket_workflow(json_data, dataset_id) -> Union[list[pm.Phenopacket], pm.Phenopacket]:
    project_id = Project.objects.get(datasets=dataset_id)
    project_schemas: Iterable[ExtensionSchemaDict] = ProjectJsonSchema.objects.filter(project_id=project_id).values(
        "json_schema",
        "required",
        "schema_type",
    )

    # Map with key:schema_type and value:json_schema
    extension_schemas: Dict[str, ExtensionSchemaDict] = {
        proj_schema["schema_type"].lower(): proj_schema
        for proj_schema in project_schemas
    }
    json_schema = patch_project_schemas(PHENOPACKET_SCHEMA, extension_schemas)

    # Converts camelCase keys to snake_case for workflow ingests.
    # Ingests made with HTTP through /pivate/ingest are converted to snake_case by a django middleware
    json_data = decamelize(json_data)

    # First, validate all phenopackets
    map_if_list(validate_phenopacket, json_data, json_schema)

    # Then, actually try to ingest them (if the validation passes); we don't need to re-do validation here.
    return map_if_list(ingest_phenopacket, json_data, dataset_id, json_schema=json_schema, validate=False)
