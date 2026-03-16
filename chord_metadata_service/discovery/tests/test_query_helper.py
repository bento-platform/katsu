from django.core.exceptions import ValidationError
from django.test import TransactionTestCase, override_settings
from structlog.stdlib import get_logger

from chord_metadata_service.authz.types import DataPermissions
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.discovery.api_views import QueryHelper
from chord_metadata_service.discovery.pydantic_models import DiscoveryQuery
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope

from .constants import DISCOVERY_CONFIG_TEST


class QueryHelperTest(TransactionTestCase):

    def setUp(self):
        self.fts_query = DiscoveryQuery(fts="cancer", filters={})
        self.filters_query = DiscoveryQuery(filters={"sex": "MALE"})
        self.scope = ValidatedDiscoveryScope(project=None, dataset=None)
        self.dt_permissions = {
            DATA_TYPE_PHENOPACKET: DataPermissions(bool_=True, counts=True, data=False),
            DATA_TYPE_EXPERIMENT: DataPermissions(bool_=True, counts=True, data=False),
        }
        self.dt_permissions_full = {
            DATA_TYPE_PHENOPACKET: DataPermissions(bool_=True, counts=True, data=True),
            DATA_TYPE_EXPERIMENT: DataPermissions(bool_=True, counts=True, data=True),
        }
        self.logger = get_logger("query-helper-test")

    def test_property_methods(self):
        qh = QueryHelper(self.fts_query, self.scope, self.dt_permissions, self.logger)
        self.assertEqual(qh.scope, self.scope)
        self.assertEqual(qh.dt_permissions, self.dt_permissions)

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_empty_querying_fts(self):
        # nothing here
        qh = QueryHelper(self.fts_query, self.scope, self.dt_permissions_full, self.logger)
        qs, qe = await qh.get_query_queryset_and_queried_entities("phenopacket")
        # TODO: queried entities for FTS?
        self.assertEqual(qe, frozenset({}))

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_empty_querying_fts_forbidden(self):
        # not enough permissions
        qh = QueryHelper(self.fts_query, self.scope, self.dt_permissions, self.logger)
        with self.assertRaises(ValidationError) as e:
            await qh.get_query_queryset_and_queried_entities("phenopacket")
        self.assertEqual(
            str(e.exception),
            "['Insufficient permissions to access discovery (<ValidatedDiscoveryScope project=None dataset=None>)']",
        )

    @override_settings(CONFIG_PUBLIC=DISCOVERY_CONFIG_TEST)
    async def test_querying_filters_full_perms(self):
        # nothing here
        qh = QueryHelper(self.filters_query, self.scope, self.dt_permissions_full, self.logger)
        qs, qe = await qh.get_query_queryset_and_queried_entities("phenopacket")
        self.assertEqual(qe, frozenset({"individual"}))
