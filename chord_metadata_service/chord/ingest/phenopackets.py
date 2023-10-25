from __future__ import annotations

import uuid

from dateutil.parser import isoparse
from decimal import Decimal
from chord_metadata_service.chord.models import Project, ProjectJsonSchema, Dataset
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.patients.values import KaryotypicSex
from chord_metadata_service.restapi.schema_utils import patch_project_schemas
from chord_metadata_service.restapi.types import ExtensionSchemaDict
from chord_metadata_service.restapi.utils import iso_duration_to_years

from .exceptions import IngestError
from .resources import ingest_resource
from .schema import schema_validation
from .utils import map_if_list, query_and_check_nulls

from typing import Any, Dict, Iterable, Optional, Union


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
        negated=pf.get("negated", False),
        modifier=pf.get("modifier", []),  # TODO: Validate ontology term in schema...
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
    validation = schema_validation(phenopacket_data, schema)
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
    for k in ("alternate_ids", "age", "sex", "taxonomy"):
        subject_query.update(query_and_check_nulls(subject, k))

    # - Check if age is represented as a duration string (vs. age range values) and convert it to years
    age_numeric_value: Optional[Decimal] = None
    age_unit_value: Optional[str] = None
    if "age" in subject:
        if "age" in subject["age"]:
            age_numeric_value, age_unit_value = iso_duration_to_years(subject["age"]["age"])

    # --------------------------------------------------------------------------------------------------------------

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
    # TODO: This should probably be a JSON field, or compound key with code/body_site
    procedure, _ = pm.Procedure.objects.get_or_create(**bs["procedure"])

    bs_query = query_and_check_nulls(bs, "individual_id", lambda i: pm.Individual.objects.get(id=i))
    for k in ("sampled_tissue", "taxonomy", "individual_age_at_collection", "histological_diagnosis",
              "tumor_progression", "tumor_grade"):
        bs_query.update(query_and_check_nulls(bs, k))

    bs_obj, bs_created = pm.Biosample.objects.get_or_create(
        id=bs["id"],
        description=bs.get("description", ""),
        procedure=procedure,
        is_control_sample=bs.get("is_control_sample", False),
        diagnostic_markers=bs.get("diagnostic_markers", []),
        extra_properties=bs.get("extra_properties", {}),
        **bs_query
    )

    variants_db = []
    if "variants" in bs:
        for variant in bs["variants"]:
            variant_obj, _ = pm.Variant.objects.get_or_create(
                allele_type=variant["allele_type"],
                allele=variant["allele"],
                zygosity=variant.get("zygosity", {}),
                extra_properties=variant.get("extra_properties", {})
            )
            variants_db.append(variant_obj)

    if bs_created:
        bs_pfs = [get_or_create_phenotypic_feature(pf) for pf in bs.get("phenotypic_features", [])]
        bs_obj.phenotypic_features.set(bs_pfs)

        if variants_db:
            bs_obj.variants.set(variants_db)

    # TODO: Update phenotypic features otherwise?

    return bs_obj


def get_or_create_gene(g: dict) -> pm.Gene:
    # TODO: Validate CURIE
    # TODO: Rename alternate_id
    g_obj, _ = pm.Gene.objects.get_or_create(
        id=g["id"],
        alternate_ids=g.get("alternate_ids", []),
        symbol=g["symbol"],
        extra_properties=g.get("extra_properties", {})
    )
    return g_obj


def get_or_create_disease(disease) -> pm.Disease:
    d_obj, _ = pm.Disease.objects.get_or_create(
        term=disease["term"],
        disease_stage=disease.get("disease_stage", []),
        tnm_finding=disease.get("tnm_finding", []),
        extra_properties=disease.get("extra_properties", {}),
        **query_and_check_nulls(disease, "onset")
    )
    return d_obj


def get_or_create_hts_file(hts_file) -> pm.HtsFile:
    htsf_obj, _ = pm.HtsFile.objects.get_or_create(
        uri=hts_file["uri"],
        description=hts_file.get("description", None),
        hts_format=hts_file["hts_format"],
        genome_assembly=hts_file["genome_assembly"],
        individual_to_sample_identifiers=hts_file.get("individual_to_sample_identifiers", None),
        extra_properties=hts_file.get("extra_properties", {})
    )
    return hts_file


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
    #  biosamples: [...]
    #  genes: [...]
    #  diseases: [...]
    #  hts_files: [...]
    #  meta_data: {..., resources: [...]}

    new_phenopacket_id = phenopacket_data.get("id", str(uuid.uuid4()))

    subject = phenopacket_data.get("subject")

    phenotypic_features = phenopacket_data.get("phenotypic_features", [])

    # Pre-process biosamples; historically (<2.17.3) we were running into issues because a missing individual_id in
    # the biosample meant it would be left as None rather than properly associated with a specified subject.
    #   - Here, we tag the biosample with the subject's ID if a subject is specified, since the Phenopacket spec
    #     explicitly says of the biosamples field:
    #       "This field describes samples that have been derived from the patient who is the object of the Phenopacket"
    biosamples = [
        {**bs, "individual_id": subject["id"]} if subject else bs
        for bs in phenopacket_data.get("biosamples", [])
    ]

    # Pull other fields out of the phenopacket input
    genes = phenopacket_data.get("genes", [])
    diseases = phenopacket_data.get("diseases", [])
    hts_files = phenopacket_data.get("hts_files", [])
    meta_data = phenopacket_data["meta_data"]  # required to be present, so no .get()
    resources = meta_data.get("resources", [])

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

    # Get or create all genes in the phenopacket
    # TODO: May want to augment alternate_ids
    genes_db = [get_or_create_gene(g) for g in genes]

    # Get or create all diseases in the phenopacket
    diseases_db = [get_or_create_disease(disease) for disease in diseases]

    # Get or create all manually-specified HTS files in the phenopacket
    hts_files_db = [get_or_create_hts_file(hts_file) for hts_file in hts_files]

    # Get or create all resources (ontologies, etc.) in the phenopacket
    resources_db = [ingest_resource(rs) for rs in resources]

    # Create phenopacket metadata object
    meta_data_obj = pm.MetaData(
        created_by=meta_data["created_by"],
        submitted_by=meta_data.get("submitted_by"),
        phenopacket_schema_version="1.0.0-RC3",
        external_references=meta_data.get("external_references", []),
        extra_properties=meta_data.get("extra_properties", {}),
    )
    meta_data_obj.save()

    # Attach resources to the metadata object
    meta_data_obj.resources.set(resources_db)

    # Create the phenopacket object...
    new_phenopacket = pm.Phenopacket(
        id=new_phenopacket_id,
        subject=subject_obj,
        meta_data=meta_data_obj,
        dataset=Dataset.objects.get(identifier=dataset_id),
    )

    # ... save it to the database...
    new_phenopacket.save()

    # ... and attach all the other objects to it.
    new_phenopacket.phenotypic_features.set(phenotypic_features_db)
    new_phenopacket.biosamples.set(biosamples_db)
    new_phenopacket.genes.set(genes_db)
    new_phenopacket.diseases.set(diseases_db)
    new_phenopacket.hts_files.set(hts_files_db)

    return new_phenopacket


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

    # First, validate all phenopackets
    map_if_list(validate_phenopacket, json_data, json_schema)

    # Then, actually try to ingest them (if the validation passes); we don't need to re-do validation here.
    return map_if_list(ingest_phenopacket, json_data, dataset_id, json_schema=json_schema, validate=False)
