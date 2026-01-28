from __future__ import annotations

import uuid
from structlog.stdlib import BoundLogger

from chord_metadata_service.chord.models import Dataset
from chord_metadata_service.experiments import models as em
from chord_metadata_service.experiments.schemas import EXPERIMENT_SCHEMA, EXPERIMENT_RESULT_SCHEMA
from chord_metadata_service.phenopackets import models as pm

from .resources import ingest_resource
from .schema import schema_validation
from .utils import get_single_ontology_term

__all__ = [
    "create_instrument",
    "create_experiment_result",
    "validate_experiment",
    "ingest_experiment",
    "ingest_experiments_workflow",
    "ingest_derived_experiment_results",
]

from .exceptions import IngestError


def create_instrument(instrument: dict) -> em.Instrument:
    instrument_obj, _ = em.Instrument.objects.get_or_create(
        identifier=instrument.get("identifier", str(uuid.uuid4()))
    )

    # Backwards compatibility for v19
    # Allows ingestion of "device" and "model" values as instrument.device
    if device := instrument.get("device"):
        instrument_obj.device = device
    elif model := instrument.get("model"):
        instrument_obj.device = model

    instrument_obj.device = instrument.get("device")
    instrument_obj.device_ontology = instrument.get("device_ontology")
    instrument_obj.description = instrument.get("description")
    instrument_obj.extra_properties = instrument.get("extra_properties", {})
    instrument_obj.save()
    return instrument_obj


def create_experiment_result(er: dict) -> em.ExperimentResult:
    er_obj = em.ExperimentResult(
        identifier=er.get("identifier"),
        description=er.get("description"),
        filename=er.get("filename"),
        url=er.get("url"),
        indices=er.get("indices", []),
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


def validate_experiment(experiment_data, lg: BoundLogger, idx: int | None = None) -> None:
    # Validate experiment data against experiments schema.
    validation = schema_validation(experiment_data, EXPERIMENT_SCHEMA, obj_idx=idx, logger=lg)
    if not validation:
        # TODO: Report more precise errors
        raise IngestError(
            f"Failed schema validation for experiment{(' ' + str(idx)) if idx is not None else ''} "
            f"(check Katsu logs for more information)")


def ingest_experiment(
    experiment_data: dict,
    dataset_id: str,
    lg: BoundLogger,
    validate: bool = True,
    idx: int | None = None,
) -> em.Experiment:
    """Ingests a single experiment."""

    if validate:
        # Validate experiment data against experiments schema prior to ingestion, if specified.
        # `validate` may be false if the experiment has already been validated.
        validate_experiment(experiment_data, lg, idx)

    new_experiment_id = experiment_data.get("id", str(uuid.uuid4()))
    description = experiment_data.get("description")
    study_type = experiment_data.get("study_type")
    experiment_type = experiment_data["experiment_type"]
    experiment_ontology = get_single_ontology_term(experiment_data, "experiment_ontology")
    molecule = experiment_data.get("molecule")
    molecule_ontology = get_single_ontology_term(experiment_data, "molecule_ontology")
    # library fields
    library_strategy = experiment_data.get("library_strategy")
    library_source = experiment_data.get("library_source")
    library_selection = experiment_data.get("library_selection")
    library_layout = experiment_data.get("library_layout")
    library_id = experiment_data.get("library_id")
    library_extract_id = experiment_data.get("library_extract_id")
    insert_size = experiment_data.get("insert_size")
    library_description = experiment_data.get("library_description")
    # protocol fields
    protocol_url = experiment_data.get("protocol_url")
    extraction_protocol = experiment_data.get("extraction_protocol")
    reference_registry_id = experiment_data.get("reference_registry_id")
    qc_flags = experiment_data.get("qc_flags", [])

    biosample_id = experiment_data.get("biosample")
    experiment_results = experiment_data.get("experiment_results", [])
    instrument = experiment_data.get("instrument", {})
    extra_properties = experiment_data.get("extra_properties", {})

    biosample: pm.Biosample | None = None

    # get existing biosample id
    if biosample_id is not None:
        try:
            biosample = pm.Biosample.objects.get(id=biosample_id)
        except pm.Biosample.DoesNotExist as e:
            lg.error("ingest_experiment: could not find biosample", biosample_id=biosample_id)
            raise e

    # create related experiment results
    experiment_results_db = [create_experiment_result(er) for er in experiment_results]

    # create related instrument
    instrument_db = create_instrument(instrument)

    # create new experiment - create(...) calls save(...), which automatically populates fts_extra
    new_experiment = em.Experiment.objects.create(
        id=new_experiment_id,
        description=description,
        study_type=study_type,
        experiment_type=experiment_type,
        experiment_ontology=experiment_ontology,
        molecule=molecule,
        molecule_ontology=molecule_ontology,
        library_strategy=library_strategy,
        library_source=library_source,
        library_selection=library_selection,
        library_layout=library_layout,
        library_id=library_id,
        library_extract_id=library_extract_id,
        insert_size=insert_size,
        protocol_url=protocol_url,
        library_description=library_description,
        extraction_protocol=extraction_protocol,
        reference_registry_id=reference_registry_id,
        qc_flags=qc_flags,
        biosample=biosample,
        instrument=instrument_db,
        extra_properties=extra_properties,
        dataset=Dataset.objects.get(identifier=dataset_id)
    )

    # create m2m relationships
    new_experiment.experiment_results.set(experiment_results_db)

    return new_experiment


def ingest_experiments_workflow(json_data, dataset_id: str, lg: BoundLogger) -> list[em.Experiment]:
    dataset = Dataset.objects.get(identifier=dataset_id)
    lg = lg.bind(project_id=str(dataset.project_id), dataset_id=dataset_id)

    for rs in json_data.get("resources", []):
        dataset.additional_resources.add(ingest_resource(rs))

    exps = json_data.get("experiments", [])

    # First, validate all experiments with the schema before creating anything in the database.
    for idx, exp in enumerate(exps):
        validate_experiment(exp, lg, idx)

    # Then, if everything passes, ingest the experiments. Don't re-do the validation in this case.
    return [ingest_experiment(exp, dataset_id, lg, validate=False) for exp in exps]


def ingest_derived_experiment_results(
    json_data: list[dict], dataset_id: str, lg: BoundLogger
) -> list[em.ExperimentResult]:
    """ Reads a JSON file containing a list of experiment results and adds them
        to the database.
        The linkage to experiments is inferred from the `derived_from` category
        in `extra_properties`
    """

    # First, validate all experiment results with the schema before creating anything in the database.

    for idx, exp_result in enumerate(json_data):
        validation = schema_validation(exp_result, EXPERIMENT_RESULT_SCHEMA, obj_idx=idx, logger=lg)
        if not validation:
            # TODO: Report more precise errors
            raise IngestError(
                f"Failed schema validation for experiment result {idx} "
                f"(check Katsu logs for more information)")

    # If everything passes, perform the actual ingestion next.

    exp_res_list: list[em.ExperimentResult] = []
    # Create a map of experiment results identifier to experiment id.
    # Prefetch results due to the many-to-many relationship
    exp = em.Experiment.objects.filter(dataset_id=dataset_id).prefetch_related("experiment_results")
    exp_result2exp = dict()
    for row in exp.values("id", "experiment_results__identifier"):
        exp_result2exp[row["experiment_results__identifier"]] = row["id"]

    for idx, exp_result in enumerate(json_data):
        derived_identifier = exp_result['extra_properties']['derived_from']
        experiment_id = exp_result2exp.get(derived_identifier, None)
        if experiment_id is None:
            lg.warning(
                "ingest_derived_experiment_results: derived file could not be associated with experiment",
                file_format=exp_result["file_format"],
                filename=exp_result["filename"],
                derived_id=derived_identifier,
            )
            continue

        new_experiment_results = em.ExperimentResult.objects.create(**exp_result)

        # Add experiment results to the parent experiment (as a many-to-many
        # relationship)
        exp = em.Experiment.objects.get(pk=experiment_id)
        exp.experiment_results.add(new_experiment_results)

        exp_res_list.append(new_experiment_results)

    return exp_res_list
