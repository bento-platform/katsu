import os
import shutil
import tempfile

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.export.cbioportal import CBIO_FILES_SET
from chord_metadata_service.chord.export.utils import EXPORT_DIR
from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON
from chord_metadata_service.logger import logger

from .constants import VALID_DATA_USE_1
from .example_ingest import EXAMPLE_INGEST_PHENOPACKET


class ExportTest(AuthzAPITestCase):
    def setUp(self) -> None:
        # Creates a test database and populate with a phenopacket test file

        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        self.study_id = str(self.d.identifier)

        self.p = WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET, self.d.identifier, logger
        )

        self.base_export_payload = {
            "format": "cbioportal",
            "object_type": "dataset",
            "object_id": self.study_id,
        }

    def test_export_cbio_no_body(self):
        # Test with no export body
        r = self.one_authz_post(reverse("export"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_cbio_no_path(self):
        # Test with no output_path: expect a tar archive to be returned
        r = self.one_authz_post(reverse("export"), json=self.base_export_payload)
        self.assertEqual(r.get('Content-Disposition'), f"attachment; filename=\"{self.study_id}.tar.gz\"")
        # TODO: More

    def test_export_cbio_with_path(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            # Test with output_path provided: expect files created in this directory
            r = self.one_authz_post(reverse("export"), json={**self.base_export_payload, "output_path": tmp_dir})
            self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
            # TODO: just write within the directory that has been provided
            export_path = os.path.join(tmp_dir, EXPORT_DIR, self.study_id)
            self.assertTrue(os.path.exists(export_path))
            for export_file in CBIO_FILES_SET:
                self.assertTrue(os.path.exists(os.path.join(export_path, export_file)))

        finally:
            shutil.rmtree(tmp_dir)

        # TODO: More

    def test_export_cbio_forbidden(self):
        r = self.one_no_authz_post(reverse("export"), json=self.base_export_payload)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
