import json
import uuid

from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.models import Table, TableOwnership
from chord_metadata_service.experiments import models as em
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA, EXPERIMENT_RESULT_SCHEMA
from chord_metadata_service.phenopackets import models as pm

from typing import Optional

from .logger import logger
from .resources import ingest_resource
from .schema import schema_validation
from .utils import get_output_or_raise, workflow_file_output_to_path

__all__ = [
    "ingest_experiments_workflow",
    "ingest_maf_derived_from_vcf_workflow",
]

from .exceptions import IngestError


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
        extra_properties=er.get("extra_properties", {})
    )
    er_obj.save()
    return er_obj


def ingest_experiment(experiment_data, table_id, idx: Optional[int] = None):
    """Ingests a single experiment."""

    # validate experiment data against experiments schema
    validation = schema_validation(experiment_data, EXPERIMENT_SCHEMA)
    if not validation:
        # TODO: Report more precise errors
        raise IngestError(
            f"Failed schema validation for experiment{(' ' + str(idx)) if idx is not None else ''} "
            f"(check Katsu logs for more information)")

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
    biosample_id = experiment_data.get("biosample")
    experiment_results = experiment_data.get("experiment_results", [])
    instrument = experiment_data.get("instrument", {})
    extra_properties = experiment_data.get("extra_properties", {})

    biosample: Optional[pm.Biosample] = None

    # get existing biosample id
    if biosample_id is not None:
        try:
            biosample = pm.Biosample.objects.get(id=biosample_id)
        except pm.Biosample.DoesNotExist as e:
            logger.error(f"Could not find biosample with ID: {biosample_id}")
            raise e

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
        table=Table.objects.get(ownership_record_id=table_id, data_type=DATA_TYPE_EXPERIMENT)
    )

    # create m2m relationships
    new_experiment.experiment_results.set(experiment_results_db)

    return new_experiment


def ingest_experiments_workflow(workflow_outputs, table_id):
    with workflow_file_output_to_path(get_output_or_raise(workflow_outputs, "json_document")) as json_doc_path:
        logger.info(f"Attempting ingestion of experiments from path: {json_doc_path}")
        with open(json_doc_path, "r") as jf:
            json_data = json.load(jf)

    dataset = TableOwnership.objects.get(table_id=table_id).dataset

    for rs in json_data.get("resources", []):
        dataset.additional_resources.add(ingest_resource(rs))

    return [ingest_experiment(exp, table_id, idx=idx) for idx, exp in enumerate(json_data.get("experiments", []))]


def ingest_derived_experiment_results(json_data):
    """ Reads a JSON file containing a list of experiment results and adds them
        to the database.
        The linkage to experiments is inferred from the `derived_from` category
        in `extra_properties`
    """

    exp_res_list = []
    # Create a map of experiment results identifier to experiment id.
    # Prefetch results due to the many-to-many relationship
    exp = em.Experiment.objects.all().prefetch_related("experiment_results")
    exp_result2exp = dict()
    for row in exp.values("id", "experiment_results__identifier"):
        exp_result2exp[row["experiment_results__identifier"]] = row["id"]

    for idx, exp_result in enumerate(json_data):
        validation = schema_validation(exp_result, EXPERIMENT_RESULT_SCHEMA)
        if not validation:
            # TODO: Report more precise errors
            raise IngestError(
                f"Failed schema validation for experiment result {idx} "
                f"(check Katsu logs for more information)")

        derived_identifier = exp_result['extra_properties']['derived_from']
        experiment_id = exp_result2exp.get(derived_identifier, None)
        if experiment_id is None:
            logger.warning(f"{exp_result['file_format']} file {exp_result['filename']} derived from \
                file {derived_identifier} could not be associated with an experiment.")
            continue

        new_experiment_results = em.ExperimentResult.objects.create(**exp_result)

        # Add experiment results to the parent experiment (as a many-to-many
        # relationship)
        exp = em.Experiment.objects.get(pk=experiment_id)
        exp.experiment_results.add(new_experiment_results)

        exp_res_list.append(new_experiment_results)

    return exp_res_list


# The table_id is required to fit the bento_ingest.schema.json in bento_lib,
# but it is unused. It can be set to any valid table_id or to one of the override
# values defined in view_ingest.py
def ingest_maf_derived_from_vcf_workflow(workflow_outputs, table_id):
    with workflow_file_output_to_path(get_output_or_raise(workflow_outputs, "json_document")) as json_doc_path:
        logger.info(f"Attempting ingestion of MAF-derived-from-VCF JSON from path: {json_doc_path}")
        with open(json_doc_path, "r") as fh:
            json_data = json.load(fh)

    return ingest_derived_experiment_results(json_data)
