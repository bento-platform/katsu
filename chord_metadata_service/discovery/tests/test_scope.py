import uuid

from chord_metadata_service.chord import models as cm
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.tests.constants import VALID_DATASET_PRIMARY_CONTACT
from chord_metadata_service.chord.tests.helpers import ProjectTestCase
from chord_metadata_service.discovery.exceptions import DiscoveryScopeException
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope, INSTANCE_SCOPE, get_discovery_scope


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

    def test_scope_eq(self):
        self.assertEqual(self.project_scope, ValidatedDiscoveryScope(self.project, None))
        self.assertEqual(INSTANCE_SCOPE, ValidatedDiscoveryScope(None, None))
        self.assertEqual(ValidatedDiscoveryScope(None, None), ValidatedDiscoveryScope(None, None))
        self.assertEqual(self.project_dataset_scope, ValidatedDiscoveryScope(self.project, self.dataset))
        self.assertNotEqual(INSTANCE_SCOPE, self.project_scope)
        self.assertNotEqual(INSTANCE_SCOPE, self.project_dataset_scope)
        self.assertNotEqual(self.project_scope, ValidatedDiscoveryScope(self.project_2, None))

    def test_scope_hash(self):
        self.assertEqual(hash(self.instance_scope), hash("|"))
        self.assertEqual(hash(self.project_scope), hash(f"{self.project.identifier}|"))
        self.assertEqual(
            hash(self.project_dataset_scope),
            hash(f"{self.project.identifier}|{self.dataset.identifier}"),
        )

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


class GetDiscoveryScopeTestCase(ProjectTestCase):
    study_id = "STUDY0002"

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        # Datasets from PCGL use the PCGL study ID (not a UUID) as their identifier
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="PCGL study",
            description="Some PCGL study",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT,
            identifier=cls.study_id,
            project=str(cls.project.identifier),
        )
        cls.study_dataset = cm.Dataset.from_schema(schema)
        cls.study_dataset.save()
        cls.other_project = cm.Project.objects.create(title="Project 2", description="")

    async def test_uuid_dataset_id(self):
        scope = await get_discovery_scope(None, str(self.dataset.identifier))
        self.assertEqual(scope, ValidatedDiscoveryScope(self.project, self.dataset))

    async def test_external_dataset_id(self):
        # project is inferred from the dataset
        scope = await get_discovery_scope(None, self.study_id)
        self.assertEqual(scope.project_id, str(self.project.identifier))
        self.assertEqual(scope.dataset_id, self.study_id)

        scope = await get_discovery_scope(str(self.project.identifier), self.study_id)
        self.assertEqual(scope.dataset_id, self.study_id)

    async def test_dataset_id_not_found(self):
        with self.assertRaises(DiscoveryScopeException) as cm_:
            await get_discovery_scope(None, "STUDY9999")
        self.assertIn("STUDY9999", cm_.exception.message["message"])

    async def test_invalid_dataset_ids(self):
        for bad_id in ("a\nb", "STUDY0002\n", "<script>", "a b", "x" * 129):
            with self.subTest(bad_id=bad_id):
                with self.assertRaises(DiscoveryScopeException) as cm_:
                    await get_discovery_scope(None, bad_id)
                self.assertNotIn(bad_id, cm_.exception.message["message"])
                self.assertIn("<invalid ID>", cm_.exception.message["message"])

    async def test_invalid_project_id(self):
        # project IDs are still UUIDs
        for bad_id in ("not-a-uuid", self.study_id):
            with self.subTest(bad_id=bad_id):
                with self.assertRaises(DiscoveryScopeException) as cm_:
                    await get_discovery_scope(bad_id, None)
                self.assertNotIn(bad_id, cm_.exception.message["message"])

    async def test_dataset_id_charset(self):
        # No "." (format suffix separator in API routes), no ":" ("<project id>:<dataset id>" separator in workflow
        # inputs), and IDs must start with a letter or digit (see DATASET_ID_REGEX)
        for bad_id in ("PCGL.STUDY1", "proj:STUDY1", "-x", "_a"):
            with self.subTest(bad_id=bad_id):
                with self.assertRaises(DiscoveryScopeException) as cm_:
                    await get_discovery_scope(None, bad_id)
                self.assertIn("<invalid ID>", cm_.exception.message["message"])

    async def test_nonexistent_project_id(self):
        with self.assertRaises(DiscoveryScopeException):
            await get_discovery_scope(str(uuid.uuid4()), self.study_id)

    async def test_dataset_in_another_project(self):
        # An existing dataset must not resolve under an existing project it does not belong to; otherwise, grants on
        # that project would apply to the dataset.
        with self.assertRaises(DiscoveryScopeException):
            await get_discovery_scope(str(self.other_project.identifier), self.study_id)
