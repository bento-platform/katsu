import uuid

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import Dataset, DatasetTranslation
from chord_metadata_service.chord.tests.constants import VALID_DATASET_PRIMARY_CONTACT
from chord_metadata_service.phenopackets.tests.helpers import PhenoTestCase


class DatasetTranslationTest(AuthzAPITestCase, PhenoTestCase):

    # ---- helpers ----

    def _translation_url(self, language: str = "") -> str:
        if language:
            return reverse("dataset-translations-detail", kwargs={
                "identifier": self.dataset.identifier,
                "language": language,
            })
        return reverse("dataset-translations-list", kwargs={"identifier": self.dataset.identifier})

    def _translation_payload(self, title: str = "Test Translation") -> dict:
        return {
            "schema_version": "1.0",
            "title": title,
            "description": "Test translation description",
            "primary_contact": VALID_DATASET_PRIMARY_CONTACT,
            "identifier": str(self.dataset.identifier),
            "project": str(self.project.identifier),
        }

    def _make_translation(self, language: str) -> DatasetTranslation:
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title=f"Translation {language}",
            description="Test",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT,
            identifier=str(self.dataset.identifier),
            project=str(self.project.identifier),
        )
        translation = DatasetTranslation.from_schema(
            schema, dataset_id=self.dataset.identifier, language=language
        )
        translation.save()
        return translation

    # ---- DatasetSerializer language/translation behavior ----

    def test_get_dataset_language_fallback(self):
        # DatasetSerializer.to_representation: language != "en", no translation → fallback "en"
        r = self.client.get(
            reverse("dataset-detail", kwargs={"identifier": self.dataset.identifier}),
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r["Content-Language"], "en")

    def test_get_dataset_with_translation(self):
        # DatasetSerializer.to_representation: language != "en", translation found → uses translation
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Jeu de données fr",
            description="Description française",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT,
            identifier=str(self.dataset.identifier),
            project=str(self.project.identifier),
        )
        translation = DatasetTranslation.from_schema(
            schema, dataset_id=self.dataset.identifier, language="fr"
        )
        translation.save()
        self.addCleanup(translation.delete)

        r = self.client.get(
            reverse("dataset-detail", kwargs={"identifier": self.dataset.identifier}),
            HTTP_ACCEPT_LANGUAGE="fr",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r["Content-Language"], "fr")
        self.assertEqual(r.json()["title"], "Jeu de données fr")

    def test_get_translation_has_timestamps(self):
        # DatasetTranslationSerializer.to_representation: adds created_at and updated_at
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Dataset Translation",
            description="Test",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT,
            identifier=str(self.dataset.identifier),
            project=str(self.project.identifier),
        )
        translation = DatasetTranslation.from_schema(
            schema, dataset_id=self.dataset.identifier, language="de"
        )
        translation.save()
        self.addCleanup(translation.delete)

        r = self.client.get(
            reverse("dataset-translations-detail", kwargs={
                "identifier": self.dataset.identifier,
                "language": "de",
            })
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertIn("created_at", data)
        self.assertIn("updated_at", data)

    # ---- DatasetTranslationViewSet CRUD ----

    def test_list_translations(self):
        # DatasetTranslationViewSet.list: returns empty paginated list when no translations exist
        r = self.client.get(self._translation_url())
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json()["count"], 0)

    def test_create_translation(self):
        # DatasetTranslationViewSet.create: happy path → 201, translation saved to DB
        payload = self._translation_payload()
        payload["language"] = "fr"
        r = self.one_authz_post(self._translation_url(), json=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.addCleanup(lambda: DatasetTranslation.objects.filter(
            dataset=self.dataset, language="fr").delete())

    def test_create_translation_dataset_not_found(self):
        # DatasetTranslationViewSet.create: dataset DoesNotExist → 404
        url = reverse("dataset-translations-list", kwargs={"identifier": str(uuid.uuid4())})
        r = self.one_authz_post(url, json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_translation_forbidden(self):
        # DatasetTranslationViewSet.create: authz false → 403
        r = self.one_no_authz_post(self._translation_url(), json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_translation(self):
        # DatasetTranslationViewSet.update: success → 200
        self._make_translation("es")
        r = self.one_authz_put(self._translation_url("es"), json=self._translation_payload("Updated ES Title"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_update_translation_not_found(self):
        # DatasetTranslationViewSet.update: translation DoesNotExist → 404
        r = self.one_authz_put(self._translation_url("zz"), json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_translation_forbidden(self):
        # DatasetTranslationViewSet.update: authz false → 403
        self._make_translation("it")
        r = self.one_no_authz_put(self._translation_url("it"), json=self._translation_payload())
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_del_translation(self):
        # DatasetTranslationViewSet.destroy: success → 204, translation removed from DB
        self._make_translation("pt")
        r = self.one_authz_delete(self._translation_url("pt"))
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(DatasetTranslation.DoesNotExist):
            DatasetTranslation.objects.get(dataset=self.dataset, language="pt")

    def test_del_translation_not_found(self):
        # DatasetTranslationViewSet.destroy: translation DoesNotExist → 404
        r = self.one_authz_delete(self._translation_url("zz"))
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

    def test_del_translation_forbidden(self):
        # DatasetTranslationViewSet.destroy: authz false → 403, translation still in DB
        self._make_translation("ja")
        r = self.one_no_authz_delete(self._translation_url("ja"))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(DatasetTranslation.objects.filter(dataset=self.dataset, language="ja").exists())


ROLE_PI = "Principal Investigator"
ROLE_RESEARCHER = "Researcher"


class DatasetTranslationValidationTest(AuthzAPITestCase, PhenoTestCase):
    """Tests for translation validation: roles immutable, arrays cannot grow."""

    def _make_dataset(self, primary_contact=None, **kwargs) -> Dataset:
        contact = primary_contact or VALID_DATASET_PRIMARY_CONTACT
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title=f"Validation DS {uuid.uuid4().hex[:8]}",
            description="Test",
            primary_contact=contact,
            identifier=str(uuid.uuid4()),
            project=str(self.project.identifier),
            **kwargs,
        )
        ds = Dataset.from_schema(schema)
        ds.save()
        self.addCleanup(ds.delete)
        return ds

    def _list_url(self, dataset: Dataset) -> str:
        return reverse("dataset-translations-list", kwargs={"identifier": dataset.identifier})

    def _detail_url(self, dataset: Dataset, language: str) -> str:
        return reverse("dataset-translations-detail", kwargs={
            "identifier": dataset.identifier,
            "language": language,
        })

    def _payload(self, dataset: Dataset, primary_contact=None, **kwargs) -> dict:
        return {
            "schema_version": "1.0",
            "title": "Translated Title",
            "description": "Translated description",
            "primary_contact": primary_contact or VALID_DATASET_PRIMARY_CONTACT,
            "identifier": str(dataset.identifier),
            "project": str(self.project.identifier),
            **kwargs,
        }

    def _make_translation_in_db(
        self, dataset: Dataset, language: str, primary_contact=None, **kwargs
    ) -> DatasetTranslation:
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title=f"Translation {language}",
            description="Test",
            primary_contact=primary_contact or VALID_DATASET_PRIMARY_CONTACT,
            identifier=str(dataset.identifier),
            project=str(self.project.identifier),
            **kwargs,
        )
        t = DatasetTranslation.from_schema(schema, dataset_id=dataset.identifier, language=language)
        t.save()
        self.addCleanup(t.delete)
        return t

    # ---- Rule 1: roles immutable ----

    def test_create_translation_primary_contact_role_change_rejected(self):
        # canonical has ROLE_PI; translation sends empty roles → 400
        contact_with_role = {"type": "person", "name": "Test Contact", "roles": [ROLE_PI]}
        ds = self._make_dataset(primary_contact=contact_with_role)
        payload = self._payload(ds, language="fr")
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("primary_contact", r.json())

    def test_create_translation_primary_contact_role_added_rejected(self):
        # canonical has empty roles; translation adds ROLE_PI → 400
        ds = self._make_dataset()
        payload = self._payload(
            ds,
            primary_contact={"type": "person", "name": "Test Contact", "roles": [ROLE_PI]},
            language="fr",
        )
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("primary_contact", r.json())

    def test_create_translation_stakeholder_role_change_rejected(self):
        # canonical stakeholder has ROLE_PI; translation sends ROLE_RESEARCHER → 400
        stakeholder = {"type": "person", "name": "Stakeholder", "roles": [ROLE_PI]}
        ds = self._make_dataset(stakeholders=[stakeholder])
        payload = self._payload(
            ds,
            stakeholders=[{"type": "person", "name": "Stakeholder FR", "roles": [ROLE_RESEARCHER]}],
            language="fr",
        )
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stakeholders", r.json())

    def test_update_translation_primary_contact_role_change_rejected(self):
        # existing translation, PUT changes roles → 400
        contact_with_role = {"type": "person", "name": "Test Contact", "roles": [ROLE_PI]}
        ds = self._make_dataset(primary_contact=contact_with_role)
        self._make_translation_in_db(ds, "es", primary_contact=contact_with_role)
        payload = self._payload(ds, language="es")  # roles=[] differs from canonical ROLE_PI
        r = self.one_authz_put(self._detail_url(ds, "es"), json=payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("primary_contact", r.json())

    def test_create_translation_roles_same_ok(self):
        # same roles → 201
        contact_with_role = {"type": "person", "name": "Test Contact", "roles": [ROLE_PI]}
        ds = self._make_dataset(primary_contact=contact_with_role)
        payload = self._payload(ds, primary_contact=contact_with_role, language="fr")
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    # ---- Rule 2: arrays cannot grow ----

    def test_create_translation_keywords_grow_rejected(self):
        # canonical has 1 keyword; translation sends 2 → 400
        ds = self._make_dataset(keywords=["cancer"])
        payload = self._payload(ds, keywords=["cancer", "genomics"], language="fr")
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("keywords", r.json())

    def test_create_translation_stakeholders_grow_rejected(self):
        # canonical has 1 stakeholder; translation sends 2 → 400
        stakeholder = {"type": "person", "name": "A", "roles": [ROLE_PI]}
        ds = self._make_dataset(stakeholders=[stakeholder])
        payload = self._payload(
            ds,
            stakeholders=[
                {"type": "person", "name": "A FR", "roles": [ROLE_PI]},
                {"type": "person", "name": "B FR", "roles": [ROLE_RESEARCHER]},
            ],
            language="fr",
        )
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stakeholders", r.json())

    def test_update_translation_array_grows_rejected(self):
        # existing translation, PUT adds keyword → 400
        ds = self._make_dataset(keywords=["cancer"])
        self._make_translation_in_db(ds, "de", keywords=["Krebs"])
        payload = self._payload(ds, keywords=["Krebs", "Genomik"], language="de")
        r = self.one_authz_put(self._detail_url(ds, "de"), json=payload)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("keywords", r.json())

    def test_create_translation_array_same_size_ok(self):
        # same number of keywords → 201
        ds = self._make_dataset(keywords=["cancer"])
        payload = self._payload(ds, keywords=["cancer FR"], language="fr")
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_translation_array_shrinks_ok(self):
        # fewer keywords than canonical → 201
        ds = self._make_dataset(keywords=["cancer", "genomics"])
        payload = self._payload(ds, keywords=["cancer FR"], language="fr")
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_translation_no_arrays_ok(self):
        # canonical has keywords, translation omits them entirely → 201
        ds = self._make_dataset(keywords=["cancer"])
        payload = self._payload(ds, language="fr")
        r = self.one_authz_post(self._list_url(ds), json=payload)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
