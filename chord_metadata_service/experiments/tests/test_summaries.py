from chord_metadata_service.authz.tests.helpers import PermissionsTestCaseMixin
from chord_metadata_service.chord import models as cm
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1
from chord_metadata_service.discovery.scope import ValidatedDiscoveryScope, INSTANCE_SCOPE
from ..summaries import dt_experiment_summary
from .helpers import ExperimentTestCase


class ExperimentSummaryTest(ExperimentTestCase, PermissionsTestCaseMixin):

    empty_response = {
        "count": 0,
        "data_type_specific": {
            "experiments": {
                "count": 0,
                "study_type": {},
                "experiment_type": {},
                "molecule": {},
                "library_strategy": {},
                "library_source": {},
                "library_selection": {},
                "library_layout": {},
                "extraction_protocol": {},
            },
            "experiment_results": {"count": 0, "file_format": {}, "data_output_type": {}, "usage": {}},
            "instruments": {"count": 0, "model": {}, "platform": {}},
        },
    }

    def setUp(self):
        super().setUp()

        self.empty_project = cm.Project.objects.create(title="Empty Project", description="")
        self.empty_dataset = cm.Dataset.objects.create(
            title="Empty Dataset", description="", data_use=VALID_DATA_USE_1, project=self.empty_project
        )

    async def test_summary_1_exp_no_perms_whole_instance(self):
        self.maxDiff = None

        subtest_params = [(self.permissions_none, self.empty_response), (self.permissions_bool, self.empty_response)]

        for params in subtest_params:
            with self.subTest(params=params):
                r = await dt_experiment_summary(INSTANCE_SCOPE, params[0])
                self.assertDictEqual(r, params[1])

    async def test_summary_1_exp_full_perms_whole_instance(self):
        self.maxDiff = None

        r = await dt_experiment_summary(INSTANCE_SCOPE, self.permissions_full)
        self.assertDictEqual(r, {
            "count": 1,
            "data_type_specific": {
                "experiments": {
                    "count": 1,
                    "experiment_type": {"DNA Methylation": 1},
                    "extraction_protocol": {"NGS": 1},
                    "library_layout": {"Single": 1},
                    "library_selection": {"PCR": 1},
                    "library_source": {"Genomic": 1},
                    "library_strategy": {"Bisulfite-Seq": 1},
                    "study_type": {"Whole genome Sequencing": 1},
                    "molecule": {"total RNA": 1},
                },
                "experiment_results": {"count": 0, "file_format": {}, "data_output_type": {}, "usage": {}},
                "instruments": {"count": 0, "model": {}, "platform": {}},
            }
        })

    async def test_summary_empty_project(self):
        r = await dt_experiment_summary(ValidatedDiscoveryScope(self.empty_project, None), self.permissions_full)
        self.assertDictEqual(r, self.empty_response)

    async def test_summary_empty_project_dataset(self):
        r = await dt_experiment_summary(
            ValidatedDiscoveryScope(self.empty_project, self.empty_dataset), self.permissions_full
        )
        self.assertDictEqual(r, self.empty_response)