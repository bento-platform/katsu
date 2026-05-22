import uuid
import re

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import DatasetV2, DatasetV2Translation
from chord_metadata_service.chord.tests.constants import VALID_DATASET_V2_PRIMARY_CONTACT, valid_dataset_v2
from chord_metadata_service.phenopackets.models import Phenopacket
from chord_metadata_service.phenopackets.tests.helpers import PhenoTestCase
from chord_metadata_service.chord.data_types import DATA_TYPES, DATA_TYPE_PHENOPACKET, DATA_TYPE_EXPERIMENT
from chord_metadata_service.experiments.models import Experiment


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

    def test_get_dataset_v2_language_fallback(self):
        # DatasetV2Serializer.to_representation: language != "en", no translation → fallback "en"
        r = self.client.get(
            reverse("chord-dataset-detail", kwargs={"identifier": self.dataset_v2.identifier}),
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r["Content-Language"], "en")

    def test_get_dataset_v2_with_translation(self):
        # DatasetV2Serializer.to_representation: language != "en", translation found → uses translation
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Jeu de données fr",
            description="Description française",
            primary_contact=VALID_DATASET_V2_PRIMARY_CONTACT,
            identifier=str(self.dataset_v2.identifier),
            project=str(self.project.identifier),
        )
        translation = DatasetV2Translation.from_schema(
            schema, dataset_id=self.dataset_v2.identifier, language="fr"
        )
        translation.save()
        self.addCleanup(translation.delete)

        r = self.client.get(
            reverse("chord-dataset-detail", kwargs={"identifier": self.dataset_v2.identifier}),
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r["Content-Language"], "fr")
        self.assertEqual(r.json()["title"], "Jeu de données fr")

    def test_get_translation_has_timestamps(self):
        # DatasetV2TranslationSerializer.to_representation: adds created_at and updated_at
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Dataset Translation",
            description="Test",
            primary_contact=VALID_DATASET_V2_PRIMARY_CONTACT,
            identifier=str(self.dataset_v2.identifier),
            project=str(self.project.identifier),
        )
        translation = DatasetV2Translation.from_schema(
            schema, dataset_id=self.dataset_v2.identifier, language="de"
        )
        translation.save()
        self.addCleanup(translation.delete)

        r = self.client.get(
            reverse("chord-dataset-v2-translation-detail", kwargs={
                "identifier": self.dataset_v2.identifier,
                "language": "de",
            })
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    # ---- helpers ----

    def _translation_url(self, language: str = "") -> str:
        if language:
            return reverse("chord-dataset-v2-translation-detail", kwargs={
                "identifier": self.dataset_v2.identifier,
                "language": language,
            })
        return reverse("chord-dataset-v2-translation-list", kwargs={"identifier": self.dataset_v2.identifier})

    def _translation_payload(self, title: str = "Test Translation") -> dict:
        return {
            "schema_version": "1.0",
            "title": title,
            "description": "Test translation description",
            "primary_contact": VALID_DATASET_V2_PRIMARY_CONTACT,
            "identifier": str(self.dataset_v2.identifier),
            "project": str(self.project.identifier),
        }

    def _make_translation(self, language: str) -> DatasetV2Translation:
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title=f"Translation {language}",
            description="Test",
            primary_contact=VALID_DATASET_V2_PRIMARY_CONTACT,
            identifier=str(self.dataset_v2.identifier),
            project=str(self.project.identifier),
        )
        translation = DatasetV2Translation.from_schema(
            schema, dataset_id=self.dataset_v2.identifier, language=language
        )
        translation.save()
        return translation

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

    # ---- DatasetV2TranslationViewSet ----

    def test_list_translations(self):
        # DatasetV2TranslationViewSet.list: returns empty paginated list when no translations exist
        r = self.client.get(self._translation_url())
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json()["count"], 0)

    def test_create_translation_dataset_not_found(self):
        # DatasetV2TranslationViewSet.create: dataset DoesNotExist → 404
        url = reverse("chord-dataset-v2-translation-list", kwargs={"identifier": str(uuid.uuid4())})
        r = self.one_authz_post(url, json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_translation_forbidden(self):
        # DatasetV2TranslationViewSet.create: authz false → 403
        r = self.one_no_authz_post(self._translation_url(), json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_translation(self):
        # DatasetV2TranslationViewSet.update: success → 200
        self._make_translation("es")
        r = self.one_authz_put(self._translation_url("es"), json=self._translation_payload("Updated ES Title"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_update_translation_not_found(self):
        # DatasetV2TranslationViewSet.update: translation DoesNotExist → 404
        r = self.one_authz_put(self._translation_url("zz"), json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_translation_forbidden(self):
        # DatasetV2TranslationViewSet.update: authz false → 403
        self._make_translation("it")
        r = self.one_no_authz_put(self._translation_url("it"), json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_del_translation(self):
        # DatasetV2TranslationViewSet.destroy: success → 204, translation removed from DB
        self._make_translation("pt")
        r = self.one_authz_delete(self._translation_url("pt"))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(DatasetV2Translation.DoesNotExist):
            DatasetV2Translation.objects.get(dataset=self.dataset_v2, language="pt")

    def test_del_translation_not_found(self):
        # DatasetV2TranslationViewSet.destroy: translation DoesNotExist → 404
        r = self.one_authz_delete(self._translation_url("zz"))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_del_translation_forbidden(self):
        # DatasetV2TranslationViewSet.destroy: authz false → 403, translation still in DB
        self._make_translation("ja")
        r = self.one_no_authz_delete(self._translation_url("ja"))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(DatasetV2Translation.objects.filter(dataset=self.dataset_v2, language="ja").exists())
