import uuid
import re

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.models import DatasetV2
from chord_metadata_service.chord.tests.constants import valid_dataset_v2
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.tests.helpers import PhenoTestCase
from chord_metadata_service.chord.data_types import DATA_TYPES, DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments.models import Experiment
from chord_metadata_service.resources.models import Resource

VALID_RESOURCE_HPO = {
    "id": "hp",
    "name": "Human Phenotype Ontology",
    "url": "http://purl.obolibrary.org/obo/hp.owl",
    "version": "2024-04-26",
    "namespace_prefix": "HP",
    "iri_prefix": "http://purl.obolibrary.org/obo/HP_",
}

VALID_RESOURCE_MONDO = {
    "id": "mondo",
    "name": "Mondo Disease Ontology",
    "url": "http://purl.obolibrary.org/obo/mondo.owl",
    "version": "2024-05-08",
    "namespace_prefix": "MONDO",
    "iri_prefix": "http://purl.obolibrary.org/obo/MONDO_",
}


class BentoDatasetsTest(AuthzAPITestCase, PhenoTestCase):

    def setUp(self) -> None:
        super().setUp()
        self.entities_by_data_type = {
            DATA_TYPE_PHENOPACKET: {
                'class': Phenopacket,
                'entity': self.phenopacket,
            },
            DATA_TYPE_EXPERIMENT: {
                'class': Experiment,
                'entity': self.experiment
            }
        }

    def test_list_datasets(self):
        r = self.client.get(reverse("chord-dataset-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(1, r.data["count"])
        self.assertEqual(self.dataset_v2.title, r.data["results"][0]["title"])

    def test_get_dataset(self):
        r = self.client.get(reverse("chord-dataset-detail", kwargs={"identifier": self.dataset_v2.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(str(self.dataset_v2.identifier), r.data["identifier"])
        self.assertEqual(self.dataset_v2.title, r.data["title"])
        self.assertEqual(str(self.project.identifier), str(r.data["project"]))

    def test_del_dataset(self):
        r = self.one_authz_delete(reverse("chord-dataset-detail", kwargs={"identifier": self.dataset_v2.identifier}))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(DatasetV2.DoesNotExist):
            self.dataset_v2.refresh_from_db()

    def test_del_dataset_forbidden(self):
        r = self.one_no_authz_delete(reverse("chord-dataset-detail", kwargs={"identifier": self.dataset_v2.identifier}))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.dataset_v2.refresh_from_db()  # confirm this still exists in database, otherwise it'll raise DoesNotExist

    def test_dataset_summary(self):
        self.maxDiff = None  # allow full assertDictEqual diff if something goes awry
        r = self.dt_authz_full_get(reverse("chord-dataset-summary", kwargs={"identifier": self.dataset_v2.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual(type(data), dict)
        self.assertDictEqual(data, {
            "phenopacket": {
                "count": 1,
                "data_type_specific": {
                    "biosamples": {
                        "count": 2,
                        "histological_diagnosis": {"Infiltrating Urothelial Carcinoma": 2},
                        "is_control_sample": {"False": 1, "True": 1},
                        "sampled_tissue": {"urinary bladder": 1, "wall of urinary bladder": 1},
                        "taxonomy": {"Homo sapiens": 2}
                    },
                    "diseases": {
                        "count": 1,
                        "term": {"Spinocerebellar ataxia 1": 1}
                    },
                    "individuals": {
                        "age": {"40": 1},
                        "count": 1,
                        "karyotypic_sex": {
                            "OTHER_KARYOTYPE": 0,
                            "UNKNOWN_KARYOTYPE": 1,
                            "XO": 0,
                            "XX": 0,
                            "XXX": 0,
                            "XXXX": 0,
                            "XXXY": 0,
                            "XXY": 0,
                            "XXYY": 0,
                            "XY": 0,
                            "XYY": 0,
                        },
                        "sex": {
                            "FEMALE": 0,
                            "MALE": 1,
                            "OTHER_SEX": 0,
                            "UNKNOWN_SEX": 0,
                        },
                        "taxonomy": {},
                    },
                    "phenotypic_features": {
                        "count": 1,
                        "type": {"Proptosis": 3},
                    },
                },
            },
            "experiment": {
                "count": 1,
                "data_type_specific": {
                    "experiment_results": {
                        "count": 0,
                        "data_output_type": {},
                        "file_format": {},
                        "usage": {}
                    },
                    "experiments": {
                        "count": 1,
                        "experiment_type": {"DNA Methylation": 1},
                        "extraction_protocol": {"NGS": 1},
                        "library_layout": {"Single": 1},
                        "library_selection": {"PCR": 1},
                        "library_source": {"Genomic": 1},
                        "library_strategy": {"Bisulfite-Seq": 1},
                        "molecule": {"total RNA": 1},
                        "study_type": {"Whole genome Sequencing": 1}
                    },
                    "instruments": {
                        "count": 0,
                        "device": {}
                    }
                },
            }
        })

    def test_dataset_summary_not_a_uuid(self):
        r = self.dt_authz_full_get(reverse("chord-dataset-summary", kwargs={"identifier": "not-a-uuid"}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_dataset_summary_not_found(self):
        r = self.dt_authz_full_get(reverse("chord-dataset-summary", kwargs={"identifier": str(uuid.uuid4())}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_dataset_data_type_summary(self):
        r = self.dt_authz_full_get(
            reverse("chord-dataset-data-type-summary", kwargs={"identifier": self.dataset_v2.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        r = self.dt_authz_full_get(
            reverse("chord-dataset-data-type-summary", kwargs={"identifier": str(uuid.uuid4())}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        r = self.dt_authz_full_get(
            reverse("chord-dataset-data-type-summary", kwargs={"identifier": "not-a-uuid"}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def _dataset_data_type_url(self, dt: str, ds_id: str = ""):
        return reverse("chord-dataset-data-type", kwargs={
            "identifier": ds_id or self.dataset_v2.identifier,
            "data_type": dt
        })

    def test_get_dataset_data_type(self):
        for dt, dt_def in DATA_TYPES.items():
            if not dt_def["queryable"]:
                continue

            with self.subTest(params=(dt, dt_def)):
                url = self._dataset_data_type_url(dt)

                r = self.dt_authz_full_get(url)
                self.assertEqual(r.status_code, status.HTTP_200_OK)
                c = r.json()
                self.assertIn("last_ingested", c)
                # Check timestamp format for last_ingested
                timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z")
                self.assertTrue(timestamp_pattern.match(c["last_ingested"]))
                del c["last_ingested"]

                self.assertDictEqual(c, {
                    "id": dt,
                    "label": "Clinical Data",
                    **DATA_TYPES[dt],
                    "queryable": True,
                    "count": 1
                })

                r = self.dt_authz_none_get(url)
                self.assertEqual(r.status_code, status.HTTP_200_OK)
                c = r.json()
                self.assertIn("last_ingested", c)
                # Check timestamp format for last_ingested
                timestamp_pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{6}Z")
                self.assertTrue(timestamp_pattern.match(c["last_ingested"]))
                del c["last_ingested"]

                self.assertDictEqual(c, {
                    "id": dt,
                    "label": "Clinical Data",
                    **DATA_TYPES[dt],
                    "queryable": True,
                    # no count - no permissions to see it
                })

    def test_get_dataset_data_type_dne(self):
        subtest_params = [
            (self._dataset_data_type_url(DATA_TYPE_PHENOPACKET, str(uuid.uuid4())), status.HTTP_404_NOT_FOUND),
            (self._dataset_data_type_url(DATA_TYPE_PHENOPACKET, "not-a-uuid"), status.HTTP_404_NOT_FOUND),
            (self._dataset_data_type_url("does-not-exist"), status.HTTP_404_NOT_FOUND),
        ]

        for params in subtest_params:
            with self.subTest(params=params):
                r = self.dt_authz_full_get(params[0])
                self.assertEqual(r.status_code, params[1])

    def test_del_dataset_data_type(self):
        for dt in DATA_TYPES:
            if not DATA_TYPES[dt]["queryable"]:
                continue

            with self.subTest(params=(dt,)):
                r = self.one_authz_delete(self._dataset_data_type_url(dt))
                self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
                with self.assertRaises(self.entities_by_data_type[dt]["class"].DoesNotExist):
                    self.entities_by_data_type[dt]["entity"].refresh_from_db()

    def test_del_dataset_data_type_forbidden(self):
        for dt in DATA_TYPES:
            if not DATA_TYPES[dt]["queryable"]:
                continue

            with self.subTest(params=(dt,)):
                r = self.one_no_authz_delete(self._dataset_data_type_url(dt))
                self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
                self.entities_by_data_type[dt]["entity"].refresh_from_db()  # Should NOT raise DoesNotExist

    def test_dataset_update(self):
        url = f"/api/datasets/{self.dataset_v2.identifier}"
        payload = {
            "schema_version": "1.0",
            "title": "Updated title",
            "description": "Updated description",
            "primary_contact": {"type": "person", "name": "Test Contact", "roles": []},
            "project": str(self.project.identifier),
        }

        r = self.one_authz_put(url, json=payload)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.dataset_v2.refresh_from_db()
        self.assertEqual(self.dataset_v2.title, payload["title"])

    def test_create_dataset_v2_auto_identifier(self):
        # DatasetV2Serializer.to_internal_value: no identifier in payload → auto-generates UUID
        r = self.one_authz_post(
            reverse("chord-dataset-list"),
            json=valid_dataset_v2(str(self.project.identifier), title="New Dataset"),
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        data = r.json()
        self.assertIn("identifier", data)
        self.assertTrue(len(data["identifier"]) > 0)

    def test_create_dataset_v2_explicit_identifier(self):
        # DatasetV2Serializer.to_internal_value: identifier provided in payload → no auto-generate
        explicit_id = str(uuid.uuid4())
        r = self.one_authz_post(
            reverse("chord-dataset-list"),
            json={**valid_dataset_v2(str(self.project.identifier), title="Explicit ID Dataset"),
                  "identifier": explicit_id},
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r.json()["identifier"], explicit_id)

    # ---- ProjectSerializer: DatasetSerializer.get_counts and DatasetV2Serializer.to_representation (no prefetch) ----

    def test_project_get_serializes_legacy_dataset_counts(self):
        # DatasetSerializer.get_counts: project GET serializes legacy Dataset, calling get_counts
        r = self.client.get(reverse("project-detail", kwargs={"pk": self.project.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertIn("datasets", data)
        self.assertEqual(len(data["datasets"]), 1)

    def test_project_get_with_language_no_prefetch(self):
        # DatasetV2Serializer.to_representation: instances nested in ProjectSerializer have no
        # prefetched_translations → falls through to DB lookup (DoesNotExist → None → English fallback)
        r = self.client.get(
            reverse("project-detail", kwargs={"pk": self.project.identifier}),
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertIn("datasets_v2", data)
        self.assertEqual(len(data["datasets_v2"]), 1)

    # ---- DatasetV2ViewSet.resources ----

    def test_get_dataset_resources(self):
        # DatasetV2ViewSet.resources: success path returns empty resource list
        r = self.client.get(reverse("chord-dataset-resources", kwargs={"identifier": self.dataset_v2.identifier}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json(), [])

    def test_get_dataset_resources_not_found(self):
        # DatasetV2ViewSet.resources: Http404 branch → 404
        r = self.client.get(reverse("chord-dataset-resources", kwargs={"identifier": str(uuid.uuid4())}))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    # ---- DatasetV2ViewSet.get_queryset project_id filter ----

    def test_list_datasets_project_filter(self):
        # DatasetV2ViewSet.get_queryset: project_id query param filters results
        r = self.client.get(reverse("chord-dataset-list") + f"?project_id={self.project.identifier}")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.data["count"], 1)

    # ---- DatasetV2ViewSet.summary ----

    def test_dataset_v2_summary(self):
        r = self.dt_authz_full_get(
            reverse("chord-dataset-v2-summary", kwargs={"identifier": self.dataset_v2.identifier})
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertIn("phenopacket", data)
        self.assertIn("experiment", data)

    def test_dataset_v2_summary_not_found(self):
        r = self.dt_authz_full_get(
            reverse("chord-dataset-v2-summary", kwargs={"identifier": str(uuid.uuid4())})
        )
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    # ---- DatasetV2Serializer._sync_schema_resources ----

    def test_create_dataset_with_resources_syncs_additional_resources(self):
        # Resources in the KatsuDatasetModel payload are upserted into additional_resources on create.
        r = self.one_authz_post(
            reverse("chord-dataset-list"),
            json={
                **valid_dataset_v2(str(self.project.identifier), title="Dataset with resources"),
                "resources": [VALID_RESOURCE_HPO, VALID_RESOURCE_MONDO],
            },
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        ds = DatasetV2.objects.get(identifier=r.json()["identifier"])
        additional = list(ds.additional_resources.values_list("id", flat=True))
        self.assertIn("HP:2024-04-26", additional)
        self.assertIn("MONDO:2024-05-08", additional)
        self.assertEqual(len(additional), 2)

        # Resources are also created in the Resource table.
        self.assertTrue(Resource.objects.filter(id="HP:2024-04-26").exists())
        self.assertTrue(Resource.objects.filter(id="MONDO:2024-05-08").exists())

    def test_create_dataset_without_resources_leaves_additional_resources_empty(self):
        r = self.one_authz_post(
            reverse("chord-dataset-list"),
            json=valid_dataset_v2(str(self.project.identifier), title="Dataset no resources"),
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        ds = DatasetV2.objects.get(identifier=r.json()["identifier"])
        self.assertEqual(ds.additional_resources.count(), 0)

    def test_update_dataset_with_resources_syncs_additional_resources(self):
        # Create without resources first, then update with resources.
        r = self.one_authz_post(
            reverse("chord-dataset-list"),
            json=valid_dataset_v2(str(self.project.identifier), title="Dataset update test"),
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        ds_id = r.json()["identifier"]

        r = self.one_authz_put(
            f"/api/datasets/{ds_id}",
            json={
                **valid_dataset_v2(str(self.project.identifier), title="Dataset update test"),
                "identifier": ds_id,
                "resources": [VALID_RESOURCE_HPO],
            },
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        ds = DatasetV2.objects.get(identifier=ds_id)
        additional = list(ds.additional_resources.values_list("id", flat=True))
        self.assertIn("HP:2024-04-26", additional)
