import uuid
from django.test import override_settings
from bento_lib.discovery import DiscoveryConfig

from aioresponses import aioresponses
from django.urls import reverse
from rest_framework import status
from .constants import (
    VALID_PROJECT_1,
    valid_dataset_1,
    dats_dataset,
    VALID_DATS_CREATORS,
    INVALID_DATS_CREATORS,
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
            valid_dataset_1(self.project["identifier"]),
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 2",
                "dats_file": {},  # Valid dats_file JSON object
                "conditions_of_access": "",
            },
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 3",
                "dats_file": "{}",  # Valid dats_file JSON string
                "conditions_of_access": "somewebsite.ca",
            },
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 4",
                "dats_file": "{}",  # Valid dats_file JSON string
                "discovery": DISCOVERY_CONFIG_TEST_DICT,
            },
        ]

        self.dats_valid_payload = dats_dataset(self.project["identifier"], VALID_DATS_CREATORS)
        self.dats_invalid_payload = dats_dataset(self.project["identifier"], INVALID_DATS_CREATORS)

        self.invalid_dataset_coa = {
            **valid_dataset_1(self.project["identifier"]),
            "title": "Dataset 5",
            "conditions_of_access": None,  # Invalid condition of access; must be a string
        }

        self.invalid_payloads = [
            self.invalid_dataset_coa,
            {
                "title": "aa",
                "description": "Test Dataset",
                "project": self.project["identifier"],
            },
            {
                "title": "Dataset 1",
                "description": "Test Dataset",
                "project": None,
            },
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 4",
                "dats_file": "INVALID_JSON_STRING",
            },
            {
                **valid_dataset_1(self.project["identifier"]),
                "title": "Dataset 2",
                "data_use": {},  # Invalid data use object
            },
        ]

    def test_create_dataset(self):
        for i, d in enumerate(self.valid_payloads, 1):
            r = self.one_authz_post("/api/datasets", json=d)

            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Dataset.objects.count(), i)
            self.assertEqual(Dataset.objects.get(title=d["title"]).description, d["description"])
            self.assertDictEqual(Dataset.objects.get(title=d["title"]).data_use, d["data_use"])

        self.assertEqual(Dataset.objects.count(), len(self.valid_payloads))

    def test_create_dataset_invalid(self):
        for d in self.invalid_payloads:
            r = self.one_authz_post("/api/datasets", json=d)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_dataset_forbidden(self):
        r = self.one_no_authz_post("/api/datasets", json=self.valid_payloads[0])
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_conditions_of_access(self):
        for d in self.valid_payloads:
            r = self.one_authz_post("/api/datasets", json=d)

            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Dataset.objects.get(title=d["title"]).conditions_of_access,
                             d.get("conditions_of_access", ""))

    def test_invalid_conditions_of_access(self):
        d = self.invalid_dataset_coa
        r = self.one_authz_post("/api/datasets", json=d)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dataset_discovery_put_get(self):
        r = self.one_authz_post("/api/datasets", json=valid_dataset_1(self.project["identifier"]))
        d = r.json()
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r = self.one_authz_put(f"/api/datasets/{d['identifier']}", json={**d, "discovery": DISCOVERY_CONFIG_TEST_DICT})
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        r = self.one_authz_get(f"/api/datasets/{d['identifier']}")
        self.assertDictEqual(r.json()["discovery"], DISCOVERY_CONFIG_TEST.model_dump(mode="json"))

    def test_dats(self):
        payload = {**self.dats_valid_payload, 'dats_file': {}}

        r = self.one_authz_post('/api/datasets', json=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r_invalid = self.one_authz_post("/api/datasets", json=self.dats_invalid_payload)
        self.assertEqual(r_invalid.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(Dataset.objects.count(), 1)

        dataset_id = Dataset.objects.first().identifier

        # no auth needed for this
        response = self.client.get(f"/api/datasets/{dataset_id}/dats")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, payload['dats_file'])

        # non-existant dataset
        response = self.client.get(f"/api/datasets/{uuid.uuid4()}/dats")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # non-existant dataset (non-UUID)
        response = self.client.get("/api/datasets/does-not-exist/dats")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_dats_as_attachment(self):
        payload = {**self.dats_valid_payload, 'dats_file': {}}

        r = self.one_authz_post('/api/datasets', json=payload)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        dataset_id = Dataset.objects.first().identifier

        subtest_params = [
            ("?attachment=true", True),
            ("?attachment=false", False),
            ("?attachment=", False),
            ("", False),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                response = self.client.get(f"/api/datasets/{dataset_id}/dats{params[0]}")
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertDictEqual(response.data, payload['dats_file'])
                if params[1]:
                    self.assertEqual(
                        response.headers["Content-Disposition"],
                        f"attachment; filename=\"{dataset_id}_dats.json\""
                    )
                else:
                    self.assertNotIn("Content-Disposition", response.headers)

    def test_resources(self):
        resource = {
            "id": "NCBITaxon:2023-09-14",
            "name": "NCBI Taxonomy OBO Edition",
            "version": "2023-09-14",
            "namespace_prefix": "NCBITaxon",
            "url": "http://purl.obolibrary.org/obo/ncbitaxon/2023-09-14/ncbitaxon.owl",
            "iri_prefix": "http://purl.obolibrary.org/obo/NCBITaxon_",
        }

        r = self.one_authz_post("/api/resources", json=resource)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r = self.one_authz_post(
            "/api/datasets",
            json={
                **valid_dataset_1(self.project["identifier"]),
                "additional_resources": [resource["id"]],
            },
        )

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        dataset_id = Dataset.objects.first().identifier
        r = self.client.get(f"/api/datasets/{dataset_id}/resources")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data), 1)
        self.assertEqual(r.data[0]["id"], resource["id"])

        # non-existant dataset
        r = self.client.get(f"/api/datasets/{uuid.uuid4()}/resources")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


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

            # Verify counts field exists
            dataset = res["results"][0]
            self.assertIn("counts", dataset)
            self.assertIsInstance(dataset["counts"], dict)

            # Verify all expected entity types are in counts
            expected_entities = ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]
            for entity in expected_entities:
                self.assertIn(entity, dataset["counts"])


class DatasetDetailAPITest(AuthzAPITestCase, ProjectTestCase):

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_dataset_detail_with_counts(self):
        with aioresponses() as m:
            # Mock authorization for the main request AND for counts computation
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)
            self.mock_authz_eval_result(m, self.dt_counts_eval_res)

            r = self.client.get(f"/api/datasets/{self.dataset.identifier}")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            dataset = r.json()

            # Verify counts field exists
            self.assertIn("counts", dataset)
            self.assertIsInstance(dataset["counts"], dict)

            # Verify all expected entity types are in counts
            expected_entities = ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]
            for entity in expected_entities:
                self.assertIn(entity, dataset["counts"])
                # Since there's no data, counts should be 0
                self.assertEqual(dataset["counts"][entity], 0)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    def test_dataset_detail_with_bool_permissions(self):
        with aioresponses() as m:
            # Mock authorization with boolean-only permissions
            self.mock_authz_eval_result(m, self.dt_bool_eval_res)
            self.mock_authz_eval_result(m, self.dt_bool_eval_res)

            r = self.client.get(f"/api/datasets/{self.dataset.identifier}")
            self.assertEqual(r.status_code, status.HTTP_200_OK)
            dataset = r.json()

            # Verify counts field exists
            self.assertIn("counts", dataset)

            # With boolean permissions, counts should be booleans
            for entity in ["phenopacket", "individual", "biosample", "experiment", "experiment_result"]:
                self.assertIn(entity, dataset["counts"])
                self.assertIsInstance(dataset["counts"][entity], bool)
                # Since there's no data, should be False
                self.assertFalse(dataset["counts"][entity])


class UpdateDatasetTest(AuthzAPITestCase, ProjectTestCase):

    def setUp(self):
        super().setUp()

        self.dats_invalid_payload = dats_dataset(str(self.project.identifier), INVALID_DATS_CREATORS)

        self.project_2 = Project.objects.create(title="Project 2", description="")

        self.valid_update = {
            "title": self.dataset.title + "!",
            "description": self.dataset.description,
            "data_use": self.dataset.data_use,
            "project": str(self.dataset.project.identifier),
        }

    def test_update_dataset(self):
        r = self.one_authz_put(f"/api/datasets/{self.dataset.identifier}", json=self.valid_update)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.dataset.refresh_from_db()
        self.assertEqual(self.dataset.title, self.valid_update["title"])

    def test_update_dataset_partial(self):
        r = self.one_authz_patch(
            f"/api/datasets/{self.dataset.identifier}", json={"title": self.valid_update["title"]}
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.dataset.refresh_from_db()
        self.assertEqual(self.dataset.title, self.valid_update["title"])

    def test_update_dataset_changed_project(self):
        r = self.one_authz_put(
            f"/api/datasets/{self.dataset.identifier}",
            json={
                **self.valid_update,
                "project": str(self.project_2.identifier),
            }
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        res = r.json()
        self.assertEqual(res["message"], "Bad Request")
        self.assertEqual(res["errors"][0]["message"], "Dataset project ID cannot change")

    def test_update_dataset_bad_dats_json(self):
        r = self.one_authz_put(
            f"/api/datasets/{self.dataset.identifier}",
            json={**self.valid_update, "dats_file": "asdf"},  # asdf is not JSON
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        res = r.json()
        self.assertEqual(res["message"], "Bad Request")
        self.assertEqual(
            res["errors"][0]["message"],
            (
                "Submitted dataset.dats_file data is not a valid JSON string. Make sure the string value is JSON "
                "compatible, or submit dats_file as a JSON object."
            )
        )

    def test_update_dataset_forbidden(self):
        r = self.one_no_authz_put(f"/api/datasets/{self.dataset.identifier}", json=self.valid_update)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_dataset_not_found(self):
        r = self.one_authz_put(f"/api/datasets/{uuid.uuid4()}", json=self.valid_update)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class DeleteDatasetTest(AuthzAPITestCase, ProjectTestCase):

    def test_delete_dataset(self):
        r = self.one_authz_delete(f"/api/datasets/{self.dataset.identifier}")
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Dataset.DoesNotExist):  # must not exist in DB anymore
            self.dataset.refresh_from_db()

    def test_delete_dataset_forbidden(self):
        r = self.one_no_authz_delete(f"/api/datasets/{self.dataset.identifier}")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.dataset.refresh_from_db()  # must not raise DoesNotExist

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
