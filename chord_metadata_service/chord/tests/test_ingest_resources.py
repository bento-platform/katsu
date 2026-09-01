from bento_lib.ontologies.common_resources import NCBI_TAXON_2025_12_03
from structlog.stdlib import get_logger
from .helpers import ProjectTestCase, ModelFieldsTestMixin
from chord_metadata_service.chord.ingest.resources import ingest_resource

logger = get_logger("test")

NCBITAXON_RESOURCE = {
    # id field is ignored
    "name": "NCBI Taxonomy OBO Edition",
    "url": "http://purl.obolibrary.org/obo/ncbitaxon.owl",
    "version": "2018-07-27",
    "namespace_prefix": "NCBITaxon",
    "iri_prefix": "http://purl.obolibrary.org/obo/NCBITaxon_",
}


class IngestResourcesTest(ProjectTestCase, ModelFieldsTestMixin):
    def test_ingest_new_resource(self):
        res = ingest_resource(NCBITAXON_RESOURCE, logger)
        res.refresh_from_db()

        self.assertEqual(res.id, "NCBITaxon:2018-07-27")
        self.assertEqual(res.name, "NCBI Taxonomy OBO Edition")
        self.assertEqual(res.url, "http://purl.obolibrary.org/obo/ncbitaxon.owl")
        self.assertEqual(res.version, "2018-07-27")
        self.assertEqual(res.namespace_prefix, "NCBITaxon")
        self.assertEqual(res.iri_prefix, "http://purl.obolibrary.org/obo/NCBITaxon_")

    def test_ingest_new_resource_from_bento_lib(self):
        res = ingest_resource(NCBI_TAXON_2025_12_03.model_dump(mode="json"), logger)
        res.refresh_from_db()

        self.assertEqual(res.id, "NCBITaxon:2025-12-03")
        self.assertEqual(res.name, NCBI_TAXON_2025_12_03.name)
        self.assertEqual(res.url, str(NCBI_TAXON_2025_12_03.url))
        self.assertEqual(res.version, NCBI_TAXON_2025_12_03.version)
        self.assertEqual(res.namespace_prefix, NCBI_TAXON_2025_12_03.namespace_prefix)
        self.assertEqual(res.iri_prefix, str(NCBI_TAXON_2025_12_03.iri_prefix))

    def test_ingest_existing_resource_as_is(self):
        res1 = ingest_resource(NCBI_TAXON_2025_12_03.model_dump(mode="json"), logger)
        res2 = ingest_resource(NCBI_TAXON_2025_12_03.model_dump(mode="json"), logger)
        self.assertEqual(res1, res2)

    def test_ingest_updated_resource(self):
        res1 = ingest_resource(NCBITAXON_RESOURCE, logger)

        res2 = ingest_resource(
            {
                **NCBITAXON_RESOURCE,
                "url": f"https://purl.obolibrary.org/obo/ncbitaxon/{NCBITAXON_RESOURCE['version']}/ncbitaxon.owl",
            },
            logger,
        )

        self.assertEqual(res1, res2)
        self.assertEqual(res1.url, "http://purl.obolibrary.org/obo/ncbitaxon.owl")
        res1.refresh_from_db()
        self.assertEqual(res1.url, "https://purl.obolibrary.org/obo/ncbitaxon/2018-07-27/ncbitaxon.owl")
