import json
from http import HTTPStatus

from django.conf import settings

from chord_metadata_service.mohpackets.models import (
    Biomarker,
    Comorbidity,
    Donor,
    Exposure,
    FollowUp,
    PrimaryDiagnosis,
    Radiation,
    SampleRegistration,
    Specimen,
    Surgery,
    SystemicTherapy,
    Treatment,
)
from chord_metadata_service.mohpackets.tests.endpoints.base import BaseTestCase

class DownloadClinicalDataTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.download_url = "/v3/download/clinical_data/"
        # Use user_2 who has access to all datasets for most tests
        self.authorized_token = self.user_2.token
        self.unauthorized_token = "invalid_token"

    def _post_request(self, data=None, token=None):
        """Helper method to make POST requests."""
        if data is None:
            data = {}
        if token is None:
            token = self.authorized_token
        return self.client.post(
            self.download_url,
            data=json.dumps(data),
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )

    def test_download_authorized(self):
        """
        Test that an authorized user can access the download endpoint.
        """
        response = self._post_request(token=self.authorized_token)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_download_unauthorized(self):
        """
        Test that an unauthorized user receives a 401 response.
        """
        response = self._post_request(token=self.unauthorized_token)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_download_permissions(self):
        """
        Test that users only receive data from datasets they have permission for.
        user_0 only has access to program_0
        """
        user_0_token = self.user_0.token
        authorized_datasets = settings.LOCAL_OPA_DATASET.get(user_0_token, {}).get(
            "read_datasets", []
        )
        self.assertEqual(
            authorized_datasets, [self.programs[0].program_id]
        )  # Ensure setup is correct

        response = self._post_request(token=user_0_token)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        # Check that all returned donors belong to the authorized program
        donor_program_ids = {donor["program_id"] for donor in data["donors"]}
        self.assertEqual(donor_program_ids, set(authorized_datasets))

        # Verify related data also belongs to authorized donors/programs
        donor_uuids_in_response = {
            donor["submitter_donor_id"] for donor in data["donors"]
        }
        self.assertTrue(
            all(
                pd["submitter_donor_id"] in donor_uuids_in_response
                for pd in data["primary_diagnoses"]
            )
        )
        self.assertTrue(
            all(
                sp["submitter_donor_id"] in donor_uuids_in_response
                for sp in data["specimens"]
            )
        )

    def test_download_no_filters(self):
        """
        Test downloading data with no filters applied.
        Should return all data the user is authorized for.
        """
        response = self._post_request()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        # Check counts against expected total data for user_2 (all data)
        self.assertEqual(len(data["donors"]), Donor.objects.count())
        self.assertEqual(
            len(data["primary_diagnoses"]), PrimaryDiagnosis.objects.count()
        )
        self.assertEqual(len(data["specimens"]), Specimen.objects.count())
        self.assertEqual(
            len(data["sample_registrations"]), SampleRegistration.objects.count()
        )
        self.assertEqual(len(data["treatments"]), Treatment.objects.count())
        self.assertEqual(
            len(data["systemic_therapies"]), SystemicTherapy.objects.count()
        )
        self.assertEqual(len(data["radiations"]), Radiation.objects.count())
        self.assertEqual(len(data["surgeries"]), Surgery.objects.count())
        self.assertEqual(len(data["follow_ups"]), FollowUp.objects.count())
        self.assertEqual(len(data["biomarkers"]), Biomarker.objects.count())
        self.assertEqual(len(data["comorbidities"]), Comorbidity.objects.count())
        self.assertEqual(len(data["exposures"]), Exposure.objects.count())

    def test_filter_program_id(self):
        """Test filtering by program_id."""
        program_to_filter = self.programs[0].program_id
        filters = {"program_id": [program_to_filter]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        expected_donor_count = Donor.objects.filter(
            program_id=program_to_filter
        ).count()
        self.assertEqual(len(data["donors"]), expected_donor_count)
        self.assertTrue(
            all(d["program_id"] == program_to_filter for d in data["donors"])
        )

    def test_filter_primary_site(self):
        """Test filtering by primary_site."""
        site_to_filter = self.primary_diagnoses[0].primary_site
        filters = {"primary_site": [site_to_filter]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        expected_donor_ids = set(
            PrimaryDiagnosis.objects.filter(primary_site=site_to_filter).values_list(
                "submitter_donor_id", flat=True
            )
        )
        response_donor_ids = {d["submitter_donor_id"] for d in data["donors"]}

        self.assertEqual(response_donor_ids, expected_donor_ids)
        # Verify related primary diagnoses have the correct site
        self.assertTrue(
            any(
                pd["primary_site"] == site_to_filter for pd in data["primary_diagnoses"]
            )
        )

    def test_filter_treatment_type(self):
        """Test filtering by treatment_type."""
        type_to_filter = self.treatments[0].treatment_type[
            0
        ]
        filters = {"treatment_type": [type_to_filter]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        expected_donor_ids = set(
            Treatment.objects.filter(
                treatment_type__contains=[type_to_filter]  # Use contains for ArrayField
            ).values_list("submitter_donor_id", flat=True)
        )
        response_donor_ids = {d["submitter_donor_id"] for d in data["donors"]}

        self.assertEqual(response_donor_ids, expected_donor_ids)
        # Verify related treatments contain the correct type
        self.assertTrue(
            any(type_to_filter in t["treatment_type"] for t in data["treatments"])
        )

    def test_filter_drug_name(self):
        """Test filtering by systemic_therapy_drug_name."""
        drug_to_filter = self.systemic_therapies[0].drug_name
        filters = {"systemic_therapy_drug_name": [drug_to_filter]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        expected_donor_ids = set(
            SystemicTherapy.objects.filter(drug_name=drug_to_filter).values_list(
                "submitter_donor_id", flat=True
            )
        )
        response_donor_ids = {d["submitter_donor_id"] for d in data["donors"]}

        self.assertEqual(response_donor_ids, expected_donor_ids)
        # Verify related therapies have the correct drug name
        self.assertTrue(
            any(st["drug_name"] == drug_to_filter for st in data["systemic_therapies"])
        )

    def test_filter_biosample_id(self):
        """Test filtering by biosample_id."""
        sample_reg = self.sample_registrations[0]
        program_id = sample_reg.program_id
        sample_id = sample_reg.submitter_sample_id
        biosample_id_to_filter = f"{program_id}~{sample_id}"

        filters = {"biosample_id": [biosample_id_to_filter]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        # Expect only the donor associated with this specific sample registration
        self.assertEqual(len(data["donors"]), 1)
        self.assertEqual(
            data["donors"][0]["submitter_donor_id"],
            str(sample_reg.submitter_donor_id),
        )
        self.assertEqual(
            len(data["sample_registrations"]),
            SampleRegistration.objects.filter(
                submitter_donor_id=data["donors"][0]["submitter_donor_id"]
            ).count(),
        )
        self.assertEqual(
            data["sample_registrations"][0]["submitter_sample_id"], sample_id
        )

    def test_filter_invalid_biosample_id_format(self):
        """Test filtering with an invalid biosample_id format."""
        filters = {"biosample_id": ["invalid-format"]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertIn("Invalid format for biosample_id", response.json()["error"])

    def test_filter_combined(self):
        """Test filtering by combining multiple criteria."""
        program_to_filter = self.programs[0].program_id
        site_to_filter = self.primary_diagnoses[0].primary_site

        # Find expected donors matching both criteria
        expected_donor_uuids = set(
            Donor.objects.filter(
                program_id=program_to_filter,
                primarydiagnosis__primary_site=site_to_filter,
            ).values_list("submitter_donor_id", flat=True)
        )

        filters = {"program_id": [program_to_filter], "primary_site": [site_to_filter]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        response_donor_uuids = {d["submitter_donor_id"] for d in data["donors"]}
        self.assertEqual(response_donor_uuids, expected_donor_uuids)
        self.assertTrue(
            all(d["program_id"] == program_to_filter for d in data["donors"])
        )
        self.assertTrue(
            any(
                pd["primary_site"] == site_to_filter for pd in data["primary_diagnoses"]
            )
        )

    def test_filter_no_results(self):
        """Test filtering with criteria that match no records."""
        filters = {"program_id": ["NON_EXISTENT_PROGRAM"]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("No matching records found", response.json()["message"])

    def test_response_structure_and_content(self):
        """
        Verify the overall response structure and that related data matches filtered donors.
        """
        program_to_filter = self.programs[0].program_id
        filters = {"program_id": [program_to_filter]}
        response = self._post_request(data=filters)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = response.json()

        # Check top-level keys
        expected_keys = {
            "donors",
            "primary_diagnoses",
            "specimens",
            "sample_registrations",
            "treatments",
            "systemic_therapies",
            "radiations",
            "surgeries",
            "follow_ups",
            "biomarkers",
            "comorbidities",
            "exposures",
        }
        self.assertEqual(set(data.keys()), expected_keys)

        # Get the ID of the donors returned
        filtered_donor_ids = {donor["submitter_donor_id"] for donor in data["donors"]}

        # Verify that all items in related lists belong to the filtered donors
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["primary_diagnoses"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["specimens"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["sample_registrations"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["treatments"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["systemic_therapies"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["radiations"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["surgeries"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["follow_ups"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["biomarkers"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["comorbidities"]
            )
        )
        self.assertTrue(
            all(
                item["submitter_donor_id"] in filtered_donor_ids
                for item in data["exposures"]
            )
        )
