from uuid import uuid4
from django.test import TransactionTestCase, TestCase
from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET

from chord_metadata_service.chord.models import Dataset, Project, Table, TableOwnership
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1


class ProjectTestCase(TestCase):
    """
    Helper TransactionTestCase class that creates a Project, Dataset, TableOwnership and Table.
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
        cls.table_ownership = TableOwnership.objects.create(
            table_id=str(uuid4()),
            service_id=str(uuid4()),
            service_artifact="variant",
            dataset=cls.dataset
        )
        cls.table = Table.objects.create(
            ownership_record=cls.table_ownership,
            name="Table 1",
            data_type=DATA_TYPE_PHENOPACKET
        )
        return super().setUpTestData()
