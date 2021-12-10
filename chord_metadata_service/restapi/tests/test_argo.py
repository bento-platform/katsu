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
    valid_medication_statement
)


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
        # tnm staging 1
        tnm_staging = invalid_tnm_staging(self.cancer_condition_2)
        for item in ["stage_group", "primary_tumor_category", "regional_nodes_category", "distant_metastases_category"]:
            tnm_staging[item] = {
                "data_value": {
                    "id": "001",
                    "label": "test stage group"
                }
            }
        self.tnm_staging = TNMStaging.objects.create(**tnm_staging)
        # tnm staging 2
        tnm_staging_2 = deepcopy(tnm_staging)
        tnm_staging_2["id"] = "tnm_staging:02"
        tnm_staging_2["tnm_type"] = "pathologic"
        self.tnm_staging_2 = TNMStaging.objects.create(**tnm_staging_2)

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
        print(get_resp_obj)
        # donor
        self.assertEqual(get_resp_obj["composition_objects"][0]["donor"]["submitter_donor_id"], "patient:1")
        self.assertEqual(get_resp_obj["composition_objects"][0]["donor"]["gender"], "Female")
        # primary_diagnoses
        self.assertIn("Carcinosarcoma",
                      get_resp_obj["composition_objects"][0]["primary_diagnoses"][0]["cancer_type_code"]["label"])
        # tnm staging clinical
        for field in ["clinical_stage_group", "clinical_t_category",
                      "clinical_n_category", "clinical_m_category"]:
            self.assertIsInstance(get_resp_obj["composition_objects"][0]["primary_diagnoses"][1][field],
                                  list)
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
