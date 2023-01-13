import contextlib
import json
import logging
import os
import re
import requests
import requests_unixsocket
import shutil
import tempfile
import uuid
import jsonschema

from dateutil.parser import isoparse
from typing import Callable
from urllib.parse import urlparse

from django.conf import settings

from bento_lib.drs.utils import get_access_method_of_type, fetch_drs_record_by_uri

from chord_metadata_service.chord.data_types import (
    DATA_TYPE_EXPERIMENT,
    DATA_TYPE_PHENOPACKET,
    DATA_TYPE_READSET,
)
from chord_metadata_service.chord.models import Table, TableOwnership
from chord_metadata_service.experiments import models as em
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.resources import models as rm, utils as ru
from chord_metadata_service.restapi.fhir_ingest import (
    ingest_patients,
    ingest_observations,
    ingest_conditions,
    ingest_specimens,
)
from chord_metadata_service.phenopackets.schemas import PHENOPACKET_SCHEMA
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA
from chord_metadata_service.restapi.utils import iso_duration_to_years

requests_unixsocket.monkeypatch()

__all__ = [
    "METADATA_WORKFLOWS",
    "WORKFLOWS_PATH",
    "IngestError",
    "ingest_resource",
    "ingest_experiments_workflow",
    "ingest_phenopacket_workflow",
    "WORKFLOW_INGEST_FUNCTION_MAP",
]

logger = logging.getLogger(__name__)

WORKFLOW_PHENOPACKETS_JSON = "phenopackets_json"
WORKFLOW_EXPERIMENTS_JSON = "experiments_json"
WORKFLOW_FHIR_JSON = "fhir_json"
WORKFLOW_READSET = "readset"
WORKFLOW_CBIOPORTAL = "cbioportal"

METADATA_WORKFLOWS = {
    "ingestion": {
        WORKFLOW_PHENOPACKETS_JSON: {
            "name": "Bento Phenopackets-Compatible JSON",
            "description": "This ingestion workflow will validate and import a Phenopackets schema-compatible "
            "JSON document.",
            "data_type": DATA_TYPE_PHENOPACKET,
            "file": "phenopackets_json.wdl",
            "inputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "required": True,
                    "extensions": [".json"],
                }
            ],
            "outputs": [
                {"id": "json_document", "type": "file", "value": "{json_document}"}
            ],
        },
        WORKFLOW_EXPERIMENTS_JSON: {
            "name": "Bento Experiments JSON",
            "description": "This ingestion workflow will validate and import a Bento Experiments schema-compatible "
            "JSON document.",
            "data_type": DATA_TYPE_EXPERIMENT,
            "file": "experiments_json.wdl",
            "inputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "required": True,
                    "extensions": [".json"],
                }
            ],
            "outputs": [
                {"id": "json_document", "type": "file", "value": "{json_document}"}
            ],
        },
        WORKFLOW_FHIR_JSON: {
            "name": "FHIR Resources JSON",
            "description": "This ingestion workflow will validate and import a FHIR schema-compatible "
            "JSON document, and convert it to the Bento metadata service's internal Phenopackets-based "
            "data model.",
            "data_type": DATA_TYPE_PHENOPACKET,
            "file": "fhir_json.wdl",
            "inputs": [
                {
                    "id": "patients",
                    "type": "file",
                    "required": True,
                    "extensions": [".json"],
                },
                {
                    "id": "observations",
                    "type": "file",
                    "required": False,
                    "extensions": [".json"],
                },
                {
                    "id": "conditions",
                    "type": "file",
                    "required": False,
                    "extensions": [".json"],
                },
                {
                    "id": "specimens",
                    "type": "file",
                    "required": False,
                    "extensions": [".json"],
                },
                {"id": "created_by", "required": False, "type": "string"},
            ],
            "outputs": [
                {"id": "patients", "type": "file", "value": "{patients}"},
                {"id": "observations", "type": "file", "value": "{observations}"},
                {"id": "conditions", "type": "file", "value": "{conditions}"},
                {"id": "specimens", "type": "file", "value": "{specimens}"},
                {"id": "created_by", "type": "string", "value": "{created_by}"},
            ],
        },
        WORKFLOW_READSET: {
            "name": "Readset",
            "description": "This workflow will copy readset files over to DRS.",
            "data_type": DATA_TYPE_READSET,
            "file": "readset.wdl",
            "inputs": [
                {
                    "id": "readset_files",
                    "type": "file[]",
                    "required": True,
                    "extensions": [".cram", ".bam", ".bigWig", ".bigBed", ".bw", ".bb"],
                }
            ],
            "outputs": [
                {
                    "id": "readset_files",
                    "type": "file[]",
                    "map_from_input": "readset_files",
                    "value": "{}",
                }
            ],
        },
    },
    "analysis": {},
    "export": {
        WORKFLOW_CBIOPORTAL: {
            "name": "cBioPortal",
            "description": "This workflow creates a bundle for cBioPortal ingestion.",
            "data_type": None,
            "file": "cbioportal_export.wdl",
            "inputs": [
                {
                    "id": "dataset_id",
                    "type": "string",
                    "required": True,
                }
            ],
            "outputs": [
                {
                    "id": "cbioportal_archive",
                    "type": "file",
                    "map_from_input": "dataset_id",
                    "value": "{}.tar",
                }
            ],
        }
    },
}

WORKFLOWS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "workflows")


class IngestError(Exception):
    pass


def schema_validation(obj, schema):
    v = jsonschema.Draft7Validator(schema, format_checker=jsonschema.FormatChecker())
    try:
        jsonschema.validate(obj, schema, format_checker=jsonschema.FormatChecker())
        logger.info("JSON schema validation passed.")
        return True
    except jsonschema.exceptions.ValidationError:
        errors = [e for e in v.iter_errors(obj)]
        logger.info("JSON schema validation failed.")
        for i, error in enumerate(errors, 1):
            logger.error(
                f"{i} Validation error in {'.'.join(str(v) for v in error.path)}: {error.message}"
            )
        return False


def create_phenotypic_feature(pf):
    pf_obj = pm.PhenotypicFeature(
        description=pf.get("description", ""),
        pftype=pf["type"],
        negated=pf.get("negated", False),
        severity=pf.get("severity"),
        modifier=pf.get("modifier", []),  # TODO: Validate ontology term in schema...
        onset=pf.get("onset"),
        evidence=pf.get("evidence"),  # TODO: Separate class?
        extra_properties=pf.get("extra_properties", {}),
    )

    pf_obj.save()
    return pf_obj


def create_experiment_result(er):
    er_obj = em.ExperimentResult(
        identifier=er.get("identifier"),
        description=er.get("description"),
        filename=er.get("filename"),
        genome_assembly_id=er.get("genome_assembly_id"),
        file_format=er.get("file_format"),
        data_output_type=er.get("data_output_type"),
        usage=er.get("usage"),
        creation_date=er.get("creation_date"),
        created_by=er.get("created_by"),
        extra_properties=er.get("extra_properties", {}),
    )
    er_obj.save()
    return er_obj


def create_instrument(instrument):
    instrument_obj, _ = em.Instrument.objects.get_or_create(
        identifier=instrument.get("identifier", str(uuid.uuid4()))
    )
    instrument_obj.platform = instrument.get("platform")
    instrument_obj.description = instrument.get("description")
    instrument_obj.model = instrument.get("model")
    instrument_obj.extra_properties = instrument.get("extra_properties", {})
    instrument_obj.save()
    return instrument_obj


def _query_and_check_nulls(obj: dict, key: str, transform: Callable = lambda x: x):
    value = obj.get(key)
    return {f"{key}__isnull": True} if value is None else {key: transform(value)}


def ingest_resource(resource: dict) -> rm.Resource:
    namespace_prefix = resource["namespace_prefix"].strip()
    version = resource.get("version", "").strip()
    assigned_resource_id = ru.make_resource_id(namespace_prefix, version)

    rs_obj, _ = rm.Resource.objects.get_or_create(
        # If this doesn't match assigned_resource_id, it'll throw anyway
        id=resource.get("id", assigned_resource_id),
        name=resource["name"],
        namespace_prefix=namespace_prefix,
        url=resource["url"],
        version=version,
        iri_prefix=resource["iri_prefix"],
        extra_properties=resource.get("extra_properties", {})
        # TODO extra_properties
    )

    return rs_obj


def ingest_experiment(experiment_data, table_id):
    """Ingests a single experiment."""

    # validate experiment data against experiments schema
    validation = schema_validation(experiment_data, EXPERIMENT_SCHEMA)
    if not validation:
        return

    new_experiment_id = experiment_data.get("id", str(uuid.uuid4()))
    study_type = experiment_data.get("study_type")
    experiment_type = experiment_data["experiment_type"]
    experiment_ontology = experiment_data.get("experiment_ontology", [])
    molecule = experiment_data.get("molecule")
    molecule_ontology = experiment_data.get("molecule_ontology", [])
    library_strategy = experiment_data.get("library_strategy")
    library_source = experiment_data.get("library_source")
    library_selection = experiment_data.get("library_selection")
    library_layout = experiment_data.get("library_layout")
    extraction_protocol = experiment_data.get("extraction_protocol")
    reference_registry_id = experiment_data.get("reference_registry_id")
    qc_flags = experiment_data.get("qc_flags", [])
    biosample = experiment_data.get("biosample")
    experiment_results = experiment_data.get("experiment_results", [])
    instrument = experiment_data.get("instrument", {})
    extra_properties = experiment_data.get("extra_properties", {})
    # get existing biosample id
    if biosample is not None:
        biosample = pm.Biosample.objects.get(id=biosample)  # TODO: Handle error nicer
    # create related experiment results
    experiment_results_db = [create_experiment_result(er) for er in experiment_results]
    # create related instrument
    instrument_db = create_instrument(instrument)
    # create new experiment
    new_experiment = em.Experiment.objects.create(
        id=new_experiment_id,
        study_type=study_type,
        experiment_type=experiment_type,
        experiment_ontology=experiment_ontology,
        molecule=molecule,
        molecule_ontology=molecule_ontology,
        library_strategy=library_strategy,
        library_source=library_source,
        library_selection=library_selection,
        library_layout=library_layout,
        extraction_protocol=extraction_protocol,
        reference_registry_id=reference_registry_id,
        qc_flags=qc_flags,
        biosample=biosample,
        instrument=instrument_db,
        extra_properties=extra_properties,
        table=Table.objects.get(
            ownership_record_id=table_id, data_type=DATA_TYPE_EXPERIMENT
        ),
    )
    # create m2m relationships
    new_experiment.experiment_results.set(experiment_results_db)

    return new_experiment


def ingest_phenopacket(phenopacket_data, table_id):
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
        subject_query = _query_and_check_nulls(
            subject, "date_of_birth", transform=isoparse
        )
        for k in ("alternate_ids", "age", "sex", "karyotypic_sex", "taxonomy"):
            subject_query.update(_query_and_check_nulls(subject, k))

        # check if age is represented as a duration string (vs. age range values) and convert it to years
        age_numeric_value = None
        age_unit_value = None
        if "age" in subject:
            if "age" in subject["age"]:
                age_numeric_value, age_unit_value = iso_duration_to_years(
                    subject["age"]["age"]
                )

        subject, _ = pm.Individual.objects.get_or_create(
            id=subject["id"],
            race=subject.get("race", ""),
            ethnicity=subject.get("ethnicity", ""),
            age_numeric=age_numeric_value,
            age_unit=age_unit_value if age_unit_value else "",
            extra_properties=subject.get("extra_properties", {}),
            **subject_query,
        )

    phenotypic_features_db = [
        create_phenotypic_feature(pf) for pf in phenotypic_features
    ]

    biosamples_db = []
    for bs in biosamples:
        # TODO: This should probably be a JSON field, or compound key with code/body_site
        procedure, _ = pm.Procedure.objects.get_or_create(**bs["procedure"])

        bs_query = _query_and_check_nulls(
            bs, "individual_id", lambda i: pm.Individual.objects.get(id=i)
        )
        for k in (
            "sampled_tissue",
            "taxonomy",
            "individual_age_at_collection",
            "histological_diagnosis",
            "tumor_progression",
            "tumor_grade",
        ):
            bs_query.update(_query_and_check_nulls(bs, k))

        bs_obj, bs_created = pm.Biosample.objects.get_or_create(
            id=bs["id"],
            description=bs.get("description", ""),
            procedure=procedure,
            is_control_sample=bs.get("is_control_sample", False),
            diagnostic_markers=bs.get("diagnostic_markers", []),
            extra_properties=bs.get("extra_properties", {}),
            **bs_query,
        )

        variants_db = []
        if "variants" in bs:
            for variant in bs["variants"]:
                variant_obj, _ = pm.Variant.objects.get_or_create(
                    allele_type=variant["allele_type"],
                    allele=variant["allele"],
                    zygosity=variant.get("zygosity", {}),
                    extra_properties=variant.get("extra_properties", {}),
                )
                variants_db.append(variant_obj)

        if bs_created:
            bs_pfs = [
                create_phenotypic_feature(pf)
                for pf in bs.get("phenotypic_features", [])
            ]
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
            extra_properties=g.get("extra_properties", {}),
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
            **_query_and_check_nulls(disease, "onset"),
        )
        diseases_db.append(d_obj.id)

    hts_files_db = []
    for htsfile in hts_files:
        htsf_obj, _ = pm.HtsFile.objects.get_or_create(
            uri=htsfile["uri"],
            description=htsfile.get("description", None),
            hts_format=htsfile["hts_format"],
            genome_assembly=htsfile["genome_assembly"],
            individual_to_sample_identifiers=htsfile.get(
                "individual_to_sample_identifiers", None
            ),
            extra_properties=htsfile.get("extra_properties", {}),
        )
        hts_files_db.append(htsf_obj)

    resources_db = [ingest_resource(rs) for rs in meta_data.get("resources", [])]

    meta_data_obj = pm.MetaData(
        created_by=meta_data["created_by"],
        submitted_by=meta_data.get("submitted_by"),
        phenopacket_schema_version="1.0.0-RC3",
        external_references=meta_data.get("external_references", []),
        extra_properties=meta_data.get("extra_properties", {}),
    )
    meta_data_obj.save()

    meta_data_obj.resources.set(resources_db)

    new_phenopacket = pm.Phenopacket(
        id=new_phenopacket_id,
        subject=subject,
        meta_data=meta_data_obj,
        table=Table.objects.get(
            ownership_record_id=table_id, data_type=DATA_TYPE_PHENOPACKET
        ),
    )

    new_phenopacket.save()

    new_phenopacket.phenotypic_features.set(phenotypic_features_db)
    new_phenopacket.biosamples.set(biosamples_db)
    new_phenopacket.genes.set(genes_db)
    new_phenopacket.diseases.set(diseases_db)
    new_phenopacket.hts_files.set(hts_files_db)

    return new_phenopacket


def _map_if_list(fn, data, *args):
    # TODO: Any sequence?
    return [fn(d, *args) for d in data] if isinstance(data, list) else fn(data, *args)


def _get_output_or_raise(workflow_outputs, key):
    if key not in workflow_outputs:
        raise IngestError(f"Missing workflow output: {key}")

    return workflow_outputs[key]


DRS_URI_SCHEME = "drs"
FILE_URI_SCHEME = "file"
HTTP_URI_SCHEME = "http"
HTTPS_URI_SCHEME = "https"

WINDOWS_DRIVE_SCHEME = re.compile(r"^[a-zA-Z]$")


def _workflow_http_download(tmp_dir: str, http_uri: str) -> str:
    # TODO: Sanity check: no external insecure HTTP calls
    # TODO: Disable HTTPS cert check in debug mode
    # TODO: Handle response exceptions

    r = requests.get(http_uri)

    if not r.ok:
        raise IngestError(
            f"HTTP error encountered while downloading ingestion URI: {http_uri}"
        )

    data_path = f"{tmp_dir}ingest_download_data"

    with open(data_path, "wb") as df:
        df.write(r.content)

    return data_path


@contextlib.contextmanager
def _workflow_file_output_to_path(file_uri_or_path: str):
    # TODO: Should be able to download from DRS instead of using file URIs directly

    parsed_file_uri = urlparse(file_uri_or_path)

    if WINDOWS_DRIVE_SCHEME.match(parsed_file_uri.scheme):
        # In Windows, file paths can start with c:/ or similar (which is the drive letter.) This will get handled
        # as a 'scheme' by urlparse, so we use a regex to detect Windows-style drive 'schemes'.
        yield file_uri_or_path
        return

    if parsed_file_uri.scheme in (FILE_URI_SCHEME, ""):
        # File URI, or file path with no URI scheme (in which case implicitly assume a 'file://' in front)
        yield parsed_file_uri.path
        return

    # From here on out, we're dealing with downloads - check to make sure we
    # have somewhere to put the temporary files.

    should_del = False
    tmp_dir = settings.SERVICE_TEMP

    if tmp_dir is None:
        tmp_dir = tempfile.mkdtemp()
        should_del = True

    if not os.access(tmp_dir, os.W_OK):
        raise IngestError(f"Directory does not exist or is not writable: {tmp_dir}")

    try:
        tmp_dir = tmp_dir.rstrip("/") + "/"

        if parsed_file_uri.scheme == DRS_URI_SCHEME:  # DRS object URI
            drs_obj = fetch_drs_record_by_uri(file_uri_or_path, settings.DRS_URL)

            file_access = get_access_method_of_type(drs_obj, "file")
            if file_access:
                yield urlparse(file_access["access_url"]["url"]).path
                return

            # TODO: Some mechanism to do this with auth
            http_access = get_access_method_of_type(drs_obj, "http")
            if http_access:
                # TODO: Handle DRS headers field if available - how to do this with grace and compatibility with
                #  Bento's auth system?
                yield _workflow_http_download(tmp_dir, http_access["access_url"]["url"])
                return

            # If we get here, we have a DRS object we cannot handle; raise an error.
            raise IngestError(
                f"Cannot handle DRS object {file_uri_or_path}: No file or http access methods"
            )

        elif parsed_file_uri.scheme in (HTTP_URI_SCHEME, HTTPS_URI_SCHEME):
            yield _workflow_http_download(tmp_dir, file_uri_or_path)

        else:
            # If we get here, we have a scheme we cannot handle; raise an error.
            raise IngestError(
                f"Cannot handle workflow output URI scheme: {parsed_file_uri.scheme}"
            )

    finally:
        # Clean up the temporary directory if necessary
        if should_del and tmp_dir:
            shutil.rmtree(tmp_dir)


def ingest_experiments_workflow(workflow_outputs, table_id):
    with _workflow_file_output_to_path(
        _get_output_or_raise(workflow_outputs, "json_document")
    ) as json_doc_path:
        logger.info(f"Attempting ingestion of experiments from path: {json_doc_path}")
        with open(json_doc_path, "r") as jf:
            json_data = json.load(jf)

            dataset = TableOwnership.objects.get(table_id=table_id).dataset

            for rs in json_data.get("resources", []):
                dataset.additional_resources.add(ingest_resource(rs))

            return [
                ingest_experiment(exp, table_id)
                for exp in json_data.get("experiments", [])
            ]


def ingest_phenopacket_workflow(workflow_outputs, table_id):
    with _workflow_file_output_to_path(
        _get_output_or_raise(workflow_outputs, "json_document")
    ) as json_doc_path:
        logger.info(f"Attempting ingestion of phenopackets from path: {json_doc_path}")
        with open(json_doc_path, "r") as jf:
            json_data = json.load(jf)
            return _map_if_list(ingest_phenopacket, json_data, table_id)


def ingest_fhir_workflow(workflow_outputs, table_id):
    with _workflow_file_output_to_path(
        _get_output_or_raise(workflow_outputs, "patients")
    ) as patients_path:
        logger.info(f"Attempting ingestion of patients from path: {patients_path}")
        with open(patients_path, "r") as pf:
            patients_data = json.load(pf)
            phenopacket_ids = ingest_patients(
                patients_data,
                table_id,
                workflow_outputs.get("created_by") or "Imported from file.",
            )

    if "observations" in workflow_outputs:
        with _workflow_file_output_to_path(
            workflow_outputs["observations"]
        ) as observations_path:
            logger.info(
                f"Attempting ingestion of observations from path: {observations_path}"
            )
            with open(observations_path, "r") as of:
                observations_data = json.load(of)
                ingest_observations(phenopacket_ids, observations_data)

    if "conditions" in workflow_outputs:
        with _workflow_file_output_to_path(
            workflow_outputs["conditions"]
        ) as conditions_path:
            logger.info(
                f"Attempting ingestion of conditions from path: {conditions_path}"
            )
            with open(conditions_path, "r") as cf:
                conditions_data = json.load(cf)
                ingest_conditions(phenopacket_ids, conditions_data)

    if "specimens" in workflow_outputs:
        with _workflow_file_output_to_path(
            workflow_outputs["specimens"]
        ) as specimens_path:
            logger.info(
                f"Attempting ingestion of specimens from path: {specimens_path}"
            )
            with open(specimens_path, "r") as sf:
                specimens_data = json.load(sf)
                ingest_specimens(phenopacket_ids, specimens_data)


# the table_id is required to fit the bento_ingest.schema.json in bento_lib
# it can be any existing table_id which can be validated
# the workflow only performs copying files over to the DRS
def ingest_readset_workflow(workflow_outputs, table_id):
    logger.info(f"Current workflow outputs : {workflow_outputs}")
    for readset_file in _get_output_or_raise(workflow_outputs, "readset_files"):
        with _workflow_file_output_to_path(readset_file) as readset_file_path:
            logger.info(
                f"Attempting ingestion of Readset file from path: {readset_file_path}"
            )


WORKFLOW_INGEST_FUNCTION_MAP = {
    WORKFLOW_EXPERIMENTS_JSON: ingest_experiments_workflow,
    WORKFLOW_PHENOPACKETS_JSON: ingest_phenopacket_workflow,
    WORKFLOW_FHIR_JSON: ingest_fhir_workflow,
    WORKFLOW_READSET: ingest_readset_workflow,
}
