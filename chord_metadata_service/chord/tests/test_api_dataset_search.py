import uuid

from aioresponses import aioresponses
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import Dataset, Project
from chord_metadata_service.chord.tests.constants import VALID_DATASET_PRIMARY_CONTACT
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, MetaData, Phenopacket
from chord_metadata_service.phenopackets.tests.constants import VALID_INDIVIDUAL_1, VALID_META_DATA_1, valid_biosample_1


def _make_dataset(*, project: Project, title: str, **fields) -> Dataset:
    schema = KatsuDatasetModel(
        schema_version="1.0",
        title=title,
        primary_contact=VALID_DATASET_PRIMARY_CONTACT,
        identifier=str(uuid.uuid4()),
        project=str(project.identifier),
        **fields,
    )
    ds = Dataset.from_schema(schema)
    ds.save()
    ds.refresh_from_db()
    return ds


class DatasetCatalogueSearchTestCase(TestCase):
    """
    Covers the search/facet/sort/pagination behaviour of GET /datasets: search (incl. diacritics), facet
    AND-across/OR-within semantics, own-facet-exclusion in facet counts, zero-count selected facet values, sort
    options, pagination, and post-migration facet column population.
    """

    @classmethod
    def setUpTestData(cls):
        cls.project_1 = Project.objects.create(title="Project One", description="")
        cls.project_2 = Project.objects.create(title="Project Two", description="")

        cls.dataset_a = _make_dataset(
            project=cls.project_1,
            title="Alpha Breast Cancer Cohort",
            description="Étude portant sur le cancer du sein",
            domain=["Oncology", "Genomics"],
            taxa=["Homo sapiens"],
            keywords=["breast cancer", "genomics"],
            license={
                "label": "CC-BY-4.0",
                "type": "Creative Commons",
                "url": "https://creativecommons.org/licenses/by/4.0/",
            },
            study_status="ONGOING",
            study_context="CLINICAL",
            program_name="Program X",
            privacy="Open",
            release_date="2024-01-01",
            last_modified="2024-06-01",
        )
        cls.dataset_b = _make_dataset(
            project=cls.project_1,
            title="Beta Rare Disease Registry",
            description="A registry for rare inherited diseases",
            domain=["Rare Disease"],
            taxa=["Mus musculus"],
            keywords=["registry"],
            study_status="COMPLETED",
            study_context="RESEARCH",
            program_name="Program Y",
            privacy="Controlled Access",
            release_date="2023-01-01",
            last_modified="2023-06-01",
        )
        cls.dataset_c = _make_dataset(
            project=cls.project_2,
            title="Gamma Unaffiliated Study",
            description="A study with no program",
            study_status="ONGOING",
            release_date="2025-01-01",
            last_modified="2025-06-01",
        )

        # Give dataset_a a single individual + biosample, so it ranks above b/c on the count-based sorts.
        individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
        biosample = Biosample.objects.create(**valid_biosample_1(individual))
        meta_data = MetaData.objects.create(**VALID_META_DATA_1)
        phenopacket = Phenopacket.objects.create(
            id="phenopacket:catalogue-test-1",
            subject=individual,
            meta_data=meta_data,
            dataset=cls.dataset_a,
        )
        phenopacket.biosamples.set([biosample])

    def setUp(self):
        self.client = APIClient()
        self.url = reverse("dataset-list")

    # ---- facet column backfill / model save() derivation ----

    def test_facet_columns_populated_on_save(self):
        self.dataset_a.refresh_from_db()
        self.assertEqual(self.dataset_a.program_name, "Program X")
        self.assertEqual(self.dataset_a.privacy, "Open")
        self.assertEqual(self.dataset_a.study_status, "ONGOING")
        self.assertEqual(self.dataset_a.study_context, "CLINICAL")
        self.assertEqual(sorted(self.dataset_a.domain), ["Genomics", "Oncology"])
        self.assertEqual(self.dataset_a.taxa_labels, ["Homo sapiens"])
        self.assertEqual(sorted(self.dataset_a.keyword_labels), ["breast cancer", "genomics"])
        self.assertEqual(self.dataset_a.license_label, "CC-BY-4.0")

        self.dataset_c.refresh_from_db()
        self.assertIsNone(self.dataset_c.program_name)
        self.assertIsNone(self.dataset_c.domain)
        self.assertIsNone(self.dataset_c.taxa_labels)
        self.assertIsNone(self.dataset_c.keyword_labels)
        self.assertIsNone(self.dataset_c.license_label)

    # ---- search ----

    def test_search_matches_title(self):
        r = self.client.get(self.url, {"q": "breast"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        titles = [row["title"] for row in r.data["results"]]
        self.assertIn(self.dataset_a.title, titles)
        self.assertNotIn(self.dataset_b.title, titles)

    def test_search_is_diacritic_insensitive(self):
        # dataset_a's description contains "Étude ... cancer", searching without accents should still match.
        r = self.client.get(self.url, {"q": "etude"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        titles = [row["title"] for row in r.data["results"]]
        self.assertIn(self.dataset_a.title, titles)

    def test_search_matches_domain_and_keywords(self):
        r = self.client.get(self.url, {"q": "oncology"})
        titles = [row["title"] for row in r.data["results"]]
        self.assertIn(self.dataset_a.title, titles)

        r = self.client.get(self.url, {"q": "registry"})
        titles = [row["title"] for row in r.data["results"]]
        self.assertIn(self.dataset_b.title, titles)

    def test_search_no_match(self):
        r = self.client.get(self.url, {"q": "nonexistent-term-xyz"})
        self.assertEqual(r.data["count"], 0)
        self.assertEqual(r.data["results"], [])

    # ---- facet filtering: AND across facets, OR within a facet ----

    def test_facet_filter_scalar(self):
        r = self.client.get(self.url, {"status": "ONGOING"})
        titles = {row["title"] for row in r.data["results"]}
        self.assertEqual(titles, {self.dataset_a.title, self.dataset_c.title})

    def test_facet_filter_or_within_facet(self):
        r = self.client.get(self.url, {"status": ["ONGOING", "COMPLETED"]})
        self.assertEqual(r.data["count"], 3)

    def test_facet_filter_and_across_facets(self):
        r = self.client.get(self.url, {"status": "ONGOING", "program": "Program X"})
        titles = {row["title"] for row in r.data["results"]}
        self.assertEqual(titles, {self.dataset_a.title})

    def test_facet_filter_array_field(self):
        r = self.client.get(self.url, {"taxon": "Homo sapiens"})
        titles = {row["title"] for row in r.data["results"]}
        self.assertEqual(titles, {self.dataset_a.title})

    def test_facet_filter_project(self):
        r = self.client.get(self.url, {"project": str(self.project_2.identifier)})
        titles = {row["title"] for row in r.data["results"]}
        self.assertEqual(titles, {self.dataset_c.title})

    # ---- facet counts: exclude own filter, include zero-count selected values (opt-in via ?include=facets) ----

    def test_facets_not_included_by_default(self):
        r = self.client.get(self.url, {"status": "ONGOING"})
        self.assertNotIn("facets", r.data)

    def test_facet_counts_exclude_own_filter(self):
        r = self.client.get(self.url, {"status": "ONGOING", "include": "facets"})
        status_facet = {row["value"]: row["count"] for row in r.data["facets"]["status"]}
        # Both options should still be present with their full (status-unfiltered) counts.
        self.assertEqual(status_facet.get("ONGOING"), 2)
        self.assertEqual(status_facet.get("COMPLETED"), 1)

    def test_facet_counts_respect_other_active_facets(self):
        r = self.client.get(self.url, {"status": "ONGOING", "include": "facets"})
        program_facet = {row["value"]: row["count"] for row in r.data["facets"]["program"]}
        # program facet is scoped by the active status=ONGOING filter, so Program Y (dataset_b, COMPLETED) is absent.
        self.assertEqual(program_facet.get("Program X"), 1)
        self.assertNotIn("Program Y", program_facet)

    def test_facet_counts_include_zero_count_selected_value(self):
        r = self.client.get(self.url, {"program": "Nonexistent Program", "include": "facets"})
        self.assertEqual(r.data["count"], 0)
        program_facet = {row["value"]: row["count"] for row in r.data["facets"]["program"]}
        self.assertEqual(program_facet.get("Nonexistent Program"), 0)
        # real programs still listed too
        self.assertIn("Program X", program_facet)

    # ---- sorting ----

    def test_sort_title_az(self):
        r = self.client.get(self.url, {"sort": "title_az"})
        titles = [row["title"] for row in r.data["results"]]
        self.assertEqual(titles, sorted(titles))

    def test_sort_created_desc(self):
        r = self.client.get(self.url, {"sort": "created_desc"})
        titles = [row["title"] for row in r.data["results"]]
        self.assertEqual(titles, [self.dataset_c.title, self.dataset_a.title, self.dataset_b.title])

    def test_sort_individuals_desc_unauthenticated_is_rejected(self):
        # individuals_desc/biosamples_desc require a real censored count, which needs an authenticated caller (see
        # DatasetCountSortTestCase below for the authenticated behavior) — an anonymous request is rejected outright
        # rather than silently served under a different sort.
        r = self.client.get(self.url, {"sort": "individuals_desc"})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_sort_falls_back_to_default(self):
        r = self.client.get(self.url, {"sort": "not-a-real-option"})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["count"], 3)

    # ---- pagination ----

    def test_pagination_defaults_and_page_size(self):
        r = self.client.get(self.url, {"page_size": 2})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data["results"]), 2)
        self.assertEqual(r.data["count"], 3)

    def test_pagination_second_page(self):
        r = self.client.get(self.url, {"page_size": 2, "page": 2})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(len(r.data["results"]), 1)

    # ---- response shape ----

    def test_response_includes_project_detail(self):
        r = self.client.get(self.url, {"q": "breast"})
        row = r.data["results"][0]
        self.assertEqual(row["project_detail"]["identifier"], str(self.project_1.identifier))
        self.assertEqual(row["project_detail"]["title"], self.project_1.title)
        self.assertIn("counts_by_entity", row)


class DatasetCountSortTestCase(AuthzAPITestCase):
    """
    Covers individuals_desc/biosamples_desc sort for authenticated requests: backed by a real per-dataset censored
    count (chord/dataset_search.py::sort_by_censored_counts), evaluated via one batched authz call rather than the
    raw DB count. Per-dataset threshold math itself belongs to discovery/censorship.py's own test suite — this only
    checks that the sort path is wired to real permissions, not a static/raw count.
    """

    def setUp(self):
        self.project = Project.objects.create(title="Count Sort Project", description="")
        self.dataset_a = _make_dataset(
            project=self.project, title="Has Data", description="Has data.", last_modified="2024-01-01"
        )
        self.dataset_b = _make_dataset(
            project=self.project, title="No Data", description="No data.", last_modified="2024-01-01"
        )
        self.dataset_c = _make_dataset(
            project=self.project, title="Also No Data", description="Also no data.", last_modified="2024-01-01"
        )

        individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
        biosample = Biosample.objects.create(**valid_biosample_1(individual))
        meta_data = MetaData.objects.create(**VALID_META_DATA_1)
        phenopacket = Phenopacket.objects.create(
            id="phenopacket:count-sort-test-1",
            subject=individual,
            meta_data=meta_data,
            dataset=self.dataset_a,
        )
        phenopacket.biosamples.set([biosample])

        # sort_by_censored_counts materializes in identifier order, so the authz mock's result rows must line up
        # with datasets sorted the same way.
        self.datasets_by_identifier = sorted(
            (self.dataset_a, self.dataset_b, self.dataset_c), key=lambda ds: str(ds.identifier)
        )

        self.url = reverse("dataset-list")
        self.auth_headers = {"HTTP_AUTHORIZATION": "Bearer test-token"}

    def test_count_sort_requires_authentication(self):
        r = self.client.get(self.url, {"sort": "individuals_desc"})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_count_sort_requires_authentication_biosamples(self):
        r = self.client.get(self.url, {"sort": "biosamples_desc"})
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_count_sort_authenticated_with_full_permissions_uses_real_counts(self):
        with aioresponses() as m:
            self.mock_authz_eval_result(m, [[True, True, True]] * 3)  # bool, counts, data — for each dataset
            r = self.client.get(self.url, {"sort": "individuals_desc"}, **self.auth_headers)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        titles = [row["title"] for row in r.data["results"]]
        self.assertEqual(titles[0], self.dataset_a.title)

    def test_count_sort_authenticated_without_permissions_censors_to_zero(self):
        with aioresponses() as m:
            self.mock_authz_eval_result(m, [[False, False, False]] * 3)
            r = self.client.get(self.url, {"sort": "individuals_desc"}, **self.auth_headers)

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # With no permissions on any dataset, every count censors to 0, so the sort falls through to its
        # identifier tie-break — dataset_a's real count of 1 must not leak through.
        expected_order = [str(ds.identifier) for ds in self.datasets_by_identifier]
        self.assertEqual([row["identifier"] for row in r.data["results"]], expected_order)
