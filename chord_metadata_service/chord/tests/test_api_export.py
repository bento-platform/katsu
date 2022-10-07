import json
import os
import shutil
import tempfile
import uuid

from django.urls import reverse
from chord_metadata_service.chord.export_cbio import CBIO_FILES_SET
from chord_metadata_service.chord.export_utils import EXPORT_DIR
from rest_framework import status
from rest_framework.test import APITestCase

from ..views_ingest import METADATA_WORKFLOWS
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
# noinspection PyProtectedMember
from chord_metadata_service.chord.ingest import (
    WORKFLOW_PHENOPACKETS_JSON,
    WORKFLOW_INGEST_FUNCTION_MAP,
)

from .constants import VALID_DATA_USE_1
from .example_ingest import (
    EXAMPLE_INGEST_OUTPUTS,
)


def generate_phenopackets_ingest(table_id):
    return {
        "table_id": table_id,
        "workflow_id": "phenopackets_json",
        "workflow_metadata": METADATA_WORKFLOWS["ingestion"]["phenopackets_json"],
        "workflow_outputs": {
            "json_document": ""  # TODO
        },
        "workflow_params": {
            "json_document": ""  # TODO
        }
    }


class ExportTest(APITestCase):
    def setUp(self) -> None:
        # Creates a test database and populate with a phenopacket test file

        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        self.study_id = str(self.d.identifier)

        # TODO: Real service ID
        # table for phenopackets
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

        # table for experiments metadata
        to_exp = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(),
                                               service_artifact="experiments", dataset=self.d)
        self.t_exp = Table.objects.create(ownership_record=to_exp, name="Table 2", data_type=DATA_TYPE_EXPERIMENT)

        self.p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_OUTPUTS, self.t.identifier)

    def test_export_cbio(self):
        # Test with no export body
        r = self.client.post(reverse("export"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        try:
            tmp_dir = tempfile.mkdtemp()

            export_payload = {
                "format": "cbioportal",
                "object_type": "dataset",
                "object_id": self.study_id,
            }

            # Test with no output_path: expect a tar archive to be returned
            r = self.client.post(reverse("export"), data=json.dumps(export_payload), content_type="application/json")
            self.assertEqual(r.get('Content-Disposition'), f"attachment; filename=\"{self.study_id}.tar.gz\"")

            # Test with output_path provided: expect files created in this directory
            export_payload["output_path"] = tmp_dir

            r = self.client.post(reverse("export"), data=json.dumps(export_payload), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
            # TODO: just write within the directory that has been provided
            export_path = os.path.join(tmp_dir, EXPORT_DIR, self.study_id)
            self.assertTrue(os.path.exists(export_path))
            for export_file in CBIO_FILES_SET:
                self.assertTrue(os.path.exists(os.path.join(export_path, export_file)))

        finally:
            shutil.rmtree(tmp_dir)

        # TODO: More
