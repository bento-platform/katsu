from .logger import logger
from .utils import get_output_or_raise, workflow_file_output_to_path


# the table_id is required to fit the bento_ingest.schema.json in bento_lib
# it can be any existing table_id which can be validated
# the workflow only performs copying files over to the DRS
# TODO: make a workflow to deposit files on DRS
def ingest_readset_workflow(workflow_outputs, dataset_id):
    logger.info(f"Current workflow outputs : {workflow_outputs}")
    for readset_file in get_output_or_raise(workflow_outputs, "readset_files"):
        with workflow_file_output_to_path(readset_file) as readset_file_path:
            logger.info(f"Attempting ingestion of Readset file from path: {readset_file_path}")
