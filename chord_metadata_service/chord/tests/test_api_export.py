import json
import os
import shutil
import tempfile

from django.urls import reverse
from chord_metadata_service.chord.export.cbioportal import CBIO_FILES_SET
from chord_metadata_service.chord.export.utils import EXPORT_DIR
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON

from .constants import VALID_DATA_USE_1
from .example_ingest import EXAMPLE_INGEST_PHENOPACKET


class ExportTest(APITestCase):
    def setUp(self) -> None:
        # Creates a test database and populate with a phenopacket test file

        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        self.study_id = str(self.d.identifier)

        self.p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](EXAMPLE_INGEST_PHENOPACKET, self.d.identifier)

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
