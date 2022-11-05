import json
import uuid

from dateutil.parser import isoparse

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.models import Table
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.restapi.utils import iso_duration_to_years

from .logger import logger
from .resources import ingest_resource
from .schema import schema_validation
from .utils import get_output_or_raise, map_if_list, query_and_check_nulls, workflow_file_output_to_path

from typing import Any, Optional


def create_phenotypic_feature(pf):
    pf_obj = pm.PhenotypicFeature(
        description=pf.get("description", ""),
        pftype=pf["type"],
        negated=pf.get("negated", False),
        severity=pf.get("severity"),
        modifier=pf.get("modifier", []),  # TODO: Validate ontology term in schema...
        onset=pf.get("onset"),
        evidence=pf.get("evidence"),  # TODO: Separate class?
        extra_properties=pf.get("extra_properties", {})
    )

    pf_obj.save()
    return pf_obj


def ingest_phenopacket(phenopacket_data: dict[str, Any], table_id: str) -> Optional[pm.Phenopacket]:
    """Ingests a single phenopacket."""

    # validate phenopackets data against phenopacket schema
    validation = schema_validation(phenopacket_data, PHENOPACKET_SCHEMA)
    if not validation:
        return

    new_phenopacket_id = phenopacket_data.get("id", str(uuid.uuid4()))

    subject = phenopacket_data.get("subject")
    phenotypic_features = phenopacket_data.get("phenotypic_features", [])
    biosamples = phenopacket_data.get("biosamples", [])
    genes = phenopacket_data.get("genes", [])
    diseases = phenopacket_data.get("diseases", [])
    hts_files = phenopacket_data.get("hts_files", [])
    meta_data = phenopacket_data["meta_data"]

    if subject:
        # Be a bit flexible with the subject date_of_birth field for Signature; convert blank strings to None.
        subject["date_of_birth"] = subject.get("date_of_birth") or None
        subject_query = query_and_check_nulls(subject, "date_of_birth", transform=isoparse)
        for k in ("alternate_ids", "age", "sex", "karyotypic_sex", "taxonomy"):
            subject_query.update(query_and_check_nulls(subject, k))

        # check if age is represented as a duration string (vs. age range values) and convert it to years
        age_numeric_value = None
        age_unit_value = None
        if "age" in subject:
            if "age" in subject["age"]:
                age_numeric_value, age_unit_value = iso_duration_to_years(subject["age"]["age"])

        subject, _ = pm.Individual.objects.get_or_create(
            id=subject["id"],
            race=subject.get("race", ""),
            ethnicity=subject.get("ethnicity", ""),
            age_numeric=age_numeric_value,
            age_unit=age_unit_value if age_unit_value else "",
            extra_properties=subject.get("extra_properties", {}),
            **subject_query
        )

    phenotypic_features_db = [create_phenotypic_feature(pf) for pf in phenotypic_features]

    biosamples_db = []
    for bs in biosamples:
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
            bs_pfs = [create_phenotypic_feature(pf) for pf in bs.get("phenotypic_features", [])]
            bs_obj.phenotypic_features.set(bs_pfs)

            if variants_db:
                bs_obj.variants.set(variants_db)

        # TODO: Update phenotypic features otherwise?

        biosamples_db.append(bs_obj)

    # TODO: May want to augment alternate_ids
    genes_db = []
    for g in genes:
        # TODO: Validate CURIE
        # TODO: Rename alternate_id
        g_obj, _ = pm.Gene.objects.get_or_create(
            id=g["id"],
            alternate_ids=g.get("alternate_ids", []),
            symbol=g["symbol"],
            extra_properties=g.get("extra_properties", {})
        )
        genes_db.append(g_obj)

    diseases_db = []
    for disease in diseases:
        # TODO: Primary key, should this be a model?
        d_obj, _ = pm.Disease.objects.get_or_create(
            term=disease["term"],
            disease_stage=disease.get("disease_stage", []),
            tnm_finding=disease.get("tnm_finding", []),
            extra_properties=disease.get("extra_properties", {}),
            **query_and_check_nulls(disease, "onset")
        )
        diseases_db.append(d_obj.id)

    hts_files_db = []
    for htsfile in hts_files:
        htsf_obj, _ = pm.HtsFile.objects.get_or_create(
            uri=htsfile["uri"],
            description=htsfile.get("description", None),
            hts_format=htsfile["hts_format"],
            genome_assembly=htsfile["genome_assembly"],
            individual_to_sample_identifiers=htsfile.get("individual_to_sample_identifiers", None),
            extra_properties=htsfile.get("extra_properties", {})
        )
        hts_files_db.append(htsf_obj)

    resources_db = [ingest_resource(rs) for rs in meta_data.get("resources", [])]

    meta_data_obj = pm.MetaData(
        created_by=meta_data["created_by"],
        submitted_by=meta_data.get("submitted_by"),
        phenopacket_schema_version="1.0.0-RC3",
        external_references=meta_data.get("external_references", []),
        extra_properties=meta_data.get("extra_properties", {})
    )
    meta_data_obj.save()

    meta_data_obj.resources.set(resources_db)

    new_phenopacket = pm.Phenopacket(
        id=new_phenopacket_id,
        subject=subject,
        meta_data=meta_data_obj,
        table=Table.objects.get(ownership_record_id=table_id, data_type=DATA_TYPE_PHENOPACKET)
    )

    new_phenopacket.save()

    new_phenopacket.phenotypic_features.set(phenotypic_features_db)
    new_phenopacket.biosamples.set(biosamples_db)
    new_phenopacket.genes.set(genes_db)
    new_phenopacket.diseases.set(diseases_db)
    new_phenopacket.hts_files.set(hts_files_db)

    return new_phenopacket


def ingest_phenopacket_workflow(workflow_outputs, table_id):
    with workflow_file_output_to_path(get_output_or_raise(workflow_outputs, "json_document")) as json_doc_path:
        logger.info(f"Attempting ingestion of phenopackets from path: {json_doc_path}")
        with open(json_doc_path, "r") as jf:
            json_data = json.load(jf)

    return map_if_list(ingest_phenopacket, json_data, table_id)
