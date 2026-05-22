import uuid

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import DatasetV2Translation
from chord_metadata_service.chord.tests.constants import VALID_DATASET_V2_PRIMARY_CONTACT
from chord_metadata_service.phenopackets.tests.helpers import PhenoTestCase


class DatasetTranslationTest(AuthzAPITestCase, PhenoTestCase):

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

    # ---- DatasetV2Serializer language/translation behavior ----

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

    # ---- DatasetV2TranslationViewSet CRUD ----

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
