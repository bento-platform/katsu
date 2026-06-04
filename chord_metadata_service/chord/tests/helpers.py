import uuid

from django.db.models import Model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from chord_metadata_service.authz.tests.helpers import AuthzAPITestCase
from chord_metadata_service.chord.dataset_schema import KatsuDatasetModel
from chord_metadata_service.chord.models import Dataset, Project
from chord_metadata_service.chord.tests.constants import (
    VALID_PROJECT_1,
    VALID_DATASET_PRIMARY_CONTACT,
)
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope
from chord_metadata_service.restapi.utils import remove_computed_properties


__all__ = [
    "ProjectTestCase",
    "ModelFieldsTestMixin",
    "AuthzAPITestCaseWithProjectJSON",
]


class ProjectTestCase(TestCase):
    """
    Helper TransactionTestCase class that creates a Project and Dataset.
    Data is created once for the whole test case at the class level
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.project = Project.objects.create(title="Project 1", description="")
        schema = KatsuDatasetModel(
            schema_version="1.0",
            title="Dataset 1",
            description="Some dataset",
            primary_contact=VALID_DATASET_PRIMARY_CONTACT,
            identifier=str(uuid.uuid4()),
            project=str(cls.project.identifier),
        )
        cls.dataset = Dataset.from_schema(schema)
        cls.dataset.save()
        cls.dataset.refresh_from_db()
        cls.scope = ValidatedDiscoveryScope(cls.project, cls.dataset)

        return super().setUpTestData()


class ModelFieldsTestMixin(TestCase):
    """
    Helper TestCase mixin class providing functions to test data ingestion on all fields of a model.
    """

    def assert_model_fields_list_equal(self, db_list: list[Model], ground_truths: list[dict],
                                       ignore_fields: list[str], field_maps: dict | None = None):
        """
        List wrapper for assert_model_fields_equal.
        """
        self.assertEqual(len(db_list), len(ground_truths))
        for idx, db_obj in enumerate(db_list):
            ground_truth = ground_truths[idx]
            self.assert_model_fields_equal(
                db_obj=db_obj,
                ground_truth=ground_truth,
                ignore_fields=ignore_fields,
                field_maps=field_maps
            )

    def assert_model_fields_equal(self, db_obj: Model, ground_truth: dict,
                                  ignore_fields: list[str], field_maps: dict | None = None):
        """
        Compares the fields of db_obj (exluding ignore_fields, if any) with the values of ground_truth.
        """
        model_fields = [f.name for f in db_obj._meta.get_fields() if f.name not in ignore_fields]
        for field in model_fields:
            gt_value = ground_truth.get(field)
            if gt_value and field == "extra_properties":
                # remove non-ingested computed properties from gt to compare
                gt_value = remove_computed_properties(gt_value)
            # Apply field mapping, if any
            model_field = (field_maps or {}).get(field, field)
            if gt_value:
                # we expect the db_obj to contain this ground truth value
                self.assertEqual(getattr(db_obj, model_field), gt_value)


class AuthzAPITestCaseWithProjectJSON(AuthzAPITestCase):
    def setUp(self) -> None:
        super().setUp()
        r = self.one_authz_post(reverse("project-list"), json=VALID_PROJECT_1)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.project = r.json()
