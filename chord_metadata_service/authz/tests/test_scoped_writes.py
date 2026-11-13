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
        self.instrument = ex_m.Instrument.objects.create(**ex_c.valid_instrument())
        self.exp_a = ex_m.Experiment.objects.create(**ex_c.valid_experiment(self.bs_a, self.instrument, self.ds_a))

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

        self.project = project
        self.scope_a = f"?dataset={self.ds_a.identifier}"
        self.pheno_url_a = reverse("phenopackets-list") + self.scope_a
        self.pheno_url_project = reverse("phenopackets-list") + f"?project={project.identifier}"

    def _new_phenopacket(self, **kwargs) -> dict:
        meta = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_1)
        return {
            **ph_c.valid_phenopacket(subject=self.ind_a.id, meta_data=meta.id, id="pheno:new"),
            "dataset": str(self.ds_a.identifier),
            **kwargs,
        }

    def _new_biosample(self, individual_id: str, biosample_id: str = "biosample:new") -> dict:
        return {**ph_c.valid_biosample_1(individual_id), "id": biosample_id, "individual": individual_id}

    def _make_other_project(self) -> tuple[Project, Dataset, ph_m.Phenopacket]:
        # Project 2 with dataset C, holding individual C in a phenopacket
        project_2 = Project.objects.create(title="Project 2", description="")
        ds_c = _make_dataset(project_2, "Dataset C")
        ind_c = ph_m.Individual.objects.create(**{**ph_c.VALID_INDIVIDUAL_1, "id": "patient:c"})
        meta_c = ph_m.MetaData.objects.create(**ph_c.VALID_META_DATA_2)
        pheno_c = ph_m.Phenopacket.objects.create(id="pheno:c", subject=ind_c, meta_data=meta_c, dataset=ds_c)
        return project_2, ds_c, pheno_c

    # (a) writes into another dataset

    def test_create_phenopacket_in_other_dataset_rejected(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(dataset=str(self.ds_b.identifier)))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not exist", str(r.json()))
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_move_phenopacket_to_other_dataset_rejected(self):
        r = self.one_authz_patch(
            reverse("phenopackets-detail", args=[self.pheno_a.id]) + self.scope_a,
            json={"dataset": str(self.ds_b.identifier)},
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.pheno_a.refresh_from_db()
        self.assertEqual(self.pheno_a.dataset_id, self.ds_a.identifier)

    def test_move_experiment_to_other_dataset_rejected(self):
        r = self.one_authz_patch(
            reverse("experiments-detail", args=[self.exp_a.id]) + self.scope_a,
            json={"dataset": str(self.ds_b.identifier)},
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.exp_a.refresh_from_db()
        self.assertEqual(self.exp_a.dataset_id, self.ds_a.identifier)

    def test_detach_phenopacket_from_dataset_forbidden(self):
        # Unsetting the dataset would act as a delete without the delete permission
        r = self.one_authz_patch(
            reverse("phenopackets-detail", args=[self.pheno_a.id]) + self.scope_a, json={"dataset": None}
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        self.pheno_a.refresh_from_db()
        self.assertEqual(self.pheno_a.dataset_id, self.ds_a.identifier)

    def test_detach_experiment_from_dataset_forbidden(self):
        r = self.one_authz_patch(
            reverse("experiments-detail", args=[self.exp_a.id]) + self.scope_a, json={"dataset": None}
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

    def test_create_phenopacket_with_biosample_linked_through_experiments_rejected(self):
        # Biosample without phenopackets, but with an individual and an experiment in dataset B
        bs_x = ph_m.Biosample.objects.create(**{**ph_c.valid_biosample_2(self.ind_b), "id": "biosample_id:x"})
        ex_m.Experiment.objects.create(**ex_c.valid_experiment(bs_x, self.instrument, self.ds_b, num_experiment=3))
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(biosamples=[bs_x.id]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_create_phenopacket_with_biosample_of_shared_individual_linked_outside_rejected(self):
        # The biosample's individual is shared with dataset A, but the biosample itself is only linked to dataset B (via
        # an experiment); referencing it from A would pull B's experiment into A.
        ph_m.Phenopacket.objects.create(id="pheno:b-in-a", subject=self.ind_b, meta_data=self.meta_a, dataset=self.ds_a)
        bs_x = ph_m.Biosample.objects.create(**{**ph_c.valid_biosample_2(self.ind_b), "id": "biosample_id:x"})
        ex_m.Experiment.objects.create(**ex_c.valid_experiment(bs_x, self.instrument, self.ds_b, num_experiment=3))
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(biosamples=[bs_x.id]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    # writes which stay in scope are still allowed

    def test_scoped_ingest_order(self):
        # individual (already in A) -> biosample -> experiment / phenopacket, all under dataset A's scope
        r = self.one_authz_post(reverse("biosamples-list") + self.scope_a, json=self._new_biosample(self.ind_a.id))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

        r = self.one_authz_patch(
            reverse("experiments-detail", args=[self.exp_a.id]) + self.scope_a, json={"biosample": "biosample:new"}
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(biosamples=["biosample:new"]))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_biosample_for_shared_individual(self):
        # An individual with phenopackets in both A and B may get new biosamples under either dataset's scope
        ph_m.Phenopacket.objects.create(id="pheno:b-in-a", subject=self.ind_b, meta_data=self.meta_a, dataset=self.ds_a)
        for ds, bs_id in ((self.ds_a, "biosample:new-a"), (self.ds_b, "biosample:new-b")):
            with self.subTest(dataset=ds.title):
                r = self.one_authz_post(
                    reverse("biosamples-list") + f"?dataset={ds.identifier}",
                    json=self._new_biosample(self.ind_b.id, bs_id),
                )
                self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_biosample_for_out_of_scope_individual_rejected(self):
        r = self.one_authz_post(reverse("biosamples-list") + self.scope_a, json=self._new_biosample(self.ind_b.id))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(ph_m.Biosample.objects.filter(id="biosample:new").exists())

    def test_create_phenopacket_with_biosample_of_out_of_scope_individual_rejected(self):
        # Biosample with no phenopacket or experiment, whose only link is an individual in dataset B
        bs_y = ph_m.Biosample.objects.create(**{**ph_c.valid_biosample_2(self.ind_b), "id": "biosample_id:y"})
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(biosamples=[bs_y.id]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_phenopacket_with_subject_linked_only_through_experiments(self):
        # An individual whose only dataset link is an experiment in A (through a biosample) may be referenced from A
        ind_c = ph_m.Individual.objects.create(**{**ph_c.VALID_INDIVIDUAL_1, "id": "patient:c"})
        bs_c = ph_m.Biosample.objects.create(**{**ph_c.valid_biosample_2(ind_c), "id": "biosample_id:c"})
        ex_m.Experiment.objects.create(**ex_c.valid_experiment(bs_c, self.instrument, self.ds_a, num_experiment=4))
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(subject=ind_c.id))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_update_phenopacket_with_shared_meta_data(self):
        # Metadata shared with a phenopacket in dataset B is still visible in dataset A, so it may be referenced
        self.pheno_b.meta_data = self.meta_a
        self.pheno_b.save()
        r = self.one_authz_patch(
            reverse("phenopackets-detail", args=[self.pheno_a.id]) + self.scope_a, json={"meta_data": self.meta_a.id}
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)

    def test_create_phenopacket_in_scope(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(biosamples=[self.bs_a.id]))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ph_m.Phenopacket.objects.get(id="pheno:new").dataset_id, self.ds_a.identifier)

    def test_create_phenopacket_with_orphan_subject(self):
        r = self.one_authz_post(self.pheno_url_a, json=self._new_phenopacket(subject=self.ind_orphan.id))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    # project scopes

    def test_create_phenopacket_in_project_scope(self):
        # Any dataset of the project may be written to under the project's scope
        r = self.one_authz_post(self.pheno_url_project, json=self._new_phenopacket(dataset=str(self.ds_b.identifier)))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ph_m.Phenopacket.objects.get(id="pheno:new").dataset_id, self.ds_b.identifier)

    def test_create_phenopacket_with_subject_from_other_dataset_in_project_scope(self):
        # Individual B is in dataset B, which is in the same project as dataset A
        r = self.one_authz_post(self.pheno_url_project, json=self._new_phenopacket(subject=self.ind_b.id))
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)

    def test_create_phenopacket_in_other_project_rejected(self):
        _, ds_c, _ = self._make_other_project()
        r = self.one_authz_post(self.pheno_url_project, json=self._new_phenopacket(dataset=str(ds_c.identifier)))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not exist", str(r.json()))
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_create_phenopacket_with_subject_from_other_project_rejected(self):
        _, _, pheno_c = self._make_other_project()
        r = self.one_authz_post(self.pheno_url_project, json=self._new_phenopacket(subject=pheno_c.subject_id))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("does not exist", str(r.json()))
        self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

    def test_move_phenopacket_to_other_project_rejected(self):
        _, ds_c, _ = self._make_other_project()
        r = self.one_authz_patch(
            reverse("phenopackets-detail", args=[self.pheno_a.id]) + f"?project={self.project.identifier}",
            json={"dataset": str(ds_c.identifier)},
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.pheno_a.refresh_from_db()
        self.assertEqual(self.pheno_a.dataset_id, self.ds_a.identifier)

    def test_create_phenopacket_with_invalid_project_scope_rejected(self):
        project_2, _, _ = self._make_other_project()
        for desc, scope in (
            ("non-existent project", f"?project={uuid.uuid4()}"),
            ("non-UUID project", "?project=not-a-uuid"),
            ("dataset outside of project", f"?project={project_2.identifier}&dataset={self.ds_a.identifier}"),
        ):
            with self.subTest(scope=desc):
                r = self.one_authz_post(reverse("phenopackets-list") + scope, json=self._new_phenopacket())
                self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertFalse(ph_m.Phenopacket.objects.filter(id="pheno:new").exists())

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

    def test_individual_update_response_filtered_by_scope(self):
        ph_m.Phenopacket.objects.create(id="pheno:b-in-a", subject=self.ind_b, meta_data=self.meta_a, dataset=self.ds_a)

        r = self.one_authz_patch(
            reverse("individuals-detail", args=[self.ind_b.id]) + self.scope_a, json={"sex": "MALE"}
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual([p["id"] for p in data["phenopackets"]], ["pheno:b-in-a"])
        self.assertEqual(data.get("biosamples", []), [])

    def test_individual_nested_experiments_filtered_by_scope(self):
        # dataset A's biosample also has an experiment in dataset B
        exp_b = ex_m.Experiment.objects.create(
            **ex_c.valid_experiment(self.bs_a, self.instrument, self.ds_b, num_experiment=2)
        )

        r = self.one_authz_get(reverse("individuals-detail", args=[self.ind_a.id]) + self.scope_a)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        data = r.json()
        self.assertEqual([e["id"] for e in data["biosamples"][0]["experiments"]], [self.exp_a.id])
        self.assertEqual([e["id"] for e in data["phenopackets"][0]["biosamples"][0]["experiments"]], [self.exp_a.id])

        r = self.one_authz_get(reverse("individuals-detail", args=[self.ind_a.id]))
        data = r.json()
        self.assertEqual(sorted(e["id"] for e in data["biosamples"][0]["experiments"]), [self.exp_a.id, exp_b.id])

    def test_individual_batch_nested_records_filtered_by_scope(self):
        ph_m.Phenopacket.objects.create(id="pheno:b-in-a", subject=self.ind_b, meta_data=self.meta_a, dataset=self.ds_a)

        r = self.one_authz_post(reverse("batch/individuals") + self.scope_a, json={"id": [self.ind_b.id]})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        results = r.json()
        results = results.get("results", results) if isinstance(results, dict) else results
        self.assertEqual(len(results), 1)
        self.assertEqual([p["id"] for p in results[0]["phenopackets"]], ["pheno:b-in-a"])
        self.assertEqual(results[0].get("biosamples", []), [])
