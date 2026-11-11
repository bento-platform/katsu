import uuid

from django.urls import reverse
from rest_framework import status

from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import Dataset, Project
from chord_metadata_service.chord.tests.constants import VALID_DATASET_PRIMARY_CONTACT
from chord_metadata_service.experiments import models as ex_m
from chord_metadata_service.experiments.tests import constants as ex_c
from chord_metadata_service.phenopackets import models as ph_m
from chord_metadata_service.phenopackets.tests import constants as ph_c

from .helpers import AuthzAPITestCase


def _make_dataset(project: Project, title: str) -> Dataset:
    ds = Dataset.from_schema(
        KatsuDatasetModel(
            schema_version="1.0",
            title=title,
            description=title,
            primary_contact=VALID_DATASET_PRIMARY_CONTACT,
            identifier=str(uuid.uuid4()),
            project=str(project.identifier),
        )
    )
    ds.save()
    ds.refresh_from_db()
    return ds


class ScopedWriteTest(AuthzAPITestCase):
    """
    Permissions are evaluated against the scope in the query string; these tests make sure the request body of a
    create/update cannot reach outside of that scope.
    """

    def setUp(self):
        project = Project.objects.create(title="Project 1", description="")
        self.ds_a = _make_dataset(project, "Dataset A")
        self.ds_b = _make_dataset(project, "Dataset B")

        # Dataset A: individual 1 with a phenopacket, a biosample and an experiment
        self.ind_a = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_1)
        self.meta_a = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        self.pheno_a = ph_m.Phenopacket.objects.create(
            id="pheno:a", subject=self.ind_a, meta_data=self.meta_a, dataset=self.ds_a
        )
        self.bs_a = ph_m.Biosample.objects.create(**ph_c.valid_biosample_1(self.ind_a))
        self.pheno_a.biosamples.add(self.bs_a)
        instrument = ex_m.Instrument.objects.create(**ex_c.valid_instrument())
        self.exp_a = ex_m.Experiment.objects.create(**ex_c.valid_experiment(self.bs_a, instrument, self.ds_a))

        # Dataset B: the "victim" individual 2 with a phenopacket and a biosample
        self.ind_b = ph_m.Individual.objects.create(**ph_c.VALID_INDIVIDUAL_2)
        self.meta_b = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_2)
        self.pheno_b = ph_m.Phenopacket.objects.create(
            id="pheno:b", subject=self.ind_b, meta_data=self.meta_b, dataset=self.ds_b
        )
        self.bs_b = ph_m.Biosample.objects.create(**ph_c.valid_biosample_2(self.ind_b))
        self.pheno_b.biosamples.add(self.bs_b)

        # Individual without any phenopackets - not part of any dataset yet
        self.ind_orphan = ph_m.Individual.objects.create(**{**ph_c.VALID_INDIVIDUAL_1, "id": "patient:orphan"})

        self.scope_a = f"?dataset={self.ds_a.identifier}"
        self.pheno_url_a = reverse("phenopackets-list") + self.scope_a

    def _new_phenopacket(self, **kwargs) -> dict:
        meta = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        return {
            **ph_c.valid_phenopacket(subject=self.ind_a.id, meta_data=meta.id, id="pheno:new"),
            "dataset": str(self.ds_a.identifier),
            **kwargs,
        }

    # (a) writes into another dataset

    def test_create_phenopacket_in_other_dataset_forbidden(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(dataset=str(self.ds_b.identifier)))
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_move_phenopacket_to_other_dataset_forbidden(self):
        r = self.one_authz_patch(
            reverse("phenopackets-detail", args=[self.pheno_a.id]) + self.scope_a,
            json={"dataset": str(self.ds_b.identifier)},
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.pheno_a.refresh_from_db()
        self.assertEqual(self.pheno_a.dataset_id, self.ds_a.identifier)

    def test_move_experiment_to_other_dataset_forbidden(self):
        r = self.one_authz_patch(
            reverse("experiments-detail", args=[self.exp_a.id]) + self.scope_a,
            json={"dataset": str(self.ds_b.identifier)},
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.exp_a.refresh_from_db()
        self.assertEqual(self.exp_a.dataset_id, self.ds_a.identifier)

    # (b) references to objects in another dataset

    def test_create_phenopacket_with_out_of_scope_subject_rejected(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(subject=self.ind_b.id))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        # Same error as for a non-existent ID, so the response does not confirm that the ID exists
        self.assertIn("does not exist", str(r.json()))
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_create_phenopacket_with_out_of_scope_biosample_rejected(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(biosamples=[self.bs_b.id]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_create_phenopacket_with_out_of_scope_meta_data_rejected(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(meta_data=self.meta_b.id))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_patch_experiment_with_out_of_scope_biosample_rejected(self):
        r = self.one_authz_patch(
            reverse("experiments-detail", args=[self.exp_a.id]) + self.scope_a,
            json={"biosample": self.bs_b.id},
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.exp_a.refresh_from_db()
        self.assertEqual(self.exp_a.biosample_id, self.bs_a.id)

    # writes which stay in scope are still allowed

    def test_create_phenopacket_in_scope(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(biosamples=[self.bs_a.id]))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ph_m.Phenopacket.objects.get(id="pheno:new").dataset_id, self.ds_a.identifier)

    def test_create_phenopacket_with_orphan_subject(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(subject=self.ind_orphan.id))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    # nested records of shared individuals are filtered by scope

    def test_individual_nested_records_filtered_by_scope(self):
        # individual B is (legitimately) shared with dataset A through a second phenopacket
        ph_m.Phenopacket.objects.create(id="pheno:b-in-a", subject=self.ind_b, meta_data=self.meta_a, dataset=self.ds_a)

        r = self.one_authz_get(reverse("individuals-detail", args=[self.ind_b.id]) + self.scope_a)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual([p["id"] for p in data["phenopackets"]], ["pheno:b-in-a"])
        self.assertEqual(data.get("biosamples", []), [])  # empty fields are omitted

        # without a scope (whole instance), everything is still returned
        r = self.one_authz_get(reverse("individuals-detail", args=[self.ind_b.id]))
        data = r.json()
        self.assertEqual(sorted(p["id"] for p in data["phenopackets"]), ["pheno:b", "pheno:b-in-a"])
        self.assertEqual([b["id"] for b in data["biosamples"]], [self.bs_b.id])

    def test_individual_batch_nested_records_filtered_by_scope(self):
        ph_m.Phenopacket.objects.create(id="pheno:b-in-a", subject=self.ind_b, meta_data=self.meta_a, dataset=self.ds_a)

        r = self.one_authz_post(reverse("batch/individuals") + self.scope_a, json={"id": [self.ind_b.id]})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        results = r.json()
        results = results.get("results", results) if isinstance(results, dict) else results
        self.assertEqual(len(results), 1)
        self.assertEqual([p["id"] for p in results[0]["phenopackets"]], ["pheno:b-in-a"])
        self.assertEqual(results[0].get("biosamples", []), [])
