from django.test import TestCase

from chord_metadata_service.chord.models import Dataset, Project
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1


class ProjectTestCase(TestCase):
    """
    Helper TransactionTestCase class that creates a Project, Dataset.
    Data is created once for the whole test case at the class level
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.project = Project.objects.create(title="Project 1", description="")
        cls.dataset = Dataset.objects.create(
            title="Dataset 1",
            description="Some dataset",
            data_use=VALID_DATA_USE_1,
            project=cls.project
        )

        return super().setUpTestData()
