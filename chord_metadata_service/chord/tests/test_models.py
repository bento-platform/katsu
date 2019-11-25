from django.test import TestCase
from ..models import *
from .constants import VALID_DATA_USE_1


P2_DESC = "This is a good project..."


class ProjectTest(TestCase):
    def setUp(self) -> None:
        Project.objects.create(name="Project 1", description="", data_use=VALID_DATA_USE_1)
        Project.objects.create(name="Project 2", description=P2_DESC, data_use=VALID_DATA_USE_1)

    def test_project(self):
        p1 = Project.objects.get(name="Project 1")
        p2 = Project.objects.get(name="Project 2")

        self.assertEqual(p1.description, "")
        self.assertEqual(p2.description, P2_DESC)

        self.assertDictEqual(p1.data_use, VALID_DATA_USE_1)
        self.assertDictEqual(p2.data_use, VALID_DATA_USE_1)


class DatasetTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(name="Project 1", description="", data_use=VALID_DATA_USE_1)
        Dataset.objects.create(name="Dataset 1", description="Some dataset", project=p)

    def test_dataset(self):
        p = Project.objects.get(name="Project 1")
        d = Dataset.objects.get(name="Dataset 1")

        self.assertEqual(d.description, "Some dataset")
        self.assertEqual(d.project, p)

        self.assertIn(d.dataset_id, set(d2.dataset_id for d2 in p.datasets.all()))
