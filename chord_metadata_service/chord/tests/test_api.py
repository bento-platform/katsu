import uuid

from aioresponses import aioresponses
from django.urls import reverse
from django.test import override_settings
from rest_framework import status
from .constants import (
    VALID_PROJECT_1,
    valid_dataset,
    PROJECT_JSON_SCHEMA_MISSING_PROJECT,
    valid_project_json_schema,
)
from .helpers import ProjectTestCase, AuthzAPITestCaseWithProjectJSON
from ..models import Project, Dataset, ProjectJsonSchema
from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.discovery.tests.constants import DISCOVERY_CONFIG_TEST, DISCOVERY_CONFIG_TEST_DICT


class CreateProjectAPITest(AuthzAPITestCase):
    def setUp(self) -> None:
        self.valid_payloads = [
            VALID_PROJECT_1,
            {
                "title": "Project 2",
                "description": "",
            },
            {
                "title": "Project 3",
                "description": "Lorem",
                "discovery": DISCOVERY_CONFIG_TEST_DICT,
            }
        ]

        self.invalid_payloads = [
            {
                "title": "Project 1",
                "description": "",
                "discovery": {"fake": "prop"}  # invalid discovery
            },
            {
                "title": "aa",  # name must be at least 3 characters
                "description": "",
            },
            {
                "title": "Project 3",
                "description": "Lorem",
                "discovery": [DISCOVERY_CONFIG_TEST_DICT],  # wrapped in list
            }
        ]

    def test_create_project(self):
        for i, p in enumerate(self.valid_payloads, 1):
            r = self.one_authz_post(reverse("project-list"), json=p)
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Project.objects.count(), i)
            self.assertEqual(Project.objects.get(title=p["title"]).description, p["description"])

        self.assertEqual(Project.objects.count(), len(self.valid_payloads))

    def test_create_project_invalid(self):
        for p in self.invalid_payloads:
            r = self.one_authz_post(reverse("project-list"), json=p)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_forbidden(self):
        r = self.one_no_authz_post(reverse("project-list"), json=self.valid_payloads[0])
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class ListProjectAPITest(AuthzAPITestCaseWithProjectJSON):

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_list_projects(self):
        with aioresponses() as m:
            # Mock authorization for counts computation
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)

            r = self.client.get("/api/projects")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            res = r.json()
            self.assertEqual(len(res["results"]), 1)

            # Verify counts field exists
            project = res["results"][0]
            self.assertIn("counts", project)
            self.assertIsInstance(project["counts"], dict)

            # Verify all expected entity types are in counts
            expected_entities = ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]
            for entity in expected_entities:
                self.assertIn(entity, project["counts"])


class ProjectDetailAPITest(AuthzAPITestCaseWithProjectJSON):

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_project_detail_with_counts(self):
        with aioresponses() as m:
            # Mock authorization for the main request AND for counts computation
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)

            r = self.client.get(f"/api/projects/{self.project['identifier']}")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            project = r.json()

            # Verify counts field exists
            self.assertIn("counts", project)
            self.assertIsInstance(project["counts"], dict)

            # Verify all expected entity types are in counts
            expected_entities = ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]
            for entity in expected_entities:
                self.assertIn(entity, project["counts"])
                # Since there's no data, counts should be 0
                self.assertEqual(project["counts"][entity], 0)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_project_detail_with_bool_permissions(self):
        with aioresponses() as m:
            # Mock authorization with boolean-only permissions
            self.mock_authz_eval_result(m, self.dt_bool_eval_res)
            self.mock_authz_eval_result(m, self.dt_bool_eval_res)

            r = self.client.get(f"/api/projects/{self.project['identifier']}")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            project = r.json()

            # Verify counts field exists
            self.assertIn("counts", project)

            # With boolean permissions, counts should be booleans
            for entity in ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]:
                self.assertIn(entity, project["counts"])
                self.assertIsInstance(project["counts"][entity], bool)
                # Since there's no data, should be False
                self.assertFalse(project["counts"][entity])


class UpdateProjectTest(AuthzAPITestCaseWithProjectJSON):
    def setUp(self) -> None:
        super().setUp()
        self.update_body = {**self.without_times(self.project), "title": "Project 1!"}

    @staticmethod
    def without_times(d: dict) -> dict:
        return {k: v for k, v in d.items() if k not in ("updated", "created")}

    def test_project_update(self):
        r = self.one_authz_put(f"/api/projects/{self.project['identifier']}", json=self.update_body)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(self.without_times(r.json()), self.without_times(self.update_body))

    def test_project_update_not_found(self):
        r = self.one_authz_put("/api/projects/not-found", json=self.update_body)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_update_forbidden(self):
        r = self.one_no_authz_put(f"/api/projects/{self.project['identifier']}", json=self.update_body)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_project_discovery_put_get(self):
        # starting from VALID_PROJECT_1, which is a very basic project without a discovery configuration.

        r = self.one_authz_put(
            f"/api/projects/{self.project['identifier']}",
            json={**self.without_times(self.project), "discovery": DISCOVERY_CONFIG_TEST_DICT},
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        r = self.one_authz_get(f"/api/projects/{self.project['identifier']}")
        self.assertDictEqual(r.json()["discovery"], DISCOVERY_CONFIG_TEST.model_dump(mode="json"))


class DeleteProjectTest(AuthzAPITestCaseWithProjectJSON):
    def test_delete_project(self):
        r = self.one_authz_delete(f"/api/projects/{self.project['identifier']}")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_project_not_found(self):
        r = self.one_authz_delete("/api/projects/not-found")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_forbidden(self):
        r = self.one_no_authz_delete(f"/api/projects/{self.project['identifier']}")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class CreateDatasetTest(AuthzAPITestCaseWithProjectJSON):
    def setUp(self) -> None:
        super().setUp()

        self.valid_payloads = [
            valid_dataset(self.project["identifier"]),
            valid_dataset(self.project["identifier"], title="Dataset 2"),
            valid_dataset(self.project["identifier"], title="Dataset 3",
                             discovery=DISCOVERY_CONFIG_TEST_DICT),
        ]

        _pc = {"type": "person", "name": "X", "roles": []}
        self.invalid_payloads = [
            # Missing schema_version
            {"title": "Dataset Bad", "description": "Test",
             "primary_contact": _pc, "project": self.project["identifier"]},
            # Missing project
            {"schema_version": "1.0", "title": "Dataset Bad",
             "description": "Test", "primary_contact": _pc},
            # Missing primary_contact
            {"schema_version": "1.0", "title": "Dataset Bad",
             "description": "Test", "project": self.project["identifier"]},
        ]

    def test_create_dataset(self):
        for i, d in enumerate(self.valid_payloads, 1):
            r = self.one_authz_post("/api/datasets", json=d)
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Dataset.objects.count(), i)
            self.assertEqual(Dataset.objects.filter(title=d["title"]).first().title, d["title"])

        self.assertEqual(Dataset.objects.count(), len(self.valid_payloads))

    def test_create_dataset_invalid(self):
        for d in self.invalid_payloads:
            r = self.one_authz_post("/api/datasets", json=d)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_dataset_forbidden(self):
        r = self.one_no_authz_post("/api/datasets", json=self.valid_payloads[0])
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_dataset_discovery_put_get(self):
        r = self.one_authz_post("/api/datasets", json=valid_dataset(self.project["identifier"]))
        d = r.json()
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r = self.one_authz_put(f"/api/datasets/{d['identifier']}", json={**d, "discovery": DISCOVERY_CONFIG_TEST_DICT})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        r = self.one_authz_get(f"/api/datasets/{d['identifier']}")
        self.assertDictEqual(r.json()["discovery"], DISCOVERY_CONFIG_TEST.model_dump(mode="json"))


class DatasetListAPITest(AuthzAPITestCase, ProjectTestCase):

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_list_datasets(self):
        with aioresponses() as m:
            # Mock authorization for counts computation
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)

            r = self.client.get("/api/datasets")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            res = r.json()
            self.assertEqual(len(res["results"]), 1)

            # Verify counts_by_entity field exists
            dataset = res["results"][0]
            self.assertIn("counts_by_entity", dataset)
            self.assertIsInstance(dataset["counts_by_entity"], dict)

            # Verify all expected entity types are in counts_by_entity
            expected_entities = ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]
            for entity in expected_entities:
                self.assertIn(entity, dataset["counts_by_entity"])


class DatasetDetailAPITest(AuthzAPITestCase, ProjectTestCase):

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_dataset_detail_with_counts(self):
        with aioresponses() as m:
            # Mock authorization for the main request AND for counts computation
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)

            r = self.client.get(f"/api/datasets/{self.dataset_v2.identifier}")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            dataset = r.json()

            # Verify counts_by_entity field exists
            self.assertIn("counts_by_entity", dataset)
            self.assertIsInstance(dataset["counts_by_entity"], dict)

            # Verify all expected entity types are in counts_by_entity
            expected_entities = ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]
            for entity in expected_entities:
                self.assertIn(entity, dataset["counts_by_entity"])
                # Since there's no data, counts should be 0
                self.assertEqual(dataset["counts_by_entity"][entity], 0)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_dataset_detail_with_bool_permissions(self):
        with aioresponses() as m:
            # Mock authorization with boolean-only permissions
            self.mock_authz_eval_result(m, self.dt_bool_eval_res)
            self.mock_authz_eval_result(m, self.dt_bool_eval_res)

            r = self.client.get(f"/api/datasets/{self.dataset_v2.identifier}")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            dataset = r.json()

            # Verify counts_by_entity field exists
            self.assertIn("counts_by_entity", dataset)

            # With boolean permissions, counts should be booleans
            for entity in ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]:
                self.assertIn(entity, dataset["counts_by_entity"])
                self.assertIsInstance(dataset["counts_by_entity"][entity], bool)
                # Since there's no data, should be False
                self.assertFalse(dataset["counts_by_entity"][entity])


class UpdateDatasetTest(AuthzAPITestCase, ProjectTestCase):

    def setUp(self):
        super().setUp()

        self.project_2 = Project.objects.create(title="Project 2", description="")

        self.valid_update = {
            "schema_version": "1.0",
            "title": self.dataset_v2.title + "!",
            "description": "Updated description",
            "primary_contact": {"type": "person", "name": "Test Contact", "roles": []},
            "project": str(self.dataset_v2.project_id),
        }

    def test_update_dataset(self):
        r = self.one_authz_put(f"/api/datasets/{self.dataset_v2.identifier}", json=self.valid_update)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.dataset_v2.refresh_from_db()
        self.assertEqual(self.dataset_v2.title, self.valid_update["title"])

    def test_update_dataset_partial(self):
        r = self.one_authz_patch(
            f"/api/datasets/{self.dataset_v2.identifier}", json={"title": self.valid_update["title"]}
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.dataset_v2.refresh_from_db()
        self.assertEqual(self.dataset_v2.title, self.valid_update["title"])

    def test_update_dataset_changed_project(self):
        r = self.one_authz_put(
            f"/api/datasets/{self.dataset_v2.identifier}",
            json={
                **self.valid_update,
                "project": str(self.project_2.identifier),
            }
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        res = r.json()
        self.assertEqual(res["message"], "Bad Request")
        self.assertEqual(res["errors"][0]["message"], "Dataset project ID cannot change")

    def test_update_dataset_forbidden(self):
        r = self.one_no_authz_put(f"/api/datasets/{self.dataset_v2.identifier}", json=self.valid_update)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_dataset_not_found(self):
        r = self.one_authz_put(f"/api/datasets/{uuid.uuid4()}", json=self.valid_update)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class DeleteDatasetTest(AuthzAPITestCase, ProjectTestCase):

    def test_delete_dataset(self):
        r = self.one_authz_delete(f"/api/datasets/{self.dataset_v2.identifier}")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Dataset.DoesNotExist):  # must not exist in DB anymore
            self.dataset_v2.refresh_from_db()

    def test_delete_dataset_forbidden(self):
        r = self.one_no_authz_delete(f"/api/datasets/{self.dataset_v2.identifier}")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.dataset_v2.refresh_from_db()  # must not raise DoesNotExist

    def test_delete_dataset_not_found(self):
        r = self.client.delete(f"/api/datasets/{uuid.uuid4()}")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class CreateProjectJsonSchema(AuthzAPITestCaseWithProjectJSON):

    def setUp(self) -> None:
        super().setUp()

        # Valid payload and project_id
        self.project_json_schema_valid_payload = valid_project_json_schema(project_id=self.project["identifier"])
        # Invalid project_id
        self.project_json_schema_invalid_payload = valid_project_json_schema(project_id="an-id-that-does-not-exist")

    def test_create_project_json_schema(self):
        r = self.one_authz_post("/api/project_json_schemas", json=self.project_json_schema_valid_payload)
        r_invalid = self.one_authz_post("/api/project_json_schemas", json=self.project_json_schema_invalid_payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r_invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ProjectJsonSchema.objects.count(), 1)

    def test_create_project_json_schema_missing_project(self):
        r = self.one_authz_post("/api/project_json_schemas", json=PROJECT_JSON_SCHEMA_MISSING_PROJECT)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_project_json_schema_forbidden(self):
        r = self.one_no_authz_post("/api/project_json_schemas", json=self.project_json_schema_valid_payload)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_constraint(self):
        r = self.one_authz_post("/api/project_json_schemas", json=self.project_json_schema_valid_payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r_duplicate = self.one_authz_post("/api/project_json_schemas", json=self.project_json_schema_valid_payload)
        # used to be an IntegrityError raised; upgrade to DRF 3.15 made this a 400:
        self.assertEqual(r_duplicate.status_code, status.HTTP_400_BAD_REQUEST)


class UpdateProjectJsonSchema(AuthzAPITestCaseWithProjectJSON):

    def setUp(self) -> None:
        super().setUp()

        self.pjs = self.one_authz_post(
            "/api/project_json_schemas", json=valid_project_json_schema(project_id=self.project["identifier"])
        ).json()

        upd = valid_project_json_schema(project_id=self.project["identifier"], )
        upd["required"] = True
        self.upd = upd

    def test_update_project_json_schema(self):
        self.assertEqual(ProjectJsonSchema.objects.get(id=self.pjs['id']).required, False)
        r = self.one_authz_put(f"/api/project_json_schemas/{self.pjs['id']}", json=self.upd)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(ProjectJsonSchema.objects.get(id=self.pjs['id']).required, True)

    def test_update_project_json_schema_not_found(self):
        # don't need auth
        r = self.client.put("/api/project_json_schemas/does-not-exist", json=self.upd)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_project_json_schema_forbidden(self):
        r = self.one_no_authz_put(f"/api/project_json_schemas/{self.pjs['id']}", json=self.upd)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class DeleteProjectJsonSchema(AuthzAPITestCaseWithProjectJSON):

    def setUp(self) -> None:
        super().setUp()

        self.pjs = self.one_authz_post(
            "/api/project_json_schemas", json=valid_project_json_schema(project_id=self.project["identifier"])
        ).json()

    def test_delete_project_json_schema(self):
        r = self.one_authz_delete(f"/api/project_json_schemas/{self.pjs['id']}")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_project_json_schema_not_found(self):
        r = self.one_authz_delete("/api/project_json_schemas/does-not-exist")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_project_json_schema_forbidden(self):
        r = self.one_no_authz_delete(f"/api/project_json_schemas/{self.pjs['id']}")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
