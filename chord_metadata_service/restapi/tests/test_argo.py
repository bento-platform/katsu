from copy import deepcopy

from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.patients.tests.constants import VALID_INDIVIDUAL
from chord_metadata_service.mcode.models import (
    CancerCondition,
    TNMStaging,
    CancerRelatedProcedure,
    MedicationStatement,
    MCodePacket
)
from chord_metadata_service.mcode.tests.constants import (
    valid_cancer_condition,
    invalid_tnm_staging,
    valid_cancer_related_procedure,
    valid_medication_statement,
    valid_genetic_specimen,
)
from chord_metadata_service.restapi.argo_utils import argo_administrative_gender
from chord_metadata_service.restapi.tests.utils import get_response


class ARGOMcodepacketTest(APITestCase):
    """ Test module for testing conversion of mcodepacket to argo fields."""

    def setUp(self) -> None:
        self.subject = Individual.objects.create(**VALID_INDIVIDUAL)
        self.cancer_condition = CancerCondition.objects.create(**valid_cancer_condition())
        cancer_condition_2 = valid_cancer_condition()
        cancer_condition_2["id"] = "cancer_condition:02"
        cancer_condition_2["extra_properties"] = {
            "lymph_nodes_examined_status": "Cannot be determined",
            "age_at_diagnosis": 47
        }
        self.cancer_condition_2 = CancerCondition.objects.create(**cancer_condition_2)
        # make tnm staging valid
        # tnm staging 1 clinical
        tnm_staging = invalid_tnm_staging(self.cancer_condition_2)
        for item in ["stage_group", "primary_tumor_category", "regional_nodes_category", "distant_metastases_category"]:
            tnm_staging[item] = {
                "data_value": {
                    "id": "001",
                    "label": "test stage group"
                }
            }
        self.tnm_staging = TNMStaging.objects.create(**tnm_staging)
        # tnm staging 2 pathologic
        tnm_staging_2 = deepcopy(tnm_staging)
        tnm_staging_2["id"] = "tnm_staging:02"
        tnm_staging_2["tnm_type"] = "pathologic"
        self.tnm_staging_2 = TNMStaging.objects.create(**tnm_staging_2)
        # tnm staging 3 clinical
        tnm_staging_3 = deepcopy(tnm_staging)
        tnm_staging_3["id"] = "tnm_staging:03"
        self.tnm_staging_3 = TNMStaging.objects.create(**tnm_staging_3)

        self.cancer_related_procedure = CancerRelatedProcedure.objects.create(**valid_cancer_related_procedure())
        self.medication_statement = MedicationStatement.objects.create(**valid_medication_statement())
        self.mcodepacket = MCodePacket.objects.create(
            id="mcodepacket:01",
            subject=self.subject,
            cancer_disease_status={
                "id": "001",
                "label": "patient's condition improved"
            }
        )
        self.mcodepacket.cancer_condition.set([self.cancer_condition, self.cancer_condition_2])
        self.mcodepacket.cancer_related_procedures.set([self.cancer_related_procedure])
        self.mcodepacket.medication_statement.set([self.medication_statement])

    def test_get_argo(self):
        get_resp = self.client.get("/api/mcodepackets?format=argo")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        # donor
        self.assertEqual(get_resp_obj["composition_objects"][0]["donor"]["submitter_donor_id"], "patient:1")
        self.assertEqual(get_resp_obj["composition_objects"][0]["donor"]["gender"], "Female")
        # primary_diagnoses
        self.assertIn("Carcinosarcoma",
                      get_resp_obj["composition_objects"][0]["primary_diagnoses"][0]["cancer_type_code"]["label"])
        # tnm staging clinical
        # second primary diagnosis (cancer condition 2) has two clinical tnm stagings
        for field in ["clinical_stage_group", "clinical_t_category",
                      "clinical_n_category", "clinical_m_category"]:
            self.assertIsInstance(get_resp_obj["composition_objects"][0]["primary_diagnoses"][1][field],
                                  list)
            self.assertEqual(len(get_resp_obj["composition_objects"][0]["primary_diagnoses"][1][field]), 2)
        # tnm staging pathlogical
        for field in ["pathological_stage_group", "pathological_t_category",
                      "pathological_n_category", "pathological_m_category"]:
            self.assertIsInstance(get_resp_obj["composition_objects"][0]["primary_diagnoses"][1]["specimen"][field],
                                  list)
        # treatments
        self.assertEqual("Radiation therapy",
                         get_resp_obj["composition_objects"][0]["treatments"][0]["treatment_type"])
        self.assertIn("Betatron teleradiotherapy",
                      get_resp_obj["composition_objects"][0]["treatments"][0]["radiation_therapy_modality"]["label"])
        self.assertEqual("Mammary gland sinus",
                         get_resp_obj["composition_objects"][0]["treatments"][0]
                         ["anatomical_site_irradiated"][0]["label"])
        self.assertIn("Curative",
                      get_resp_obj["composition_objects"][0]["treatments"][0]["treatment_intent"]["label"])
        self.assertIsInstance(get_resp_obj["composition_objects"][0]["primary_diagnoses"][1]["specimen"],
                              dict)
        # therapies
        self.assertIsInstance(
            get_resp_obj["composition_objects"][0]["immunotherapies_chemotherapies_hormone_therapies"],
            list
        )
        self.assertIn(
            "Verapamil",
            get_resp_obj["composition_objects"][0]["immunotherapies_chemotherapies_hormone_therapies"][0]
            ["drug_rxnormcui"]["label"]
        )


class ARGODonorTest(APITestCase):
    """ Test module for testing conversion of individual to argo donor."""

    def setUp(self):
        self.donor = VALID_INDIVIDUAL
        valid_individual_2 = deepcopy(VALID_INDIVIDUAL)
        valid_individual_2["id"] = "patient:2"
        valid_individual_2["sex"] = "OTHER_SEX"
        # test if argo fields were saved to extra_properties
        valid_individual_2["extra_properties"] = {
            "cause_of_death": "Unknown",
            "survival_time": 2,
            "primary_site": "Breast"
        }
        self.donor_2 = valid_individual_2
        invalid_individual_3 = deepcopy(VALID_INDIVIDUAL)
        invalid_individual_3["id"] = "patient:3"
        invalid_individual_3["sex"] = "No value"
        self.donor_3 = invalid_individual_3

    def test_get_argo(self):
        create_object_response = get_response("individual-list", self.donor)
        self.assertEqual(create_object_response.status_code, status.HTTP_201_CREATED)
        get_resp = self.client.get("/api/individuals?format=argo")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        for donor in get_resp_obj["donors"]:
            self.assertIsNotNone(donor["gender"])
            self.assertIsNotNone(donor["submitter_donor_id"])
            self.assertIsNotNone(donor["vital_status"])

    def test_gender_condition_1(self):
        create_object_response = get_response("individual-list", self.donor_2)
        self.assertEqual(create_object_response.status_code, status.HTTP_201_CREATED)
        get_resp = self.client.get("/api/individuals/patient:2?format=argo")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsNotNone(get_resp_obj["gender"])
        self.assertEqual(get_resp_obj["gender"], "Other")
        self.assertEqual(get_resp_obj["submitter_donor_id"], "patient:2")
        self.assertEqual(get_resp_obj["cause_of_death"], "Unknown")
        self.assertEqual(get_resp_obj["survival_time"], 2)
        self.assertEqual(get_resp_obj["primary_site"], "Breast")

    def test_gender_condition_2(self):
        create_object_response = get_response("individual-list", self.donor_3)
        self.assertEqual(create_object_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_value_error(self):
        with self.assertRaises(ValueError):
            argo_administrative_gender(self.donor_3["sex"])


class ARGOSpecimenTest(APITestCase):
    """ Test module for testing conversion of genetic specimen to argo specimen."""

    def setUp(self):
        self.specimen = valid_genetic_specimen("specimen:01")

    def test_get_argo(self):
        create_object_response = get_response("geneticspecimen-list", self.specimen)
        self.assertEqual(create_object_response.status_code, status.HTTP_201_CREATED)
        get_resp = self.client.get("/api/geneticspecimens?format=argo")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsNotNone(get_resp_obj["specimens"][0]["submitter_specimen_id"])
        self.assertIsInstance(get_resp_obj["specimens"][0]["submitter_specimen_id"], str)
        self.assertIsNotNone(get_resp_obj["specimens"][0]["specimen_type"])
        self.assertIsInstance(get_resp_obj["specimens"][0]["specimen_type"], dict)
        self.assertIsNotNone(get_resp_obj["specimens"][0]["specimen_tissue_source"])
        self.assertIsInstance(get_resp_obj["specimens"][0]["specimen_tissue_source"], dict)
        self.assertIsNotNone(get_resp_obj["specimens"][0]["specimen_laterality"])
        self.assertIsInstance(get_resp_obj["specimens"][0]["specimen_laterality"], dict)


class ARGOPrimaryDiagnosisTest(APITestCase):
    """ Test module for testing conversion of cancer condition to argo primary diagnosis."""

    def setUp(self):
        self.primary_diagnosis = valid_cancer_condition()

    def test_get_argo(self):
        create_object_response = get_response("cancercondition-list", self.primary_diagnosis)
        self.assertEqual(create_object_response.status_code, status.HTTP_201_CREATED)
        get_resp = self.client.get("/api/cancerconditions?format=argo")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsNotNone(get_resp_obj["primary_diagnoses"][0]["submitter_primary_diagnosis_id"])
        self.assertIsInstance(get_resp_obj["primary_diagnoses"][0]["submitter_primary_diagnosis_id"], str)
        self.assertIsNotNone(get_resp_obj["primary_diagnoses"][0]["cancer_type_code"])
        self.assertIsInstance(get_resp_obj["primary_diagnoses"][0]["cancer_type_code"], dict)


class ARGOTreatmentTest(APITestCase):
    """ Test module for testing conversion of cancer related procedure to argo treatment."""

    def setUp(self):
        self.treatment = valid_cancer_related_procedure()

    def test_get_argo(self):
        create_object_response = get_response("cancerrelatedprocedure-list", self.treatment)
        self.assertEqual(create_object_response.status_code, status.HTTP_201_CREATED)
        get_resp = self.client.get("/api/cancerrelatedprocedures?format=argo")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsNotNone(get_resp_obj["treatments"][0]["submitter_treatment_id"])
        self.assertIsInstance(get_resp_obj["treatments"][0]["submitter_treatment_id"], str)
        self.assertIsNotNone(get_resp_obj["treatments"][0]["treatment_type"])
        self.assertIsInstance(get_resp_obj["treatments"][0]["treatment_type"], str)
        # radiation procedure only
        self.assertEqual(get_resp_obj["treatments"][0]["treatment_type"], "Radiation therapy")
        self.assertIsNotNone(get_resp_obj["treatments"][0]["radiation_therapy_modality"])
        self.assertIsInstance(get_resp_obj["treatments"][0]["radiation_therapy_modality"], dict)
        self.assertIsNotNone(get_resp_obj["treatments"][0]["anatomical_site_irradiated"])
        # TODO run schema validation on ingest and check type
        # self.assertIsInstance(get_resp_obj["treatments"][0]["anatomical_site_irradiated"], dict)


class ARGOTherapyTest(APITestCase):
    """ Test module for testing conversion of medication statement to argo -therapy."""

    def setUp(self):
        self.therapy = valid_medication_statement()

    def test_get_argo(self):
        create_object_response = get_response("medicationstatement-list", self.therapy)
        self.assertEqual(create_object_response.status_code, status.HTTP_201_CREATED)
        get_resp = self.client.get("/api/medicationstatements?format=argo")
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        results = get_resp.json()["immunotherapies_chemotherapies_hormone_therapies"]
        self.assertIsNotNone(results[0]["submitter_treatment_id"])
        self.assertIsInstance(results[0]["submitter_treatment_id"], str)
        self.assertIsNotNone(results[0]["drug_rxnormcui"])
        self.assertIsInstance(results[0]["drug_rxnormcui"], dict)
        self.assertIn("label", results[0]["drug_rxnormcui"])
        self.assertIn("id", results[0]["drug_rxnormcui"])
