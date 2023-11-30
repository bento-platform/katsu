
<h1 id="moh-service-api">MoH Service API v3.0.0</h1>

This is the RESTful API for the MoH Service. Based on https://raw.githubusercontent.com/CanDIG/katsu/ff7da80a6ccbfceea7dceac21b7e06946ad6ee57/chord_metadata_service/mohpackets/docs/schema.json

Base URLs:

# Authentication

- HTTP Authentication, scheme: bearer

<h1 id="moh-service-api-default">Default</h1>

## chord_metadata_service_mohpackets_apis_core_service_info

<a id="opIdchord_metadata_service_mohpackets_apis_core_service_info"></a>

`GET /v2/service-info`

*Service Info*

<h1 id="moh-service-api-ingest">ingest</h1>

## chord_metadata_service_mohpackets_apis_ingestion_create_program

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_program"></a>

`POST /v2/ingest/program/`

*Create Program*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_program-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ProgramModelSchema](#schemaprogrammodelschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_donor

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_donor"></a>

`POST /v2/ingest/donor/`

*Create Donor*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_donor-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[DonorIngestSchema](#schemadonoringestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_biomarker

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_biomarker"></a>

`POST /v2/ingest/biomarker/`

*Create Biomarker*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_biomarker-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[BiomarkerIngestSchema](#schemabiomarkeringestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_chemotherapy

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_chemotherapy"></a>

`POST /v2/ingest/chemotherapy/`

*Create Chemotherapy*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_chemotherapy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ChemotherapyIngestSchema](#schemachemotherapyingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_comorbidity

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_comorbidity"></a>

`POST /v2/ingest/comorbidity/`

*Create Comorbidity*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_comorbidity-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ComorbidityIngestSchema](#schemacomorbidityingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_exposure

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_exposure"></a>

`POST /v2/ingest/exposure/`

*Create Exposure*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_exposure-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ExposureIngestSchema](#schemaexposureingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_follow_up

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_follow_up"></a>

`POST /v2/ingest/follow_up/`

*Create Follow Up*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_follow_up-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[FollowUpIngestSchema](#schemafollowupingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_hormone_therapy

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_hormone_therapy"></a>

`POST /v2/ingest/hormone_therapy/`

*Create Hormone Therapy*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_hormone_therapy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[HormoneTherapyIngestSchema](#schemahormonetherapyingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_immunotherapy

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_immunotherapy"></a>

`POST /v2/ingest/immunotherapy/`

*Create Immunotherapy*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_immunotherapy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ImmunotherapyIngestSchema](#schemaimmunotherapyingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_primary_diagnosis

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_primary_diagnosis"></a>

`POST /v2/ingest/primary_diagnosis/`

*Create Primary Diagnosis*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_primary_diagnosis-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[PrimaryDiagnosisIngestSchema](#schemaprimarydiagnosisingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_radiation

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_radiation"></a>

`POST /v2/ingest/radiation/`

*Create Radiation*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_radiation-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[RadiationIngestSchema](#schemaradiationingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_sample_registration

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_sample_registration"></a>

`POST /v2/ingest/sample_registration/`

*Create Sample Registration*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_sample_registration-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[SampleRegistrationIngestSchema](#schemasampleregistrationingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_specimen

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_specimen"></a>

`POST /v2/ingest/specimen/`

*Create Specimen*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_specimen-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[SpecimenIngestSchema](#schemaspecimeningestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_surgery

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_surgery"></a>

`POST /v2/ingest/surgery/`

*Create Surgery*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_surgery-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[SurgeryIngestSchema](#schemasurgeryingestschema)|true|none|

## chord_metadata_service_mohpackets_apis_ingestion_create_treatment

<a id="opIdchord_metadata_service_mohpackets_apis_ingestion_create_treatment"></a>

`POST /v2/ingest/treatment/`

*Create Treatment*

<h3 id="chord_metadata_service_mohpackets_apis_ingestion_create_treatment-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[TreatmentIngestSchema](#schematreatmentingestschema)|true|none|

<h1 id="moh-service-api-authorized">authorized</h1>

## chord_metadata_service_mohpackets_apis_clinical_data_delete_program

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_delete_program"></a>

`DELETE /v2/authorized/program/{program_id}/`

*Delete Program*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_delete_program-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|path|string|true|none|

> Example responses

> 404 Response

```json
{
  "property1": "string",
  "property2": "string"
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_get_donor_with_clinical_data

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_get_donor_with_clinical_data"></a>

`GET /v2/authorized/donor_with_clinical_data/program/{program_id}/donor/{donor_id}`

*Get Donor With Clinical Data*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_get_donor_with_clinical_data-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|path|string|true|none|
|donor_id|path|string|true|none|

> Example responses

> 200 Response

```json
{
  "primary_diagnoses": [
    {
      "specimens": [
        {
          "sample_registrations": [
            {
              "submitter_sample_id": "string",
              "specimen_tissue_source": "string",
              "tumour_normal_designation": "string",
              "specimen_type": "string",
              "sample_type": "string"
            }
          ],
          "submitter_specimen_id": "string",
          "pathological_tumour_staging_system": "string",
          "pathological_t_category": "string",
          "pathological_n_category": "string",
          "pathological_m_category": "string",
          "pathological_stage_group": "string",
          "specimen_collection_date": "string",
          "specimen_storage": "string",
          "specimen_processing": "string",
          "tumour_histological_type": "string",
          "specimen_anatomic_location": "string",
          "specimen_laterality": "string",
          "reference_pathology_confirmed_diagnosis": "string",
          "reference_pathology_confirmed_tumour_presence": "string",
          "tumour_grading_system": "string",
          "tumour_grade": "string",
          "percent_tumour_cells_range": "string",
          "percent_tumour_cells_measurement_method": "string"
        }
      ],
      "treatments": [
        {
          "chemotherapies": [
            {
              "drug_reference_database": "string",
              "drug_name": "string",
              "drug_reference_identifier": "string",
              "chemotherapy_drug_dose_units": "string",
              "prescribed_cumulative_drug_dose": 0,
              "actual_cumulative_drug_dose": 0
            }
          ],
          "immunotherapies": [
            {
              "drug_reference_database": "string",
              "immunotherapy_type": "string",
              "drug_name": "string",
              "drug_reference_identifier": "string",
              "immunotherapy_drug_dose_units": "string",
              "prescribed_cumulative_drug_dose": 0,
              "actual_cumulative_drug_dose": 0
            }
          ],
          "hormone_therapies": [
            {
              "drug_reference_database": "string",
              "drug_name": "string",
              "drug_reference_identifier": "string",
              "hormone_drug_dose_units": "string",
              "prescribed_cumulative_drug_dose": 0,
              "actual_cumulative_drug_dose": 0
            }
          ],
          "radiations": [
            {
              "radiation_therapy_modality": "string",
              "radiation_therapy_type": "string",
              "radiation_therapy_fractions": 0,
              "radiation_therapy_dosage": 0,
              "anatomical_site_irradiated": "string",
              "radiation_boost": true,
              "reference_radiation_treatment_id": "string"
            }
          ],
          "surgeries": [
            {
              "submitter_specimen_id": "string",
              "surgery_type": "string",
              "surgery_site": "string",
              "surgery_location": "string",
              "tumour_length": 0,
              "tumour_width": 0,
              "greatest_dimension_tumour": 0,
              "tumour_focality": "string",
              "residual_tumour_classification": "string",
              "margin_types_involved": [
                null
              ],
              "margin_types_not_involved": [
                null
              ],
              "margin_types_not_assessed": [
                null
              ],
              "lymphovascular_invasion": "string",
              "perineural_invasion": "string"
            }
          ],
          "followups": [
            {
              "submitter_follow_up_id": "string",
              "date_of_followup": "string",
              "disease_status_at_followup": "string",
              "relapse_type": "string",
              "date_of_relapse": "string",
              "method_of_progression_status": [
                null
              ],
              "anatomic_site_progression_or_recurrence": [
                null
              ],
              "recurrence_tumour_staging_system": "string",
              "recurrence_t_category": "string",
              "recurrence_n_category": "string",
              "recurrence_m_category": "string",
              "recurrence_stage_group": "string"
            }
          ],
          "submitter_treatment_id": "string",
          "treatment_type": [
            null
          ],
          "is_primary_treatment": "string",
          "line_of_treatment": 0,
          "treatment_start_date": "string",
          "treatment_end_date": "string",
          "treatment_setting": "string",
          "treatment_intent": "string",
          "days_per_cycle": 0,
          "number_of_cycles": 0,
          "response_to_treatment_criteria_method": "string",
          "response_to_treatment": "string",
          "status_of_treatment": "string"
        }
      ],
      "followups": [
        {
          "submitter_follow_up_id": "string",
          "date_of_followup": "string",
          "disease_status_at_followup": "string",
          "relapse_type": "string",
          "date_of_relapse": "string",
          "method_of_progression_status": [
            null
          ],
          "anatomic_site_progression_or_recurrence": [
            null
          ],
          "recurrence_tumour_staging_system": "string",
          "recurrence_t_category": "string",
          "recurrence_n_category": "string",
          "recurrence_m_category": "string",
          "recurrence_stage_group": "string"
        }
      ],
      "submitter_primary_diagnosis_id": "string",
      "date_of_diagnosis": "string",
      "cancer_type_code": "string",
      "basis_of_diagnosis": "string",
      "laterality": "string",
      "lymph_nodes_examined_status": "string",
      "lymph_nodes_examined_method": "string",
      "number_lymph_nodes_positive": 0,
      "clinical_tumour_staging_system": "string",
      "clinical_t_category": "string",
      "clinical_n_category": "string",
      "clinical_m_category": "string",
      "clinical_stage_group": "string"
    }
  ],
  "followups": [
    {
      "submitter_follow_up_id": "string",
      "date_of_followup": "string",
      "disease_status_at_followup": "string",
      "relapse_type": "string",
      "date_of_relapse": "string",
      "method_of_progression_status": [
        null
      ],
      "anatomic_site_progression_or_recurrence": [
        null
      ],
      "recurrence_tumour_staging_system": "string",
      "recurrence_t_category": "string",
      "recurrence_n_category": "string",
      "recurrence_m_category": "string",
      "recurrence_stage_group": "string"
    }
  ],
  "biomarkers": [
    {
      "submitter_specimen_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "submitter_treatment_id": "string",
      "submitter_follow_up_id": "string",
      "test_date": "string",
      "psa_level": 0,
      "ca125": 0,
      "cea": 0,
      "er_status": "string",
      "er_percent_positive": 0,
      "pr_status": "string",
      "pr_percent_positive": 0,
      "her2_ihc_status": "string",
      "her2_ish_status": "string",
      "hpv_ihc_status": "string",
      "hpv_pcr_status": "string",
      "hpv_strain": [
        null
      ]
    }
  ],
  "exposures": [
    {
      "tobacco_smoking_status": "string",
      "tobacco_type": [
        null
      ],
      "pack_years_smoked": 0
    }
  ],
  "comorbidities": [
    {
      "prior_malignancy": "string",
      "laterality_of_prior_malignancy": "string",
      "age_at_comorbidity_diagnosis": 0,
      "comorbidity_type_code": "string",
      "comorbidity_treatment_status": "string",
      "comorbidity_treatment": "string"
    }
  ],
  "submitter_donor_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "is_deceased": true,
  "lost_to_followup_after_clinical_event_identifier": "string",
  "lost_to_followup_reason": "string",
  "date_alive_after_lost_to_followup": "string",
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": [
    null
  ]
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_programs

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_programs"></a>

`GET /v2/authorized/programs/`

*List Programs*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_programs-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "program_id": "string",
      "metadata": {},
      "created": "2019-08-24T14:15:22Z",
      "updated": "2019-08-24T14:15:22Z"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_donors

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_donors"></a>

`GET /v2/authorized/donors/`

*List Donors*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_donors-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|query|any|false|none|
|program_id|query|any|false|none|
|gender|query|any|false|none|
|sex_at_birth|query|any|false|none|
|is_deceased|query|any|false|none|
|lost_to_followup_after_clinical_event_identifier|query|any|false|none|
|lost_to_followup_reason|query|any|false|none|
|date_alive_after_lost_to_followup|query|any|false|none|
|cause_of_death|query|any|false|none|
|date_of_birth|query|any|false|none|
|date_of_death|query|any|false|none|
|primary_site|query|array[string]|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "cause_of_death": "Died of cancer",
      "submitter_donor_id": "string",
      "date_of_birth": "string",
      "date_of_death": "string",
      "primary_site": [
        "Accessory sinuses"
      ],
      "gender": "Man",
      "sex_at_birth": "Male",
      "lost_to_followup_reason": "Completed study",
      "date_alive_after_lost_to_followup": "string",
      "program_id": "string",
      "is_deceased": true,
      "lost_to_followup_after_clinical_event_identifier": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_primary_diagnoses

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_primary_diagnoses"></a>

`GET /v2/authorized/primary_diagnoses/`

*List Primary Diagnoses*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_primary_diagnoses-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|query|any|false|none|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|date_of_diagnosis|query|any|false|none|
|cancer_type_code|query|any|false|none|
|basis_of_diagnosis|query|any|false|none|
|laterality|query|any|false|none|
|lymph_nodes_examined_status|query|any|false|none|
|lymph_nodes_examined_method|query|any|false|none|
|number_lymph_nodes_positive|query|any|false|none|
|clinical_tumour_staging_system|query|any|false|none|
|clinical_t_category|query|any|false|none|
|clinical_n_category|query|any|false|none|
|clinical_m_category|query|any|false|none|
|clinical_stage_group|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "submitter_primary_diagnosis_id": "string",
      "date_of_diagnosis": "string",
      "basis_of_diagnosis": "Clinical investigation",
      "lymph_nodes_examined_status": "Cannot be determined",
      "lymph_nodes_examined_method": "Imaging",
      "clinical_tumour_staging_system": "AJCC 8th edition",
      "clinical_t_category": "T0",
      "clinical_n_category": "N0",
      "clinical_m_category": "M0",
      "clinical_stage_group": "Stage 0",
      "laterality": "Bilateral",
      "program_id": "string",
      "submitter_donor_id": "string",
      "cancer_type_code": "string",
      "number_lymph_nodes_positive": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_biomarkers

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_biomarkers"></a>

`GET /v2/authorized/biomarkers/`

*List Biomarkers*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_biomarkers-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_specimen_id|query|any|false|none|
|submitter_primary_diagnosis_id|query|any|false|none|
|submitter_treatment_id|query|any|false|none|
|submitter_follow_up_id|query|any|false|none|
|test_date|query|any|false|none|
|psa_level|query|any|false|none|
|ca125|query|any|false|none|
|cea|query|any|false|none|
|er_status|query|any|false|none|
|er_percent_positive|query|any|false|none|
|pr_status|query|any|false|none|
|pr_percent_positive|query|any|false|none|
|her2_ihc_status|query|any|false|none|
|her2_ish_status|query|any|false|none|
|hpv_ihc_status|query|any|false|none|
|hpv_pcr_status|query|any|false|none|
|hpv_strain|query|array[string]|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "er_status": "Cannot be determined",
      "pr_status": "Cannot be determined",
      "her2_ihc_status": "Cannot be determined",
      "her2_ish_status": "Cannot be determined",
      "hpv_ihc_status": "Cannot be determined",
      "hpv_pcr_status": "Cannot be determined",
      "hpv_strain": [
        "HPV16"
      ],
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_specimen_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "submitter_treatment_id": "string",
      "submitter_follow_up_id": "string",
      "test_date": "string",
      "psa_level": 0,
      "ca125": 0,
      "cea": 0,
      "er_percent_positive": 0,
      "pr_percent_positive": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_chemotherapies

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_chemotherapies"></a>

`GET /v2/authorized/chemotherapies/`

*List Chemotherapies*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_chemotherapies-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_treatment_id|query|any|false|none|
|drug_reference_database|query|any|false|none|
|drug_name|query|any|false|none|
|drug_reference_identifier|query|any|false|none|
|chemotherapy_drug_dose_units|query|any|false|none|
|prescribed_cumulative_drug_dose|query|any|false|none|
|actual_cumulative_drug_dose|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "chemotherapy_drug_dose_units": "mg/m2",
      "drug_reference_database": "RxNorm",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_comorbidities

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_comorbidities"></a>

`GET /v2/authorized/comorbidities/`

*List Comorbidities*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_comorbidities-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|prior_malignancy|query|any|false|none|
|laterality_of_prior_malignancy|query|any|false|none|
|age_at_comorbidity_diagnosis|query|any|false|none|
|comorbidity_type_code|query|any|false|none|
|comorbidity_treatment_status|query|any|false|none|
|comorbidity_treatment|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "prior_malignancy": "Yes",
      "laterality_of_prior_malignancy": "Bilateral",
      "comorbidity_type_code": "string",
      "comorbidity_treatment_status": "Yes",
      "comorbidity_treatment": "string",
      "program_id": "string",
      "submitter_donor_id": "string",
      "age_at_comorbidity_diagnosis": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_exposures

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_exposures"></a>

`GET /v2/authorized/exposures/`

*List Exposures*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_exposures-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|tobacco_smoking_status|query|any|false|none|
|tobacco_type|query|array[string]|false|none|
|pack_years_smoked|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "tobacco_smoking_status": "Current reformed smoker for <= 15 years",
      "tobacco_type": [
        "Chewing Tobacco"
      ],
      "program_id": "string",
      "submitter_donor_id": "string",
      "pack_years_smoked": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_follow_ups

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_follow_ups"></a>

`GET /v2/authorized/follow_ups/`

*List Follow Ups*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_follow_ups-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_follow_up_id|query|any|false|none|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_primary_diagnosis_id|query|any|false|none|
|submitter_treatment_id|query|any|false|none|
|date_of_followup|query|any|false|none|
|disease_status_at_followup|query|any|false|none|
|relapse_type|query|any|false|none|
|date_of_relapse|query|any|false|none|
|method_of_progression_status|query|array[string]|false|none|
|anatomic_site_progression_or_recurrence|query|array[string]|false|none|
|recurrence_tumour_staging_system|query|any|false|none|
|recurrence_t_category|query|any|false|none|
|recurrence_n_category|query|any|false|none|
|recurrence_m_category|query|any|false|none|
|recurrence_stage_group|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "submitter_follow_up_id": "string",
      "disease_status_at_followup": "Complete remission",
      "relapse_type": "Distant recurrence/metastasis",
      "date_of_followup": "string",
      "date_of_relapse": "string",
      "method_of_progression_status": [
        "Imaging (procedure)"
      ],
      "anatomic_site_progression_or_recurrence": [
        "string"
      ],
      "recurrence_tumour_staging_system": "AJCC 8th edition",
      "recurrence_t_category": "T0",
      "recurrence_n_category": "N0",
      "recurrence_m_category": "M0",
      "recurrence_stage_group": "Stage 0",
      "treatment_uuid": "6ec39d1c-44a6-43bb-80b2-ee9580e3c70b",
      "primary_diagnosis_uuid": "3459cde2-44be-4900-9ef0-b6de408c756d",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "submitter_treatment_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_hormone_therapies

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_hormone_therapies"></a>

`GET /v2/authorized/hormone_therapies/`

*List Hormone Therapies*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_hormone_therapies-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_treatment_id|query|any|false|none|
|drug_reference_database|query|any|false|none|
|drug_name|query|any|false|none|
|drug_reference_identifier|query|any|false|none|
|hormone_drug_dose_units|query|any|false|none|
|prescribed_cumulative_drug_dose|query|any|false|none|
|actual_cumulative_drug_dose|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "hormone_drug_dose_units": "mg/m2",
      "drug_reference_database": "RxNorm",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_immunotherapies

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_immunotherapies"></a>

`GET /v2/authorized/immunotherapies/`

*List Immunotherapies*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_immunotherapies-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_treatment_id|query|any|false|none|
|drug_reference_database|query|any|false|none|
|immunotherapy_type|query|any|false|none|
|drug_name|query|any|false|none|
|drug_reference_identifier|query|any|false|none|
|immunotherapy_drug_dose_units|query|any|false|none|
|prescribed_cumulative_drug_dose|query|any|false|none|
|actual_cumulative_drug_dose|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "immunotherapy_type": "Cell-based",
      "drug_reference_database": "RxNorm",
      "immunotherapy_drug_dose_units": "mg/m2",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_radiations

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_radiations"></a>

`GET /v2/authorized/radiations/`

*List Radiations*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_radiations-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_treatment_id|query|any|false|none|
|radiation_therapy_modality|query|any|false|none|
|radiation_therapy_type|query|any|false|none|
|radiation_therapy_fractions|query|any|false|none|
|radiation_therapy_dosage|query|any|false|none|
|anatomical_site_irradiated|query|any|false|none|
|radiation_boost|query|any|false|none|
|reference_radiation_treatment_id|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "radiation_therapy_modality": "Megavoltage radiation therapy using photons (procedure)",
      "radiation_therapy_type": "External",
      "anatomical_site_irradiated": "Left Abdomen",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "radiation_therapy_fractions": 0,
      "radiation_therapy_dosage": 0,
      "radiation_boost": true,
      "reference_radiation_treatment_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_sample_registrations

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_sample_registrations"></a>

`GET /v2/authorized/sample_registrations/`

*List Sample Registrations*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_sample_registrations-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_sample_id|query|any|false|none|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_specimen_id|query|any|false|none|
|specimen_tissue_source|query|any|false|none|
|tumour_normal_designation|query|any|false|none|
|specimen_type|query|any|false|none|
|sample_type|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "submitter_sample_id": "string",
      "specimen_tissue_source": "Abdominal fluid",
      "tumour_normal_designation": "Normal",
      "specimen_type": "Cell line - derived from normal",
      "sample_type": "Amplified DNA",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_specimen_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_specimens

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_specimens"></a>

`GET /v2/authorized/specimens/`

*List Specimens*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_specimens-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_specimen_id|query|any|false|none|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_primary_diagnosis_id|query|any|false|none|
|pathological_tumour_staging_system|query|any|false|none|
|pathological_t_category|query|any|false|none|
|pathological_n_category|query|any|false|none|
|pathological_m_category|query|any|false|none|
|pathological_stage_group|query|any|false|none|
|specimen_collection_date|query|any|false|none|
|specimen_storage|query|any|false|none|
|specimen_processing|query|any|false|none|
|tumour_histological_type|query|any|false|none|
|specimen_anatomic_location|query|any|false|none|
|specimen_laterality|query|any|false|none|
|reference_pathology_confirmed_diagnosis|query|any|false|none|
|reference_pathology_confirmed_tumour_presence|query|any|false|none|
|tumour_grading_system|query|any|false|none|
|tumour_grade|query|any|false|none|
|percent_tumour_cells_range|query|any|false|none|
|percent_tumour_cells_measurement_method|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "submitter_specimen_id": "string",
      "pathological_tumour_staging_system": "AJCC 8th edition",
      "pathological_t_category": "T0",
      "pathological_n_category": "N0",
      "pathological_m_category": "M0",
      "pathological_stage_group": "Stage 0",
      "specimen_collection_date": "string",
      "specimen_storage": "Cut slide",
      "tumour_histological_type": "string",
      "specimen_anatomic_location": "string",
      "reference_pathology_confirmed_diagnosis": "Yes",
      "reference_pathology_confirmed_tumour_presence": "Yes",
      "tumour_grading_system": "FNCLCC grading system",
      "tumour_grade": "Low grade",
      "percent_tumour_cells_range": "0-19%",
      "percent_tumour_cells_measurement_method": "Genomics",
      "specimen_processing": "Cryopreservation in liquid nitrogen (dead tissue)",
      "specimen_laterality": "Left",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_primary_diagnosis_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_surgeries

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_surgeries"></a>

`GET /v2/authorized/surgeries/`

*List Surgeries*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_surgeries-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_treatment_id|query|any|false|none|
|submitter_specimen_id|query|any|false|none|
|surgery_type|query|any|false|none|
|surgery_site|query|any|false|none|
|surgery_location|query|any|false|none|
|tumour_length|query|any|false|none|
|tumour_width|query|any|false|none|
|greatest_dimension_tumour|query|any|false|none|
|tumour_focality|query|any|false|none|
|residual_tumour_classification|query|any|false|none|
|margin_types_involved|query|array[string]|false|none|
|margin_types_not_involved|query|array[string]|false|none|
|margin_types_not_assessed|query|array[string]|false|none|
|lymphovascular_invasion|query|any|false|none|
|perineural_invasion|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "surgery_type": "Ablation",
      "surgery_site": "string",
      "surgery_location": "Local recurrence",
      "tumour_focality": "Cannot be assessed",
      "residual_tumour_classification": "Not applicable",
      "margin_types_involved": [
        "Circumferential resection margin"
      ],
      "margin_types_not_involved": [
        "Circumferential resection margin"
      ],
      "margin_types_not_assessed": [
        "Circumferential resection margin"
      ],
      "lymphovascular_invasion": "Absent",
      "perineural_invasion": "Absent",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "submitter_specimen_id": "string",
      "tumour_length": 0,
      "tumour_width": 0,
      "greatest_dimension_tumour": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

## chord_metadata_service_mohpackets_apis_clinical_data_list_treatments

<a id="opIdchord_metadata_service_mohpackets_apis_clinical_data_list_treatments"></a>

`GET /v2/authorized/treatments/`

*List Treatments*

<h3 id="chord_metadata_service_mohpackets_apis_clinical_data_list_treatments-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_treatment_id|query|any|false|none|
|program_id|query|any|false|none|
|submitter_donor_id|query|any|false|none|
|submitter_primary_diagnosis_id|query|any|false|none|
|treatment_type|query|array[string]|false|none|
|is_primary_treatment|query|any|false|none|
|line_of_treatment|query|any|false|none|
|treatment_start_date|query|any|false|none|
|treatment_end_date|query|any|false|none|
|treatment_setting|query|any|false|none|
|treatment_intent|query|any|false|none|
|days_per_cycle|query|any|false|none|
|number_of_cycles|query|any|false|none|
|response_to_treatment_criteria_method|query|any|false|none|
|response_to_treatment|query|any|false|none|
|status_of_treatment|query|any|false|none|
|page|query|integer|false|none|
|page_size|query|integer|false|none|

> Example responses

> 200 Response

```json
{
  "items": [
    {
      "submitter_treatment_id": "string",
      "treatment_type": [
        "Bone marrow transplant"
      ],
      "is_primary_treatment": "Yes",
      "treatment_start_date": "string",
      "treatment_end_date": "string",
      "treatment_setting": "Adjuvant",
      "treatment_intent": "Curative",
      "response_to_treatment_criteria_method": "RECIST 1.1",
      "response_to_treatment": "Complete response",
      "status_of_treatment": "Treatment completed as prescribed",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "line_of_treatment": 0,
      "days_per_cycle": 0,
      "number_of_cycles": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}
```

<h1 id="moh-service-api-discovery">discovery</h1>

## chord_metadata_service_mohpackets_apis_discovery_discover_programs

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_programs"></a>

`GET /v2/discovery/programs/`

*Discover Programs*

> Example responses

> 200 Response

```json
{
  "cohort_list": [
    "string"
  ]
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_donors

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_donors"></a>

`GET /v2/discovery/donors/`

*Discover Donors*

<h3 id="chord_metadata_service_mohpackets_apis_discovery_discover_donors-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|query|any|false|none|
|program_id|query|any|false|none|
|gender|query|any|false|none|
|sex_at_birth|query|any|false|none|
|is_deceased|query|any|false|none|
|lost_to_followup_after_clinical_event_identifier|query|any|false|none|
|lost_to_followup_reason|query|any|false|none|
|date_alive_after_lost_to_followup|query|any|false|none|
|cause_of_death|query|any|false|none|
|date_of_birth|query|any|false|none|
|date_of_death|query|any|false|none|
|primary_site|query|array[string]|false|none|

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_specimens

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_specimens"></a>

`GET /v2/discovery/specimen/`

*Discover Specimens*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_sample_registrations

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_sample_registrations"></a>

`GET /v2/discovery/sample_registrations/`

*Discover Sample Registrations*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_primary_diagnoses

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_primary_diagnoses"></a>

`GET /v2/discovery/primary_diagnoses/`

*Discover Primary Diagnoses*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_treatments

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_treatments"></a>

`GET /v2/discovery/treatments/`

*Discover Treatments*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_chemotherapies

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_chemotherapies"></a>

`GET /v2/discovery/chemotherapies/`

*Discover Chemotherapies*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_hormone_therapies

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_hormone_therapies"></a>

`GET /v2/discovery/hormone_therapies/`

*Discover Hormone Therapies*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_radiations

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_radiations"></a>

`GET /v2/discovery/radiations/`

*Discover Radiations*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_immunotherapies

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_immunotherapies"></a>

`GET /v2/discovery/immunotherapies/`

*Discover Immunotherapies*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_surgeries

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_surgeries"></a>

`GET /v2/discovery/surgeries/`

*Discover Surgeries*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_follow_ups

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_follow_ups"></a>

`GET /v2/discovery/follow_ups/`

*Discover Follow Ups*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_biomarkers

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_biomarkers"></a>

`GET /v2/discovery/biomarkers/`

*Discover Biomarkers*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_comorbidities

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_comorbidities"></a>

`GET /v2/discovery/comorbidities/`

*Discover Comorbidities*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_exposures

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_exposures"></a>

`GET /v2/discovery/exposures/`

*Discover Exposures*

> Example responses

> 200 Response

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_sidebar_list

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_sidebar_list"></a>

`GET /v2/discovery/sidebar_list/`

*Discover Sidebar List*

Retrieve the list of available values for all fields (including for
datasets that the user is not authorized to view)

> Example responses

> 200 Response

```json
{}
```

<h1 id="moh-service-api-overview">overview</h1>

## chord_metadata_service_mohpackets_apis_discovery_discover_cohort_count

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_cohort_count"></a>

`GET /v2/discovery/overview/cohort_count/`

*Discover Cohort Count*

Return the number of cohorts in the database.

> Example responses

> 200 Response

```json
{
  "property1": 0,
  "property2": 0
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_patients_per_cohort

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_patients_per_cohort"></a>

`GET /v2/discovery/overview/patients_per_cohort/`

*Discover Patients Per Cohort*

Return the number of patients per cohort in the database.

> Example responses

> 200 Response

```json
{
  "property1": 0,
  "property2": 0
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_individual_count

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_individual_count"></a>

`GET /v2/discovery/overview/individual_count/`

*Discover Individual Count*

Return the number of individuals in the database.

> Example responses

> 200 Response

```json
{
  "property1": 0,
  "property2": 0
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_gender_count

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_gender_count"></a>

`GET /v2/discovery/overview/gender_count/`

*Discover Gender Count*

Return the count for every gender in the database.

> Example responses

> 200 Response

```json
{
  "property1": 0,
  "property2": 0
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_cancer_type_count

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_cancer_type_count"></a>

`GET /v2/discovery/overview/cancer_type_count/`

*Discover Cancer Type Count*

Return the count for every cancer type in the database.

> Example responses

> 200 Response

```json
{
  "property1": 0,
  "property2": 0
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_treatment_type_count

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_treatment_type_count"></a>

`GET /v2/discovery/overview/treatment_type_count/`

*Discover Treatment Type Count*

Return the count for every treatment type in the database.

> Example responses

> 200 Response

```json
{
  "property1": 0,
  "property2": 0
}
```

## chord_metadata_service_mohpackets_apis_discovery_discover_diagnosis_age_count

<a id="opIdchord_metadata_service_mohpackets_apis_discovery_discover_diagnosis_age_count"></a>

`GET /v2/discovery/overview/diagnosis_age_count/`

*Discover Diagnosis Age Count*

Return the count for age of diagnosis in the database.
If there are multiple date_of_diagnosis, get the earliest

> Example responses

> 200 Response

```json
{
  "property1": 0,
  "property2": 0
}
```

# Schemas

<h2 id="tocS_ProgramModelSchema">ProgramModelSchema</h2>

<a id="schemaprogrammodelschema"></a>
<a id="schema_ProgramModelSchema"></a>
<a id="tocSprogrammodelschema"></a>
<a id="tocsprogrammodelschema"></a>

```json
{
  "program_id": "string",
  "metadata": {},
  "created": "2019-08-24T14:15:22Z",
  "updated": "2019-08-24T14:15:22Z"
}

```

ProgramModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|metadata|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|object|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|created|string(date-time)|false|none|none|
|updated|string(date-time)|false|none|none|

<h2 id="tocS_DonorIngestSchema">DonorIngestSchema</h2>

<a id="schemadonoringestschema"></a>
<a id="schema_DonorIngestSchema"></a>
<a id="tocSdonoringestschema"></a>
<a id="tocsdonoringestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "is_deceased": true,
  "lost_to_followup_after_clinical_event_identifier": "string",
  "lost_to_followup_reason": "string",
  "date_alive_after_lost_to_followup": "string",
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": [
    null
  ]
}

```

DonorIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|gender|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sex_at_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|is_deceased|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_after_clinical_event_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_reason|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_alive_after_lost_to_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cause_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|primary_site|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_BiomarkerIngestSchema">BiomarkerIngestSchema</h2>

<a id="schemabiomarkeringestschema"></a>
<a id="schema_BiomarkerIngestSchema"></a>
<a id="tocSbiomarkeringestschema"></a>
<a id="tocsbiomarkeringestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string",
  "test_date": "string",
  "psa_level": 0,
  "ca125": 0,
  "cea": 0,
  "er_status": "string",
  "er_percent_positive": 0,
  "pr_status": "string",
  "pr_percent_positive": 0,
  "her2_ihc_status": "string",
  "her2_ish_status": "string",
  "hpv_ihc_status": "string",
  "hpv_pcr_status": "string",
  "hpv_strain": [
    null
  ]
}

```

BiomarkerIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|test_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|psa_level|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ca125|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cea|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ish_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_pcr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_strain|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ChemotherapyIngestSchema">ChemotherapyIngestSchema</h2>

<a id="schemachemotherapyingestschema"></a>
<a id="schema_ChemotherapyIngestSchema"></a>
<a id="tocSchemotherapyingestschema"></a>
<a id="tocschemotherapyingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_reference_database": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "chemotherapy_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

ChemotherapyIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|chemotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ComorbidityIngestSchema">ComorbidityIngestSchema</h2>

<a id="schemacomorbidityingestschema"></a>
<a id="schema_ComorbidityIngestSchema"></a>
<a id="tocScomorbidityingestschema"></a>
<a id="tocscomorbidityingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": 0,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string"
}

```

ComorbidityIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality_of_prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|age_at_comorbidity_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ExposureIngestSchema">ExposureIngestSchema</h2>

<a id="schemaexposureingestschema"></a>
<a id="schema_ExposureIngestSchema"></a>
<a id="tocSexposureingestschema"></a>
<a id="tocsexposureingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "tobacco_smoking_status": "string",
  "tobacco_type": [
    null
  ],
  "pack_years_smoked": 0
}

```

ExposureIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|tobacco_smoking_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tobacco_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pack_years_smoked|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_FollowUpIngestSchema">FollowUpIngestSchema</h2>

<a id="schemafollowupingestschema"></a>
<a id="schema_FollowUpIngestSchema"></a>
<a id="tocSfollowupingestschema"></a>
<a id="tocsfollowupingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "treatment_uuid_id": "4bc59108-57b8-4a2c-8af7-388e0b2e5e0b",
  "primary_diagnosis_uuid_id": "ba89c3f7-52e0-44a8-83f8-a180c68404f8",
  "submitter_follow_up_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "date_of_followup": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": [
    null
  ],
  "anatomic_site_progression_or_recurrence": [
    null
  ],
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string"
}

```

FollowUpIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_uuid_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(uuid)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|primary_diagnosis_uuid_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(uuid)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|disease_status_at_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|relapse_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_relapse|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|method_of_progression_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|anatomic_site_progression_or_recurrence|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_HormoneTherapyIngestSchema">HormoneTherapyIngestSchema</h2>

<a id="schemahormonetherapyingestschema"></a>
<a id="schema_HormoneTherapyIngestSchema"></a>
<a id="tocShormonetherapyingestschema"></a>
<a id="tocshormonetherapyingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_reference_database": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "hormone_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

HormoneTherapyIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hormone_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ImmunotherapyIngestSchema">ImmunotherapyIngestSchema</h2>

<a id="schemaimmunotherapyingestschema"></a>
<a id="schema_ImmunotherapyIngestSchema"></a>
<a id="tocSimmunotherapyingestschema"></a>
<a id="tocsimmunotherapyingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_reference_database": "string",
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "immunotherapy_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

ImmunotherapyIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PrimaryDiagnosisIngestSchema">PrimaryDiagnosisIngestSchema</h2>

<a id="schemaprimarydiagnosisingestschema"></a>
<a id="schema_PrimaryDiagnosisIngestSchema"></a>
<a id="tocSprimarydiagnosisingestschema"></a>
<a id="tocsprimarydiagnosisingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_donor_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "laterality": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": 0,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string"
}

```

PrimaryDiagnosisIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cancer_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|basis_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_lymph_nodes_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_RadiationIngestSchema">RadiationIngestSchema</h2>

<a id="schemaradiationingestschema"></a>
<a id="schema_RadiationIngestSchema"></a>
<a id="tocSradiationingestschema"></a>
<a id="tocsradiationingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": 0,
  "radiation_therapy_dosage": 0,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string"
}

```

RadiationIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|radiation_therapy_modality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_fractions|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_dosage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|anatomical_site_irradiated|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_boost|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_radiation_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_SampleRegistrationIngestSchema">SampleRegistrationIngestSchema</h2>

<a id="schemasampleregistrationingestschema"></a>
<a id="schema_SampleRegistrationIngestSchema"></a>
<a id="tocSsampleregistrationingestschema"></a>
<a id="tocssampleregistrationingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_sample_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string"
}

```

SampleRegistrationIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_sample_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string|true|none|none|
|specimen_tissue_source|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_normal_designation|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sample_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_SpecimenIngestSchema">SpecimenIngestSchema</h2>

<a id="schemaspecimeningestschema"></a>
<a id="schema_SpecimenIngestSchema"></a>
<a id="tocSspecimeningestschema"></a>
<a id="tocsspecimeningestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_specimen_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "specimen_processing": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "specimen_laterality": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string"
}

```

SpecimenIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|
|pathological_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_collection_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_storage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_processing|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_histological_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_anatomic_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_tumour_presence|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grading_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grade|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_range|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_measurement_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_SurgeryIngestSchema">SurgeryIngestSchema</h2>

<a id="schemasurgeryingestschema"></a>
<a id="schema_SurgeryIngestSchema"></a>
<a id="tocSsurgeryingestschema"></a>
<a id="tocssurgeryingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "submitter_specimen_id": "string",
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": 0,
  "tumour_width": 0,
  "greatest_dimension_tumour": 0,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": [
    null
  ],
  "margin_types_not_involved": [
    null
  ],
  "margin_types_not_assessed": [
    null
  ],
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string"
}

```

SurgeryIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_site|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_length|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_width|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|greatest_dimension_tumour|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_focality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|residual_tumour_classification|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_involved|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_not_involved|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_not_assessed|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymphovascular_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|perineural_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_TreatmentIngestSchema">TreatmentIngestSchema</h2>

<a id="schematreatmentingestschema"></a>
<a id="schema_TreatmentIngestSchema"></a>
<a id="tocStreatmentingestschema"></a>
<a id="tocstreatmentingestschema"></a>

```json
{
  "program_id": "string",
  "uuid": "string",
  "submitter_treatment_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "treatment_type": [
    null
  ],
  "is_primary_treatment": "string",
  "line_of_treatment": 0,
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": 0,
  "number_of_cycles": 0,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "status_of_treatment": "string"
}

```

TreatmentIngestSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|
|treatment_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|is_primary_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|line_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_start_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_end_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_setting|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_intent|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|days_per_cycle|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_of_cycles|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment_criteria_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_DonorWithClinicalDataSchema">DonorWithClinicalDataSchema</h2>

<a id="schemadonorwithclinicaldataschema"></a>
<a id="schema_DonorWithClinicalDataSchema"></a>
<a id="tocSdonorwithclinicaldataschema"></a>
<a id="tocsdonorwithclinicaldataschema"></a>

```json
{
  "primary_diagnoses": [
    {
      "specimens": [
        {
          "sample_registrations": [
            {
              "submitter_sample_id": "string",
              "specimen_tissue_source": "string",
              "tumour_normal_designation": "string",
              "specimen_type": "string",
              "sample_type": "string"
            }
          ],
          "submitter_specimen_id": "string",
          "pathological_tumour_staging_system": "string",
          "pathological_t_category": "string",
          "pathological_n_category": "string",
          "pathological_m_category": "string",
          "pathological_stage_group": "string",
          "specimen_collection_date": "string",
          "specimen_storage": "string",
          "specimen_processing": "string",
          "tumour_histological_type": "string",
          "specimen_anatomic_location": "string",
          "specimen_laterality": "string",
          "reference_pathology_confirmed_diagnosis": "string",
          "reference_pathology_confirmed_tumour_presence": "string",
          "tumour_grading_system": "string",
          "tumour_grade": "string",
          "percent_tumour_cells_range": "string",
          "percent_tumour_cells_measurement_method": "string"
        }
      ],
      "treatments": [
        {
          "chemotherapies": [
            {
              "drug_reference_database": "string",
              "drug_name": "string",
              "drug_reference_identifier": "string",
              "chemotherapy_drug_dose_units": "string",
              "prescribed_cumulative_drug_dose": 0,
              "actual_cumulative_drug_dose": 0
            }
          ],
          "immunotherapies": [
            {
              "drug_reference_database": "string",
              "immunotherapy_type": "string",
              "drug_name": "string",
              "drug_reference_identifier": "string",
              "immunotherapy_drug_dose_units": "string",
              "prescribed_cumulative_drug_dose": 0,
              "actual_cumulative_drug_dose": 0
            }
          ],
          "hormone_therapies": [
            {
              "drug_reference_database": "string",
              "drug_name": "string",
              "drug_reference_identifier": "string",
              "hormone_drug_dose_units": "string",
              "prescribed_cumulative_drug_dose": 0,
              "actual_cumulative_drug_dose": 0
            }
          ],
          "radiations": [
            {
              "radiation_therapy_modality": "string",
              "radiation_therapy_type": "string",
              "radiation_therapy_fractions": 0,
              "radiation_therapy_dosage": 0,
              "anatomical_site_irradiated": "string",
              "radiation_boost": true,
              "reference_radiation_treatment_id": "string"
            }
          ],
          "surgeries": [
            {
              "submitter_specimen_id": "string",
              "surgery_type": "string",
              "surgery_site": "string",
              "surgery_location": "string",
              "tumour_length": 0,
              "tumour_width": 0,
              "greatest_dimension_tumour": 0,
              "tumour_focality": "string",
              "residual_tumour_classification": "string",
              "margin_types_involved": [
                null
              ],
              "margin_types_not_involved": [
                null
              ],
              "margin_types_not_assessed": [
                null
              ],
              "lymphovascular_invasion": "string",
              "perineural_invasion": "string"
            }
          ],
          "followups": [
            {
              "submitter_follow_up_id": "string",
              "date_of_followup": "string",
              "disease_status_at_followup": "string",
              "relapse_type": "string",
              "date_of_relapse": "string",
              "method_of_progression_status": [
                null
              ],
              "anatomic_site_progression_or_recurrence": [
                null
              ],
              "recurrence_tumour_staging_system": "string",
              "recurrence_t_category": "string",
              "recurrence_n_category": "string",
              "recurrence_m_category": "string",
              "recurrence_stage_group": "string"
            }
          ],
          "submitter_treatment_id": "string",
          "treatment_type": [
            null
          ],
          "is_primary_treatment": "string",
          "line_of_treatment": 0,
          "treatment_start_date": "string",
          "treatment_end_date": "string",
          "treatment_setting": "string",
          "treatment_intent": "string",
          "days_per_cycle": 0,
          "number_of_cycles": 0,
          "response_to_treatment_criteria_method": "string",
          "response_to_treatment": "string",
          "status_of_treatment": "string"
        }
      ],
      "followups": [
        {
          "submitter_follow_up_id": "string",
          "date_of_followup": "string",
          "disease_status_at_followup": "string",
          "relapse_type": "string",
          "date_of_relapse": "string",
          "method_of_progression_status": [
            null
          ],
          "anatomic_site_progression_or_recurrence": [
            null
          ],
          "recurrence_tumour_staging_system": "string",
          "recurrence_t_category": "string",
          "recurrence_n_category": "string",
          "recurrence_m_category": "string",
          "recurrence_stage_group": "string"
        }
      ],
      "submitter_primary_diagnosis_id": "string",
      "date_of_diagnosis": "string",
      "cancer_type_code": "string",
      "basis_of_diagnosis": "string",
      "laterality": "string",
      "lymph_nodes_examined_status": "string",
      "lymph_nodes_examined_method": "string",
      "number_lymph_nodes_positive": 0,
      "clinical_tumour_staging_system": "string",
      "clinical_t_category": "string",
      "clinical_n_category": "string",
      "clinical_m_category": "string",
      "clinical_stage_group": "string"
    }
  ],
  "followups": [
    {
      "submitter_follow_up_id": "string",
      "date_of_followup": "string",
      "disease_status_at_followup": "string",
      "relapse_type": "string",
      "date_of_relapse": "string",
      "method_of_progression_status": [
        null
      ],
      "anatomic_site_progression_or_recurrence": [
        null
      ],
      "recurrence_tumour_staging_system": "string",
      "recurrence_t_category": "string",
      "recurrence_n_category": "string",
      "recurrence_m_category": "string",
      "recurrence_stage_group": "string"
    }
  ],
  "biomarkers": [
    {
      "submitter_specimen_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "submitter_treatment_id": "string",
      "submitter_follow_up_id": "string",
      "test_date": "string",
      "psa_level": 0,
      "ca125": 0,
      "cea": 0,
      "er_status": "string",
      "er_percent_positive": 0,
      "pr_status": "string",
      "pr_percent_positive": 0,
      "her2_ihc_status": "string",
      "her2_ish_status": "string",
      "hpv_ihc_status": "string",
      "hpv_pcr_status": "string",
      "hpv_strain": [
        null
      ]
    }
  ],
  "exposures": [
    {
      "tobacco_smoking_status": "string",
      "tobacco_type": [
        null
      ],
      "pack_years_smoked": 0
    }
  ],
  "comorbidities": [
    {
      "prior_malignancy": "string",
      "laterality_of_prior_malignancy": "string",
      "age_at_comorbidity_diagnosis": 0,
      "comorbidity_type_code": "string",
      "comorbidity_treatment_status": "string",
      "comorbidity_treatment": "string"
    }
  ],
  "submitter_donor_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "is_deceased": true,
  "lost_to_followup_after_clinical_event_identifier": "string",
  "lost_to_followup_reason": "string",
  "date_alive_after_lost_to_followup": "string",
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": [
    null
  ]
}

```

DonorWithClinicalDataSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|primary_diagnoses|[[NestedPrimaryDiagnosisSchema](#schemanestedprimarydiagnosisschema)]|true|none|none|
|followups|[[NestedFollowUpSchema](#schemanestedfollowupschema)]|true|none|none|
|biomarkers|[[NestedBiomarkerSchema](#schemanestedbiomarkerschema)]|true|none|none|
|exposures|[[NestedExposureSchema](#schemanestedexposureschema)]|true|none|none|
|comorbidities|[[NestedComorbiditySchema](#schemanestedcomorbidityschema)]|true|none|none|
|submitter_donor_id|string|true|none|none|
|program_id|string|true|none|none|
|gender|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sex_at_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|is_deceased|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_after_clinical_event_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_reason|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_alive_after_lost_to_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cause_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|primary_site|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedBiomarkerSchema">NestedBiomarkerSchema</h2>

<a id="schemanestedbiomarkerschema"></a>
<a id="schema_NestedBiomarkerSchema"></a>
<a id="tocSnestedbiomarkerschema"></a>
<a id="tocsnestedbiomarkerschema"></a>

```json
{
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string",
  "test_date": "string",
  "psa_level": 0,
  "ca125": 0,
  "cea": 0,
  "er_status": "string",
  "er_percent_positive": 0,
  "pr_status": "string",
  "pr_percent_positive": 0,
  "her2_ihc_status": "string",
  "her2_ish_status": "string",
  "hpv_ihc_status": "string",
  "hpv_pcr_status": "string",
  "hpv_strain": [
    null
  ]
}

```

NestedBiomarkerSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|test_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|psa_level|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ca125|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cea|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ish_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_pcr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_strain|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedChemotherapySchema">NestedChemotherapySchema</h2>

<a id="schemanestedchemotherapyschema"></a>
<a id="schema_NestedChemotherapySchema"></a>
<a id="tocSnestedchemotherapyschema"></a>
<a id="tocsnestedchemotherapyschema"></a>

```json
{
  "drug_reference_database": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "chemotherapy_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

NestedChemotherapySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|chemotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedComorbiditySchema">NestedComorbiditySchema</h2>

<a id="schemanestedcomorbidityschema"></a>
<a id="schema_NestedComorbiditySchema"></a>
<a id="tocSnestedcomorbidityschema"></a>
<a id="tocsnestedcomorbidityschema"></a>

```json
{
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": 0,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string"
}

```

NestedComorbiditySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality_of_prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|age_at_comorbidity_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedExposureSchema">NestedExposureSchema</h2>

<a id="schemanestedexposureschema"></a>
<a id="schema_NestedExposureSchema"></a>
<a id="tocSnestedexposureschema"></a>
<a id="tocsnestedexposureschema"></a>

```json
{
  "tobacco_smoking_status": "string",
  "tobacco_type": [
    null
  ],
  "pack_years_smoked": 0
}

```

NestedExposureSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tobacco_smoking_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tobacco_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pack_years_smoked|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedFollowUpSchema">NestedFollowUpSchema</h2>

<a id="schemanestedfollowupschema"></a>
<a id="schema_NestedFollowUpSchema"></a>
<a id="tocSnestedfollowupschema"></a>
<a id="tocsnestedfollowupschema"></a>

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": [
    null
  ],
  "anatomic_site_progression_or_recurrence": [
    null
  ],
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string"
}

```

NestedFollowUpSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|string|true|none|none|
|date_of_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|disease_status_at_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|relapse_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_relapse|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|method_of_progression_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|anatomic_site_progression_or_recurrence|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedHormoneTherapySchema">NestedHormoneTherapySchema</h2>

<a id="schemanestedhormonetherapyschema"></a>
<a id="schema_NestedHormoneTherapySchema"></a>
<a id="tocSnestedhormonetherapyschema"></a>
<a id="tocsnestedhormonetherapyschema"></a>

```json
{
  "drug_reference_database": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "hormone_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

NestedHormoneTherapySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hormone_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedImmunotherapySchema">NestedImmunotherapySchema</h2>

<a id="schemanestedimmunotherapyschema"></a>
<a id="schema_NestedImmunotherapySchema"></a>
<a id="tocSnestedimmunotherapyschema"></a>
<a id="tocsnestedimmunotherapyschema"></a>

```json
{
  "drug_reference_database": "string",
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "immunotherapy_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

NestedImmunotherapySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedPrimaryDiagnosisSchema">NestedPrimaryDiagnosisSchema</h2>

<a id="schemanestedprimarydiagnosisschema"></a>
<a id="schema_NestedPrimaryDiagnosisSchema"></a>
<a id="tocSnestedprimarydiagnosisschema"></a>
<a id="tocsnestedprimarydiagnosisschema"></a>

```json
{
  "specimens": [
    {
      "sample_registrations": [
        {
          "submitter_sample_id": "string",
          "specimen_tissue_source": "string",
          "tumour_normal_designation": "string",
          "specimen_type": "string",
          "sample_type": "string"
        }
      ],
      "submitter_specimen_id": "string",
      "pathological_tumour_staging_system": "string",
      "pathological_t_category": "string",
      "pathological_n_category": "string",
      "pathological_m_category": "string",
      "pathological_stage_group": "string",
      "specimen_collection_date": "string",
      "specimen_storage": "string",
      "specimen_processing": "string",
      "tumour_histological_type": "string",
      "specimen_anatomic_location": "string",
      "specimen_laterality": "string",
      "reference_pathology_confirmed_diagnosis": "string",
      "reference_pathology_confirmed_tumour_presence": "string",
      "tumour_grading_system": "string",
      "tumour_grade": "string",
      "percent_tumour_cells_range": "string",
      "percent_tumour_cells_measurement_method": "string"
    }
  ],
  "treatments": [
    {
      "chemotherapies": [
        {
          "drug_reference_database": "string",
          "drug_name": "string",
          "drug_reference_identifier": "string",
          "chemotherapy_drug_dose_units": "string",
          "prescribed_cumulative_drug_dose": 0,
          "actual_cumulative_drug_dose": 0
        }
      ],
      "immunotherapies": [
        {
          "drug_reference_database": "string",
          "immunotherapy_type": "string",
          "drug_name": "string",
          "drug_reference_identifier": "string",
          "immunotherapy_drug_dose_units": "string",
          "prescribed_cumulative_drug_dose": 0,
          "actual_cumulative_drug_dose": 0
        }
      ],
      "hormone_therapies": [
        {
          "drug_reference_database": "string",
          "drug_name": "string",
          "drug_reference_identifier": "string",
          "hormone_drug_dose_units": "string",
          "prescribed_cumulative_drug_dose": 0,
          "actual_cumulative_drug_dose": 0
        }
      ],
      "radiations": [
        {
          "radiation_therapy_modality": "string",
          "radiation_therapy_type": "string",
          "radiation_therapy_fractions": 0,
          "radiation_therapy_dosage": 0,
          "anatomical_site_irradiated": "string",
          "radiation_boost": true,
          "reference_radiation_treatment_id": "string"
        }
      ],
      "surgeries": [
        {
          "submitter_specimen_id": "string",
          "surgery_type": "string",
          "surgery_site": "string",
          "surgery_location": "string",
          "tumour_length": 0,
          "tumour_width": 0,
          "greatest_dimension_tumour": 0,
          "tumour_focality": "string",
          "residual_tumour_classification": "string",
          "margin_types_involved": [
            null
          ],
          "margin_types_not_involved": [
            null
          ],
          "margin_types_not_assessed": [
            null
          ],
          "lymphovascular_invasion": "string",
          "perineural_invasion": "string"
        }
      ],
      "followups": [
        {
          "submitter_follow_up_id": "string",
          "date_of_followup": "string",
          "disease_status_at_followup": "string",
          "relapse_type": "string",
          "date_of_relapse": "string",
          "method_of_progression_status": [
            null
          ],
          "anatomic_site_progression_or_recurrence": [
            null
          ],
          "recurrence_tumour_staging_system": "string",
          "recurrence_t_category": "string",
          "recurrence_n_category": "string",
          "recurrence_m_category": "string",
          "recurrence_stage_group": "string"
        }
      ],
      "submitter_treatment_id": "string",
      "treatment_type": [
        null
      ],
      "is_primary_treatment": "string",
      "line_of_treatment": 0,
      "treatment_start_date": "string",
      "treatment_end_date": "string",
      "treatment_setting": "string",
      "treatment_intent": "string",
      "days_per_cycle": 0,
      "number_of_cycles": 0,
      "response_to_treatment_criteria_method": "string",
      "response_to_treatment": "string",
      "status_of_treatment": "string"
    }
  ],
  "followups": [
    {
      "submitter_follow_up_id": "string",
      "date_of_followup": "string",
      "disease_status_at_followup": "string",
      "relapse_type": "string",
      "date_of_relapse": "string",
      "method_of_progression_status": [
        null
      ],
      "anatomic_site_progression_or_recurrence": [
        null
      ],
      "recurrence_tumour_staging_system": "string",
      "recurrence_t_category": "string",
      "recurrence_n_category": "string",
      "recurrence_m_category": "string",
      "recurrence_stage_group": "string"
    }
  ],
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "laterality": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": 0,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string"
}

```

NestedPrimaryDiagnosisSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimens|[[NestedSpecimenSchema](#schemanestedspecimenschema)]|true|none|none|
|treatments|[[NestedTreatmentSchema](#schemanestedtreatmentschema)]|true|none|none|
|followups|[[NestedFollowUpSchema](#schemanestedfollowupschema)]|true|none|none|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cancer_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|basis_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_lymph_nodes_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedRadiationSchema">NestedRadiationSchema</h2>

<a id="schemanestedradiationschema"></a>
<a id="schema_NestedRadiationSchema"></a>
<a id="tocSnestedradiationschema"></a>
<a id="tocsnestedradiationschema"></a>

```json
{
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": 0,
  "radiation_therapy_dosage": 0,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string"
}

```

NestedRadiationSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_modality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_fractions|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_dosage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|anatomical_site_irradiated|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_boost|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_radiation_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedSampleRegistrationSchema">NestedSampleRegistrationSchema</h2>

<a id="schemanestedsampleregistrationschema"></a>
<a id="schema_NestedSampleRegistrationSchema"></a>
<a id="tocSnestedsampleregistrationschema"></a>
<a id="tocsnestedsampleregistrationschema"></a>

```json
{
  "submitter_sample_id": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string"
}

```

NestedSampleRegistrationSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_sample_id|string|true|none|none|
|specimen_tissue_source|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_normal_designation|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sample_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedSpecimenSchema">NestedSpecimenSchema</h2>

<a id="schemanestedspecimenschema"></a>
<a id="schema_NestedSpecimenSchema"></a>
<a id="tocSnestedspecimenschema"></a>
<a id="tocsnestedspecimenschema"></a>

```json
{
  "sample_registrations": [
    {
      "submitter_sample_id": "string",
      "specimen_tissue_source": "string",
      "tumour_normal_designation": "string",
      "specimen_type": "string",
      "sample_type": "string"
    }
  ],
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "specimen_processing": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "specimen_laterality": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string"
}

```

NestedSpecimenSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sample_registrations|[[NestedSampleRegistrationSchema](#schemanestedsampleregistrationschema)]|true|none|none|
|submitter_specimen_id|string|true|none|none|
|pathological_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_collection_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_storage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_processing|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_histological_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_anatomic_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_tumour_presence|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grading_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grade|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_range|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_measurement_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedSurgerySchema">NestedSurgerySchema</h2>

<a id="schemanestedsurgeryschema"></a>
<a id="schema_NestedSurgerySchema"></a>
<a id="tocSnestedsurgeryschema"></a>
<a id="tocsnestedsurgeryschema"></a>

```json
{
  "submitter_specimen_id": "string",
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": 0,
  "tumour_width": 0,
  "greatest_dimension_tumour": 0,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": [
    null
  ],
  "margin_types_not_involved": [
    null
  ],
  "margin_types_not_assessed": [
    null
  ],
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string"
}

```

NestedSurgerySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_site|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_length|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_width|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|greatest_dimension_tumour|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_focality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|residual_tumour_classification|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_involved|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_not_involved|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_not_assessed|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymphovascular_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|perineural_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_NestedTreatmentSchema">NestedTreatmentSchema</h2>

<a id="schemanestedtreatmentschema"></a>
<a id="schema_NestedTreatmentSchema"></a>
<a id="tocSnestedtreatmentschema"></a>
<a id="tocsnestedtreatmentschema"></a>

```json
{
  "chemotherapies": [
    {
      "drug_reference_database": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "chemotherapy_drug_dose_units": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "immunotherapies": [
    {
      "drug_reference_database": "string",
      "immunotherapy_type": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "immunotherapy_drug_dose_units": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "hormone_therapies": [
    {
      "drug_reference_database": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "hormone_drug_dose_units": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "radiations": [
    {
      "radiation_therapy_modality": "string",
      "radiation_therapy_type": "string",
      "radiation_therapy_fractions": 0,
      "radiation_therapy_dosage": 0,
      "anatomical_site_irradiated": "string",
      "radiation_boost": true,
      "reference_radiation_treatment_id": "string"
    }
  ],
  "surgeries": [
    {
      "submitter_specimen_id": "string",
      "surgery_type": "string",
      "surgery_site": "string",
      "surgery_location": "string",
      "tumour_length": 0,
      "tumour_width": 0,
      "greatest_dimension_tumour": 0,
      "tumour_focality": "string",
      "residual_tumour_classification": "string",
      "margin_types_involved": [
        null
      ],
      "margin_types_not_involved": [
        null
      ],
      "margin_types_not_assessed": [
        null
      ],
      "lymphovascular_invasion": "string",
      "perineural_invasion": "string"
    }
  ],
  "followups": [
    {
      "submitter_follow_up_id": "string",
      "date_of_followup": "string",
      "disease_status_at_followup": "string",
      "relapse_type": "string",
      "date_of_relapse": "string",
      "method_of_progression_status": [
        null
      ],
      "anatomic_site_progression_or_recurrence": [
        null
      ],
      "recurrence_tumour_staging_system": "string",
      "recurrence_t_category": "string",
      "recurrence_n_category": "string",
      "recurrence_m_category": "string",
      "recurrence_stage_group": "string"
    }
  ],
  "submitter_treatment_id": "string",
  "treatment_type": [
    null
  ],
  "is_primary_treatment": "string",
  "line_of_treatment": 0,
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": 0,
  "number_of_cycles": 0,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "status_of_treatment": "string"
}

```

NestedTreatmentSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|chemotherapies|[[NestedChemotherapySchema](#schemanestedchemotherapyschema)]|true|none|none|
|immunotherapies|[[NestedImmunotherapySchema](#schemanestedimmunotherapyschema)]|true|none|none|
|hormone_therapies|[[NestedHormoneTherapySchema](#schemanestedhormonetherapyschema)]|true|none|none|
|radiations|[[NestedRadiationSchema](#schemanestedradiationschema)]|true|none|none|
|surgeries|[[NestedSurgerySchema](#schemanestedsurgeryschema)]|true|none|none|
|followups|[[NestedFollowUpSchema](#schemanestedfollowupschema)]|true|none|none|
|submitter_treatment_id|string|true|none|none|
|treatment_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[any]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|is_primary_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|line_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_start_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_end_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_setting|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_intent|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|days_per_cycle|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_of_cycles|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment_criteria_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_Input">Input</h2>

<a id="schemainput"></a>
<a id="schema_Input"></a>
<a id="tocSinput"></a>
<a id="tocsinput"></a>

```json
{
  "page": 1,
  "page_size": 1
}

```

Input

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|page|integer|false|none|none|
|page_size|integer|false|none|none|

<h2 id="tocS_ProgramFilterSchema">ProgramFilterSchema</h2>

<a id="schemaprogramfilterschema"></a>
<a id="schema_ProgramFilterSchema"></a>
<a id="tocSprogramfilterschema"></a>
<a id="tocsprogramfilterschema"></a>

```json
{
  "program_id": "string"
}

```

ProgramFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PagedProgramModelSchema">PagedProgramModelSchema</h2>

<a id="schemapagedprogrammodelschema"></a>
<a id="schema_PagedProgramModelSchema"></a>
<a id="tocSpagedprogrammodelschema"></a>
<a id="tocspagedprogrammodelschema"></a>

```json
{
  "items": [
    {
      "program_id": "string",
      "metadata": {},
      "created": "2019-08-24T14:15:22Z",
      "updated": "2019-08-24T14:15:22Z"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedProgramModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[ProgramModelSchema](#schemaprogrammodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_DonorFilterSchema">DonorFilterSchema</h2>

<a id="schemadonorfilterschema"></a>
<a id="schema_DonorFilterSchema"></a>
<a id="tocSdonorfilterschema"></a>
<a id="tocsdonorfilterschema"></a>

```json
{
  "submitter_donor_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "is_deceased": true,
  "lost_to_followup_after_clinical_event_identifier": "string",
  "lost_to_followup_reason": "string",
  "date_alive_after_lost_to_followup": "string",
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": [
    "string"
  ]
}

```

DonorFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|gender|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sex_at_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|is_deceased|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_after_clinical_event_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_reason|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_alive_after_lost_to_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cause_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|primary_site|[string]|false|none|none|

<h2 id="tocS_CauseOfDeathEnum">CauseOfDeathEnum</h2>

<a id="schemacauseofdeathenum"></a>
<a id="schema_CauseOfDeathEnum"></a>
<a id="tocScauseofdeathenum"></a>
<a id="tocscauseofdeathenum"></a>

```json
"Died of cancer"

```

CauseOfDeathEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|CauseOfDeathEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|CauseOfDeathEnum|Died of cancer|
|CauseOfDeathEnum|Died of other reasons|
|CauseOfDeathEnum|Unknown|

<h2 id="tocS_DonorModelSchema">DonorModelSchema</h2>

<a id="schemadonormodelschema"></a>
<a id="schema_DonorModelSchema"></a>
<a id="tocSdonormodelschema"></a>
<a id="tocsdonormodelschema"></a>

```json
{
  "cause_of_death": "Died of cancer",
  "submitter_donor_id": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": [
    "Accessory sinuses"
  ],
  "gender": "Man",
  "sex_at_birth": "Male",
  "lost_to_followup_reason": "Completed study",
  "date_alive_after_lost_to_followup": "string",
  "program_id": "string",
  "is_deceased": true,
  "lost_to_followup_after_clinical_event_identifier": "string"
}

```

DonorModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cause_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[CauseOfDeathEnum](#schemacauseofdeathenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|date_of_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_death|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|primary_site|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[PrimarySiteEnum](#schemaprimarysiteenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|gender|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[GenderEnum](#schemagenderenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sex_at_birth|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SexAtBirthEnum](#schemasexatbirthenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_reason|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[LostToFollowupReasonEnum](#schemalosttofollowupreasonenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_alive_after_lost_to_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|is_deceased|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lost_to_followup_after_clinical_event_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_GenderEnum">GenderEnum</h2>

<a id="schemagenderenum"></a>
<a id="schema_GenderEnum"></a>
<a id="tocSgenderenum"></a>
<a id="tocsgenderenum"></a>

```json
"Man"

```

GenderEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|GenderEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|GenderEnum|Man|
|GenderEnum|Woman|
|GenderEnum|Non-binary|

<h2 id="tocS_LostToFollowupReasonEnum">LostToFollowupReasonEnum</h2>

<a id="schemalosttofollowupreasonenum"></a>
<a id="schema_LostToFollowupReasonEnum"></a>
<a id="tocSlosttofollowupreasonenum"></a>
<a id="tocslosttofollowupreasonenum"></a>

```json
"Completed study"

```

LostToFollowupReasonEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|LostToFollowupReasonEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|LostToFollowupReasonEnum|Completed study|
|LostToFollowupReasonEnum|Discharged to palliative care|
|LostToFollowupReasonEnum|Lost contact|
|LostToFollowupReasonEnum|Not applicable|
|LostToFollowupReasonEnum|Unknown|
|LostToFollowupReasonEnum|Withdrew from study|

<h2 id="tocS_PagedDonorModelSchema">PagedDonorModelSchema</h2>

<a id="schemapageddonormodelschema"></a>
<a id="schema_PagedDonorModelSchema"></a>
<a id="tocSpageddonormodelschema"></a>
<a id="tocspageddonormodelschema"></a>

```json
{
  "items": [
    {
      "cause_of_death": "Died of cancer",
      "submitter_donor_id": "string",
      "date_of_birth": "string",
      "date_of_death": "string",
      "primary_site": [
        "Accessory sinuses"
      ],
      "gender": "Man",
      "sex_at_birth": "Male",
      "lost_to_followup_reason": "Completed study",
      "date_alive_after_lost_to_followup": "string",
      "program_id": "string",
      "is_deceased": true,
      "lost_to_followup_after_clinical_event_identifier": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedDonorModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[DonorModelSchema](#schemadonormodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PrimarySiteEnum">PrimarySiteEnum</h2>

<a id="schemaprimarysiteenum"></a>
<a id="schema_PrimarySiteEnum"></a>
<a id="tocSprimarysiteenum"></a>
<a id="tocsprimarysiteenum"></a>

```json
"Accessory sinuses"

```

PrimarySiteEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|PrimarySiteEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|PrimarySiteEnum|Accessory sinuses|
|PrimarySiteEnum|Adrenal gland|
|PrimarySiteEnum|Anus and anal canal|
|PrimarySiteEnum|Base of tongue|
|PrimarySiteEnum|Bladder|
|PrimarySiteEnum|Bones, joints and articular cartilage of limbs|
|PrimarySiteEnum|Bones, joints and articular cartilage of other and unspecified sites|
|PrimarySiteEnum|Brain|
|PrimarySiteEnum|Breast|
|PrimarySiteEnum|Bronchus and lung|
|PrimarySiteEnum|Cervix uteri|
|PrimarySiteEnum|Colon|
|PrimarySiteEnum|Connective, subcutaneous and other soft tissues|
|PrimarySiteEnum|Corpus uteri|
|PrimarySiteEnum|Esophagus|
|PrimarySiteEnum|Eye and adnexa|
|PrimarySiteEnum|Floor of mouth|
|PrimarySiteEnum|Gallbladder|
|PrimarySiteEnum|Gum|
|PrimarySiteEnum|Heart, mediastinum, and pleura|
|PrimarySiteEnum|Hematopoietic and reticuloendothelial systems|
|PrimarySiteEnum|Hypopharynx|
|PrimarySiteEnum|Kidney|
|PrimarySiteEnum|Larynx|
|PrimarySiteEnum|Lip|
|PrimarySiteEnum|Liver and intrahepatic bile ducts|
|PrimarySiteEnum|Lymph nodes|
|PrimarySiteEnum|Meninges|
|PrimarySiteEnum|Nasal cavity and middle ear|
|PrimarySiteEnum|Nasopharynx|
|PrimarySiteEnum|Oropharynx|
|PrimarySiteEnum|Other and ill-defined digestive organs|
|PrimarySiteEnum|Other and ill-defined sites|
|PrimarySiteEnum|Other and ill-defined sites in lip, oral cavity and pharynx|
|PrimarySiteEnum|Other and ill-defined sites within respiratory system and intrathoracic organs|
|PrimarySiteEnum|Other and unspecified female genital organs|
|PrimarySiteEnum|Other and unspecified major salivary glands|
|PrimarySiteEnum|Other and unspecified male genital organs|
|PrimarySiteEnum|Other and unspecified parts of biliary tract|
|PrimarySiteEnum|Other and unspecified parts of mouth|
|PrimarySiteEnum|Other and unspecified parts of tongue|
|PrimarySiteEnum|Other and unspecified urinary organs|
|PrimarySiteEnum|Other endocrine glands and related structures|
|PrimarySiteEnum|Ovary|
|PrimarySiteEnum|Palate|
|PrimarySiteEnum|Pancreas|
|PrimarySiteEnum|Parotid gland|
|PrimarySiteEnum|Penis|
|PrimarySiteEnum|Peripheral nerves and autonomic nervous system|
|PrimarySiteEnum|Placenta|
|PrimarySiteEnum|Prostate gland|
|PrimarySiteEnum|Pyriform sinus|
|PrimarySiteEnum|Rectosigmoid junction|
|PrimarySiteEnum|Rectum|
|PrimarySiteEnum|Renal pelvis|
|PrimarySiteEnum|Retroperitoneum and peritoneum|
|PrimarySiteEnum|Skin|
|PrimarySiteEnum|Small intestine|
|PrimarySiteEnum|Spinal cord, cranial nerves, and other parts of central nervous system|
|PrimarySiteEnum|Stomach|
|PrimarySiteEnum|Testis|
|PrimarySiteEnum|Thymus|
|PrimarySiteEnum|Thyroid gland|
|PrimarySiteEnum|Tonsil|
|PrimarySiteEnum|Trachea|
|PrimarySiteEnum|Ureter|
|PrimarySiteEnum|Uterus, NOS|
|PrimarySiteEnum|Vagina|
|PrimarySiteEnum|Vulva|
|PrimarySiteEnum|Unknown primary site|

<h2 id="tocS_SexAtBirthEnum">SexAtBirthEnum</h2>

<a id="schemasexatbirthenum"></a>
<a id="schema_SexAtBirthEnum"></a>
<a id="tocSsexatbirthenum"></a>
<a id="tocssexatbirthenum"></a>

```json
"Male"

```

SexAtBirthEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SexAtBirthEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SexAtBirthEnum|Male|
|SexAtBirthEnum|Female|
|SexAtBirthEnum|Other|
|SexAtBirthEnum|Unknown|

<h2 id="tocS_PrimaryDiagnosisFilterSchema">PrimaryDiagnosisFilterSchema</h2>

<a id="schemaprimarydiagnosisfilterschema"></a>
<a id="schema_PrimaryDiagnosisFilterSchema"></a>
<a id="tocSprimarydiagnosisfilterschema"></a>
<a id="tocsprimarydiagnosisfilterschema"></a>

```json
{
  "submitter_primary_diagnosis_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "laterality": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": 0,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string"
}

```

PrimaryDiagnosisFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cancer_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|basis_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_lymph_nodes_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_BasisOfDiagnosisEnum">BasisOfDiagnosisEnum</h2>

<a id="schemabasisofdiagnosisenum"></a>
<a id="schema_BasisOfDiagnosisEnum"></a>
<a id="tocSbasisofdiagnosisenum"></a>
<a id="tocsbasisofdiagnosisenum"></a>

```json
"Clinical investigation"

```

BasisOfDiagnosisEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|BasisOfDiagnosisEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|BasisOfDiagnosisEnum|Clinical investigation|
|BasisOfDiagnosisEnum|Clinical|
|BasisOfDiagnosisEnum|Cytology|
|BasisOfDiagnosisEnum|Death certificate only|
|BasisOfDiagnosisEnum|Histology of a metastasis|
|BasisOfDiagnosisEnum|Histology of a primary tumour|
|BasisOfDiagnosisEnum|Specific tumour markers|
|BasisOfDiagnosisEnum|Unknown|

<h2 id="tocS_LymphNodeMethodEnum">LymphNodeMethodEnum</h2>

<a id="schemalymphnodemethodenum"></a>
<a id="schema_LymphNodeMethodEnum"></a>
<a id="tocSlymphnodemethodenum"></a>
<a id="tocslymphnodemethodenum"></a>

```json
"Imaging"

```

LymphNodeMethodEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|LymphNodeMethodEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|LymphNodeMethodEnum|Imaging|
|LymphNodeMethodEnum|Lymph node dissection/pathological exam|
|LymphNodeMethodEnum|Physical palpation of patient|

<h2 id="tocS_LymphNodeStatusEnum">LymphNodeStatusEnum</h2>

<a id="schemalymphnodestatusenum"></a>
<a id="schema_LymphNodeStatusEnum"></a>
<a id="tocSlymphnodestatusenum"></a>
<a id="tocslymphnodestatusenum"></a>

```json
"Cannot be determined"

```

LymphNodeStatusEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|LymphNodeStatusEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|LymphNodeStatusEnum|Cannot be determined|
|LymphNodeStatusEnum|No|
|LymphNodeStatusEnum|No lymph nodes found in resected specimen|
|LymphNodeStatusEnum|Not applicable|
|LymphNodeStatusEnum|Yes|

<h2 id="tocS_MCategoryEnum">MCategoryEnum</h2>

<a id="schemamcategoryenum"></a>
<a id="schema_MCategoryEnum"></a>
<a id="tocSmcategoryenum"></a>
<a id="tocsmcategoryenum"></a>

```json
"M0"

```

MCategoryEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|MCategoryEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|MCategoryEnum|M0|
|MCategoryEnum|M0(i+)|
|MCategoryEnum|M1|
|MCategoryEnum|M1a|
|MCategoryEnum|M1a(0)|
|MCategoryEnum|M1a(1)|
|MCategoryEnum|M1b|
|MCategoryEnum|M1b(0)|
|MCategoryEnum|M1b(1)|
|MCategoryEnum|M1c|
|MCategoryEnum|M1c(0)|
|MCategoryEnum|M1c(1)|
|MCategoryEnum|M1d|
|MCategoryEnum|M1d(0)|
|MCategoryEnum|M1d(1)|
|MCategoryEnum|M1e|
|MCategoryEnum|MX|

<h2 id="tocS_NCategoryEnum">NCategoryEnum</h2>

<a id="schemancategoryenum"></a>
<a id="schema_NCategoryEnum"></a>
<a id="tocSncategoryenum"></a>
<a id="tocsncategoryenum"></a>

```json
"N0"

```

NCategoryEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|NCategoryEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|NCategoryEnum|N0|
|NCategoryEnum|N0a|
|NCategoryEnum|N0a (biopsy)|
|NCategoryEnum|N0b|
|NCategoryEnum|N0b (no biopsy)|
|NCategoryEnum|N0(i+)|
|NCategoryEnum|N0(i-)|
|NCategoryEnum|N0(mol+)|
|NCategoryEnum|N0(mol-)|
|NCategoryEnum|N1|
|NCategoryEnum|N1a|
|NCategoryEnum|N1a(sn)|
|NCategoryEnum|N1b|
|NCategoryEnum|N1c|
|NCategoryEnum|N1mi|
|NCategoryEnum|N2|
|NCategoryEnum|N2a|
|NCategoryEnum|N2b|
|NCategoryEnum|N2c|
|NCategoryEnum|N2mi|
|NCategoryEnum|N3|
|NCategoryEnum|N3a|
|NCategoryEnum|N3b|
|NCategoryEnum|N3c|
|NCategoryEnum|N4|
|NCategoryEnum|NX|

<h2 id="tocS_PagedPrimaryDiagnosisModelSchema">PagedPrimaryDiagnosisModelSchema</h2>

<a id="schemapagedprimarydiagnosismodelschema"></a>
<a id="schema_PagedPrimaryDiagnosisModelSchema"></a>
<a id="tocSpagedprimarydiagnosismodelschema"></a>
<a id="tocspagedprimarydiagnosismodelschema"></a>

```json
{
  "items": [
    {
      "submitter_primary_diagnosis_id": "string",
      "date_of_diagnosis": "string",
      "basis_of_diagnosis": "Clinical investigation",
      "lymph_nodes_examined_status": "Cannot be determined",
      "lymph_nodes_examined_method": "Imaging",
      "clinical_tumour_staging_system": "AJCC 8th edition",
      "clinical_t_category": "T0",
      "clinical_n_category": "N0",
      "clinical_m_category": "M0",
      "clinical_stage_group": "Stage 0",
      "laterality": "Bilateral",
      "program_id": "string",
      "submitter_donor_id": "string",
      "cancer_type_code": "string",
      "number_lymph_nodes_positive": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedPrimaryDiagnosisModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[PrimaryDiagnosisModelSchema](#schemaprimarydiagnosismodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PrimaryDiagnosisLateralityEnum">PrimaryDiagnosisLateralityEnum</h2>

<a id="schemaprimarydiagnosislateralityenum"></a>
<a id="schema_PrimaryDiagnosisLateralityEnum"></a>
<a id="tocSprimarydiagnosislateralityenum"></a>
<a id="tocsprimarydiagnosislateralityenum"></a>

```json
"Bilateral"

```

PrimaryDiagnosisLateralityEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|PrimaryDiagnosisLateralityEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|PrimaryDiagnosisLateralityEnum|Bilateral|
|PrimaryDiagnosisLateralityEnum|Left|
|PrimaryDiagnosisLateralityEnum|Midline|
|PrimaryDiagnosisLateralityEnum|Not a paired site|
|PrimaryDiagnosisLateralityEnum|Right|
|PrimaryDiagnosisLateralityEnum|Unilateral, side not specified|
|PrimaryDiagnosisLateralityEnum|Unknown|

<h2 id="tocS_PrimaryDiagnosisModelSchema">PrimaryDiagnosisModelSchema</h2>

<a id="schemaprimarydiagnosismodelschema"></a>
<a id="schema_PrimaryDiagnosisModelSchema"></a>
<a id="tocSprimarydiagnosismodelschema"></a>
<a id="tocsprimarydiagnosismodelschema"></a>

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "basis_of_diagnosis": "Clinical investigation",
  "lymph_nodes_examined_status": "Cannot be determined",
  "lymph_nodes_examined_method": "Imaging",
  "clinical_tumour_staging_system": "AJCC 8th edition",
  "clinical_t_category": "T0",
  "clinical_n_category": "N0",
  "clinical_m_category": "M0",
  "clinical_stage_group": "Stage 0",
  "laterality": "Bilateral",
  "program_id": "string",
  "submitter_donor_id": "string",
  "cancer_type_code": "string",
  "number_lymph_nodes_positive": 0
}

```

PrimaryDiagnosisModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|string|true|none|none|
|date_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|basis_of_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[BasisOfDiagnosisEnum](#schemabasisofdiagnosisenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[LymphNodeStatusEnum](#schemalymphnodestatusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymph_nodes_examined_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[LymphNodeMethodEnum](#schemalymphnodemethodenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourStagingSystemEnum](#schematumourstagingsystemenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TCategoryEnum](#schematcategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[NCategoryEnum](#schemancategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[MCategoryEnum](#schemamcategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|clinical_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[StageGroupEnum](#schemastagegroupenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[PrimaryDiagnosisLateralityEnum](#schemaprimarydiagnosislateralityenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cancer_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_lymph_nodes_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_StageGroupEnum">StageGroupEnum</h2>

<a id="schemastagegroupenum"></a>
<a id="schema_StageGroupEnum"></a>
<a id="tocSstagegroupenum"></a>
<a id="tocsstagegroupenum"></a>

```json
"Stage 0"

```

StageGroupEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|StageGroupEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|StageGroupEnum|Stage 0|
|StageGroupEnum|Stage 0a|
|StageGroupEnum|Stage 0is|
|StageGroupEnum|Stage 1|
|StageGroupEnum|Stage 1A|
|StageGroupEnum|Stage 1B|
|StageGroupEnum|Stage A|
|StageGroupEnum|Stage B|
|StageGroupEnum|Stage C|
|StageGroupEnum|Stage I|
|StageGroupEnum|Stage IA|
|StageGroupEnum|Stage IA1|
|StageGroupEnum|Stage IA2|
|StageGroupEnum|Stage IA3|
|StageGroupEnum|Stage IAB|
|StageGroupEnum|Stage IAE|
|StageGroupEnum|Stage IAES|
|StageGroupEnum|Stage IAS|
|StageGroupEnum|Stage IB|
|StageGroupEnum|Stage IB1|
|StageGroupEnum|Stage IB2|
|StageGroupEnum|Stage IBE|
|StageGroupEnum|Stage IBES|
|StageGroupEnum|Stage IBS|
|StageGroupEnum|Stage IC|
|StageGroupEnum|Stage IE|
|StageGroupEnum|Stage IEA|
|StageGroupEnum|Stage IEB|
|StageGroupEnum|Stage IES|
|StageGroupEnum|Stage II|
|StageGroupEnum|Stage II bulky|
|StageGroupEnum|Stage IIA|
|StageGroupEnum|Stage IIA1|
|StageGroupEnum|Stage IIA2|
|StageGroupEnum|Stage IIAE|
|StageGroupEnum|Stage IIAES|
|StageGroupEnum|Stage IIAS|
|StageGroupEnum|Stage IIB|
|StageGroupEnum|Stage IIBE|
|StageGroupEnum|Stage IIBES|
|StageGroupEnum|Stage IIBS|
|StageGroupEnum|Stage IIC|
|StageGroupEnum|Stage IIE|
|StageGroupEnum|Stage IIEA|
|StageGroupEnum|Stage IIEB|
|StageGroupEnum|Stage IIES|
|StageGroupEnum|Stage III|
|StageGroupEnum|Stage IIIA|
|StageGroupEnum|Stage IIIA1|
|StageGroupEnum|Stage IIIA2|
|StageGroupEnum|Stage IIIAE|
|StageGroupEnum|Stage IIIAES|
|StageGroupEnum|Stage IIIAS|
|StageGroupEnum|Stage IIIB|
|StageGroupEnum|Stage IIIBE|
|StageGroupEnum|Stage IIIBES|
|StageGroupEnum|Stage IIIBS|
|StageGroupEnum|Stage IIIC|
|StageGroupEnum|Stage IIIC1|
|StageGroupEnum|Stage IIIC2|
|StageGroupEnum|Stage IIID|
|StageGroupEnum|Stage IIIE|
|StageGroupEnum|Stage IIIES|
|StageGroupEnum|Stage IIIS|
|StageGroupEnum|Stage IIS|
|StageGroupEnum|Stage IS|
|StageGroupEnum|Stage IV|
|StageGroupEnum|Stage IVA|
|StageGroupEnum|Stage IVA1|
|StageGroupEnum|Stage IVA2|
|StageGroupEnum|Stage IVAE|
|StageGroupEnum|Stage IVAES|
|StageGroupEnum|Stage IVAS|
|StageGroupEnum|Stage IVB|
|StageGroupEnum|Stage IVBE|
|StageGroupEnum|Stage IVBES|
|StageGroupEnum|Stage IVBS|
|StageGroupEnum|Stage IVC|
|StageGroupEnum|Stage IVE|
|StageGroupEnum|Stage IVES|
|StageGroupEnum|Stage IVS|
|StageGroupEnum|In situ|
|StageGroupEnum|Localized|
|StageGroupEnum|Regionalized|
|StageGroupEnum|Distant|
|StageGroupEnum|Stage L1|
|StageGroupEnum|Stage L2|
|StageGroupEnum|Stage M|
|StageGroupEnum|Stage Ms|
|StageGroupEnum|Stage 2A|
|StageGroupEnum|Stage 2B|
|StageGroupEnum|Stage 3|
|StageGroupEnum|Stage 4|
|StageGroupEnum|Stage 4S|
|StageGroupEnum|Occult Carcinoma|

<h2 id="tocS_TCategoryEnum">TCategoryEnum</h2>

<a id="schematcategoryenum"></a>
<a id="schema_TCategoryEnum"></a>
<a id="tocStcategoryenum"></a>
<a id="tocstcategoryenum"></a>

```json
"T0"

```

TCategoryEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TCategoryEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TCategoryEnum|T0|
|TCategoryEnum|T1|
|TCategoryEnum|T1a|
|TCategoryEnum|T1a1|
|TCategoryEnum|T1a2|
|TCategoryEnum|T1a(s)|
|TCategoryEnum|T1a(m)|
|TCategoryEnum|T1b|
|TCategoryEnum|T1b1|
|TCategoryEnum|T1b2|
|TCategoryEnum|T1b(s)|
|TCategoryEnum|T1b(m)|
|TCategoryEnum|T1c|
|TCategoryEnum|T1d|
|TCategoryEnum|T1mi|
|TCategoryEnum|T2|
|TCategoryEnum|T2(s)|
|TCategoryEnum|T2(m)|
|TCategoryEnum|T2a|
|TCategoryEnum|T2a1|
|TCategoryEnum|T2a2|
|TCategoryEnum|T2b|
|TCategoryEnum|T2c|
|TCategoryEnum|T2d|
|TCategoryEnum|T3|
|TCategoryEnum|T3(s)|
|TCategoryEnum|T3(m)|
|TCategoryEnum|T3a|
|TCategoryEnum|T3b|
|TCategoryEnum|T3c|
|TCategoryEnum|T3d|
|TCategoryEnum|T3e|
|TCategoryEnum|T4|
|TCategoryEnum|T4a|
|TCategoryEnum|T4a(s)|
|TCategoryEnum|T4a(m)|
|TCategoryEnum|T4b|
|TCategoryEnum|T4b(s)|
|TCategoryEnum|T4b(m)|
|TCategoryEnum|T4c|
|TCategoryEnum|T4d|
|TCategoryEnum|T4e|
|TCategoryEnum|Ta|
|TCategoryEnum|Tis|
|TCategoryEnum|Tis(DCIS)|
|TCategoryEnum|Tis(LAMN)|
|TCategoryEnum|Tis(LCIS)|
|TCategoryEnum|Tis(Paget)|
|TCategoryEnum|Tis(Paget's)|
|TCategoryEnum|Tis pu|
|TCategoryEnum|Tis pd|
|TCategoryEnum|TX|

<h2 id="tocS_TumourStagingSystemEnum">TumourStagingSystemEnum</h2>

<a id="schematumourstagingsystemenum"></a>
<a id="schema_TumourStagingSystemEnum"></a>
<a id="tocStumourstagingsystemenum"></a>
<a id="tocstumourstagingsystemenum"></a>

```json
"AJCC 8th edition"

```

TumourStagingSystemEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TumourStagingSystemEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TumourStagingSystemEnum|AJCC 8th edition|
|TumourStagingSystemEnum|AJCC 7th edition|
|TumourStagingSystemEnum|AJCC 6th edition|
|TumourStagingSystemEnum|Ann Arbor staging system|
|TumourStagingSystemEnum|Binet staging system|
|TumourStagingSystemEnum|Durie-Salmon staging system|
|TumourStagingSystemEnum|FIGO staging system|
|TumourStagingSystemEnum|International Neuroblastoma Risk Group Staging System|
|TumourStagingSystemEnum|International Neuroblastoma Staging System|
|TumourStagingSystemEnum|Lugano staging system|
|TumourStagingSystemEnum|Rai staging system|
|TumourStagingSystemEnum|Revised International staging system (RISS)|
|TumourStagingSystemEnum|SEER staging system|
|TumourStagingSystemEnum|St Jude staging system|

<h2 id="tocS_BiomarkerFilterSchema">BiomarkerFilterSchema</h2>

<a id="schemabiomarkerfilterschema"></a>
<a id="schema_BiomarkerFilterSchema"></a>
<a id="tocSbiomarkerfilterschema"></a>
<a id="tocsbiomarkerfilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string",
  "test_date": "string",
  "psa_level": 0,
  "ca125": 0,
  "cea": 0,
  "er_status": "string",
  "er_percent_positive": 0,
  "pr_status": "string",
  "pr_percent_positive": 0,
  "her2_ihc_status": "string",
  "her2_ish_status": "string",
  "hpv_ihc_status": "string",
  "hpv_pcr_status": "string",
  "hpv_strain": [
    "string"
  ]
}

```

BiomarkerFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|test_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|psa_level|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ca125|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cea|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ish_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_pcr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_strain|[string]|false|none|none|

<h2 id="tocS_BiomarkerModelSchema">BiomarkerModelSchema</h2>

<a id="schemabiomarkermodelschema"></a>
<a id="schema_BiomarkerModelSchema"></a>
<a id="tocSbiomarkermodelschema"></a>
<a id="tocsbiomarkermodelschema"></a>

```json
{
  "er_status": "Cannot be determined",
  "pr_status": "Cannot be determined",
  "her2_ihc_status": "Cannot be determined",
  "her2_ish_status": "Cannot be determined",
  "hpv_ihc_status": "Cannot be determined",
  "hpv_pcr_status": "Cannot be determined",
  "hpv_strain": [
    "HPV16"
  ],
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string",
  "test_date": "string",
  "psa_level": 0,
  "ca125": 0,
  "cea": 0,
  "er_percent_positive": 0,
  "pr_percent_positive": 0
}

```

BiomarkerModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ErPrHpvStatusEnum](#schemaerprhpvstatusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ErPrHpvStatusEnum](#schemaerprhpvstatusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[Her2StatusEnum](#schemaher2statusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|her2_ish_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[Her2StatusEnum](#schemaher2statusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_ihc_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ErPrHpvStatusEnum](#schemaerprhpvstatusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_pcr_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ErPrHpvStatusEnum](#schemaerprhpvstatusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hpv_strain|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[HpvStrainEnum](#schemahpvstrainenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|test_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|psa_level|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ca125|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cea|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|er_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pr_percent_positive|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ErPrHpvStatusEnum">ErPrHpvStatusEnum</h2>

<a id="schemaerprhpvstatusenum"></a>
<a id="schema_ErPrHpvStatusEnum"></a>
<a id="tocSerprhpvstatusenum"></a>
<a id="tocserprhpvstatusenum"></a>

```json
"Cannot be determined"

```

ErPrHpvStatusEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ErPrHpvStatusEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|ErPrHpvStatusEnum|Cannot be determined|
|ErPrHpvStatusEnum|Negative|
|ErPrHpvStatusEnum|Not applicable|
|ErPrHpvStatusEnum|Positive|
|ErPrHpvStatusEnum|Unknown|

<h2 id="tocS_Her2StatusEnum">Her2StatusEnum</h2>

<a id="schemaher2statusenum"></a>
<a id="schema_Her2StatusEnum"></a>
<a id="tocSher2statusenum"></a>
<a id="tocsher2statusenum"></a>

```json
"Cannot be determined"

```

Her2StatusEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|Her2StatusEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|Her2StatusEnum|Cannot be determined|
|Her2StatusEnum|Equivocal|
|Her2StatusEnum|Positive|
|Her2StatusEnum|Negative|
|Her2StatusEnum|Not applicable|
|Her2StatusEnum|Unknown|

<h2 id="tocS_HpvStrainEnum">HpvStrainEnum</h2>

<a id="schemahpvstrainenum"></a>
<a id="schema_HpvStrainEnum"></a>
<a id="tocShpvstrainenum"></a>
<a id="tocshpvstrainenum"></a>

```json
"HPV16"

```

HpvStrainEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|HpvStrainEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|HpvStrainEnum|HPV16|
|HpvStrainEnum|HPV18|
|HpvStrainEnum|HPV31|
|HpvStrainEnum|HPV33|
|HpvStrainEnum|HPV35|
|HpvStrainEnum|HPV39|
|HpvStrainEnum|HPV45|
|HpvStrainEnum|HPV51|
|HpvStrainEnum|HPV52|
|HpvStrainEnum|HPV56|
|HpvStrainEnum|HPV58|
|HpvStrainEnum|HPV59|
|HpvStrainEnum|HPV66|
|HpvStrainEnum|HPV68|
|HpvStrainEnum|HPV73|

<h2 id="tocS_PagedBiomarkerModelSchema">PagedBiomarkerModelSchema</h2>

<a id="schemapagedbiomarkermodelschema"></a>
<a id="schema_PagedBiomarkerModelSchema"></a>
<a id="tocSpagedbiomarkermodelschema"></a>
<a id="tocspagedbiomarkermodelschema"></a>

```json
{
  "items": [
    {
      "er_status": "Cannot be determined",
      "pr_status": "Cannot be determined",
      "her2_ihc_status": "Cannot be determined",
      "her2_ish_status": "Cannot be determined",
      "hpv_ihc_status": "Cannot be determined",
      "hpv_pcr_status": "Cannot be determined",
      "hpv_strain": [
        "HPV16"
      ],
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_specimen_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "submitter_treatment_id": "string",
      "submitter_follow_up_id": "string",
      "test_date": "string",
      "psa_level": 0,
      "ca125": 0,
      "cea": 0,
      "er_percent_positive": 0,
      "pr_percent_positive": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedBiomarkerModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[BiomarkerModelSchema](#schemabiomarkermodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ChemotherapyFilterSchema">ChemotherapyFilterSchema</h2>

<a id="schemachemotherapyfilterschema"></a>
<a id="schema_ChemotherapyFilterSchema"></a>
<a id="tocSchemotherapyfilterschema"></a>
<a id="tocschemotherapyfilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_reference_database": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "chemotherapy_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

ChemotherapyFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|chemotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ChemotherapyModelSchema">ChemotherapyModelSchema</h2>

<a id="schemachemotherapymodelschema"></a>
<a id="schema_ChemotherapyModelSchema"></a>
<a id="tocSchemotherapymodelschema"></a>
<a id="tocschemotherapymodelschema"></a>

```json
{
  "chemotherapy_drug_dose_units": "mg/m2",
  "drug_reference_database": "RxNorm",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

ChemotherapyModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|chemotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[DosageUnitsEnum](#schemadosageunitsenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[DrugReferenceDbEnum](#schemadrugreferencedbenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_DosageUnitsEnum">DosageUnitsEnum</h2>

<a id="schemadosageunitsenum"></a>
<a id="schema_DosageUnitsEnum"></a>
<a id="tocSdosageunitsenum"></a>
<a id="tocsdosageunitsenum"></a>

```json
"mg/m2"

```

DosageUnitsEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|DosageUnitsEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|DosageUnitsEnum|mg/m2|
|DosageUnitsEnum|IU/m2|
|DosageUnitsEnum|IU/kg|
|DosageUnitsEnum|ug/m2|
|DosageUnitsEnum|g/m2|
|DosageUnitsEnum|mg/kg|
|DosageUnitsEnum|cells/kg|

<h2 id="tocS_DrugReferenceDbEnum">DrugReferenceDbEnum</h2>

<a id="schemadrugreferencedbenum"></a>
<a id="schema_DrugReferenceDbEnum"></a>
<a id="tocSdrugreferencedbenum"></a>
<a id="tocsdrugreferencedbenum"></a>

```json
"RxNorm"

```

DrugReferenceDbEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|DrugReferenceDbEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|DrugReferenceDbEnum|RxNorm|
|DrugReferenceDbEnum|PubChem|
|DrugReferenceDbEnum|NCI Thesaurus|

<h2 id="tocS_PagedChemotherapyModelSchema">PagedChemotherapyModelSchema</h2>

<a id="schemapagedchemotherapymodelschema"></a>
<a id="schema_PagedChemotherapyModelSchema"></a>
<a id="tocSpagedchemotherapymodelschema"></a>
<a id="tocspagedchemotherapymodelschema"></a>

```json
{
  "items": [
    {
      "chemotherapy_drug_dose_units": "mg/m2",
      "drug_reference_database": "RxNorm",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedChemotherapyModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[ChemotherapyModelSchema](#schemachemotherapymodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ComorbidityFilterSchema">ComorbidityFilterSchema</h2>

<a id="schemacomorbidityfilterschema"></a>
<a id="schema_ComorbidityFilterSchema"></a>
<a id="tocScomorbidityfilterschema"></a>
<a id="tocscomorbidityfilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": 0,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string"
}

```

ComorbidityFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality_of_prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|age_at_comorbidity_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ComorbidityModelSchema">ComorbidityModelSchema</h2>

<a id="schemacomorbiditymodelschema"></a>
<a id="schema_ComorbidityModelSchema"></a>
<a id="tocScomorbiditymodelschema"></a>
<a id="tocscomorbiditymodelschema"></a>

```json
{
  "prior_malignancy": "Yes",
  "laterality_of_prior_malignancy": "Bilateral",
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "Yes",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "age_at_comorbidity_diagnosis": 0
}

```

ComorbidityModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[uBooleanEnum](#schemaubooleanenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|laterality_of_prior_malignancy|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[MalignancyLateralityEnum](#schemamalignancylateralityenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_type_code|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[uBooleanEnum](#schemaubooleanenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|comorbidity_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|age_at_comorbidity_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_MalignancyLateralityEnum">MalignancyLateralityEnum</h2>

<a id="schemamalignancylateralityenum"></a>
<a id="schema_MalignancyLateralityEnum"></a>
<a id="tocSmalignancylateralityenum"></a>
<a id="tocsmalignancylateralityenum"></a>

```json
"Bilateral"

```

MalignancyLateralityEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|MalignancyLateralityEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|MalignancyLateralityEnum|Bilateral|
|MalignancyLateralityEnum|Left|
|MalignancyLateralityEnum|Midline|
|MalignancyLateralityEnum|Not applicable|
|MalignancyLateralityEnum|Right|
|MalignancyLateralityEnum|Unilateral, Side not specified|
|MalignancyLateralityEnum|Unknown|

<h2 id="tocS_PagedComorbidityModelSchema">PagedComorbidityModelSchema</h2>

<a id="schemapagedcomorbiditymodelschema"></a>
<a id="schema_PagedComorbidityModelSchema"></a>
<a id="tocSpagedcomorbiditymodelschema"></a>
<a id="tocspagedcomorbiditymodelschema"></a>

```json
{
  "items": [
    {
      "prior_malignancy": "Yes",
      "laterality_of_prior_malignancy": "Bilateral",
      "comorbidity_type_code": "string",
      "comorbidity_treatment_status": "Yes",
      "comorbidity_treatment": "string",
      "program_id": "string",
      "submitter_donor_id": "string",
      "age_at_comorbidity_diagnosis": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedComorbidityModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[ComorbidityModelSchema](#schemacomorbiditymodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_uBooleanEnum">uBooleanEnum</h2>

<a id="schemaubooleanenum"></a>
<a id="schema_uBooleanEnum"></a>
<a id="tocSubooleanenum"></a>
<a id="tocsubooleanenum"></a>

```json
"Yes"

```

uBooleanEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|uBooleanEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|uBooleanEnum|Yes|
|uBooleanEnum|No|
|uBooleanEnum|Unknown|

<h2 id="tocS_ExposureFilterSchema">ExposureFilterSchema</h2>

<a id="schemaexposurefilterschema"></a>
<a id="schema_ExposureFilterSchema"></a>
<a id="tocSexposurefilterschema"></a>
<a id="tocsexposurefilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "tobacco_smoking_status": "string",
  "tobacco_type": [
    "string"
  ],
  "pack_years_smoked": 0
}

```

ExposureFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tobacco_smoking_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tobacco_type|[string]|false|none|none|
|pack_years_smoked|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ExposureModelSchema">ExposureModelSchema</h2>

<a id="schemaexposuremodelschema"></a>
<a id="schema_ExposureModelSchema"></a>
<a id="tocSexposuremodelschema"></a>
<a id="tocsexposuremodelschema"></a>

```json
{
  "tobacco_smoking_status": "Current reformed smoker for <= 15 years",
  "tobacco_type": [
    "Chewing Tobacco"
  ],
  "program_id": "string",
  "submitter_donor_id": "string",
  "pack_years_smoked": 0
}

```

ExposureModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tobacco_smoking_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SmokingStatusEnum](#schemasmokingstatusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tobacco_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[TobaccoTypeEnum](#schematobaccotypeenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|pack_years_smoked|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|number|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PagedExposureModelSchema">PagedExposureModelSchema</h2>

<a id="schemapagedexposuremodelschema"></a>
<a id="schema_PagedExposureModelSchema"></a>
<a id="tocSpagedexposuremodelschema"></a>
<a id="tocspagedexposuremodelschema"></a>

```json
{
  "items": [
    {
      "tobacco_smoking_status": "Current reformed smoker for <= 15 years",
      "tobacco_type": [
        "Chewing Tobacco"
      ],
      "program_id": "string",
      "submitter_donor_id": "string",
      "pack_years_smoked": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedExposureModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[ExposureModelSchema](#schemaexposuremodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_SmokingStatusEnum">SmokingStatusEnum</h2>

<a id="schemasmokingstatusenum"></a>
<a id="schema_SmokingStatusEnum"></a>
<a id="tocSsmokingstatusenum"></a>
<a id="tocssmokingstatusenum"></a>

```json
"Current reformed smoker for <= 15 years"

```

SmokingStatusEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SmokingStatusEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SmokingStatusEnum|Current reformed smoker for <= 15 years|
|SmokingStatusEnum|Current reformed smoker for > 15 years|
|SmokingStatusEnum|Current reformed smoker, duration not specified|
|SmokingStatusEnum|Current smoker|
|SmokingStatusEnum|Lifelong non-smoker (<100 cigarettes smoked in lifetime)|
|SmokingStatusEnum|Not applicable|
|SmokingStatusEnum|Smoking history not documented|

<h2 id="tocS_TobaccoTypeEnum">TobaccoTypeEnum</h2>

<a id="schematobaccotypeenum"></a>
<a id="schema_TobaccoTypeEnum"></a>
<a id="tocStobaccotypeenum"></a>
<a id="tocstobaccotypeenum"></a>

```json
"Chewing Tobacco"

```

TobaccoTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TobaccoTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TobaccoTypeEnum|Chewing Tobacco|
|TobaccoTypeEnum|Cigar|
|TobaccoTypeEnum|Cigarettes|
|TobaccoTypeEnum|Electronic cigarettes|
|TobaccoTypeEnum|Not applicable|
|TobaccoTypeEnum|Pipe|
|TobaccoTypeEnum|Roll-ups|
|TobaccoTypeEnum|Snuff|
|TobaccoTypeEnum|Unknown|
|TobaccoTypeEnum|Waterpipe|

<h2 id="tocS_FollowUpFilterSchema">FollowUpFilterSchema</h2>

<a id="schemafollowupfilterschema"></a>
<a id="schema_FollowUpFilterSchema"></a>
<a id="tocSfollowupfilterschema"></a>
<a id="tocsfollowupfilterschema"></a>

```json
{
  "submitter_follow_up_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "date_of_followup": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": [
    "string"
  ],
  "anatomic_site_progression_or_recurrence": [
    "string"
  ],
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string"
}

```

FollowUpFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|disease_status_at_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|relapse_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_relapse|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|method_of_progression_status|[string]|false|none|none|
|anatomic_site_progression_or_recurrence|[string]|false|none|none|
|recurrence_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_DiseaseStatusFollowupEnum">DiseaseStatusFollowupEnum</h2>

<a id="schemadiseasestatusfollowupenum"></a>
<a id="schema_DiseaseStatusFollowupEnum"></a>
<a id="tocSdiseasestatusfollowupenum"></a>
<a id="tocsdiseasestatusfollowupenum"></a>

```json
"Complete remission"

```

DiseaseStatusFollowupEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|DiseaseStatusFollowupEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|DiseaseStatusFollowupEnum|Complete remission|
|DiseaseStatusFollowupEnum|Distant progression|
|DiseaseStatusFollowupEnum|Loco-regional progression|
|DiseaseStatusFollowupEnum|No evidence of disease|
|DiseaseStatusFollowupEnum|Partial remission|
|DiseaseStatusFollowupEnum|Progression not otherwise specified|
|DiseaseStatusFollowupEnum|Relapse or recurrence|
|DiseaseStatusFollowupEnum|Stable|

<h2 id="tocS_FollowUpModelSchema">FollowUpModelSchema</h2>

<a id="schemafollowupmodelschema"></a>
<a id="schema_FollowUpModelSchema"></a>
<a id="tocSfollowupmodelschema"></a>
<a id="tocsfollowupmodelschema"></a>

```json
{
  "submitter_follow_up_id": "string",
  "disease_status_at_followup": "Complete remission",
  "relapse_type": "Distant recurrence/metastasis",
  "date_of_followup": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": [
    "Imaging (procedure)"
  ],
  "anatomic_site_progression_or_recurrence": [
    "string"
  ],
  "recurrence_tumour_staging_system": "AJCC 8th edition",
  "recurrence_t_category": "T0",
  "recurrence_n_category": "N0",
  "recurrence_m_category": "M0",
  "recurrence_stage_group": "Stage 0",
  "treatment_uuid": "6ec39d1c-44a6-43bb-80b2-ee9580e3c70b",
  "primary_diagnosis_uuid": "3459cde2-44be-4900-9ef0-b6de408c756d",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}

```

FollowUpModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|string|true|none|none|
|disease_status_at_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[DiseaseStatusFollowupEnum](#schemadiseasestatusfollowupenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|relapse_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[RelapseTypeEnum](#schemarelapsetypeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_followup|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|date_of_relapse|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|method_of_progression_status|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[ProgressionStatusMethodEnum](#schemaprogressionstatusmethodenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|anatomic_site_progression_or_recurrence|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[string]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourStagingSystemEnum](#schematumourstagingsystemenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TCategoryEnum](#schematcategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[NCategoryEnum](#schemancategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[MCategoryEnum](#schemamcategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|recurrence_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[StageGroupEnum](#schemastagegroupenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(uuid)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|primary_diagnosis_uuid|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string(uuid)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PagedFollowUpModelSchema">PagedFollowUpModelSchema</h2>

<a id="schemapagedfollowupmodelschema"></a>
<a id="schema_PagedFollowUpModelSchema"></a>
<a id="tocSpagedfollowupmodelschema"></a>
<a id="tocspagedfollowupmodelschema"></a>

```json
{
  "items": [
    {
      "submitter_follow_up_id": "string",
      "disease_status_at_followup": "Complete remission",
      "relapse_type": "Distant recurrence/metastasis",
      "date_of_followup": "string",
      "date_of_relapse": "string",
      "method_of_progression_status": [
        "Imaging (procedure)"
      ],
      "anatomic_site_progression_or_recurrence": [
        "string"
      ],
      "recurrence_tumour_staging_system": "AJCC 8th edition",
      "recurrence_t_category": "T0",
      "recurrence_n_category": "N0",
      "recurrence_m_category": "M0",
      "recurrence_stage_group": "Stage 0",
      "treatment_uuid": "6ec39d1c-44a6-43bb-80b2-ee9580e3c70b",
      "primary_diagnosis_uuid": "3459cde2-44be-4900-9ef0-b6de408c756d",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "submitter_treatment_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedFollowUpModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[FollowUpModelSchema](#schemafollowupmodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ProgressionStatusMethodEnum">ProgressionStatusMethodEnum</h2>

<a id="schemaprogressionstatusmethodenum"></a>
<a id="schema_ProgressionStatusMethodEnum"></a>
<a id="tocSprogressionstatusmethodenum"></a>
<a id="tocsprogressionstatusmethodenum"></a>

```json
"Imaging (procedure)"

```

ProgressionStatusMethodEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ProgressionStatusMethodEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|ProgressionStatusMethodEnum|Imaging (procedure)|
|ProgressionStatusMethodEnum|Histopathology test (procedure)|
|ProgressionStatusMethodEnum|Assessment of symptom control (procedure)|
|ProgressionStatusMethodEnum|Physical examination procedure (procedure)|
|ProgressionStatusMethodEnum|Tumor marker measurement (procedure)|
|ProgressionStatusMethodEnum|Laboratory data interpretation (procedure)|

<h2 id="tocS_RelapseTypeEnum">RelapseTypeEnum</h2>

<a id="schemarelapsetypeenum"></a>
<a id="schema_RelapseTypeEnum"></a>
<a id="tocSrelapsetypeenum"></a>
<a id="tocsrelapsetypeenum"></a>

```json
"Distant recurrence/metastasis"

```

RelapseTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|RelapseTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|RelapseTypeEnum|Distant recurrence/metastasis|
|RelapseTypeEnum|Local recurrence|
|RelapseTypeEnum|Local recurrence and distant metastasis|
|RelapseTypeEnum|Progression (liquid tumours)|
|RelapseTypeEnum|Biochemical progression|

<h2 id="tocS_HormoneTherapyFilterSchema">HormoneTherapyFilterSchema</h2>

<a id="schemahormonetherapyfilterschema"></a>
<a id="schema_HormoneTherapyFilterSchema"></a>
<a id="tocShormonetherapyfilterschema"></a>
<a id="tocshormonetherapyfilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_reference_database": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "hormone_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

HormoneTherapyFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hormone_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_HormoneTherapyModelSchema">HormoneTherapyModelSchema</h2>

<a id="schemahormonetherapymodelschema"></a>
<a id="schema_HormoneTherapyModelSchema"></a>
<a id="tocShormonetherapymodelschema"></a>
<a id="tocshormonetherapymodelschema"></a>

```json
{
  "hormone_drug_dose_units": "mg/m2",
  "drug_reference_database": "RxNorm",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

HormoneTherapyModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|hormone_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[DosageUnitsEnum](#schemadosageunitsenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[DrugReferenceDbEnum](#schemadrugreferencedbenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PagedHormoneTherapyModelSchema">PagedHormoneTherapyModelSchema</h2>

<a id="schemapagedhormonetherapymodelschema"></a>
<a id="schema_PagedHormoneTherapyModelSchema"></a>
<a id="tocSpagedhormonetherapymodelschema"></a>
<a id="tocspagedhormonetherapymodelschema"></a>

```json
{
  "items": [
    {
      "hormone_drug_dose_units": "mg/m2",
      "drug_reference_database": "RxNorm",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedHormoneTherapyModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[HormoneTherapyModelSchema](#schemahormonetherapymodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ImmunotherapyFilterSchema">ImmunotherapyFilterSchema</h2>

<a id="schemaimmunotherapyfilterschema"></a>
<a id="schema_ImmunotherapyFilterSchema"></a>
<a id="tocSimmunotherapyfilterschema"></a>
<a id="tocsimmunotherapyfilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_reference_database": "string",
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "immunotherapy_drug_dose_units": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

ImmunotherapyFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ImmunotherapyModelSchema">ImmunotherapyModelSchema</h2>

<a id="schemaimmunotherapymodelschema"></a>
<a id="schema_ImmunotherapyModelSchema"></a>
<a id="tocSimmunotherapymodelschema"></a>
<a id="tocsimmunotherapymodelschema"></a>

```json
{
  "immunotherapy_type": "Cell-based",
  "drug_reference_database": "RxNorm",
  "immunotherapy_drug_dose_units": "mg/m2",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "drug_name": "string",
  "drug_reference_identifier": "string",
  "prescribed_cumulative_drug_dose": 0,
  "actual_cumulative_drug_dose": 0
}

```

ImmunotherapyModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ImmunotherapyTypeEnum](#schemaimmunotherapytypeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_database|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[DrugReferenceDbEnum](#schemadrugreferencedbenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_drug_dose_units|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[DosageUnitsEnum](#schemadosageunitsenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|drug_name|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_reference_identifier|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prescribed_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|actual_cumulative_drug_dose|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_ImmunotherapyTypeEnum">ImmunotherapyTypeEnum</h2>

<a id="schemaimmunotherapytypeenum"></a>
<a id="schema_ImmunotherapyTypeEnum"></a>
<a id="tocSimmunotherapytypeenum"></a>
<a id="tocsimmunotherapytypeenum"></a>

```json
"Cell-based"

```

ImmunotherapyTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ImmunotherapyTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|ImmunotherapyTypeEnum|Cell-based|
|ImmunotherapyTypeEnum|Immune checkpoint inhibitors|
|ImmunotherapyTypeEnum|Monoclonal antibodies other than immune checkpoint inhibitors|
|ImmunotherapyTypeEnum|Other immunomodulatory substances|

<h2 id="tocS_PagedImmunotherapyModelSchema">PagedImmunotherapyModelSchema</h2>

<a id="schemapagedimmunotherapymodelschema"></a>
<a id="schema_PagedImmunotherapyModelSchema"></a>
<a id="tocSpagedimmunotherapymodelschema"></a>
<a id="tocspagedimmunotherapymodelschema"></a>

```json
{
  "items": [
    {
      "immunotherapy_type": "Cell-based",
      "drug_reference_database": "RxNorm",
      "immunotherapy_drug_dose_units": "mg/m2",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "drug_name": "string",
      "drug_reference_identifier": "string",
      "prescribed_cumulative_drug_dose": 0,
      "actual_cumulative_drug_dose": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedImmunotherapyModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[ImmunotherapyModelSchema](#schemaimmunotherapymodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_RadiationFilterSchema">RadiationFilterSchema</h2>

<a id="schemaradiationfilterschema"></a>
<a id="schema_RadiationFilterSchema"></a>
<a id="tocSradiationfilterschema"></a>
<a id="tocsradiationfilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": 0,
  "radiation_therapy_dosage": 0,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string"
}

```

RadiationFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_modality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_fractions|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_dosage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|anatomical_site_irradiated|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_boost|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_radiation_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PagedRadiationModelSchema">PagedRadiationModelSchema</h2>

<a id="schemapagedradiationmodelschema"></a>
<a id="schema_PagedRadiationModelSchema"></a>
<a id="tocSpagedradiationmodelschema"></a>
<a id="tocspagedradiationmodelschema"></a>

```json
{
  "items": [
    {
      "radiation_therapy_modality": "Megavoltage radiation therapy using photons (procedure)",
      "radiation_therapy_type": "External",
      "anatomical_site_irradiated": "Left Abdomen",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "radiation_therapy_fractions": 0,
      "radiation_therapy_dosage": 0,
      "radiation_boost": true,
      "reference_radiation_treatment_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedRadiationModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[RadiationModelSchema](#schemaradiationmodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_RadiationAnatomicalSiteEnum">RadiationAnatomicalSiteEnum</h2>

<a id="schemaradiationanatomicalsiteenum"></a>
<a id="schema_RadiationAnatomicalSiteEnum"></a>
<a id="tocSradiationanatomicalsiteenum"></a>
<a id="tocsradiationanatomicalsiteenum"></a>

```json
"Left Abdomen"

```

RadiationAnatomicalSiteEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|RadiationAnatomicalSiteEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|RadiationAnatomicalSiteEnum|Left Abdomen|
|RadiationAnatomicalSiteEnum|Whole Abdomen|
|RadiationAnatomicalSiteEnum|Right Abdomen|
|RadiationAnatomicalSiteEnum|Lower Abdomen|
|RadiationAnatomicalSiteEnum|Left Lower Abdomen|
|RadiationAnatomicalSiteEnum|Right Lower Abdomen|
|RadiationAnatomicalSiteEnum|Upper Abdomen|
|RadiationAnatomicalSiteEnum|Left Upper Abdomen|
|RadiationAnatomicalSiteEnum|Right Upper Abdomen|
|RadiationAnatomicalSiteEnum|Left Adrenal|
|RadiationAnatomicalSiteEnum|Right Adrenal|
|RadiationAnatomicalSiteEnum|Bilateral Ankle|
|RadiationAnatomicalSiteEnum|Left Ankle|
|RadiationAnatomicalSiteEnum|Right Ankle|
|RadiationAnatomicalSiteEnum|Bilateral Antrum (Bull's Eye)|
|RadiationAnatomicalSiteEnum|Left Antrum|
|RadiationAnatomicalSiteEnum|Right Antrum|
|RadiationAnatomicalSiteEnum|Anus|
|RadiationAnatomicalSiteEnum|Lower Left Arm|
|RadiationAnatomicalSiteEnum|Lower Right Arm|
|RadiationAnatomicalSiteEnum|Bilateral Arms|
|RadiationAnatomicalSiteEnum|Left Arm|
|RadiationAnatomicalSiteEnum|Right Arm|
|RadiationAnatomicalSiteEnum|Upper Left Arm|
|RadiationAnatomicalSiteEnum|Upper Right Arm|
|RadiationAnatomicalSiteEnum|Left Axilla|
|RadiationAnatomicalSiteEnum|Right Axilla|
|RadiationAnatomicalSiteEnum|Skin or Soft Tissue of Back|
|RadiationAnatomicalSiteEnum|Bile Duct|
|RadiationAnatomicalSiteEnum|Bladder|
|RadiationAnatomicalSiteEnum|Lower Body|
|RadiationAnatomicalSiteEnum|Middle Body|
|RadiationAnatomicalSiteEnum|Upper Body|
|RadiationAnatomicalSiteEnum|Whole Body|
|RadiationAnatomicalSiteEnum|Boost - Area Previously Treated|
|RadiationAnatomicalSiteEnum|Brain|
|RadiationAnatomicalSiteEnum|Left Breast Boost|
|RadiationAnatomicalSiteEnum|Right Breast Boost|
|RadiationAnatomicalSiteEnum|Bilateral Breast|
|RadiationAnatomicalSiteEnum|Left Breast|
|RadiationAnatomicalSiteEnum|Right Breast|
|RadiationAnatomicalSiteEnum|Bilateral Breasts with Nodes|
|RadiationAnatomicalSiteEnum|Left Breast with Nodes|
|RadiationAnatomicalSiteEnum|Right Breast with Nodes|
|RadiationAnatomicalSiteEnum|Bilateral Buttocks|
|RadiationAnatomicalSiteEnum|Left Buttock|
|RadiationAnatomicalSiteEnum|Right Buttock|
|RadiationAnatomicalSiteEnum|Inner Canthus|
|RadiationAnatomicalSiteEnum|Outer Canthus|
|RadiationAnatomicalSiteEnum|Cervix|
|RadiationAnatomicalSiteEnum|Bilateral Chest Lung & Area Involve|
|RadiationAnatomicalSiteEnum|Left Chest|
|RadiationAnatomicalSiteEnum|Right Chest|
|RadiationAnatomicalSiteEnum|Chin|
|RadiationAnatomicalSiteEnum|Left Cheek|
|RadiationAnatomicalSiteEnum|Right Cheek|
|RadiationAnatomicalSiteEnum|Bilateral Chest Wall (W/o Breast)|
|RadiationAnatomicalSiteEnum|Left Chest Wall|
|RadiationAnatomicalSiteEnum|Right Chest Wall|
|RadiationAnatomicalSiteEnum|Bilateral Clavicle|
|RadiationAnatomicalSiteEnum|Left Clavicle|
|RadiationAnatomicalSiteEnum|Right Clavicle|
|RadiationAnatomicalSiteEnum|Coccyx|
|RadiationAnatomicalSiteEnum|Colon|
|RadiationAnatomicalSiteEnum|Whole C.N.S. (Medulla Techinque)|
|RadiationAnatomicalSiteEnum|Csf Spine (Medull Tech 2 Diff Machi|
|RadiationAnatomicalSiteEnum|Left Chestwall Boost|
|RadiationAnatomicalSiteEnum|Right Chestwall Boost|
|RadiationAnatomicalSiteEnum|Bilateral Chestwall with Nodes|
|RadiationAnatomicalSiteEnum|Left Chestwall with Nodes|
|RadiationAnatomicalSiteEnum|Right Chestwall with Nodes|
|RadiationAnatomicalSiteEnum|Left Ear|
|RadiationAnatomicalSiteEnum|Right Ear|
|RadiationAnatomicalSiteEnum|Epigastrium|
|RadiationAnatomicalSiteEnum|Lower Esophagus|
|RadiationAnatomicalSiteEnum|Middle Esophagus|
|RadiationAnatomicalSiteEnum|Upper Esophagus|
|RadiationAnatomicalSiteEnum|Entire Esophagus|
|RadiationAnatomicalSiteEnum|Ethmoid Sinus|
|RadiationAnatomicalSiteEnum|Bilateral Eyes|
|RadiationAnatomicalSiteEnum|Left Eye|
|RadiationAnatomicalSiteEnum|Right Eye|
|RadiationAnatomicalSiteEnum|Bilateral Face|
|RadiationAnatomicalSiteEnum|Left Face|
|RadiationAnatomicalSiteEnum|Right Face|
|RadiationAnatomicalSiteEnum|Left Fallopian Tubes|
|RadiationAnatomicalSiteEnum|Right Fallopian Tubes|
|RadiationAnatomicalSiteEnum|Bilateral Femur|
|RadiationAnatomicalSiteEnum|Left Femur|
|RadiationAnatomicalSiteEnum|Right Femur|
|RadiationAnatomicalSiteEnum|Left Fibula|
|RadiationAnatomicalSiteEnum|Right Fibula|
|RadiationAnatomicalSiteEnum|Finger (Including Thumbs)|
|RadiationAnatomicalSiteEnum|Floor of Mouth (Boosts)|
|RadiationAnatomicalSiteEnum|Bilateral Feet|
|RadiationAnatomicalSiteEnum|Left Foot|
|RadiationAnatomicalSiteEnum|Right Foot|
|RadiationAnatomicalSiteEnum|Forehead|
|RadiationAnatomicalSiteEnum|Posterior Fossa|
|RadiationAnatomicalSiteEnum|Gall Bladder|
|RadiationAnatomicalSiteEnum|Gingiva|
|RadiationAnatomicalSiteEnum|Bilateral Hand|
|RadiationAnatomicalSiteEnum|Left Hand|
|RadiationAnatomicalSiteEnum|Right Hand|
|RadiationAnatomicalSiteEnum|Head|
|RadiationAnatomicalSiteEnum|Bilateral Heel|
|RadiationAnatomicalSiteEnum|Left Heel|
|RadiationAnatomicalSiteEnum|Right Heel|
|RadiationAnatomicalSiteEnum|Left Hemimantle|
|RadiationAnatomicalSiteEnum|Right Hemimantle|
|RadiationAnatomicalSiteEnum|Heart|
|RadiationAnatomicalSiteEnum|Bilateral Hip|
|RadiationAnatomicalSiteEnum|Left Hip|
|RadiationAnatomicalSiteEnum|Right Hip|
|RadiationAnatomicalSiteEnum|Left Humerus|
|RadiationAnatomicalSiteEnum|Right Humerus|
|RadiationAnatomicalSiteEnum|Hypopharynx|
|RadiationAnatomicalSiteEnum|Bilateral Internal Mammary Chain|
|RadiationAnatomicalSiteEnum|Bilateral Inguinal Nodes|
|RadiationAnatomicalSiteEnum|Left Inguinal Nodes|
|RadiationAnatomicalSiteEnum|Right Inguinal Nodes|
|RadiationAnatomicalSiteEnum|Inverted 'Y' (Dog-Leg,Hockey-Stick)|
|RadiationAnatomicalSiteEnum|Left Kidney|
|RadiationAnatomicalSiteEnum|Right Kidney|
|RadiationAnatomicalSiteEnum|Bilateral Knee|
|RadiationAnatomicalSiteEnum|Left Knee|
|RadiationAnatomicalSiteEnum|Right Knee|
|RadiationAnatomicalSiteEnum|Bilateral Lacrimal Gland|
|RadiationAnatomicalSiteEnum|Left Lacrimal Gland|
|RadiationAnatomicalSiteEnum|Right Lacrimal Gland|
|RadiationAnatomicalSiteEnum|Larygopharynx|
|RadiationAnatomicalSiteEnum|Larynx|
|RadiationAnatomicalSiteEnum|Bilateral Leg|
|RadiationAnatomicalSiteEnum|Left Leg|
|RadiationAnatomicalSiteEnum|Right Leg|
|RadiationAnatomicalSiteEnum|Lower Bilateral Leg|
|RadiationAnatomicalSiteEnum|Lower Left Leg|
|RadiationAnatomicalSiteEnum|Lower Right Leg|
|RadiationAnatomicalSiteEnum|Upper Bilateral Leg|
|RadiationAnatomicalSiteEnum|Upper Left Leg|
|RadiationAnatomicalSiteEnum|Upper Right Leg|
|RadiationAnatomicalSiteEnum|Both Eyelid(s)|
|RadiationAnatomicalSiteEnum|Left Eyelid|
|RadiationAnatomicalSiteEnum|Right Eyelid|
|RadiationAnatomicalSiteEnum|Both Lip(s)|
|RadiationAnatomicalSiteEnum|Lower Lip|
|RadiationAnatomicalSiteEnum|Upper Lip|
|RadiationAnatomicalSiteEnum|Liver|
|RadiationAnatomicalSiteEnum|Bilateral Lung|
|RadiationAnatomicalSiteEnum|Left Lung|
|RadiationAnatomicalSiteEnum|Right Lung|
|RadiationAnatomicalSiteEnum|Bilateral Mandible|
|RadiationAnatomicalSiteEnum|Left Mandible|
|RadiationAnatomicalSiteEnum|Right Mandible|
|RadiationAnatomicalSiteEnum|Mantle|
|RadiationAnatomicalSiteEnum|Bilateral Maxilla|
|RadiationAnatomicalSiteEnum|Left Maxilla|
|RadiationAnatomicalSiteEnum|Right Maxilla|
|RadiationAnatomicalSiteEnum|Mediastinum|
|RadiationAnatomicalSiteEnum|Multiple Skin|
|RadiationAnatomicalSiteEnum|Nasal Fossa|
|RadiationAnatomicalSiteEnum|Nasopharynx|
|RadiationAnatomicalSiteEnum|Bilateral Neck Includes Nodes|
|RadiationAnatomicalSiteEnum|Left Neck Includes Nodes|
|RadiationAnatomicalSiteEnum|Right Neck Includes Nodes|
|RadiationAnatomicalSiteEnum|Neck - Skin|
|RadiationAnatomicalSiteEnum|Nose|
|RadiationAnatomicalSiteEnum|Oral Cavity / Buccal Mucosa|
|RadiationAnatomicalSiteEnum|Bilateral Orbit|
|RadiationAnatomicalSiteEnum|Left Orbit|
|RadiationAnatomicalSiteEnum|Right Orbit|
|RadiationAnatomicalSiteEnum|Oropharynx|
|RadiationAnatomicalSiteEnum|Bilateral Ovary|
|RadiationAnatomicalSiteEnum|Left Ovary|
|RadiationAnatomicalSiteEnum|Right Ovary|
|RadiationAnatomicalSiteEnum|Hard Palate|
|RadiationAnatomicalSiteEnum|Soft Palate|
|RadiationAnatomicalSiteEnum|Palate Unspecified|
|RadiationAnatomicalSiteEnum|Pancreas|
|RadiationAnatomicalSiteEnum|Para-Aortic Nodes|
|RadiationAnatomicalSiteEnum|Left Parotid|
|RadiationAnatomicalSiteEnum|Right Parotid|
|RadiationAnatomicalSiteEnum|Bilateral Pelvis|
|RadiationAnatomicalSiteEnum|Left Pelvis|
|RadiationAnatomicalSiteEnum|Right Pelvis|
|RadiationAnatomicalSiteEnum|Penis|
|RadiationAnatomicalSiteEnum|Perineum|
|RadiationAnatomicalSiteEnum|Pituitary|
|RadiationAnatomicalSiteEnum|Left Pleura (As in Mesothelioma)|
|RadiationAnatomicalSiteEnum|Right Pleura|
|RadiationAnatomicalSiteEnum|Prostate|
|RadiationAnatomicalSiteEnum|Pubis|
|RadiationAnatomicalSiteEnum|Pyriform Fossa (Sinuses)|
|RadiationAnatomicalSiteEnum|Left Radius|
|RadiationAnatomicalSiteEnum|Right Radius|
|RadiationAnatomicalSiteEnum|Rectum (Includes Sigmoid)|
|RadiationAnatomicalSiteEnum|Left Ribs|
|RadiationAnatomicalSiteEnum|Right Ribs|
|RadiationAnatomicalSiteEnum|Sacrum|
|RadiationAnatomicalSiteEnum|Left Salivary Gland|
|RadiationAnatomicalSiteEnum|Right Salivary Gland|
|RadiationAnatomicalSiteEnum|Bilateral Scapula|
|RadiationAnatomicalSiteEnum|Left Scapula|
|RadiationAnatomicalSiteEnum|Right Scapula|
|RadiationAnatomicalSiteEnum|Bilateral Supraclavicular Nodes|
|RadiationAnatomicalSiteEnum|Left Supraclavicular Nodes|
|RadiationAnatomicalSiteEnum|Right Supraclavicular Nodes|
|RadiationAnatomicalSiteEnum|Bilateral Scalp|
|RadiationAnatomicalSiteEnum|Left Scalp|
|RadiationAnatomicalSiteEnum|Right Scalp|
|RadiationAnatomicalSiteEnum|Scrotum|
|RadiationAnatomicalSiteEnum|Bilateral Shoulder|
|RadiationAnatomicalSiteEnum|Left Shoulder|
|RadiationAnatomicalSiteEnum|Right Shoulder|
|RadiationAnatomicalSiteEnum|Whole Body - Skin|
|RadiationAnatomicalSiteEnum|Skull|
|RadiationAnatomicalSiteEnum|Cervical & Thoracic Spine|
|RadiationAnatomicalSiteEnum|Sphenoid Sinus|
|RadiationAnatomicalSiteEnum|Cervical Spine|
|RadiationAnatomicalSiteEnum|Lumbar Spine|
|RadiationAnatomicalSiteEnum|Thoracic Spine|
|RadiationAnatomicalSiteEnum|Whole Spine|
|RadiationAnatomicalSiteEnum|Spleen|
|RadiationAnatomicalSiteEnum|Lumbo-Sacral Spine|
|RadiationAnatomicalSiteEnum|Thoracic & Lumbar Spine|
|RadiationAnatomicalSiteEnum|Sternum|
|RadiationAnatomicalSiteEnum|Stomach|
|RadiationAnatomicalSiteEnum|Submandibular Glands|
|RadiationAnatomicalSiteEnum|Left Temple|
|RadiationAnatomicalSiteEnum|Right Temple|
|RadiationAnatomicalSiteEnum|Bilateral Testis|
|RadiationAnatomicalSiteEnum|Left Testis|
|RadiationAnatomicalSiteEnum|Right Testis|
|RadiationAnatomicalSiteEnum|Thyroid|
|RadiationAnatomicalSiteEnum|Left Tibia|
|RadiationAnatomicalSiteEnum|Right Tibia|
|RadiationAnatomicalSiteEnum|Left Toes|
|RadiationAnatomicalSiteEnum|Right Toes|
|RadiationAnatomicalSiteEnum|Tongue|
|RadiationAnatomicalSiteEnum|Tonsil|
|RadiationAnatomicalSiteEnum|Trachea|
|RadiationAnatomicalSiteEnum|Left Ulna|
|RadiationAnatomicalSiteEnum|Right Ulna|
|RadiationAnatomicalSiteEnum|Left Ureter|
|RadiationAnatomicalSiteEnum|Right Ureter|
|RadiationAnatomicalSiteEnum|Urethra|
|RadiationAnatomicalSiteEnum|Uterus|
|RadiationAnatomicalSiteEnum|Uvula|
|RadiationAnatomicalSiteEnum|Vagina|
|RadiationAnatomicalSiteEnum|Vulva|
|RadiationAnatomicalSiteEnum|Abdomen|
|RadiationAnatomicalSiteEnum|Body|
|RadiationAnatomicalSiteEnum|Chest|
|RadiationAnatomicalSiteEnum|Lower Limb|
|RadiationAnatomicalSiteEnum|Neck|
|RadiationAnatomicalSiteEnum|Other|
|RadiationAnatomicalSiteEnum|Pelvis|
|RadiationAnatomicalSiteEnum|Skin|
|RadiationAnatomicalSiteEnum|Spine|
|RadiationAnatomicalSiteEnum|Upper Limb|

<h2 id="tocS_RadiationModelSchema">RadiationModelSchema</h2>

<a id="schemaradiationmodelschema"></a>
<a id="schema_RadiationModelSchema"></a>
<a id="tocSradiationmodelschema"></a>
<a id="tocsradiationmodelschema"></a>

```json
{
  "radiation_therapy_modality": "Megavoltage radiation therapy using photons (procedure)",
  "radiation_therapy_type": "External",
  "anatomical_site_irradiated": "Left Abdomen",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "radiation_therapy_fractions": 0,
  "radiation_therapy_dosage": 0,
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string"
}

```

RadiationModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_modality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[RadiationTherapyModalityEnum](#schemaradiationtherapymodalityenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TherapyTypeEnum](#schematherapytypeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|anatomical_site_irradiated|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[RadiationAnatomicalSiteEnum](#schemaradiationanatomicalsiteenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|radiation_therapy_fractions|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_dosage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_boost|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|boolean|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_radiation_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_RadiationTherapyModalityEnum">RadiationTherapyModalityEnum</h2>

<a id="schemaradiationtherapymodalityenum"></a>
<a id="schema_RadiationTherapyModalityEnum"></a>
<a id="tocSradiationtherapymodalityenum"></a>
<a id="tocsradiationtherapymodalityenum"></a>

```json
"Megavoltage radiation therapy using photons (procedure)"

```

RadiationTherapyModalityEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|RadiationTherapyModalityEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|RadiationTherapyModalityEnum|Megavoltage radiation therapy using photons (procedure)|
|RadiationTherapyModalityEnum|Radiopharmaceutical|
|RadiationTherapyModalityEnum|Teleradiotherapy using electrons (procedure)|
|RadiationTherapyModalityEnum|Teleradiotherapy protons (procedure)|
|RadiationTherapyModalityEnum|Teleradiotherapy neutrons (procedure)|
|RadiationTherapyModalityEnum|Brachytherapy (procedure)|
|RadiationTherapyModalityEnum|Other|

<h2 id="tocS_TherapyTypeEnum">TherapyTypeEnum</h2>

<a id="schematherapytypeenum"></a>
<a id="schema_TherapyTypeEnum"></a>
<a id="tocStherapytypeenum"></a>
<a id="tocstherapytypeenum"></a>

```json
"External"

```

TherapyTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TherapyTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TherapyTypeEnum|External|
|TherapyTypeEnum|Internal|

<h2 id="tocS_SampleRegistrationFilterSchema">SampleRegistrationFilterSchema</h2>

<a id="schemasampleregistrationfilterschema"></a>
<a id="schema_SampleRegistrationFilterSchema"></a>
<a id="tocSsampleregistrationfilterschema"></a>
<a id="tocssampleregistrationfilterschema"></a>

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string"
}

```

SampleRegistrationFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_sample_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_tissue_source|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_normal_designation|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sample_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PagedSampleRegistrationModelSchema">PagedSampleRegistrationModelSchema</h2>

<a id="schemapagedsampleregistrationmodelschema"></a>
<a id="schema_PagedSampleRegistrationModelSchema"></a>
<a id="tocSpagedsampleregistrationmodelschema"></a>
<a id="tocspagedsampleregistrationmodelschema"></a>

```json
{
  "items": [
    {
      "submitter_sample_id": "string",
      "specimen_tissue_source": "Abdominal fluid",
      "tumour_normal_designation": "Normal",
      "specimen_type": "Cell line - derived from normal",
      "sample_type": "Amplified DNA",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_specimen_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedSampleRegistrationModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[SampleRegistrationModelSchema](#schemasampleregistrationmodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_SampleRegistrationModelSchema">SampleRegistrationModelSchema</h2>

<a id="schemasampleregistrationmodelschema"></a>
<a id="schema_SampleRegistrationModelSchema"></a>
<a id="tocSsampleregistrationmodelschema"></a>
<a id="tocssampleregistrationmodelschema"></a>

```json
{
  "submitter_sample_id": "string",
  "specimen_tissue_source": "Abdominal fluid",
  "tumour_normal_designation": "Normal",
  "specimen_type": "Cell line - derived from normal",
  "sample_type": "Amplified DNA",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}

```

SampleRegistrationModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_sample_id|string|true|none|none|
|specimen_tissue_source|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SpecimenTissueSourceEnum](#schemaspecimentissuesourceenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_normal_designation|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourDesginationEnum](#schematumourdesginationenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SpecimenTypeEnum](#schemaspecimentypeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|sample_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SampleTypeEnum](#schemasampletypeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string|true|none|none|

<h2 id="tocS_SampleTypeEnum">SampleTypeEnum</h2>

<a id="schemasampletypeenum"></a>
<a id="schema_SampleTypeEnum"></a>
<a id="tocSsampletypeenum"></a>
<a id="tocssampletypeenum"></a>

```json
"Amplified DNA"

```

SampleTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SampleTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SampleTypeEnum|Amplified DNA|
|SampleTypeEnum|ctDNA|
|SampleTypeEnum|Other DNA enrichments|
|SampleTypeEnum|Other RNA fractions|
|SampleTypeEnum|polyA+ RNA|
|SampleTypeEnum|Protein|
|SampleTypeEnum|rRNA-depleted RNA|
|SampleTypeEnum|Total DNA|
|SampleTypeEnum|Total RNA|

<h2 id="tocS_SpecimenTissueSourceEnum">SpecimenTissueSourceEnum</h2>

<a id="schemaspecimentissuesourceenum"></a>
<a id="schema_SpecimenTissueSourceEnum"></a>
<a id="tocSspecimentissuesourceenum"></a>
<a id="tocsspecimentissuesourceenum"></a>

```json
"Abdominal fluid"

```

SpecimenTissueSourceEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SpecimenTissueSourceEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SpecimenTissueSourceEnum|Abdominal fluid|
|SpecimenTissueSourceEnum|Amniotic fluid|
|SpecimenTissueSourceEnum|Arterial blood|
|SpecimenTissueSourceEnum|Bile|
|SpecimenTissueSourceEnum|Blood derived - bone marrow|
|SpecimenTissueSourceEnum|Blood derived - peripheral blood|
|SpecimenTissueSourceEnum|Bone marrow fluid|
|SpecimenTissueSourceEnum|Bone marrow derived mononuclear cells|
|SpecimenTissueSourceEnum|Buccal cell|
|SpecimenTissueSourceEnum|Buffy coat|
|SpecimenTissueSourceEnum|Cerebrospinal fluid|
|SpecimenTissueSourceEnum|Cervical mucus|
|SpecimenTissueSourceEnum|Convalescent plasma|
|SpecimenTissueSourceEnum|Cord blood|
|SpecimenTissueSourceEnum|Duodenal fluid|
|SpecimenTissueSourceEnum|Female genital fluid|
|SpecimenTissueSourceEnum|Fetal blood|
|SpecimenTissueSourceEnum|Hydrocele fluid|
|SpecimenTissueSourceEnum|Male genital fluid|
|SpecimenTissueSourceEnum|Pancreatic fluid|
|SpecimenTissueSourceEnum|Pericardial effusion|
|SpecimenTissueSourceEnum|Pleural fluid|
|SpecimenTissueSourceEnum|Renal cyst fluid|
|SpecimenTissueSourceEnum|Saliva|
|SpecimenTissueSourceEnum|Seminal fluid|
|SpecimenTissueSourceEnum|Serum|
|SpecimenTissueSourceEnum|Solid tissue|
|SpecimenTissueSourceEnum|Sputum|
|SpecimenTissueSourceEnum|Synovial fluid|
|SpecimenTissueSourceEnum|Urine|
|SpecimenTissueSourceEnum|Venous blood|
|SpecimenTissueSourceEnum|Vitreous fluid|
|SpecimenTissueSourceEnum|Whole blood|
|SpecimenTissueSourceEnum|Wound|

<h2 id="tocS_SpecimenTypeEnum">SpecimenTypeEnum</h2>

<a id="schemaspecimentypeenum"></a>
<a id="schema_SpecimenTypeEnum"></a>
<a id="tocSspecimentypeenum"></a>
<a id="tocsspecimentypeenum"></a>

```json
"Cell line - derived from normal"

```

SpecimenTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SpecimenTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SpecimenTypeEnum|Cell line - derived from normal|
|SpecimenTypeEnum|Cell line - derived from primary tumour|
|SpecimenTypeEnum|Cell line - derived from metastatic tumour|
|SpecimenTypeEnum|Cell line - derived from xenograft tumour|
|SpecimenTypeEnum|Metastatic tumour - additional metastatic|
|SpecimenTypeEnum|Metastatic tumour - metastasis local to lymph node|
|SpecimenTypeEnum|Metastatic tumour - metastasis to distant location|
|SpecimenTypeEnum|Metastatic tumour|
|SpecimenTypeEnum|Normal - tissue adjacent to primary tumour|
|SpecimenTypeEnum|Normal|
|SpecimenTypeEnum|Primary tumour - additional new primary|
|SpecimenTypeEnum|Primary tumour - adjacent to normal|
|SpecimenTypeEnum|Primary tumour|
|SpecimenTypeEnum|Recurrent tumour|
|SpecimenTypeEnum|Tumour - unknown if derived from primary or metastatic tumour|
|SpecimenTypeEnum|Xenograft - derived from primary tumour|
|SpecimenTypeEnum|Xenograft - derived from metastatic tumour|
|SpecimenTypeEnum|Xenograft - derived from tumour cell line|

<h2 id="tocS_TumourDesginationEnum">TumourDesginationEnum</h2>

<a id="schematumourdesginationenum"></a>
<a id="schema_TumourDesginationEnum"></a>
<a id="tocStumourdesginationenum"></a>
<a id="tocstumourdesginationenum"></a>

```json
"Normal"

```

TumourDesginationEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TumourDesginationEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TumourDesginationEnum|Normal|
|TumourDesginationEnum|Tumour|

<h2 id="tocS_SpecimenFilterSchema">SpecimenFilterSchema</h2>

<a id="schemaspecimenfilterschema"></a>
<a id="schema_SpecimenFilterSchema"></a>
<a id="tocSspecimenfilterschema"></a>
<a id="tocsspecimenfilterschema"></a>

```json
{
  "submitter_specimen_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "specimen_processing": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "specimen_laterality": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string"
}

```

SpecimenFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_collection_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_storage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_processing|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_histological_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_anatomic_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_tumour_presence|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grading_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grade|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_range|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_measurement_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_CellsMeasureMethodEnum">CellsMeasureMethodEnum</h2>

<a id="schemacellsmeasuremethodenum"></a>
<a id="schema_CellsMeasureMethodEnum"></a>
<a id="tocScellsmeasuremethodenum"></a>
<a id="tocscellsmeasuremethodenum"></a>

```json
"Genomics"

```

CellsMeasureMethodEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|CellsMeasureMethodEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|CellsMeasureMethodEnum|Genomics|
|CellsMeasureMethodEnum|Image analysis|
|CellsMeasureMethodEnum|Pathology estimate by percent nuclei|
|CellsMeasureMethodEnum|Unknown|

<h2 id="tocS_ConfirmedDiagnosisTumourEnum">ConfirmedDiagnosisTumourEnum</h2>

<a id="schemaconfirmeddiagnosistumourenum"></a>
<a id="schema_ConfirmedDiagnosisTumourEnum"></a>
<a id="tocSconfirmeddiagnosistumourenum"></a>
<a id="tocsconfirmeddiagnosistumourenum"></a>

```json
"Yes"

```

ConfirmedDiagnosisTumourEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|ConfirmedDiagnosisTumourEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|ConfirmedDiagnosisTumourEnum|Yes|
|ConfirmedDiagnosisTumourEnum|No|
|ConfirmedDiagnosisTumourEnum|Not done|
|ConfirmedDiagnosisTumourEnum|Unknown|

<h2 id="tocS_PagedSpecimenModelSchema">PagedSpecimenModelSchema</h2>

<a id="schemapagedspecimenmodelschema"></a>
<a id="schema_PagedSpecimenModelSchema"></a>
<a id="tocSpagedspecimenmodelschema"></a>
<a id="tocspagedspecimenmodelschema"></a>

```json
{
  "items": [
    {
      "submitter_specimen_id": "string",
      "pathological_tumour_staging_system": "AJCC 8th edition",
      "pathological_t_category": "T0",
      "pathological_n_category": "N0",
      "pathological_m_category": "M0",
      "pathological_stage_group": "Stage 0",
      "specimen_collection_date": "string",
      "specimen_storage": "Cut slide",
      "tumour_histological_type": "string",
      "specimen_anatomic_location": "string",
      "reference_pathology_confirmed_diagnosis": "Yes",
      "reference_pathology_confirmed_tumour_presence": "Yes",
      "tumour_grading_system": "FNCLCC grading system",
      "tumour_grade": "Low grade",
      "percent_tumour_cells_range": "0-19%",
      "percent_tumour_cells_measurement_method": "Genomics",
      "specimen_processing": "Cryopreservation in liquid nitrogen (dead tissue)",
      "specimen_laterality": "Left",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_primary_diagnosis_id": "string"
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedSpecimenModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[SpecimenModelSchema](#schemaspecimenmodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PercentCellsRangeEnum">PercentCellsRangeEnum</h2>

<a id="schemapercentcellsrangeenum"></a>
<a id="schema_PercentCellsRangeEnum"></a>
<a id="tocSpercentcellsrangeenum"></a>
<a id="tocspercentcellsrangeenum"></a>

```json
"0-19%"

```

PercentCellsRangeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|PercentCellsRangeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|PercentCellsRangeEnum|0-19%|
|PercentCellsRangeEnum|20-50%|
|PercentCellsRangeEnum|51-100%|

<h2 id="tocS_SpecimenLateralityEnum">SpecimenLateralityEnum</h2>

<a id="schemaspecimenlateralityenum"></a>
<a id="schema_SpecimenLateralityEnum"></a>
<a id="tocSspecimenlateralityenum"></a>
<a id="tocsspecimenlateralityenum"></a>

```json
"Left"

```

SpecimenLateralityEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SpecimenLateralityEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SpecimenLateralityEnum|Left|
|SpecimenLateralityEnum|Not applicable|
|SpecimenLateralityEnum|Right|
|SpecimenLateralityEnum|Unknown|

<h2 id="tocS_SpecimenModelSchema">SpecimenModelSchema</h2>

<a id="schemaspecimenmodelschema"></a>
<a id="schema_SpecimenModelSchema"></a>
<a id="tocSspecimenmodelschema"></a>
<a id="tocsspecimenmodelschema"></a>

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "AJCC 8th edition",
  "pathological_t_category": "T0",
  "pathological_n_category": "N0",
  "pathological_m_category": "M0",
  "pathological_stage_group": "Stage 0",
  "specimen_collection_date": "string",
  "specimen_storage": "Cut slide",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "Yes",
  "reference_pathology_confirmed_tumour_presence": "Yes",
  "tumour_grading_system": "FNCLCC grading system",
  "tumour_grade": "Low grade",
  "percent_tumour_cells_range": "0-19%",
  "percent_tumour_cells_measurement_method": "Genomics",
  "specimen_processing": "Cryopreservation in liquid nitrogen (dead tissue)",
  "specimen_laterality": "Left",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}

```

SpecimenModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|string|true|none|none|
|pathological_tumour_staging_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourStagingSystemEnum](#schematumourstagingsystemenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_t_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TCategoryEnum](#schematcategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_n_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[NCategoryEnum](#schemancategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_m_category|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[MCategoryEnum](#schemamcategoryenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|pathological_stage_group|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[StageGroupEnum](#schemastagegroupenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_collection_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_storage|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[StorageEnum](#schemastorageenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_histological_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_anatomic_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_diagnosis|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ConfirmedDiagnosisTumourEnum](#schemaconfirmeddiagnosistumourenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|reference_pathology_confirmed_tumour_presence|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[ConfirmedDiagnosisTumourEnum](#schemaconfirmeddiagnosistumourenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grading_system|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourGradingSystemEnum](#schematumourgradingsystemenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_grade|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourGradeEnum](#schematumourgradeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_range|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[PercentCellsRangeEnum](#schemapercentcellsrangeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|percent_tumour_cells_measurement_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[CellsMeasureMethodEnum](#schemacellsmeasuremethodenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_processing|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SpecimenProcessingEnum](#schemaspecimenprocessingenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|specimen_laterality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SpecimenLateralityEnum](#schemaspecimenlateralityenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|

<h2 id="tocS_SpecimenProcessingEnum">SpecimenProcessingEnum</h2>

<a id="schemaspecimenprocessingenum"></a>
<a id="schema_SpecimenProcessingEnum"></a>
<a id="tocSspecimenprocessingenum"></a>
<a id="tocsspecimenprocessingenum"></a>

```json
"Cryopreservation in liquid nitrogen (dead tissue)"

```

SpecimenProcessingEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SpecimenProcessingEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SpecimenProcessingEnum|Cryopreservation in liquid nitrogen (dead tissue)|
|SpecimenProcessingEnum|Cryopreservation in dry ice (dead tissue)|
|SpecimenProcessingEnum|Cryopreservation of live cells in liquid nitrogen|
|SpecimenProcessingEnum|Cryopreservation - other|
|SpecimenProcessingEnum|Formalin fixed & paraffin embedded|
|SpecimenProcessingEnum|Formalin fixed - buffered|
|SpecimenProcessingEnum|Formalin fixed - unbuffered|
|SpecimenProcessingEnum|Fresh|
|SpecimenProcessingEnum|Other|
|SpecimenProcessingEnum|Unknown|

<h2 id="tocS_StorageEnum">StorageEnum</h2>

<a id="schemastorageenum"></a>
<a id="schema_StorageEnum"></a>
<a id="tocSstorageenum"></a>
<a id="tocsstorageenum"></a>

```json
"Cut slide"

```

StorageEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|StorageEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|StorageEnum|Cut slide|
|StorageEnum|Frozen in -70 freezer|
|StorageEnum|Frozen in liquid nitrogen|
|StorageEnum|Frozen in vapour phase|
|StorageEnum|Not Applicable|
|StorageEnum|Other|
|StorageEnum|Paraffin block|
|StorageEnum|RNA later frozen|
|StorageEnum|Unknown|

<h2 id="tocS_TumourGradeEnum">TumourGradeEnum</h2>

<a id="schematumourgradeenum"></a>
<a id="schema_TumourGradeEnum"></a>
<a id="tocStumourgradeenum"></a>
<a id="tocstumourgradeenum"></a>

```json
"Low grade"

```

TumourGradeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TumourGradeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TumourGradeEnum|Low grade|
|TumourGradeEnum|High grade|
|TumourGradeEnum|GX|
|TumourGradeEnum|G1|
|TumourGradeEnum|G2|
|TumourGradeEnum|G3|
|TumourGradeEnum|G4|
|TumourGradeEnum|Low|
|TumourGradeEnum|High|
|TumourGradeEnum|Grade 1|
|TumourGradeEnum|Grade 2|
|TumourGradeEnum|Grade 3|
|TumourGradeEnum|Grade 4|
|TumourGradeEnum|Grade I|
|TumourGradeEnum|Grade II|
|TumourGradeEnum|Grade III|
|TumourGradeEnum|Grade IV|
|TumourGradeEnum|Grade Group 1|
|TumourGradeEnum|Grade Group 2|
|TumourGradeEnum|Grade Group 3|
|TumourGradeEnum|Grade Group 4|
|TumourGradeEnum|Grade Group 5|

<h2 id="tocS_TumourGradingSystemEnum">TumourGradingSystemEnum</h2>

<a id="schematumourgradingsystemenum"></a>
<a id="schema_TumourGradingSystemEnum"></a>
<a id="tocStumourgradingsystemenum"></a>
<a id="tocstumourgradingsystemenum"></a>

```json
"FNCLCC grading system"

```

TumourGradingSystemEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TumourGradingSystemEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TumourGradingSystemEnum|FNCLCC grading system|
|TumourGradingSystemEnum|Four-tier grading system|
|TumourGradingSystemEnum|Gleason grade group system|
|TumourGradingSystemEnum|Grading system for GISTs|
|TumourGradingSystemEnum|Grading system for GNETs|
|TumourGradingSystemEnum|IASLC grading system|
|TumourGradingSystemEnum|ISUP grading system|
|TumourGradingSystemEnum|Nottingham grading system|
|TumourGradingSystemEnum|Nuclear grading system for DCIS|
|TumourGradingSystemEnum|Scarff-Bloom-Richardson grading system|
|TumourGradingSystemEnum|Three-tier grading system|
|TumourGradingSystemEnum|Two-tier grading system|
|TumourGradingSystemEnum|WHO grading system for CNS tumours|

<h2 id="tocS_SurgeryFilterSchema">SurgeryFilterSchema</h2>

<a id="schemasurgeryfilterschema"></a>
<a id="schema_SurgeryFilterSchema"></a>
<a id="tocSsurgeryfilterschema"></a>
<a id="tocssurgeryfilterschema"></a>

```json
{
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "submitter_specimen_id": "string",
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": 0,
  "tumour_width": 0,
  "greatest_dimension_tumour": 0,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": [
    "string"
  ],
  "margin_types_not_involved": [
    "string"
  ],
  "margin_types_not_assessed": [
    "string"
  ],
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string"
}

```

SurgeryFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_site|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_length|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_width|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|greatest_dimension_tumour|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_focality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|residual_tumour_classification|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_involved|[string]|false|none|none|
|margin_types_not_involved|[string]|false|none|none|
|margin_types_not_assessed|[string]|false|none|none|
|lymphovascular_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|perineural_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_LymphovascularInvasionEnum">LymphovascularInvasionEnum</h2>

<a id="schemalymphovascularinvasionenum"></a>
<a id="schema_LymphovascularInvasionEnum"></a>
<a id="tocSlymphovascularinvasionenum"></a>
<a id="tocslymphovascularinvasionenum"></a>

```json
"Absent"

```

LymphovascularInvasionEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|LymphovascularInvasionEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|LymphovascularInvasionEnum|Absent|
|LymphovascularInvasionEnum|Both lymphatic and small vessel and venous (large vessel) invasion|
|LymphovascularInvasionEnum|Lymphatic and small vessel invasion only|
|LymphovascularInvasionEnum|Not applicable|
|LymphovascularInvasionEnum|Present|
|LymphovascularInvasionEnum|Venous (large vessel) invasion only|
|LymphovascularInvasionEnum|Unknown|

<h2 id="tocS_MarginTypesEnum">MarginTypesEnum</h2>

<a id="schemamargintypesenum"></a>
<a id="schema_MarginTypesEnum"></a>
<a id="tocSmargintypesenum"></a>
<a id="tocsmargintypesenum"></a>

```json
"Circumferential resection margin"

```

MarginTypesEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|MarginTypesEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|MarginTypesEnum|Circumferential resection margin|
|MarginTypesEnum|Common bile duct margin|
|MarginTypesEnum|Distal margin|
|MarginTypesEnum|Not applicable|
|MarginTypesEnum|Proximal margin|
|MarginTypesEnum|Unknown|

<h2 id="tocS_PagedSurgeryModelSchema">PagedSurgeryModelSchema</h2>

<a id="schemapagedsurgerymodelschema"></a>
<a id="schema_PagedSurgeryModelSchema"></a>
<a id="tocSpagedsurgerymodelschema"></a>
<a id="tocspagedsurgerymodelschema"></a>

```json
{
  "items": [
    {
      "surgery_type": "Ablation",
      "surgery_site": "string",
      "surgery_location": "Local recurrence",
      "tumour_focality": "Cannot be assessed",
      "residual_tumour_classification": "Not applicable",
      "margin_types_involved": [
        "Circumferential resection margin"
      ],
      "margin_types_not_involved": [
        "Circumferential resection margin"
      ],
      "margin_types_not_assessed": [
        "Circumferential resection margin"
      ],
      "lymphovascular_invasion": "Absent",
      "perineural_invasion": "Absent",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_treatment_id": "string",
      "submitter_specimen_id": "string",
      "tumour_length": 0,
      "tumour_width": 0,
      "greatest_dimension_tumour": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedSurgeryModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[SurgeryModelSchema](#schemasurgerymodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PerineuralInvasionEnum">PerineuralInvasionEnum</h2>

<a id="schemaperineuralinvasionenum"></a>
<a id="schema_PerineuralInvasionEnum"></a>
<a id="tocSperineuralinvasionenum"></a>
<a id="tocsperineuralinvasionenum"></a>

```json
"Absent"

```

PerineuralInvasionEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|PerineuralInvasionEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|PerineuralInvasionEnum|Absent|
|PerineuralInvasionEnum|Cannot be assessed|
|PerineuralInvasionEnum|Not applicable|
|PerineuralInvasionEnum|Present|
|PerineuralInvasionEnum|Unknown|

<h2 id="tocS_SurgeryLocationEnum">SurgeryLocationEnum</h2>

<a id="schemasurgerylocationenum"></a>
<a id="schema_SurgeryLocationEnum"></a>
<a id="tocSsurgerylocationenum"></a>
<a id="tocssurgerylocationenum"></a>

```json
"Local recurrence"

```

SurgeryLocationEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SurgeryLocationEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SurgeryLocationEnum|Local recurrence|
|SurgeryLocationEnum|Metastatic|
|SurgeryLocationEnum|Primary|

<h2 id="tocS_SurgeryModelSchema">SurgeryModelSchema</h2>

<a id="schemasurgerymodelschema"></a>
<a id="schema_SurgeryModelSchema"></a>
<a id="tocSsurgerymodelschema"></a>
<a id="tocssurgerymodelschema"></a>

```json
{
  "surgery_type": "Ablation",
  "surgery_site": "string",
  "surgery_location": "Local recurrence",
  "tumour_focality": "Cannot be assessed",
  "residual_tumour_classification": "Not applicable",
  "margin_types_involved": [
    "Circumferential resection margin"
  ],
  "margin_types_not_involved": [
    "Circumferential resection margin"
  ],
  "margin_types_not_assessed": [
    "Circumferential resection margin"
  ],
  "lymphovascular_invasion": "Absent",
  "perineural_invasion": "Absent",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string",
  "submitter_specimen_id": "string",
  "tumour_length": 0,
  "tumour_width": 0,
  "greatest_dimension_tumour": 0
}

```

SurgeryModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SurgeryTypeEnum](#schemasurgerytypeenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_site|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_location|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[SurgeryLocationEnum](#schemasurgerylocationenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_focality|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourFocalityEnum](#schematumourfocalityenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|residual_tumour_classification|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TumourClassificationEnum](#schematumourclassificationenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_involved|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[MarginTypesEnum](#schemamargintypesenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_not_involved|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[MarginTypesEnum](#schemamargintypesenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|margin_types_not_assessed|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[MarginTypesEnum](#schemamargintypesenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|lymphovascular_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[LymphovascularInvasionEnum](#schemalymphovascularinvasionenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|perineural_invasion|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[PerineuralInvasionEnum](#schemaperineuralinvasionenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|
|submitter_specimen_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_length|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|tumour_width|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|greatest_dimension_tumour|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_SurgeryTypeEnum">SurgeryTypeEnum</h2>

<a id="schemasurgerytypeenum"></a>
<a id="schema_SurgeryTypeEnum"></a>
<a id="tocSsurgerytypeenum"></a>
<a id="tocssurgerytypeenum"></a>

```json
"Ablation"

```

SurgeryTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|SurgeryTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|SurgeryTypeEnum|Ablation|
|SurgeryTypeEnum|Axillary Clearance|
|SurgeryTypeEnum|Axillary lymph nodes sampling|
|SurgeryTypeEnum|Bilateral complete salpingo-oophorectomy|
|SurgeryTypeEnum|Biopsy|
|SurgeryTypeEnum|Bypass Gastrojejunostomy|
|SurgeryTypeEnum|Cholecystectomy|
|SurgeryTypeEnum|Cholecystojejunostomy|
|SurgeryTypeEnum|Completion Gastrectomy|
|SurgeryTypeEnum|Debridement of pancreatic and peripancreatic necrosis|
|SurgeryTypeEnum|Distal subtotal pancreatectomy|
|SurgeryTypeEnum|Drainage of abscess|
|SurgeryTypeEnum|Duodenal preserving pancreatic head resection|
|SurgeryTypeEnum|Endoscopic biopsy|
|SurgeryTypeEnum|Endoscopic brushings of gastrointestinal tract|
|SurgeryTypeEnum|Enucleation|
|SurgeryTypeEnum|Esophageal bypass surgery/jejunostomy only|
|SurgeryTypeEnum|Exploratory laparotomy|
|SurgeryTypeEnum|Fine needle aspiration biopsy|
|SurgeryTypeEnum|Gastric Antrectomy|
|SurgeryTypeEnum|Glossectomy|
|SurgeryTypeEnum|Hepatojejunostomy|
|SurgeryTypeEnum|Hysterectomy|
|SurgeryTypeEnum|Incision of thorax|
|SurgeryTypeEnum|Ivor Lewis subtotal esophagectomy|
|SurgeryTypeEnum|Laparotomy|
|SurgeryTypeEnum|Left thoracoabdominal incision|
|SurgeryTypeEnum|Lobectomy|
|SurgeryTypeEnum|Mammoplasty|
|SurgeryTypeEnum|Mastectomy|
|SurgeryTypeEnum|McKeown esophagectomy|
|SurgeryTypeEnum|Merendino procedure|
|SurgeryTypeEnum|Minimally invasive esophagectomy|
|SurgeryTypeEnum|Omentectomy|
|SurgeryTypeEnum|Ovariectomy|
|SurgeryTypeEnum|Pancreaticoduodenectomy (Whipple procedure)|
|SurgeryTypeEnum|Pancreaticojejunostomy, side-to-side anastomosis|
|SurgeryTypeEnum|Partial pancreatectomy|
|SurgeryTypeEnum|Pneumonectomy|
|SurgeryTypeEnum|Prostatectomy|
|SurgeryTypeEnum|Proximal subtotal gastrectomy|
|SurgeryTypeEnum|Pylorus-sparing Whipple operation|
|SurgeryTypeEnum|Radical pancreaticoduodenectomy|
|SurgeryTypeEnum|Radical prostatectomy|
|SurgeryTypeEnum|Reexcision|
|SurgeryTypeEnum|Segmentectomy|
|SurgeryTypeEnum|Sentinal Lymph Node Biopsy|
|SurgeryTypeEnum|Spleen preserving distal pancreatectomy|
|SurgeryTypeEnum|Splenectomy|
|SurgeryTypeEnum|Total gastrectomy|
|SurgeryTypeEnum|Total gastrectomy with extended lymphadenectomy|
|SurgeryTypeEnum|Total pancreatectomy|
|SurgeryTypeEnum|Transhiatal esophagectomy|
|SurgeryTypeEnum|Triple bypass of pancreas|
|SurgeryTypeEnum|Tumor Debulking|
|SurgeryTypeEnum|Wedge/localised gastric resection|
|SurgeryTypeEnum|Wide Local Excision|

<h2 id="tocS_TumourClassificationEnum">TumourClassificationEnum</h2>

<a id="schematumourclassificationenum"></a>
<a id="schema_TumourClassificationEnum"></a>
<a id="tocStumourclassificationenum"></a>
<a id="tocstumourclassificationenum"></a>

```json
"Not applicable"

```

TumourClassificationEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TumourClassificationEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TumourClassificationEnum|Not applicable|
|TumourClassificationEnum|RX|
|TumourClassificationEnum|R0|
|TumourClassificationEnum|R1|
|TumourClassificationEnum|R2|
|TumourClassificationEnum|Unknown|

<h2 id="tocS_TumourFocalityEnum">TumourFocalityEnum</h2>

<a id="schematumourfocalityenum"></a>
<a id="schema_TumourFocalityEnum"></a>
<a id="tocStumourfocalityenum"></a>
<a id="tocstumourfocalityenum"></a>

```json
"Cannot be assessed"

```

TumourFocalityEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TumourFocalityEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TumourFocalityEnum|Cannot be assessed|
|TumourFocalityEnum|Multifocal|
|TumourFocalityEnum|Not applicable|
|TumourFocalityEnum|Unifocal|
|TumourFocalityEnum|Unknown|

<h2 id="tocS_TreatmentFilterSchema">TreatmentFilterSchema</h2>

<a id="schematreatmentfilterschema"></a>
<a id="schema_TreatmentFilterSchema"></a>
<a id="tocStreatmentfilterschema"></a>
<a id="tocstreatmentfilterschema"></a>

```json
{
  "submitter_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "treatment_type": [
    "string"
  ],
  "is_primary_treatment": "string",
  "line_of_treatment": 0,
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": 0,
  "number_of_cycles": 0,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "status_of_treatment": "string"
}

```

TreatmentFilterSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_type|[string]|false|none|none|
|is_primary_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|line_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_start_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_end_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_setting|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_intent|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|days_per_cycle|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_of_cycles|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment_criteria_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_PagedTreatmentModelSchema">PagedTreatmentModelSchema</h2>

<a id="schemapagedtreatmentmodelschema"></a>
<a id="schema_PagedTreatmentModelSchema"></a>
<a id="tocSpagedtreatmentmodelschema"></a>
<a id="tocspagedtreatmentmodelschema"></a>

```json
{
  "items": [
    {
      "submitter_treatment_id": "string",
      "treatment_type": [
        "Bone marrow transplant"
      ],
      "is_primary_treatment": "Yes",
      "treatment_start_date": "string",
      "treatment_end_date": "string",
      "treatment_setting": "Adjuvant",
      "treatment_intent": "Curative",
      "response_to_treatment_criteria_method": "RECIST 1.1",
      "response_to_treatment": "Complete response",
      "status_of_treatment": "Treatment completed as prescribed",
      "program_id": "string",
      "submitter_donor_id": "string",
      "submitter_primary_diagnosis_id": "string",
      "line_of_treatment": 0,
      "days_per_cycle": 0,
      "number_of_cycles": 0
    }
  ],
  "count": 0,
  "next_page": 0,
  "previous_page": 0
}

```

PagedTreatmentModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|items|[[TreatmentModelSchema](#schematreatmentmodelschema)]|true|none|none|
|count|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|next_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|previous_page|any|true|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_TreatmentIntentEnum">TreatmentIntentEnum</h2>

<a id="schematreatmentintentenum"></a>
<a id="schema_TreatmentIntentEnum"></a>
<a id="tocStreatmentintentenum"></a>
<a id="tocstreatmentintentenum"></a>

```json
"Curative"

```

TreatmentIntentEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TreatmentIntentEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TreatmentIntentEnum|Curative|
|TreatmentIntentEnum|Palliative|
|TreatmentIntentEnum|Supportive|
|TreatmentIntentEnum|Diagnostic|
|TreatmentIntentEnum|Preventive|
|TreatmentIntentEnum|Guidance|
|TreatmentIntentEnum|Screening|
|TreatmentIntentEnum|Forensic|

<h2 id="tocS_TreatmentModelSchema">TreatmentModelSchema</h2>

<a id="schematreatmentmodelschema"></a>
<a id="schema_TreatmentModelSchema"></a>
<a id="tocStreatmentmodelschema"></a>
<a id="tocstreatmentmodelschema"></a>

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": [
    "Bone marrow transplant"
  ],
  "is_primary_treatment": "Yes",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "Adjuvant",
  "treatment_intent": "Curative",
  "response_to_treatment_criteria_method": "RECIST 1.1",
  "response_to_treatment": "Complete response",
  "status_of_treatment": "Treatment completed as prescribed",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "line_of_treatment": 0,
  "days_per_cycle": 0,
  "number_of_cycles": 0
}

```

TreatmentModelSchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|string|true|none|none|
|treatment_type|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[[TreatmentTypeEnum](#schematreatmenttypeenum)]|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|is_primary_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[uBooleanEnum](#schemaubooleanenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_start_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_end_date|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|string|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_setting|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TreatmentSettingEnum](#schematreatmentsettingenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_intent|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TreatmentIntentEnum](#schematreatmentintentenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment_criteria_method|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TreatmentResponseMethodEnum](#schematreatmentresponsemethodenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|response_to_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TreatmentResponseEnum](#schematreatmentresponseenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|status_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|[TreatmentStatusEnum](#schematreatmentstatusenum)|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|
|line_of_treatment|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|days_per_cycle|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

continued

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|number_of_cycles|any|false|none|none|

anyOf

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|integer|false|none|none|

or

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|» *anonymous*|null|false|none|none|

<h2 id="tocS_TreatmentResponseEnum">TreatmentResponseEnum</h2>

<a id="schematreatmentresponseenum"></a>
<a id="schema_TreatmentResponseEnum"></a>
<a id="tocStreatmentresponseenum"></a>
<a id="tocstreatmentresponseenum"></a>

```json
"Complete response"

```

TreatmentResponseEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TreatmentResponseEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TreatmentResponseEnum|Complete response|
|TreatmentResponseEnum|Partial response|
|TreatmentResponseEnum|Progressive disease|
|TreatmentResponseEnum|Stable disease|
|TreatmentResponseEnum|Immune complete response (iCR)|
|TreatmentResponseEnum|Immune partial response (iPR)|
|TreatmentResponseEnum|Immune uncomfirmed progressive disease (iUPD)|
|TreatmentResponseEnum|Immune confirmed progressive disease (iCPD)|
|TreatmentResponseEnum|Immune stable disease (iSD)|
|TreatmentResponseEnum|Complete remission|
|TreatmentResponseEnum|Partial remission|
|TreatmentResponseEnum|Minor response|
|TreatmentResponseEnum|Complete remission without measurable residual disease (CR MRD-)|
|TreatmentResponseEnum|Complete remission with incomplete hematologic recovery (CRi)|
|TreatmentResponseEnum|Morphologic leukemia-free state|
|TreatmentResponseEnum|Primary refractory disease|
|TreatmentResponseEnum|Hematologic relapse (after CR MRD-, CR, CRi)|
|TreatmentResponseEnum|Molecular relapse (after CR MRD-)|
|TreatmentResponseEnum|Physician assessed complete response|
|TreatmentResponseEnum|Physician assessed partial response|
|TreatmentResponseEnum|Physician assessed stable disease|
|TreatmentResponseEnum|No evidence of disease (NED)|
|TreatmentResponseEnum|Major response|

<h2 id="tocS_TreatmentResponseMethodEnum">TreatmentResponseMethodEnum</h2>

<a id="schematreatmentresponsemethodenum"></a>
<a id="schema_TreatmentResponseMethodEnum"></a>
<a id="tocStreatmentresponsemethodenum"></a>
<a id="tocstreatmentresponsemethodenum"></a>

```json
"RECIST 1.1"

```

TreatmentResponseMethodEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TreatmentResponseMethodEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TreatmentResponseMethodEnum|RECIST 1.1|
|TreatmentResponseMethodEnum|iRECIST|
|TreatmentResponseMethodEnum|Cheson CLL 2012 Oncology Response Criteria|
|TreatmentResponseMethodEnum|Response Assessment in Neuro-Oncology (RANO)|
|TreatmentResponseMethodEnum|AML Response Criteria|
|TreatmentResponseMethodEnum|Physician Assessed Response Criteria|
|TreatmentResponseMethodEnum|Blazer score|

<h2 id="tocS_TreatmentSettingEnum">TreatmentSettingEnum</h2>

<a id="schematreatmentsettingenum"></a>
<a id="schema_TreatmentSettingEnum"></a>
<a id="tocStreatmentsettingenum"></a>
<a id="tocstreatmentsettingenum"></a>

```json
"Adjuvant"

```

TreatmentSettingEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TreatmentSettingEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TreatmentSettingEnum|Adjuvant|
|TreatmentSettingEnum|Advanced/Metastatic|
|TreatmentSettingEnum|Neoadjuvant|
|TreatmentSettingEnum|Conditioning|
|TreatmentSettingEnum|Induction|
|TreatmentSettingEnum|Locally advanced|
|TreatmentSettingEnum|Maintenance|
|TreatmentSettingEnum|Mobilization|
|TreatmentSettingEnum|Preventative|
|TreatmentSettingEnum|Radiosensitization|
|TreatmentSettingEnum|Salvage|

<h2 id="tocS_TreatmentStatusEnum">TreatmentStatusEnum</h2>

<a id="schematreatmentstatusenum"></a>
<a id="schema_TreatmentStatusEnum"></a>
<a id="tocStreatmentstatusenum"></a>
<a id="tocstreatmentstatusenum"></a>

```json
"Treatment completed as prescribed"

```

TreatmentStatusEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TreatmentStatusEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TreatmentStatusEnum|Treatment completed as prescribed|
|TreatmentStatusEnum|Treatment incomplete due to technical or organizational problems|
|TreatmentStatusEnum|Treatment incomplete because patient died|
|TreatmentStatusEnum|Patient choice (stopped or interrupted treatment)|
|TreatmentStatusEnum|Physician decision (stopped or interrupted treatment)|
|TreatmentStatusEnum|Treatment stopped due to lack of efficacy (disease progression)|
|TreatmentStatusEnum|Treatment stopped due to acute toxicity|
|TreatmentStatusEnum|Other|
|TreatmentStatusEnum|Not applicable|
|TreatmentStatusEnum|Unknown|

<h2 id="tocS_TreatmentTypeEnum">TreatmentTypeEnum</h2>

<a id="schematreatmenttypeenum"></a>
<a id="schema_TreatmentTypeEnum"></a>
<a id="tocStreatmenttypeenum"></a>
<a id="tocstreatmenttypeenum"></a>

```json
"Bone marrow transplant"

```

TreatmentTypeEnum

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|TreatmentTypeEnum|string|false|none|none|

#### Enumerated Values

|Property|Value|
|---|---|
|TreatmentTypeEnum|Bone marrow transplant|
|TreatmentTypeEnum|Chemotherapy|
|TreatmentTypeEnum|Hormonal therapy|
|TreatmentTypeEnum|Immunotherapy|
|TreatmentTypeEnum|No treatment|
|TreatmentTypeEnum|Other targeting molecular therapy|
|TreatmentTypeEnum|Photodynamic therapy|
|TreatmentTypeEnum|Radiation therapy|
|TreatmentTypeEnum|Stem cell transplant|
|TreatmentTypeEnum|Surgery|

<h2 id="tocS_ProgramDiscoverySchema">ProgramDiscoverySchema</h2>

<a id="schemaprogramdiscoveryschema"></a>
<a id="schema_ProgramDiscoverySchema"></a>
<a id="tocSprogramdiscoveryschema"></a>
<a id="tocsprogramdiscoveryschema"></a>

```json
{
  "cohort_list": [
    "string"
  ]
}

```

ProgramDiscoverySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cohort_list|[string]|true|none|none|

<h2 id="tocS_DiscoverySchema">DiscoverySchema</h2>

<a id="schemadiscoveryschema"></a>
<a id="schema_DiscoverySchema"></a>
<a id="tocSdiscoveryschema"></a>
<a id="tocsdiscoveryschema"></a>

```json
{
  "donors_by_cohort": {
    "property1": 0,
    "property2": 0
  }
}

```

DiscoverySchema

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|donors_by_cohort|object|true|none|none|
|» **additionalProperties**|integer|false|none|none|

