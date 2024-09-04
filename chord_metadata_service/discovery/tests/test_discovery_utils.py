from chord_metadata_service.chord import models as cm
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.discovery.exceptions import DiscoveryScopeException
from chord_metadata_service.discovery.utils import ValidatedDiscoveryScope


class DiscoveryScopeBuildingTestCase(ProjectTestCase):

    def setUp(self):
        self.instance_scope = ValidatedDiscoveryScope(None, None)
        self.project_scope = ValidatedDiscoveryScope(self.project, None)
        self.project_dataset_scope = ValidatedDiscoveryScope(self.project, self.dataset)

        self.project_2 = cm.Project.objects.create(title="Project 2", description="")

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
            (self.instance_scope, {"everything": True}),
            (self.project_scope, {"project": str(self.project.identifier)}),
            (
                self.project_dataset_scope,
                {"project": str(self.project.identifier), "dataset": str(self.dataset.identifier)},
            ),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                self.assertDictEqual(params[0].as_authz_resource(), params[1])
