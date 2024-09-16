from chord_metadata_service.chord import models as cm
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.discovery.exceptions import DiscoveryScopeException
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope, INSTANCE_SCOPE


class DiscoveryScopeBuildingTestCase(ProjectTestCase):

    def setUp(self):
        self.instance_scope = INSTANCE_SCOPE
        self.project_scope = ValidatedDiscoveryScope(self.project, None)
        self.project_dataset_scope = ValidatedDiscoveryScope(self.project, self.dataset)

        self.project_2 = cm.Project.objects.create(title="Project 2", description="")

    def test_scope_getters(self):
        self.assertIsNone(self.instance_scope.project_id)
        self.assertIsNone(self.instance_scope.dataset_id)

        self.assertEqual(self.project_scope.project_id, str(self.project.identifier))
        self.assertIsNone(self.project_scope.dataset_id)

        self.assertEqual(self.project_dataset_scope.project_id, str(self.project.identifier))
        self.assertEqual(self.project_dataset_scope.dataset_id, str(self.dataset.identifier))

    def test_scope_init_fail_no_project(self):
        with self.assertRaises(DiscoveryScopeException):
            ValidatedDiscoveryScope(None, self.dataset)

    def test_scope_init_fail_wrong_parent_project(self):
        with self.assertRaises(DiscoveryScopeException):
            ValidatedDiscoveryScope(self.project_2, self.dataset)

    def test_scope_repr(self):
        subtest_params = [
            (
                self.instance_scope,
                "<ValidatedDiscoveryScope project=None dataset=None>",
            ),
            (
                self.project_scope,
                f"<ValidatedDiscoveryScope project={self.project.identifier} dataset=None>",
            ),
            (
                self.project_dataset_scope,
                f"<ValidatedDiscoveryScope project={self.project.identifier} dataset={self.dataset.identifier}>",
            ),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                self.assertEqual(repr(params[0]), params[1])

    def test_scope_authz_repr(self):
        subtest_params = [
            (self.instance_scope, {"everything": True}, None),
            (self.project_scope, {"project": str(self.project.identifier)}, None),
            (
                self.project_scope,
                {"project": str(self.project.identifier), "data_type": DATA_TYPE_PHENOPACKET},
                DATA_TYPE_PHENOPACKET,
            ),
            (
                self.project_dataset_scope,
                {"project": str(self.project.identifier), "dataset": str(self.dataset.identifier)},
                None,
            ),
            (
                self.project_dataset_scope,
                {
                    "project": str(self.project.identifier),
                    "dataset": str(self.dataset.identifier),
                    "data_type": DATA_TYPE_PHENOPACKET,
                },
                DATA_TYPE_PHENOPACKET,
            ),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                self.assertDictEqual(params[0].as_authz_resource(params[2]), params[1])
