from __future__ import annotations

import structlog.stdlib

from dateutil.parser import isoparse
from decimal import Decimal
from humps import decamelize
from structlog.stdlib import BoundLogger

from chord_metadata_service.chord.models import Project, ProjectJsonSchema, Dataset
from chord_metadata_service.geo.ingest import get_or_create_geo_location
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA, VRS_REF_REGISTRY
from chord_metadata_service.phenopackets.utils import time_element_to_years
from chord_metadata_service.patients.models import Individual, VitalStatus
from chord_metadata_service.patients.values import KaryotypicSex, PatientStatus
from chord_metadata_service.restapi.schema_utils import patch_project_schemas
from chord_metadata_service.restapi.types import ExtensionSchemaDict
from chord_metadata_service.restapi.utils import remove_computed_properties

from .exceptions import IngestError
from .resources import ingest_resource
from .schema import schema_validation
from .utils import map_if_list, query_and_check_nulls
from typing import Any, Callable, Iterable, TypeVar
from django.db.models import Model

# Generic TypeVar for django db models
T = TypeVar("T", bound=Model)


def _get_or_create_opt(key: str, data: dict, create_func: Callable[..., T]) -> T | None:
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
        severity=pf.get("severity"),
        modifiers=pf.get("modifiers", []),
        onset=pf.get("onset"),
        resolution=pf.get("resolution"),
        evidence=pf.get("evidence", []),  # TODO: Separate class for evidence?
        extra_properties=remove_computed_properties(pf.get("extra_properties", {})),
    )
    pf_obj.save()
    return pf_obj


def validate_phenopacket(
    phenopacket_data: dict[str, Any], lg: BoundLogger, schema: dict = PHENOPACKET_SCHEMA, idx: int | None = None
) -> None:
    # Validate phenopacket data against phenopackets schema.
    validation = schema_validation(phenopacket_data, schema, registry=VRS_REF_REGISTRY, obj_idx=idx, logger=lg)
    if not validation:
        # TODO: Report more precise errors
        raise IngestError(
            f"Failed schema validation for phenopacket{(' ' + str(idx)) if idx is not None else ''} "
            f"(check Katsu logs for more information)"
        )


def update_or_create_subject(subject: dict) -> pm.Individual:
    extra_properties: dict[str, Any] = remove_computed_properties(subject.get("extra_properties", {}))

    # Pre-process subject data:    ---------------------------------------------------------------------------------

    # - Be a bit flexible with the subject date_of_birth field for Signature; convert blank strings to None.
    subject["date_of_birth"] = subject.get("date_of_birth") or None
    subject_query = query_and_check_nulls(subject, "date_of_birth", transform=isoparse)
    for k in ("alternate_ids", "time_at_last_encounter", "sex", "taxonomy", "gender"):
        subject_query.update(query_and_check_nulls(subject, k))

    # --------------------------------------------------------------------------------------------------------------

    age_numeric_value: Decimal | None = None
    age_unit_value: str | None = None
    if "time_at_last_encounter" in subject:
        age_numeric_value, age_unit_value = time_element_to_years(subject["time_at_last_encounter"])

    vital_status: VitalStatus | None = None
    if vital_status_data := subject.get("vital_status"):
        vs_query = {"status": vital_status_data.get("status", PatientStatus.UNKNOWN_STATUS)}
        for k in ("time_of_death", "cause_of_death", "survival_time_in_days"):
            vs_query.update(query_and_check_nulls(vital_status_data, k))
        vital_status, _ = VitalStatus.objects.get_or_create(**vs_query)

    # Check if subject already exists
    existing_extra_properties: dict[str, Any]
    try:
        existing_subject = pm.Individual.objects.get(id=subject["id"])
        existing_extra_properties = existing_subject.extra_properties
        existing_vital_status = existing_subject.vital_status
    except pm.Individual.DoesNotExist:
        existing_extra_properties = extra_properties
        existing_vital_status = vital_status
        pass

    # --------------------------------------------------------------------------------------------------------------

    subject_obj, subject_obj_created = pm.Individual.objects.get_or_create(
        id=subject["id"],
        # if left out/null, karyotypic_sex defaults to UNKNOWN_KARYOTYPE
        karyotypic_sex=subject.get("karyotypic_sex") or KaryotypicSex.UNKNOWN_KARYOTYPE,
        age_numeric=age_numeric_value,
        age_unit=age_unit_value if age_unit_value else "",
        extra_properties=existing_extra_properties,
        vital_status=existing_vital_status,
        **subject_query,
    )

    if not subject_obj_created:
        # Add any new extra properties or vital status change to subject if they already exist
        subject_obj.extra_properties = extra_properties
        subject_obj.vital_status = vital_status
        subject_obj.save()

    return subject_obj


def get_or_create_biosample(bs: dict, lg: structlog.stdlib.BoundLogger) -> pm.Biosample:
    bs_query = query_and_check_nulls(bs, "individual_id", lambda i: pm.Individual.objects.get(id=i))
    for k in (
        "sampled_tissue",
        "taxonomy",
        "time_of_collection",
        "histological_diagnosis",
        "tumor_progression",
        "tumor_grade",
    ):
        bs_query.update(query_and_check_nulls(bs, k))

    bs_obj, bs_created = pm.Biosample.objects.get_or_create(
        id=bs["id"],
        description=bs.get("description", ""),
        procedure=bs.get("procedure", {}),
        sample_type=bs.get("sample_type", {}),
        measurements=bs.get("measurements", []),
        pathological_stage=bs.get("pathological_stage", {}),
        is_control_sample=bs.get("is_control_sample", False),
        pathological_tnm_finding=bs.get("pathological_tnm_finding", []),
        diagnostic_markers=bs.get("diagnostic_markers", []),
        extra_properties=remove_computed_properties(bs.get("extra_properties", {})),
        **bs_query,
    )

    if isinstance(bs_loc_json := bs.get("location_collected"), dict):
        bs_obj.location_collected = get_or_create_geo_location(bs_loc_json)
        # will be saved below

    if derived_from_id := bs.get("derived_from_id"):
        try:
            parent_biosample = pm.Biosample.objects.get(id=derived_from_id)
            parent_biosample.derived_biosamples.add(bs_obj)
            parent_biosample.save()
        except pm.Biosample.DoesNotExist:
            lg.warning(
                "biosample refers to non-existing 'derived_from_id' biosample",
                biosample_id=bs["id"],
                derived_from_id=derived_from_id,
            )

    if bs_created:
        bs_pfs = [get_or_create_phenotypic_feature(pf) for pf in bs.get("phenotypic_features", [])]
        bs_obj.phenotypic_features.set(bs_pfs)

    # TODO: Update phenotypic features otherwise?

    # this bs_obj.save() call does two things:
    #  - saves location_collected, if set
    #  - populates the fts_extra field with the latest data (phenotypic features)
    bs_obj.save()

    return bs_obj


def get_or_create_gene_descriptor(gene_desc) -> pm.GeneDescriptor:
    gene_descriptor, _ = pm.GeneDescriptor.objects.get_or_create(
        value_id=gene_desc["value_id"],
        symbol=gene_desc["symbol"],
        description=gene_desc.get("description", ""),
        alternate_ids=gene_desc.get("alternate_ids", []),
        xrefs=gene_desc.get("xrefs", []),
        alternate_symbols=gene_desc.get("alternate_symbols", []),
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
        allelic_state=var_desc.get("allelic_state", {}),
    )
    return variant_descriptor


def get_or_create_variant_interp(variant_interp_data: dict) -> pm.VariantInterpretation:
    variant_descriptor = get_or_create_variant_descriptor(variant_interp_data["variation_descriptor"])
    variant_interpretation, _ = pm.VariantInterpretation.objects.get_or_create(
        acmg_pathogenicity_classification=variant_interp_data["acmg_pathogenicity_classification"],
        therapeutic_actionability=variant_interp_data["therapeutic_actionability"],
        variation_descriptor=variant_descriptor,
    )
    return variant_interpretation


def get_or_create_genomic_interpretation(
    gen_interp: dict, subject: Individual | None, biosamples: list[pm.Biosample]
) -> pm.GenomicInterpretation:
    """
    Given a phenopackets-ish genomic interpretation dictionary and some context from the phenopacket being ingested,
    create a new GenomicInterpretation ORM object (or re-use an existing one if one matches).
    """

    # Check if a Biosample or Individual with subject_or_biosample_id matches the phenopacket context passed in via
    # arguments, since we shouldn't have any genomic interpretations that are trying to describe a phenopacket different
    # than the one they're in.
    subject_or_biosample_id = gen_interp["subject_or_biosample_id"]
    related_biosample = next((b for b in biosamples if str(b.id) == subject_or_biosample_id), None)
    related_subject = subject if str(subject.id) == subject_or_biosample_id else None

    if related_biosample and related_subject:
        # Cannot be both
        raise IngestError(
            f"Ambiguous GenomicInterpretation.subject_or_biosample_id {subject_or_biosample_id} "
            "points to a Biosample AND a Subject. Must point to a Biosample or a Subject, not both."
        )
    elif related_biosample:
        related_obj = related_biosample
    elif related_subject:
        related_obj = related_subject
    else:
        # Cannot be neither
        raise IngestError(
            f"GenomicInterpretation.subject_or_biosample_id {subject_or_biosample_id} "
            "has no matching Biosample or Individual in the phenopacket context."
        )

    gene_descriptor = _get_or_create_opt("gene_descriptor", gen_interp, get_or_create_gene_descriptor)
    variant_interpretation = _get_or_create_opt("variant_interpretation", gen_interp, get_or_create_variant_interp)

    gen_obj, _ = pm.GenomicInterpretation.objects.get_or_create(
        # must be one or the other of these two foreign keys, although this cannot really be modeled in SQL:
        **({"subject": related_obj} if related_subject else {}),
        **({"biosample": related_obj} if related_biosample else {}),
        # ---
        interpretation_status=gen_interp["interpretation_status"],
        gene_descriptor=gene_descriptor,
        variant_interpretation=variant_interpretation,
        extra_properties=remove_computed_properties(gen_interp.get("extra_properties", {})),
    )

    return gen_obj


def get_or_create_disease(disease) -> pm.Disease:
    d_obj, _ = pm.Disease.objects.get_or_create(
        term=disease["term"],
        excluded=disease.get("excluded", False),
        resolution=disease.get("resolution"),
        disease_stage=disease.get("disease_stage", []),
        clinical_tnm_finding=disease.get("clinical_tnm_finding", []),
        primary_site=disease.get("primary_site"),
        laterality=disease.get("laterality"),
        extra_properties=remove_computed_properties(disease.get("extra_properties", {})),
        **query_and_check_nulls(disease, "onset"),
    )
    return d_obj


def get_or_create_interpretation_diagnosis(
    interpretation: dict, subject: Individual | None, biosamples: list[pm.Biosample]
) -> pm.Diagnosis | None:
    diagnosis = interpretation.get("diagnosis")

    if not diagnosis:
        # No diagnosis to create
        return None

    # One-to-one relation between Interpretation and Diagnosis.
    # If an Interpretation has a Diagnosis, the created Diagnosis row uses the interpretation's ID as its PK
    # This ensures unique diagnoses if more than one share the same disease/extra_properties
    interpretation_id = interpretation.get("id")
    diag_obj, created = pm.Diagnosis.objects.get_or_create(
        id=interpretation_id,
        disease=diagnosis.get("disease", {}),
        extra_properties=remove_computed_properties(diagnosis.get("extra_properties", {})),
    )

    if created:
        # Create GenomicInterpretation
        genomic_interpretations_data = diagnosis.get("genomic_interpretations", [])
        genomic_interpretations = [
            get_or_create_genomic_interpretation(gen_interp, subject, biosamples)
            for gen_interp in genomic_interpretations_data
        ]
        diag_obj.genomic_interpretations.set(genomic_interpretations)
    return diag_obj


def get_or_create_interpretation(
    interpretation: dict, subject: Individual | None, biosamples: list[pm.Biosample]
) -> pm.Interpretation:
    diagnosis = get_or_create_interpretation_diagnosis(interpretation, subject, biosamples)
    interp_obj, _ = pm.Interpretation.objects.get_or_create(
        id=interpretation["id"],
        diagnosis=diagnosis,
        progress_status=interpretation["progress_status"],
        summary=interpretation.get("summary", ""),
        extra_properties=remove_computed_properties(interpretation.get("extra_properties", {})),
    )

    return interp_obj


def ingest_phenopacket(
    phenopacket_data: dict[str, Any],
    dataset_id: str,
    lg: BoundLogger,
    json_schema: dict = PHENOPACKET_SCHEMA,
    validate: bool = True,
    idx: int | None = None,
) -> pm.Phenopacket:
    """Ingests a single phenopacket."""

    if validate:
        # Validate phenopacket data against phenopackets schema prior to ingestion, if specified.
        # `validate` may be false if the phenopacket has already been validated.
        validate_phenopacket(phenopacket_data, lg, json_schema, idx)

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

    phenopacket_id = phenopacket_data.get("id")

    lg = lg.bind(phenopacket_id=phenopacket_id)

    if phenopacket_data.get("files", []):
        lg.warning("found files in phenopacket.files: these will not be ingested")

    # Abort the ingestion if the phenopacket's ID exists in the DB
    if pm.Phenopacket.objects.filter(id=phenopacket_id).exists():
        (lg.error("cannot ingest phenopacket: ID already exists in the database"),)
        raise IngestError(f"Cannot ingest phenopacket with ID {phenopacket_id}: ID already exists in the database.")

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
    # - non-Phenopackets-standard field:
    extra_properties = remove_computed_properties(phenopacket_data.get("extra_properties", {}))

    # If there's a subject attached to the phenopacket, create it
    # - or, if it already exists, *update* the extra properties if needed.
    #   This is one of the few cases of 'updating' something that exists in Katsu.
    subject_obj: pm.Individual | None = None
    if subject:  # we have a dictionary of subject data in the phenopacket
        subject_obj = update_or_create_subject(subject)

    # Get or create all phenotypic features in the phenopacket
    phenotypic_features_db = [get_or_create_phenotypic_feature(pf) for pf in phenotypic_features]

    # Get or create all biosamples in the phenopacket
    biosamples_db = [get_or_create_biosample(bs, lg) for bs in biosamples]

    # Get or create all resources (ontologies, etc.) in the phenopacket
    resources_db = [ingest_resource(rs, lg) for rs in resources]

    interpretations_db = [
        get_or_create_interpretation(interp, subject=subject_obj, biosamples=biosamples_db)
        for interp in interpretations
    ]
    diseases_db = [get_or_create_disease(disease) for disease in diseases]

    # Create phenopacket metadata object
    meta_data_obj = pm.MetaData(
        created_by=meta_data["created_by"],
        submitted_by=meta_data.get("submitted_by"),
        phenopacket_schema_version=meta_data.get("phenopacket_schema_version"),
        external_references=meta_data.get("external_references", []),
        updates=meta_data.get("updates", []),
        extra_properties=remove_computed_properties(meta_data.get("extra_properties", {})),
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
        extra_properties=extra_properties,
    )

    #  ... save it to the database...
    phenopacket.save()

    # ... and attach all the other objects to it.
    phenopacket.phenotypic_features.set(phenotypic_features_db)
    phenopacket.interpretations.set(interpretations_db)
    phenopacket.biosamples.set(biosamples_db)
    phenopacket.diseases.set(diseases_db)

    # ... and re-save it, to populate the fts_extra field from the above related models
    phenopacket.save()

    return phenopacket


def ingest_phenopacket_workflow(json_data, dataset_id, lg: BoundLogger) -> list[pm.Phenopacket] | pm.Phenopacket:
    project = Project.objects.get(identifier=Dataset.objects.get(identifier=dataset_id).project_id)
    lg = lg.bind(project_id=str(project.identifier), dataset_id=dataset_id)

    project_schemas: Iterable[ExtensionSchemaDict] = ProjectJsonSchema.objects.filter(
        project_id=project.identifier
    ).values(
        "json_schema",
        "required",
        "schema_type",
    )

    # Map with key:schema_type and value:json_schema
    extension_schemas: dict[str, ExtensionSchemaDict] = {
        proj_schema["schema_type"].lower(): proj_schema for proj_schema in project_schemas
    }
    json_schema = patch_project_schemas(PHENOPACKET_SCHEMA, extension_schemas, lg)

    # Converts camelCase keys to snake_case for workflow ingests.
    # Ingests made with HTTP through /pivate/ingest are converted to snake_case by a django middleware
    json_data = decamelize(json_data)

    # First, validate all phenopackets
    map_if_list(validate_phenopacket, json_data, lg, json_schema)

    # Then, actually try to ingest them (if the validation passes); we don't need to re-do validation here.
    return map_if_list(ingest_phenopacket, json_data, dataset_id, lg, json_schema=json_schema, validate=False)
