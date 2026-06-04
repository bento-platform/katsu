import os
import shutil
import tempfile
import uuid

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.export.cbioportal import CBIO_FILES_SET
from chord_metadata_service.chord.export.utils import EXPORT_DIR
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import Project, Dataset
from chord_metadata_service.chord.ingest import WORKFLOW_INGEST_FUNCTION_MAP
from chord_metadata_service.chord.workflows.metadata import WORKFLOW_PHENOPACKETS_JSON
from chord_metadata_service.logger import logger

from .constants import VALID_DATASET_PRIMARY_CONTACT
from .example_ingest import EXAMPLE_INGEST_PHENOPACKET


class ExportTest(AuthzAPITestCase):
    def setUp(self) -> None:
        # Creates a test database and populate with a phenopacket test file

        project = Project.objects.create(title="Project 1", description="")
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Dataset 1",
            description="Some dataset",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT,
            project=str(project.identifier),
            identifier=str(uuid.uuid4()),
        )
        dataset = Dataset.from_schema(schema)
        dataset.save()
        dataset.refresh_from_db()
        self.project_id = str(project.identifier)
        self.study_id = str(dataset.identifier)

        # Ingest test phenopackets
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_PHENOPACKETS_JSON](
            EXAMPLE_INGEST_PHENOPACKET, dataset.identifier, logger
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

    def test_export_cbio_object_dne(self):
        r = self.one_authz_post(reverse("export"), json={**self.base_export_payload, "object_id": str(uuid.uuid4())})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_cbio_format_dne(self):
        r = self.one_authz_post(reverse("export"), json={**self.base_export_payload, "format": "does-not-exist"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_cbio_dne_for_project(self):
        r = self.one_authz_post(
            reverse("export"), json={**self.base_export_payload, "object_type": "project", "object_id": self.project_id}
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_export_cbio_with_path_dne(self):
        # Test with output_path provided (but it does not exist!)
        r = self.one_authz_post(reverse("export"), json={**self.base_export_payload, "output_path": "does_not_exist"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_export_cbio_forbidden(self):
        r = self.one_no_authz_post(reverse("export"), json=self.base_export_payload)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
