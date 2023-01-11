---
title: Metadata Service API v1.0.0
language_tabs:
  - shell: Shell
  - http: HTTP
  - javascript: JavaScript
  - ruby: Ruby
  - python: Python
  - php: PHP
  - java: Java
  - go: Go
toc_footers: []
includes: []
search: true
highlight_theme: darkula
headingLevel: 2

---

<h1 id="metadata-service-api">Metadata Service API v1.0.0</h1>

Metadata Service provides a phenotypic description of an Individual in the context of biomedical research.

<h1 id="metadata-service-api-discovery">discovery</h1>

## discovery_biomarkers_list

<a id="opIddiscovery_biomarkers_list"></a>

`GET /api/v1/discovery/biomarkers/`

<h3 id="discovery_biomarkers_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_specimen_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|submitter_follow_up_id|query|string|false|none|
|test_interval|query|integer|false|none|
|psa_level|query|integer|false|none|
|ca125|query|integer|false|none|
|cea|query|integer|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "test_interval": -2147483648,
    "psa_level": -2147483648,
    "ca125": -2147483648,
    "cea": -2147483648,
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_specimen_id": "string",
    "submitter_primary_diagnosis_id": "string",
    "submitter_treatment_id": "string",
    "submitter_follow_up_id": "string"
  }
]
```

## discovery_chemotherapies_list

<a id="opIddiscovery_chemotherapies_list"></a>

`GET /api/v1/discovery/chemotherapies/`

<h3 id="discovery_chemotherapies_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|drug_name|query|string|false|none|
|drug_rxnormcui|query|string|false|none|
|chemotherapy_dosage_units|query|string|false|none|
|cumulative_drug_dosage_prescribed|query|integer|false|none|
|cumulative_drug_dosage_actual|query|integer|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "drug_name": "string",
    "drug_rxnormcui": "string",
    "chemotherapy_dosage_units": "string",
    "cumulative_drug_dosage_prescribed": -2147483648,
    "cumulative_drug_dosage_actual": -2147483648,
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## discovery_comorbidities_list

<a id="opIddiscovery_comorbidities_list"></a>

`GET /api/v1/discovery/comorbidities/`

<h3 id="discovery_comorbidities_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|prior_malignancy|query|string|false|none|
|laterality_of_prior_malignancy|query|string|false|none|
|age_at_comorbidity_diagnosis|query|integer|false|none|
|comorbidity_type_code|query|string|false|none|
|comorbidity_treatment_status|query|string|false|none|
|comorbidity_treatment|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "prior_malignancy": "string",
    "laterality_of_prior_malignancy": "string",
    "age_at_comorbidity_diagnosis": -2147483648,
    "comorbidity_type_code": "string",
    "comorbidity_treatment_status": "string",
    "comorbidity_treatment": "string",
    "program_id": "string",
    "submitter_donor_id": "string"
  }
]
```

## discovery_donors_list

<a id="opIddiscovery_donors_list"></a>

`GET /api/v1/discovery/donors/`

<h3 id="discovery_donors_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|query|string|false|none|
|program_id|query|string|false|none|
|is_deceased|query|boolean|false|none|
|cause_of_death|query|string|false|none|
|date_of_birth|query|string|false|none|
|date_of_death|query|string|false|none|
|primary_site|query|string|false|none|
|age|query|number|false|none|
|max_age|query|number|false|none|
|min_age|query|number|false|none|
|donors|query|string|false|none|
|primary_diagnosis|query|string|false|none|
|speciman|query|string|false|none|
|sample_registration|query|string|false|none|
|treatment|query|string|false|none|
|chemotherapy|query|string|false|none|
|hormone_therapy|query|string|false|none|
|radiation|query|string|false|none|
|immunotherapy|query|string|false|none|
|surgery|query|string|false|none|
|follow_up|query|string|false|none|
|biomarker|query|string|false|none|
|comorbidity|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_donor_id": "string",
    "is_deceased": true,
    "cause_of_death": "string",
    "date_of_birth": "string",
    "date_of_death": "string",
    "primary_site": "string",
    "program_id": "string"
  }
]
```

## discovery_follow_ups_list

<a id="opIddiscovery_follow_ups_list"></a>

`GET /api/v1/discovery/follow_ups/`

<h3 id="discovery_follow_ups_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_follow_up_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|date_of_followup|query|string|false|none|
|lost_to_followup|query|boolean|false|none|
|lost_to_followup_reason|query|string|false|none|
|disease_status_at_followup|query|string|false|none|
|relapse_type|query|string|false|none|
|date_of_relapse|query|string|false|none|
|method_of_progression_status|query|string|false|none|
|anatomic_site_progression_or_recurrence|query|string|false|none|
|recurrence_tumour_staging_system|query|string|false|none|
|recurrence_t_category|query|string|false|none|
|recurrence_n_category|query|string|false|none|
|recurrence_m_category|query|string|false|none|
|recurrence_stage_group|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_follow_up_id": "string",
    "date_of_followup": "string",
    "lost_to_followup": true,
    "lost_to_followup_reason": "string",
    "disease_status_at_followup": "string",
    "relapse_type": "string",
    "date_of_relapse": "string",
    "method_of_progression_status": "string",
    "anatomic_site_progression_or_recurrence": "string",
    "recurrence_tumour_staging_system": "string",
    "recurrence_t_category": "string",
    "recurrence_n_category": "string",
    "recurrence_m_category": "string",
    "recurrence_stage_group": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_primary_diagnosis_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## discovery_hormone_therapies_list

<a id="opIddiscovery_hormone_therapies_list"></a>

`GET /api/v1/discovery/hormone_therapies/`

<h3 id="discovery_hormone_therapies_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|drug_name|query|string|false|none|
|drug_rxnormcui|query|string|false|none|
|hormone_drug_dosage_units|query|string|false|none|
|cumulative_drug_dosage_prescribed|query|integer|false|none|
|cumulative_drug_dosage_actual|query|integer|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "drug_name": "string",
    "drug_rxnormcui": "string",
    "hormone_drug_dosage_units": "string",
    "cumulative_drug_dosage_prescribed": -2147483648,
    "cumulative_drug_dosage_actual": -2147483648,
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## discovery_immunotherapies_list

<a id="opIddiscovery_immunotherapies_list"></a>

`GET /api/v1/discovery/immunotherapies/`

<h3 id="discovery_immunotherapies_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|immunotherapy_type|query|string|false|none|
|drug_name|query|string|false|none|
|drug_rxnormcui|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "immunotherapy_type": "string",
    "drug_name": "string",
    "drug_rxnormcui": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## discovery_overview_retrieve

<a id="opIddiscovery_overview_retrieve"></a>

`GET /api/v1/discovery/overview`

MoH Overview schema

> Example responses

> 200 Response

```json
{
  "cohort_count": 0,
  "individual_count": 0
}
```

## discovery_primary_diagnoses_list

<a id="opIddiscovery_primary_diagnoses_list"></a>

`GET /api/v1/discovery/primary_diagnoses/`

<h3 id="discovery_primary_diagnoses_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|date_of_diagnosis|query|string|false|none|
|cancer_type_code|query|string|false|none|
|basis_of_diagnosis|query|string|false|none|
|lymph_nodes_examined_status|query|string|false|none|
|lymph_nodes_examined_method|query|string|false|none|
|number_lymph_nodes_positive|query|integer|false|none|
|clinical_tumour_staging_system|query|string|false|none|
|clinical_t_category|query|string|false|none|
|clinical_n_category|query|string|false|none|
|clinical_m_category|query|string|false|none|
|clinical_stage_group|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_primary_diagnosis_id": "string",
    "date_of_diagnosis": "string",
    "cancer_type_code": "string",
    "basis_of_diagnosis": "string",
    "lymph_nodes_examined_status": "string",
    "lymph_nodes_examined_method": "string",
    "number_lymph_nodes_positive": -2147483648,
    "clinical_tumour_staging_system": "string",
    "clinical_t_category": "string",
    "clinical_n_category": "string",
    "clinical_m_category": "string",
    "clinical_stage_group": "string",
    "program_id": "string",
    "submitter_donor_id": "string"
  }
]
```

## discovery_radiations_list

<a id="opIddiscovery_radiations_list"></a>

`GET /api/v1/discovery/radiations/`

<h3 id="discovery_radiations_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|radiation_therapy_modality|query|string|false|none|
|radiation_therapy_type|query|string|false|none|
|radiation_therapy_fractions|query|integer|false|none|
|radiation_therapy_dosage|query|integer|false|none|
|anatomical_site_irradiated|query|string|false|none|
|radiation_boost|query|boolean|false|none|
|reference_radiation_treatment_id|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "radiation_therapy_modality": "string",
    "radiation_therapy_type": "string",
    "radiation_therapy_fractions": -2147483648,
    "radiation_therapy_dosage": -2147483648,
    "anatomical_site_irradiated": "string",
    "radiation_boost": true,
    "reference_radiation_treatment_id": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## discovery_sample_registrations_list

<a id="opIddiscovery_sample_registrations_list"></a>

`GET /api/v1/discovery/sample_registrations/`

<h3 id="discovery_sample_registrations_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_sample_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_specimen_id|query|string|false|none|
|gender|query|string|false|none|
|sex_at_birth|query|string|false|none|
|specimen_tissue_source|query|string|false|none|
|tumour_normal_designation|query|string|false|none|
|specimen_type|query|string|false|none|
|sample_type|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_sample_id": "string",
    "program_id": "string",
    "gender": "string",
    "sex_at_birth": "string",
    "specimen_tissue_source": "string",
    "tumour_normal_designation": "string",
    "specimen_type": "string",
    "sample_type": "string",
    "submitter_donor_id": "string",
    "submitter_specimen_id": "string"
  }
]
```

## discovery_specimens_list

<a id="opIddiscovery_specimens_list"></a>

`GET /api/v1/discovery/specimens/`

<h3 id="discovery_specimens_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_specimen_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|pathological_tumour_staging_system|query|string|false|none|
|pathological_t_category|query|string|false|none|
|pathological_n_category|query|string|false|none|
|pathological_m_category|query|string|false|none|
|pathological_stage_group|query|string|false|none|
|specimen_collection_date|query|string|false|none|
|specimen_storage|query|string|false|none|
|tumour_histological_type|query|string|false|none|
|specimen_anatomic_location|query|string|false|none|
|reference_pathology_confirmed_diagnosis|query|string|false|none|
|reference_pathology_confirmed_tumour_presence|query|string|false|none|
|tumour_grading_system|query|string|false|none|
|tumour_grade|query|string|false|none|
|percent_tumour_cells_range|query|string|false|none|
|percent_tumour_cells_measurement_method|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_specimen_id": "string",
    "pathological_tumour_staging_system": "string",
    "pathological_t_category": "string",
    "pathological_n_category": "string",
    "pathological_m_category": "string",
    "pathological_stage_group": "string",
    "specimen_collection_date": "string",
    "specimen_storage": "string",
    "tumour_histological_type": "string",
    "specimen_anatomic_location": "string",
    "reference_pathology_confirmed_diagnosis": "string",
    "reference_pathology_confirmed_tumour_presence": "string",
    "tumour_grading_system": "string",
    "tumour_grade": "string",
    "percent_tumour_cells_range": "string",
    "percent_tumour_cells_measurement_method": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_primary_diagnosis_id": "string"
  }
]
```

## discovery_surgeries_list

<a id="opIddiscovery_surgeries_list"></a>

`GET /api/v1/discovery/surgeries/`

<h3 id="discovery_surgeries_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_specimen_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|surgery_type|query|string|false|none|
|surgery_site|query|string|false|none|
|surgery_location|query|string|false|none|
|tumour_length|query|integer|false|none|
|tumour_width|query|integer|false|none|
|greatest_dimension_tumour|query|integer|false|none|
|tumour_focality|query|string|false|none|
|residual_tumour_classification|query|string|false|none|
|margin_types_involved|query|string|false|none|
|margin_types_not_involved|query|string|false|none|
|margin_types_not_assessed|query|string|false|none|
|lymphovascular_invasion|query|string|false|none|
|perineural_invasion|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "surgery_type": "string",
    "surgery_site": "string",
    "surgery_location": "string",
    "tumour_length": -2147483648,
    "tumour_width": -2147483648,
    "greatest_dimension_tumour": -2147483648,
    "tumour_focality": "string",
    "residual_tumour_classification": "string",
    "margin_types_involved": "string",
    "margin_types_not_involved": "string",
    "margin_types_not_assessed": "string",
    "lymphovascular_invasion": "string",
    "perineural_invasion": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_specimen_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## discovery_treatments_list

<a id="opIddiscovery_treatments_list"></a>

`GET /api/v1/discovery/treatments/`

<h3 id="discovery_treatments_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_treatment_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|treatment_type|query|string|false|none|
|is_primary_treatment|query|string|false|none|
|treatment_start_date|query|string|false|none|
|treatment_end_date|query|string|false|none|
|treatment_setting|query|string|false|none|
|treatment_intent|query|string|false|none|
|days_per_cycle|query|integer|false|none|
|number_of_cycles|query|integer|false|none|
|response_to_treatment_criteria_method|query|string|false|none|
|response_to_treatment|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_treatment_id": "string",
    "treatment_type": "string",
    "is_primary_treatment": "string",
    "treatment_start_date": "string",
    "treatment_end_date": "string",
    "treatment_setting": "string",
    "treatment_intent": "string",
    "days_per_cycle": -2147483648,
    "number_of_cycles": -2147483648,
    "response_to_treatment_criteria_method": "string",
    "response_to_treatment": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_primary_diagnosis_id": "string"
  }
]
```

<h1 id="metadata-service-api-moh">moh</h1>

## moh_biomarkers_list

<a id="opIdmoh_biomarkers_list"></a>

`GET /api/v1/moh/biomarkers/`

<h3 id="moh_biomarkers_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_specimen_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|submitter_follow_up_id|query|string|false|none|
|test_interval|query|integer|false|none|
|psa_level|query|integer|false|none|
|ca125|query|integer|false|none|
|cea|query|integer|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "test_interval": -2147483648,
    "psa_level": -2147483648,
    "ca125": -2147483648,
    "cea": -2147483648,
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_specimen_id": "string",
    "submitter_primary_diagnosis_id": "string",
    "submitter_treatment_id": "string",
    "submitter_follow_up_id": "string"
  }
]
```

## moh_biomarkers_create

<a id="opIdmoh_biomarkers_create"></a>

`POST /api/v1/moh/biomarkers/`

<h3 id="moh_biomarkers_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[BiomarkerRequest](#schemabiomarkerrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "test_interval": -2147483648,
  "psa_level": -2147483648,
  "ca125": -2147483648,
  "cea": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string"
}
```

## moh_biomarkers_retrieve

<a id="opIdmoh_biomarkers_retrieve"></a>

`GET /api/v1/moh/biomarkers/{id}/`

<h3 id="moh_biomarkers_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this biomarker.|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "test_interval": -2147483648,
  "psa_level": -2147483648,
  "ca125": -2147483648,
  "cea": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string"
}
```

## moh_biomarkers_update

<a id="opIdmoh_biomarkers_update"></a>

`PUT /api/v1/moh/biomarkers/{id}/`

<h3 id="moh_biomarkers_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this biomarker.|
|body|body|[BiomarkerRequest](#schemabiomarkerrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "test_interval": -2147483648,
  "psa_level": -2147483648,
  "ca125": -2147483648,
  "cea": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string"
}
```

## moh_biomarkers_partial_update

<a id="opIdmoh_biomarkers_partial_update"></a>

`PATCH /api/v1/moh/biomarkers/{id}/`

<h3 id="moh_biomarkers_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this biomarker.|
|body|body|[PatchedBiomarkerRequest](#schemapatchedbiomarkerrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "test_interval": -2147483648,
  "psa_level": -2147483648,
  "ca125": -2147483648,
  "cea": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string"
}
```

## moh_biomarkers_destroy

<a id="opIdmoh_biomarkers_destroy"></a>

`DELETE /api/v1/moh/biomarkers/{id}/`

<h3 id="moh_biomarkers_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this biomarker.|

## moh_chemotherapies_list

<a id="opIdmoh_chemotherapies_list"></a>

`GET /api/v1/moh/chemotherapies/`

<h3 id="moh_chemotherapies_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|drug_name|query|string|false|none|
|drug_rxnormcui|query|string|false|none|
|chemotherapy_dosage_units|query|string|false|none|
|cumulative_drug_dosage_prescribed|query|integer|false|none|
|cumulative_drug_dosage_actual|query|integer|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "drug_name": "string",
    "drug_rxnormcui": "string",
    "chemotherapy_dosage_units": "string",
    "cumulative_drug_dosage_prescribed": -2147483648,
    "cumulative_drug_dosage_actual": -2147483648,
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## moh_chemotherapies_create

<a id="opIdmoh_chemotherapies_create"></a>

`POST /api/v1/moh/chemotherapies/`

<h3 id="moh_chemotherapies_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ChemotherapyRequest](#schemachemotherapyrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "chemotherapy_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_chemotherapies_retrieve

<a id="opIdmoh_chemotherapies_retrieve"></a>

`GET /api/v1/moh/chemotherapies/{id}/`

<h3 id="moh_chemotherapies_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this chemotherapy.|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "chemotherapy_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_chemotherapies_update

<a id="opIdmoh_chemotherapies_update"></a>

`PUT /api/v1/moh/chemotherapies/{id}/`

<h3 id="moh_chemotherapies_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this chemotherapy.|
|body|body|[ChemotherapyRequest](#schemachemotherapyrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "chemotherapy_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_chemotherapies_partial_update

<a id="opIdmoh_chemotherapies_partial_update"></a>

`PATCH /api/v1/moh/chemotherapies/{id}/`

<h3 id="moh_chemotherapies_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this chemotherapy.|
|body|body|[PatchedChemotherapyRequest](#schemapatchedchemotherapyrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "chemotherapy_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_chemotherapies_destroy

<a id="opIdmoh_chemotherapies_destroy"></a>

`DELETE /api/v1/moh/chemotherapies/{id}/`

<h3 id="moh_chemotherapies_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this chemotherapy.|

## moh_comorbidities_list

<a id="opIdmoh_comorbidities_list"></a>

`GET /api/v1/moh/comorbidities/`

<h3 id="moh_comorbidities_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|prior_malignancy|query|string|false|none|
|laterality_of_prior_malignancy|query|string|false|none|
|age_at_comorbidity_diagnosis|query|integer|false|none|
|comorbidity_type_code|query|string|false|none|
|comorbidity_treatment_status|query|string|false|none|
|comorbidity_treatment|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "prior_malignancy": "string",
    "laterality_of_prior_malignancy": "string",
    "age_at_comorbidity_diagnosis": -2147483648,
    "comorbidity_type_code": "string",
    "comorbidity_treatment_status": "string",
    "comorbidity_treatment": "string",
    "program_id": "string",
    "submitter_donor_id": "string"
  }
]
```

## moh_comorbidities_create

<a id="opIdmoh_comorbidities_create"></a>

`POST /api/v1/moh/comorbidities/`

<h3 id="moh_comorbidities_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ComorbidityRequest](#schemacomorbidityrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": -2147483648,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_comorbidities_retrieve

<a id="opIdmoh_comorbidities_retrieve"></a>

`GET /api/v1/moh/comorbidities/{id}/`

<h3 id="moh_comorbidities_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this comorbidity.|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": -2147483648,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_comorbidities_update

<a id="opIdmoh_comorbidities_update"></a>

`PUT /api/v1/moh/comorbidities/{id}/`

<h3 id="moh_comorbidities_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this comorbidity.|
|body|body|[ComorbidityRequest](#schemacomorbidityrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": -2147483648,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_comorbidities_partial_update

<a id="opIdmoh_comorbidities_partial_update"></a>

`PATCH /api/v1/moh/comorbidities/{id}/`

<h3 id="moh_comorbidities_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this comorbidity.|
|body|body|[PatchedComorbidityRequest](#schemapatchedcomorbidityrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": -2147483648,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_comorbidities_destroy

<a id="opIdmoh_comorbidities_destroy"></a>

`DELETE /api/v1/moh/comorbidities/{id}/`

<h3 id="moh_comorbidities_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this comorbidity.|

## moh_donors_list

<a id="opIdmoh_donors_list"></a>

`GET /api/v1/moh/donors/`

<h3 id="moh_donors_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|query|string|false|none|
|program_id|query|string|false|none|
|is_deceased|query|boolean|false|none|
|cause_of_death|query|string|false|none|
|date_of_birth|query|string|false|none|
|date_of_death|query|string|false|none|
|primary_site|query|string|false|none|
|age|query|number|false|none|
|max_age|query|number|false|none|
|min_age|query|number|false|none|
|donors|query|string|false|none|
|primary_diagnosis|query|string|false|none|
|speciman|query|string|false|none|
|sample_registration|query|string|false|none|
|treatment|query|string|false|none|
|chemotherapy|query|string|false|none|
|hormone_therapy|query|string|false|none|
|radiation|query|string|false|none|
|immunotherapy|query|string|false|none|
|surgery|query|string|false|none|
|follow_up|query|string|false|none|
|biomarker|query|string|false|none|
|comorbidity|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_donor_id": "string",
    "is_deceased": true,
    "cause_of_death": "string",
    "date_of_birth": "string",
    "date_of_death": "string",
    "primary_site": "string",
    "program_id": "string"
  }
]
```

## moh_donors_create

<a id="opIdmoh_donors_create"></a>

`POST /api/v1/moh/donors/`

<h3 id="moh_donors_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[DonorRequest](#schemadonorrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "submitter_donor_id": "string",
  "is_deceased": true,
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": "string",
  "program_id": "string"
}
```

## moh_donors_retrieve

<a id="opIdmoh_donors_retrieve"></a>

`GET /api/v1/moh/donors/{submitter_donor_id}/`

<h3 id="moh_donors_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|path|string|true|A unique value identifying this donor.|

> Example responses

> 200 Response

```json
{
  "submitter_donor_id": "string",
  "is_deceased": true,
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": "string",
  "program_id": "string"
}
```

## moh_donors_update

<a id="opIdmoh_donors_update"></a>

`PUT /api/v1/moh/donors/{submitter_donor_id}/`

<h3 id="moh_donors_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|path|string|true|A unique value identifying this donor.|
|body|body|[DonorRequest](#schemadonorrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "submitter_donor_id": "string",
  "is_deceased": true,
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": "string",
  "program_id": "string"
}
```

## moh_donors_partial_update

<a id="opIdmoh_donors_partial_update"></a>

`PATCH /api/v1/moh/donors/{submitter_donor_id}/`

<h3 id="moh_donors_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|path|string|true|A unique value identifying this donor.|
|body|body|[PatchedDonorRequest](#schemapatcheddonorrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "submitter_donor_id": "string",
  "is_deceased": true,
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": "string",
  "program_id": "string"
}
```

## moh_donors_destroy

<a id="opIdmoh_donors_destroy"></a>

`DELETE /api/v1/moh/donors/{submitter_donor_id}/`

<h3 id="moh_donors_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_donor_id|path|string|true|A unique value identifying this donor.|

## moh_follow_ups_list

<a id="opIdmoh_follow_ups_list"></a>

`GET /api/v1/moh/follow_ups/`

<h3 id="moh_follow_ups_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_follow_up_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|date_of_followup|query|string|false|none|
|lost_to_followup|query|boolean|false|none|
|lost_to_followup_reason|query|string|false|none|
|disease_status_at_followup|query|string|false|none|
|relapse_type|query|string|false|none|
|date_of_relapse|query|string|false|none|
|method_of_progression_status|query|string|false|none|
|anatomic_site_progression_or_recurrence|query|string|false|none|
|recurrence_tumour_staging_system|query|string|false|none|
|recurrence_t_category|query|string|false|none|
|recurrence_n_category|query|string|false|none|
|recurrence_m_category|query|string|false|none|
|recurrence_stage_group|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_follow_up_id": "string",
    "date_of_followup": "string",
    "lost_to_followup": true,
    "lost_to_followup_reason": "string",
    "disease_status_at_followup": "string",
    "relapse_type": "string",
    "date_of_relapse": "string",
    "method_of_progression_status": "string",
    "anatomic_site_progression_or_recurrence": "string",
    "recurrence_tumour_staging_system": "string",
    "recurrence_t_category": "string",
    "recurrence_n_category": "string",
    "recurrence_m_category": "string",
    "recurrence_stage_group": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_primary_diagnosis_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## moh_follow_ups_create

<a id="opIdmoh_follow_ups_create"></a>

`POST /api/v1/moh/follow_ups/`

<h3 id="moh_follow_ups_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[FollowUpRequest](#schemafollowuprequest)|true|none|

> Example responses

> 201 Response

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "lost_to_followup": true,
  "lost_to_followup_reason": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": "string",
  "anatomic_site_progression_or_recurrence": "string",
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_follow_ups_retrieve

<a id="opIdmoh_follow_ups_retrieve"></a>

`GET /api/v1/moh/follow_ups/{submitter_follow_up_id}/`

<h3 id="moh_follow_ups_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_follow_up_id|path|string|true|A unique value identifying this follow up.|

> Example responses

> 200 Response

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "lost_to_followup": true,
  "lost_to_followup_reason": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": "string",
  "anatomic_site_progression_or_recurrence": "string",
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_follow_ups_update

<a id="opIdmoh_follow_ups_update"></a>

`PUT /api/v1/moh/follow_ups/{submitter_follow_up_id}/`

<h3 id="moh_follow_ups_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_follow_up_id|path|string|true|A unique value identifying this follow up.|
|body|body|[FollowUpRequest](#schemafollowuprequest)|true|none|

> Example responses

> 200 Response

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "lost_to_followup": true,
  "lost_to_followup_reason": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": "string",
  "anatomic_site_progression_or_recurrence": "string",
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_follow_ups_partial_update

<a id="opIdmoh_follow_ups_partial_update"></a>

`PATCH /api/v1/moh/follow_ups/{submitter_follow_up_id}/`

<h3 id="moh_follow_ups_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_follow_up_id|path|string|true|A unique value identifying this follow up.|
|body|body|[PatchedFollowUpRequest](#schemapatchedfollowuprequest)|false|none|

> Example responses

> 200 Response

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "lost_to_followup": true,
  "lost_to_followup_reason": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": "string",
  "anatomic_site_progression_or_recurrence": "string",
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_follow_ups_destroy

<a id="opIdmoh_follow_ups_destroy"></a>

`DELETE /api/v1/moh/follow_ups/{submitter_follow_up_id}/`

<h3 id="moh_follow_ups_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_follow_up_id|path|string|true|A unique value identifying this follow up.|

## moh_hormone_therapies_list

<a id="opIdmoh_hormone_therapies_list"></a>

`GET /api/v1/moh/hormone_therapies/`

<h3 id="moh_hormone_therapies_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|drug_name|query|string|false|none|
|drug_rxnormcui|query|string|false|none|
|hormone_drug_dosage_units|query|string|false|none|
|cumulative_drug_dosage_prescribed|query|integer|false|none|
|cumulative_drug_dosage_actual|query|integer|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "drug_name": "string",
    "drug_rxnormcui": "string",
    "hormone_drug_dosage_units": "string",
    "cumulative_drug_dosage_prescribed": -2147483648,
    "cumulative_drug_dosage_actual": -2147483648,
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## moh_hormone_therapies_create

<a id="opIdmoh_hormone_therapies_create"></a>

`POST /api/v1/moh/hormone_therapies/`

<h3 id="moh_hormone_therapies_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[HormoneTherapyRequest](#schemahormonetherapyrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "hormone_drug_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_hormone_therapies_retrieve

<a id="opIdmoh_hormone_therapies_retrieve"></a>

`GET /api/v1/moh/hormone_therapies/{id}/`

<h3 id="moh_hormone_therapies_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this hormone therapy.|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "hormone_drug_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_hormone_therapies_update

<a id="opIdmoh_hormone_therapies_update"></a>

`PUT /api/v1/moh/hormone_therapies/{id}/`

<h3 id="moh_hormone_therapies_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this hormone therapy.|
|body|body|[HormoneTherapyRequest](#schemahormonetherapyrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "hormone_drug_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_hormone_therapies_partial_update

<a id="opIdmoh_hormone_therapies_partial_update"></a>

`PATCH /api/v1/moh/hormone_therapies/{id}/`

<h3 id="moh_hormone_therapies_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this hormone therapy.|
|body|body|[PatchedHormoneTherapyRequest](#schemapatchedhormonetherapyrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "hormone_drug_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_hormone_therapies_destroy

<a id="opIdmoh_hormone_therapies_destroy"></a>

`DELETE /api/v1/moh/hormone_therapies/{id}/`

<h3 id="moh_hormone_therapies_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this hormone therapy.|

## moh_immunotherapies_list

<a id="opIdmoh_immunotherapies_list"></a>

`GET /api/v1/moh/immunotherapies/`

<h3 id="moh_immunotherapies_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|immunotherapy_type|query|string|false|none|
|drug_name|query|string|false|none|
|drug_rxnormcui|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "immunotherapy_type": "string",
    "drug_name": "string",
    "drug_rxnormcui": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## moh_immunotherapies_create

<a id="opIdmoh_immunotherapies_create"></a>

`POST /api/v1/moh/immunotherapies/`

<h3 id="moh_immunotherapies_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ImmunotherapyRequest](#schemaimmunotherapyrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_immunotherapies_retrieve

<a id="opIdmoh_immunotherapies_retrieve"></a>

`GET /api/v1/moh/immunotherapies/{id}/`

<h3 id="moh_immunotherapies_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this immunotherapy.|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_immunotherapies_update

<a id="opIdmoh_immunotherapies_update"></a>

`PUT /api/v1/moh/immunotherapies/{id}/`

<h3 id="moh_immunotherapies_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this immunotherapy.|
|body|body|[ImmunotherapyRequest](#schemaimmunotherapyrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_immunotherapies_partial_update

<a id="opIdmoh_immunotherapies_partial_update"></a>

`PATCH /api/v1/moh/immunotherapies/{id}/`

<h3 id="moh_immunotherapies_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this immunotherapy.|
|body|body|[PatchedImmunotherapyRequest](#schemapatchedimmunotherapyrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_immunotherapies_destroy

<a id="opIdmoh_immunotherapies_destroy"></a>

`DELETE /api/v1/moh/immunotherapies/{id}/`

<h3 id="moh_immunotherapies_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this immunotherapy.|

## moh_primary_diagnoses_list

<a id="opIdmoh_primary_diagnoses_list"></a>

`GET /api/v1/moh/primary_diagnoses/`

<h3 id="moh_primary_diagnoses_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|date_of_diagnosis|query|string|false|none|
|cancer_type_code|query|string|false|none|
|basis_of_diagnosis|query|string|false|none|
|lymph_nodes_examined_status|query|string|false|none|
|lymph_nodes_examined_method|query|string|false|none|
|number_lymph_nodes_positive|query|integer|false|none|
|clinical_tumour_staging_system|query|string|false|none|
|clinical_t_category|query|string|false|none|
|clinical_n_category|query|string|false|none|
|clinical_m_category|query|string|false|none|
|clinical_stage_group|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_primary_diagnosis_id": "string",
    "date_of_diagnosis": "string",
    "cancer_type_code": "string",
    "basis_of_diagnosis": "string",
    "lymph_nodes_examined_status": "string",
    "lymph_nodes_examined_method": "string",
    "number_lymph_nodes_positive": -2147483648,
    "clinical_tumour_staging_system": "string",
    "clinical_t_category": "string",
    "clinical_n_category": "string",
    "clinical_m_category": "string",
    "clinical_stage_group": "string",
    "program_id": "string",
    "submitter_donor_id": "string"
  }
]
```

## moh_primary_diagnoses_create

<a id="opIdmoh_primary_diagnoses_create"></a>

`POST /api/v1/moh/primary_diagnoses/`

<h3 id="moh_primary_diagnoses_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[PrimaryDiagnosisRequest](#schemaprimarydiagnosisrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": -2147483648,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_primary_diagnoses_retrieve

<a id="opIdmoh_primary_diagnoses_retrieve"></a>

`GET /api/v1/moh/primary_diagnoses/{submitter_primary_diagnosis_id}/`

<h3 id="moh_primary_diagnoses_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|path|string|true|A unique value identifying this primary diagnosis.|

> Example responses

> 200 Response

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": -2147483648,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_primary_diagnoses_update

<a id="opIdmoh_primary_diagnoses_update"></a>

`PUT /api/v1/moh/primary_diagnoses/{submitter_primary_diagnosis_id}/`

<h3 id="moh_primary_diagnoses_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|path|string|true|A unique value identifying this primary diagnosis.|
|body|body|[PrimaryDiagnosisRequest](#schemaprimarydiagnosisrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": -2147483648,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_primary_diagnoses_partial_update

<a id="opIdmoh_primary_diagnoses_partial_update"></a>

`PATCH /api/v1/moh/primary_diagnoses/{submitter_primary_diagnosis_id}/`

<h3 id="moh_primary_diagnoses_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|path|string|true|A unique value identifying this primary diagnosis.|
|body|body|[PatchedPrimaryDiagnosisRequest](#schemapatchedprimarydiagnosisrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": -2147483648,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}
```

## moh_primary_diagnoses_destroy

<a id="opIdmoh_primary_diagnoses_destroy"></a>

`DELETE /api/v1/moh/primary_diagnoses/{submitter_primary_diagnosis_id}/`

<h3 id="moh_primary_diagnoses_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|path|string|true|A unique value identifying this primary diagnosis.|

## moh_programs_list

<a id="opIdmoh_programs_list"></a>

`GET /api/v1/moh/programs/`

<h3 id="moh_programs_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|name|query|string|false|none|
|created|query|string(date)|false|none|
|updated|query|string(date-time)|false|none|

> Example responses

> 200 Response

```json
[
  {
    "program_id": "string",
    "name": "string",
    "created": "2019-08-24",
    "updated": "2019-08-24T14:15:22Z"
  }
]
```

## moh_programs_create

<a id="opIdmoh_programs_create"></a>

`POST /api/v1/moh/programs/`

<h3 id="moh_programs_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[ProgramRequest](#schemaprogramrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "program_id": "string",
  "name": "string",
  "created": "2019-08-24",
  "updated": "2019-08-24T14:15:22Z"
}
```

## moh_programs_retrieve

<a id="opIdmoh_programs_retrieve"></a>

`GET /api/v1/moh/programs/{program_id}/`

<h3 id="moh_programs_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|path|string|true|A unique value identifying this program.|

> Example responses

> 200 Response

```json
{
  "program_id": "string",
  "name": "string",
  "created": "2019-08-24",
  "updated": "2019-08-24T14:15:22Z"
}
```

## moh_programs_update

<a id="opIdmoh_programs_update"></a>

`PUT /api/v1/moh/programs/{program_id}/`

<h3 id="moh_programs_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|path|string|true|A unique value identifying this program.|
|body|body|[ProgramRequest](#schemaprogramrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "program_id": "string",
  "name": "string",
  "created": "2019-08-24",
  "updated": "2019-08-24T14:15:22Z"
}
```

## moh_programs_partial_update

<a id="opIdmoh_programs_partial_update"></a>

`PATCH /api/v1/moh/programs/{program_id}/`

<h3 id="moh_programs_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|path|string|true|A unique value identifying this program.|
|body|body|[PatchedProgramRequest](#schemapatchedprogramrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "program_id": "string",
  "name": "string",
  "created": "2019-08-24",
  "updated": "2019-08-24T14:15:22Z"
}
```

## moh_programs_destroy

<a id="opIdmoh_programs_destroy"></a>

`DELETE /api/v1/moh/programs/{program_id}/`

<h3 id="moh_programs_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|path|string|true|A unique value identifying this program.|

## moh_radiations_list

<a id="opIdmoh_radiations_list"></a>

`GET /api/v1/moh/radiations/`

<h3 id="moh_radiations_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|radiation_therapy_modality|query|string|false|none|
|radiation_therapy_type|query|string|false|none|
|radiation_therapy_fractions|query|integer|false|none|
|radiation_therapy_dosage|query|integer|false|none|
|anatomical_site_irradiated|query|string|false|none|
|radiation_boost|query|boolean|false|none|
|reference_radiation_treatment_id|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "radiation_therapy_modality": "string",
    "radiation_therapy_type": "string",
    "radiation_therapy_fractions": -2147483648,
    "radiation_therapy_dosage": -2147483648,
    "anatomical_site_irradiated": "string",
    "radiation_boost": true,
    "reference_radiation_treatment_id": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## moh_radiations_create

<a id="opIdmoh_radiations_create"></a>

`POST /api/v1/moh/radiations/`

<h3 id="moh_radiations_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[RadiationRequest](#schemaradiationrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": -2147483648,
  "radiation_therapy_dosage": -2147483648,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_radiations_retrieve

<a id="opIdmoh_radiations_retrieve"></a>

`GET /api/v1/moh/radiations/{id}/`

<h3 id="moh_radiations_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this radiation.|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": -2147483648,
  "radiation_therapy_dosage": -2147483648,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_radiations_update

<a id="opIdmoh_radiations_update"></a>

`PUT /api/v1/moh/radiations/{id}/`

<h3 id="moh_radiations_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this radiation.|
|body|body|[RadiationRequest](#schemaradiationrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": -2147483648,
  "radiation_therapy_dosage": -2147483648,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_radiations_partial_update

<a id="opIdmoh_radiations_partial_update"></a>

`PATCH /api/v1/moh/radiations/{id}/`

<h3 id="moh_radiations_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this radiation.|
|body|body|[PatchedRadiationRequest](#schemapatchedradiationrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": -2147483648,
  "radiation_therapy_dosage": -2147483648,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_radiations_destroy

<a id="opIdmoh_radiations_destroy"></a>

`DELETE /api/v1/moh/radiations/{id}/`

<h3 id="moh_radiations_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this radiation.|

## moh_sample_registrations_list

<a id="opIdmoh_sample_registrations_list"></a>

`GET /api/v1/moh/sample_registrations/`

<h3 id="moh_sample_registrations_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_sample_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_specimen_id|query|string|false|none|
|gender|query|string|false|none|
|sex_at_birth|query|string|false|none|
|specimen_tissue_source|query|string|false|none|
|tumour_normal_designation|query|string|false|none|
|specimen_type|query|string|false|none|
|sample_type|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_sample_id": "string",
    "program_id": "string",
    "gender": "string",
    "sex_at_birth": "string",
    "specimen_tissue_source": "string",
    "tumour_normal_designation": "string",
    "specimen_type": "string",
    "sample_type": "string",
    "submitter_donor_id": "string",
    "submitter_specimen_id": "string"
  }
]
```

## moh_sample_registrations_create

<a id="opIdmoh_sample_registrations_create"></a>

`POST /api/v1/moh/sample_registrations/`

<h3 id="moh_sample_registrations_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[SampleRegistrationRequest](#schemasampleregistrationrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}
```

## moh_sample_registrations_retrieve

<a id="opIdmoh_sample_registrations_retrieve"></a>

`GET /api/v1/moh/sample_registrations/{submitter_sample_id}/`

<h3 id="moh_sample_registrations_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_sample_id|path|string|true|A unique value identifying this sample registration.|

> Example responses

> 200 Response

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}
```

## moh_sample_registrations_update

<a id="opIdmoh_sample_registrations_update"></a>

`PUT /api/v1/moh/sample_registrations/{submitter_sample_id}/`

<h3 id="moh_sample_registrations_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_sample_id|path|string|true|A unique value identifying this sample registration.|
|body|body|[SampleRegistrationRequest](#schemasampleregistrationrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}
```

## moh_sample_registrations_partial_update

<a id="opIdmoh_sample_registrations_partial_update"></a>

`PATCH /api/v1/moh/sample_registrations/{submitter_sample_id}/`

<h3 id="moh_sample_registrations_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_sample_id|path|string|true|A unique value identifying this sample registration.|
|body|body|[PatchedSampleRegistrationRequest](#schemapatchedsampleregistrationrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}
```

## moh_sample_registrations_destroy

<a id="opIdmoh_sample_registrations_destroy"></a>

`DELETE /api/v1/moh/sample_registrations/{submitter_sample_id}/`

<h3 id="moh_sample_registrations_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_sample_id|path|string|true|A unique value identifying this sample registration.|

## moh_specimens_list

<a id="opIdmoh_specimens_list"></a>

`GET /api/v1/moh/specimens/`

<h3 id="moh_specimens_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_specimen_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|pathological_tumour_staging_system|query|string|false|none|
|pathological_t_category|query|string|false|none|
|pathological_n_category|query|string|false|none|
|pathological_m_category|query|string|false|none|
|pathological_stage_group|query|string|false|none|
|specimen_collection_date|query|string|false|none|
|specimen_storage|query|string|false|none|
|tumour_histological_type|query|string|false|none|
|specimen_anatomic_location|query|string|false|none|
|reference_pathology_confirmed_diagnosis|query|string|false|none|
|reference_pathology_confirmed_tumour_presence|query|string|false|none|
|tumour_grading_system|query|string|false|none|
|tumour_grade|query|string|false|none|
|percent_tumour_cells_range|query|string|false|none|
|percent_tumour_cells_measurement_method|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_specimen_id": "string",
    "pathological_tumour_staging_system": "string",
    "pathological_t_category": "string",
    "pathological_n_category": "string",
    "pathological_m_category": "string",
    "pathological_stage_group": "string",
    "specimen_collection_date": "string",
    "specimen_storage": "string",
    "tumour_histological_type": "string",
    "specimen_anatomic_location": "string",
    "reference_pathology_confirmed_diagnosis": "string",
    "reference_pathology_confirmed_tumour_presence": "string",
    "tumour_grading_system": "string",
    "tumour_grade": "string",
    "percent_tumour_cells_range": "string",
    "percent_tumour_cells_measurement_method": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_primary_diagnosis_id": "string"
  }
]
```

## moh_specimens_create

<a id="opIdmoh_specimens_create"></a>

`POST /api/v1/moh/specimens/`

<h3 id="moh_specimens_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[SpecimenRequest](#schemaspecimenrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_specimens_retrieve

<a id="opIdmoh_specimens_retrieve"></a>

`GET /api/v1/moh/specimens/{submitter_specimen_id}/`

<h3 id="moh_specimens_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_specimen_id|path|string|true|A unique value identifying this specimen.|

> Example responses

> 200 Response

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_specimens_update

<a id="opIdmoh_specimens_update"></a>

`PUT /api/v1/moh/specimens/{submitter_specimen_id}/`

<h3 id="moh_specimens_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_specimen_id|path|string|true|A unique value identifying this specimen.|
|body|body|[SpecimenRequest](#schemaspecimenrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_specimens_partial_update

<a id="opIdmoh_specimens_partial_update"></a>

`PATCH /api/v1/moh/specimens/{submitter_specimen_id}/`

<h3 id="moh_specimens_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_specimen_id|path|string|true|A unique value identifying this specimen.|
|body|body|[PatchedSpecimenRequest](#schemapatchedspecimenrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_specimens_destroy

<a id="opIdmoh_specimens_destroy"></a>

`DELETE /api/v1/moh/specimens/{submitter_specimen_id}/`

<h3 id="moh_specimens_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_specimen_id|path|string|true|A unique value identifying this specimen.|

## moh_surgeries_list

<a id="opIdmoh_surgeries_list"></a>

`GET /api/v1/moh/surgeries/`

<h3 id="moh_surgeries_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_specimen_id|query|string|false|none|
|submitter_treatment_id|query|string|false|none|
|surgery_type|query|string|false|none|
|surgery_site|query|string|false|none|
|surgery_location|query|string|false|none|
|tumour_length|query|integer|false|none|
|tumour_width|query|integer|false|none|
|greatest_dimension_tumour|query|integer|false|none|
|tumour_focality|query|string|false|none|
|residual_tumour_classification|query|string|false|none|
|margin_types_involved|query|string|false|none|
|margin_types_not_involved|query|string|false|none|
|margin_types_not_assessed|query|string|false|none|
|lymphovascular_invasion|query|string|false|none|
|perineural_invasion|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "id": 0,
    "surgery_type": "string",
    "surgery_site": "string",
    "surgery_location": "string",
    "tumour_length": -2147483648,
    "tumour_width": -2147483648,
    "greatest_dimension_tumour": -2147483648,
    "tumour_focality": "string",
    "residual_tumour_classification": "string",
    "margin_types_involved": "string",
    "margin_types_not_involved": "string",
    "margin_types_not_assessed": "string",
    "lymphovascular_invasion": "string",
    "perineural_invasion": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_specimen_id": "string",
    "submitter_treatment_id": "string"
  }
]
```

## moh_surgeries_create

<a id="opIdmoh_surgeries_create"></a>

`POST /api/v1/moh/surgeries/`

<h3 id="moh_surgeries_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[SurgeryRequest](#schemasurgeryrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "id": 0,
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": -2147483648,
  "tumour_width": -2147483648,
  "greatest_dimension_tumour": -2147483648,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": "string",
  "margin_types_not_involved": "string",
  "margin_types_not_assessed": "string",
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_surgeries_retrieve

<a id="opIdmoh_surgeries_retrieve"></a>

`GET /api/v1/moh/surgeries/{id}/`

<h3 id="moh_surgeries_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this surgery.|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": -2147483648,
  "tumour_width": -2147483648,
  "greatest_dimension_tumour": -2147483648,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": "string",
  "margin_types_not_involved": "string",
  "margin_types_not_assessed": "string",
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_surgeries_update

<a id="opIdmoh_surgeries_update"></a>

`PUT /api/v1/moh/surgeries/{id}/`

<h3 id="moh_surgeries_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this surgery.|
|body|body|[SurgeryRequest](#schemasurgeryrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": -2147483648,
  "tumour_width": -2147483648,
  "greatest_dimension_tumour": -2147483648,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": "string",
  "margin_types_not_involved": "string",
  "margin_types_not_assessed": "string",
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_surgeries_partial_update

<a id="opIdmoh_surgeries_partial_update"></a>

`PATCH /api/v1/moh/surgeries/{id}/`

<h3 id="moh_surgeries_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this surgery.|
|body|body|[PatchedSurgeryRequest](#schemapatchedsurgeryrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "id": 0,
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": -2147483648,
  "tumour_width": -2147483648,
  "greatest_dimension_tumour": -2147483648,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": "string",
  "margin_types_not_involved": "string",
  "margin_types_not_assessed": "string",
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_treatment_id": "string"
}
```

## moh_surgeries_destroy

<a id="opIdmoh_surgeries_destroy"></a>

`DELETE /api/v1/moh/surgeries/{id}/`

<h3 id="moh_surgeries_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|id|path|integer|true|A unique integer value identifying this surgery.|

## moh_treatments_list

<a id="opIdmoh_treatments_list"></a>

`GET /api/v1/moh/treatments/`

<h3 id="moh_treatments_list-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_treatment_id|query|string|false|none|
|program_id|query|string|false|none|
|submitter_donor_id|query|string|false|none|
|submitter_primary_diagnosis_id|query|string|false|none|
|treatment_type|query|string|false|none|
|is_primary_treatment|query|string|false|none|
|treatment_start_date|query|string|false|none|
|treatment_end_date|query|string|false|none|
|treatment_setting|query|string|false|none|
|treatment_intent|query|string|false|none|
|days_per_cycle|query|integer|false|none|
|number_of_cycles|query|integer|false|none|
|response_to_treatment_criteria_method|query|string|false|none|
|response_to_treatment|query|string|false|none|

> Example responses

> 200 Response

```json
[
  {
    "submitter_treatment_id": "string",
    "treatment_type": "string",
    "is_primary_treatment": "string",
    "treatment_start_date": "string",
    "treatment_end_date": "string",
    "treatment_setting": "string",
    "treatment_intent": "string",
    "days_per_cycle": -2147483648,
    "number_of_cycles": -2147483648,
    "response_to_treatment_criteria_method": "string",
    "response_to_treatment": "string",
    "program_id": "string",
    "submitter_donor_id": "string",
    "submitter_primary_diagnosis_id": "string"
  }
]
```

## moh_treatments_create

<a id="opIdmoh_treatments_create"></a>

`POST /api/v1/moh/treatments/`

<h3 id="moh_treatments_create-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|body|body|[TreatmentRequest](#schematreatmentrequest)|true|none|

> Example responses

> 201 Response

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": "string",
  "is_primary_treatment": "string",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": -2147483648,
  "number_of_cycles": -2147483648,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_treatments_retrieve

<a id="opIdmoh_treatments_retrieve"></a>

`GET /api/v1/moh/treatments/{submitter_treatment_id}/`

<h3 id="moh_treatments_retrieve-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_treatment_id|path|string|true|A unique value identifying this treatment.|

> Example responses

> 200 Response

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": "string",
  "is_primary_treatment": "string",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": -2147483648,
  "number_of_cycles": -2147483648,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_treatments_update

<a id="opIdmoh_treatments_update"></a>

`PUT /api/v1/moh/treatments/{submitter_treatment_id}/`

<h3 id="moh_treatments_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_treatment_id|path|string|true|A unique value identifying this treatment.|
|body|body|[TreatmentRequest](#schematreatmentrequest)|true|none|

> Example responses

> 200 Response

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": "string",
  "is_primary_treatment": "string",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": -2147483648,
  "number_of_cycles": -2147483648,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_treatments_partial_update

<a id="opIdmoh_treatments_partial_update"></a>

`PATCH /api/v1/moh/treatments/{submitter_treatment_id}/`

<h3 id="moh_treatments_partial_update-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_treatment_id|path|string|true|A unique value identifying this treatment.|
|body|body|[PatchedTreatmentRequest](#schemapatchedtreatmentrequest)|false|none|

> Example responses

> 200 Response

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": "string",
  "is_primary_treatment": "string",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": -2147483648,
  "number_of_cycles": -2147483648,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}
```

## moh_treatments_destroy

<a id="opIdmoh_treatments_destroy"></a>

`DELETE /api/v1/moh/treatments/{submitter_treatment_id}/`

<h3 id="moh_treatments_destroy-parameters">Parameters</h3>

|Name|In|Type|Required|Description|
|---|---|---|---|---|
|submitter_treatment_id|path|string|true|A unique value identifying this treatment.|

# Schemas

<h2 id="tocS_Biomarker">Biomarker</h2>

<a id="schemabiomarker"></a>
<a id="schema_Biomarker"></a>
<a id="tocSbiomarker"></a>
<a id="tocsbiomarker"></a>

```json
{
  "id": 0,
  "test_interval": -2147483648,
  "psa_level": -2147483648,
  "ca125": -2147483648,
  "cea": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|test_interval|integer¦null|false|none|none|
|psa_level|integer¦null|false|none|none|
|ca125|integer¦null|false|none|none|
|cea|integer¦null|false|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string¦null|false|none|none|
|submitter_primary_diagnosis_id|string¦null|false|none|none|
|submitter_treatment_id|string¦null|false|none|none|
|submitter_follow_up_id|string¦null|false|none|none|

<h2 id="tocS_BiomarkerRequest">BiomarkerRequest</h2>

<a id="schemabiomarkerrequest"></a>
<a id="schema_BiomarkerRequest"></a>
<a id="tocSbiomarkerrequest"></a>
<a id="tocsbiomarkerrequest"></a>

```json
{
  "test_interval": -2147483648,
  "psa_level": -2147483648,
  "ca125": -2147483648,
  "cea": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|test_interval|integer¦null|false|none|none|
|psa_level|integer¦null|false|none|none|
|ca125|integer¦null|false|none|none|
|cea|integer¦null|false|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string¦null|false|none|none|
|submitter_primary_diagnosis_id|string¦null|false|none|none|
|submitter_treatment_id|string¦null|false|none|none|
|submitter_follow_up_id|string¦null|false|none|none|

<h2 id="tocS_Chemotherapy">Chemotherapy</h2>

<a id="schemachemotherapy"></a>
<a id="schema_Chemotherapy"></a>
<a id="tocSchemotherapy"></a>
<a id="tocschemotherapy"></a>

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "chemotherapy_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|drug_name|string|true|none|none|
|drug_rxnormcui|string|true|none|none|
|chemotherapy_dosage_units|string|true|none|none|
|cumulative_drug_dosage_prescribed|integer¦null|false|none|none|
|cumulative_drug_dosage_actual|integer¦null|false|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_ChemotherapyRequest">ChemotherapyRequest</h2>

<a id="schemachemotherapyrequest"></a>
<a id="schema_ChemotherapyRequest"></a>
<a id="tocSchemotherapyrequest"></a>
<a id="tocschemotherapyrequest"></a>

```json
{
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "chemotherapy_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|string|true|none|none|
|drug_rxnormcui|string|true|none|none|
|chemotherapy_dosage_units|string|true|none|none|
|cumulative_drug_dosage_prescribed|integer¦null|false|none|none|
|cumulative_drug_dosage_actual|integer¦null|false|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_Comorbidity">Comorbidity</h2>

<a id="schemacomorbidity"></a>
<a id="schema_Comorbidity"></a>
<a id="tocScomorbidity"></a>
<a id="tocscomorbidity"></a>

```json
{
  "id": 0,
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": -2147483648,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|prior_malignancy|string|true|none|none|
|laterality_of_prior_malignancy|string|true|none|none|
|age_at_comorbidity_diagnosis|integer¦null|false|none|none|
|comorbidity_type_code|string|true|none|none|
|comorbidity_treatment_status|string|true|none|none|
|comorbidity_treatment|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|

<h2 id="tocS_ComorbidityRequest">ComorbidityRequest</h2>

<a id="schemacomorbidityrequest"></a>
<a id="schema_ComorbidityRequest"></a>
<a id="tocScomorbidityrequest"></a>
<a id="tocscomorbidityrequest"></a>

```json
{
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": -2147483648,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prior_malignancy|string|true|none|none|
|laterality_of_prior_malignancy|string|true|none|none|
|age_at_comorbidity_diagnosis|integer¦null|false|none|none|
|comorbidity_type_code|string|true|none|none|
|comorbidity_treatment_status|string|true|none|none|
|comorbidity_treatment|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|

<h2 id="tocS_Donor">Donor</h2>

<a id="schemadonor"></a>
<a id="schema_Donor"></a>
<a id="tocSdonor"></a>
<a id="tocsdonor"></a>

```json
{
  "submitter_donor_id": "string",
  "is_deceased": true,
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": "string",
  "program_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|is_deceased|boolean|true|none|none|
|cause_of_death|string|true|none|none|
|date_of_birth|string|true|none|none|
|date_of_death|string|true|none|none|
|primary_site|string|true|none|none|
|program_id|string|true|none|none|

<h2 id="tocS_DonorRequest">DonorRequest</h2>

<a id="schemadonorrequest"></a>
<a id="schema_DonorRequest"></a>
<a id="tocSdonorrequest"></a>
<a id="tocsdonorrequest"></a>

```json
{
  "submitter_donor_id": "string",
  "is_deceased": true,
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": "string",
  "program_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|true|none|none|
|is_deceased|boolean|true|none|none|
|cause_of_death|string|true|none|none|
|date_of_birth|string|true|none|none|
|date_of_death|string|true|none|none|
|primary_site|string|true|none|none|
|program_id|string|true|none|none|

<h2 id="tocS_FollowUp">FollowUp</h2>

<a id="schemafollowup"></a>
<a id="schema_FollowUp"></a>
<a id="tocSfollowup"></a>
<a id="tocsfollowup"></a>

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "lost_to_followup": true,
  "lost_to_followup_reason": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": "string",
  "anatomic_site_progression_or_recurrence": "string",
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|string|true|none|none|
|date_of_followup|string|true|none|none|
|lost_to_followup|boolean¦null|false|none|none|
|lost_to_followup_reason|string|true|none|none|
|disease_status_at_followup|string|true|none|none|
|relapse_type|string|true|none|none|
|date_of_relapse|string|true|none|none|
|method_of_progression_status|string|true|none|none|
|anatomic_site_progression_or_recurrence|string|true|none|none|
|recurrence_tumour_staging_system|string|true|none|none|
|recurrence_t_category|string|true|none|none|
|recurrence_n_category|string|true|none|none|
|recurrence_m_category|string|true|none|none|
|recurrence_stage_group|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string¦null|false|none|none|
|submitter_treatment_id|string¦null|false|none|none|

<h2 id="tocS_FollowUpRequest">FollowUpRequest</h2>

<a id="schemafollowuprequest"></a>
<a id="schema_FollowUpRequest"></a>
<a id="tocSfollowuprequest"></a>
<a id="tocsfollowuprequest"></a>

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "lost_to_followup": true,
  "lost_to_followup_reason": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": "string",
  "anatomic_site_progression_or_recurrence": "string",
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|string|true|none|none|
|date_of_followup|string|true|none|none|
|lost_to_followup|boolean¦null|false|none|none|
|lost_to_followup_reason|string|true|none|none|
|disease_status_at_followup|string|true|none|none|
|relapse_type|string|true|none|none|
|date_of_relapse|string|true|none|none|
|method_of_progression_status|string|true|none|none|
|anatomic_site_progression_or_recurrence|string|true|none|none|
|recurrence_tumour_staging_system|string|true|none|none|
|recurrence_t_category|string|true|none|none|
|recurrence_n_category|string|true|none|none|
|recurrence_m_category|string|true|none|none|
|recurrence_stage_group|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string¦null|false|none|none|
|submitter_treatment_id|string¦null|false|none|none|

<h2 id="tocS_HormoneTherapy">HormoneTherapy</h2>

<a id="schemahormonetherapy"></a>
<a id="schema_HormoneTherapy"></a>
<a id="tocShormonetherapy"></a>
<a id="tocshormonetherapy"></a>

```json
{
  "id": 0,
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "hormone_drug_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|drug_name|string|true|none|none|
|drug_rxnormcui|string|true|none|none|
|hormone_drug_dosage_units|string|true|none|none|
|cumulative_drug_dosage_prescribed|integer¦null|false|none|none|
|cumulative_drug_dosage_actual|integer¦null|false|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_HormoneTherapyRequest">HormoneTherapyRequest</h2>

<a id="schemahormonetherapyrequest"></a>
<a id="schema_HormoneTherapyRequest"></a>
<a id="tocShormonetherapyrequest"></a>
<a id="tocshormonetherapyrequest"></a>

```json
{
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "hormone_drug_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|string|true|none|none|
|drug_rxnormcui|string|true|none|none|
|hormone_drug_dosage_units|string|true|none|none|
|cumulative_drug_dosage_prescribed|integer¦null|false|none|none|
|cumulative_drug_dosage_actual|integer¦null|false|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_Immunotherapy">Immunotherapy</h2>

<a id="schemaimmunotherapy"></a>
<a id="schema_Immunotherapy"></a>
<a id="tocSimmunotherapy"></a>
<a id="tocsimmunotherapy"></a>

```json
{
  "id": 0,
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|immunotherapy_type|string|true|none|none|
|drug_name|string|true|none|none|
|drug_rxnormcui|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_ImmunotherapyRequest">ImmunotherapyRequest</h2>

<a id="schemaimmunotherapyrequest"></a>
<a id="schema_ImmunotherapyRequest"></a>
<a id="tocSimmunotherapyrequest"></a>
<a id="tocsimmunotherapyrequest"></a>

```json
{
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_type|string|true|none|none|
|drug_name|string|true|none|none|
|drug_rxnormcui|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_PatchedBiomarkerRequest">PatchedBiomarkerRequest</h2>

<a id="schemapatchedbiomarkerrequest"></a>
<a id="schema_PatchedBiomarkerRequest"></a>
<a id="tocSpatchedbiomarkerrequest"></a>
<a id="tocspatchedbiomarkerrequest"></a>

```json
{
  "test_interval": -2147483648,
  "psa_level": -2147483648,
  "ca125": -2147483648,
  "cea": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string",
  "submitter_follow_up_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|test_interval|integer¦null|false|none|none|
|psa_level|integer¦null|false|none|none|
|ca125|integer¦null|false|none|none|
|cea|integer¦null|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_specimen_id|string¦null|false|none|none|
|submitter_primary_diagnosis_id|string¦null|false|none|none|
|submitter_treatment_id|string¦null|false|none|none|
|submitter_follow_up_id|string¦null|false|none|none|

<h2 id="tocS_PatchedChemotherapyRequest">PatchedChemotherapyRequest</h2>

<a id="schemapatchedchemotherapyrequest"></a>
<a id="schema_PatchedChemotherapyRequest"></a>
<a id="tocSpatchedchemotherapyrequest"></a>
<a id="tocspatchedchemotherapyrequest"></a>

```json
{
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "chemotherapy_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|string|false|none|none|
|drug_rxnormcui|string|false|none|none|
|chemotherapy_dosage_units|string|false|none|none|
|cumulative_drug_dosage_prescribed|integer¦null|false|none|none|
|cumulative_drug_dosage_actual|integer¦null|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_treatment_id|string|false|none|none|

<h2 id="tocS_PatchedComorbidityRequest">PatchedComorbidityRequest</h2>

<a id="schemapatchedcomorbidityrequest"></a>
<a id="schema_PatchedComorbidityRequest"></a>
<a id="tocSpatchedcomorbidityrequest"></a>
<a id="tocspatchedcomorbidityrequest"></a>

```json
{
  "prior_malignancy": "string",
  "laterality_of_prior_malignancy": "string",
  "age_at_comorbidity_diagnosis": -2147483648,
  "comorbidity_type_code": "string",
  "comorbidity_treatment_status": "string",
  "comorbidity_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|prior_malignancy|string|false|none|none|
|laterality_of_prior_malignancy|string|false|none|none|
|age_at_comorbidity_diagnosis|integer¦null|false|none|none|
|comorbidity_type_code|string|false|none|none|
|comorbidity_treatment_status|string|false|none|none|
|comorbidity_treatment|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|

<h2 id="tocS_PatchedDonorRequest">PatchedDonorRequest</h2>

<a id="schemapatcheddonorrequest"></a>
<a id="schema_PatchedDonorRequest"></a>
<a id="tocSpatcheddonorrequest"></a>
<a id="tocspatcheddonorrequest"></a>

```json
{
  "submitter_donor_id": "string",
  "is_deceased": true,
  "cause_of_death": "string",
  "date_of_birth": "string",
  "date_of_death": "string",
  "primary_site": "string",
  "program_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_donor_id|string|false|none|none|
|is_deceased|boolean|false|none|none|
|cause_of_death|string|false|none|none|
|date_of_birth|string|false|none|none|
|date_of_death|string|false|none|none|
|primary_site|string|false|none|none|
|program_id|string|false|none|none|

<h2 id="tocS_PatchedFollowUpRequest">PatchedFollowUpRequest</h2>

<a id="schemapatchedfollowuprequest"></a>
<a id="schema_PatchedFollowUpRequest"></a>
<a id="tocSpatchedfollowuprequest"></a>
<a id="tocspatchedfollowuprequest"></a>

```json
{
  "submitter_follow_up_id": "string",
  "date_of_followup": "string",
  "lost_to_followup": true,
  "lost_to_followup_reason": "string",
  "disease_status_at_followup": "string",
  "relapse_type": "string",
  "date_of_relapse": "string",
  "method_of_progression_status": "string",
  "anatomic_site_progression_or_recurrence": "string",
  "recurrence_tumour_staging_system": "string",
  "recurrence_t_category": "string",
  "recurrence_n_category": "string",
  "recurrence_m_category": "string",
  "recurrence_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_follow_up_id|string|false|none|none|
|date_of_followup|string|false|none|none|
|lost_to_followup|boolean¦null|false|none|none|
|lost_to_followup_reason|string|false|none|none|
|disease_status_at_followup|string|false|none|none|
|relapse_type|string|false|none|none|
|date_of_relapse|string|false|none|none|
|method_of_progression_status|string|false|none|none|
|anatomic_site_progression_or_recurrence|string|false|none|none|
|recurrence_tumour_staging_system|string|false|none|none|
|recurrence_t_category|string|false|none|none|
|recurrence_n_category|string|false|none|none|
|recurrence_m_category|string|false|none|none|
|recurrence_stage_group|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_primary_diagnosis_id|string¦null|false|none|none|
|submitter_treatment_id|string¦null|false|none|none|

<h2 id="tocS_PatchedHormoneTherapyRequest">PatchedHormoneTherapyRequest</h2>

<a id="schemapatchedhormonetherapyrequest"></a>
<a id="schema_PatchedHormoneTherapyRequest"></a>
<a id="tocSpatchedhormonetherapyrequest"></a>
<a id="tocspatchedhormonetherapyrequest"></a>

```json
{
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "hormone_drug_dosage_units": "string",
  "cumulative_drug_dosage_prescribed": -2147483648,
  "cumulative_drug_dosage_actual": -2147483648,
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|drug_name|string|false|none|none|
|drug_rxnormcui|string|false|none|none|
|hormone_drug_dosage_units|string|false|none|none|
|cumulative_drug_dosage_prescribed|integer¦null|false|none|none|
|cumulative_drug_dosage_actual|integer¦null|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_treatment_id|string|false|none|none|

<h2 id="tocS_PatchedImmunotherapyRequest">PatchedImmunotherapyRequest</h2>

<a id="schemapatchedimmunotherapyrequest"></a>
<a id="schema_PatchedImmunotherapyRequest"></a>
<a id="tocSpatchedimmunotherapyrequest"></a>
<a id="tocspatchedimmunotherapyrequest"></a>

```json
{
  "immunotherapy_type": "string",
  "drug_name": "string",
  "drug_rxnormcui": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|immunotherapy_type|string|false|none|none|
|drug_name|string|false|none|none|
|drug_rxnormcui|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_treatment_id|string|false|none|none|

<h2 id="tocS_PatchedPrimaryDiagnosisRequest">PatchedPrimaryDiagnosisRequest</h2>

<a id="schemapatchedprimarydiagnosisrequest"></a>
<a id="schema_PatchedPrimaryDiagnosisRequest"></a>
<a id="tocSpatchedprimarydiagnosisrequest"></a>
<a id="tocspatchedprimarydiagnosisrequest"></a>

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": -2147483648,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|string|false|none|none|
|date_of_diagnosis|string|false|none|none|
|cancer_type_code|string|false|none|none|
|basis_of_diagnosis|string|false|none|none|
|lymph_nodes_examined_status|string|false|none|none|
|lymph_nodes_examined_method|string|false|none|none|
|number_lymph_nodes_positive|integer¦null|false|none|none|
|clinical_tumour_staging_system|string|false|none|none|
|clinical_t_category|string|false|none|none|
|clinical_n_category|string|false|none|none|
|clinical_m_category|string|false|none|none|
|clinical_stage_group|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|

<h2 id="tocS_PatchedProgramRequest">PatchedProgramRequest</h2>

<a id="schemapatchedprogramrequest"></a>
<a id="schema_PatchedProgramRequest"></a>
<a id="tocSpatchedprogramrequest"></a>
<a id="tocspatchedprogramrequest"></a>

```json
{
  "program_id": "string",
  "name": "string",
  "created": "2019-08-24",
  "updated": "2019-08-24T14:15:22Z"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|false|none|none|
|name|string|false|none|none|
|created|string(date)|false|none|none|
|updated|string(date-time)|false|none|none|

<h2 id="tocS_PatchedRadiationRequest">PatchedRadiationRequest</h2>

<a id="schemapatchedradiationrequest"></a>
<a id="schema_PatchedRadiationRequest"></a>
<a id="tocSpatchedradiationrequest"></a>
<a id="tocspatchedradiationrequest"></a>

```json
{
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": -2147483648,
  "radiation_therapy_dosage": -2147483648,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_modality|string|false|none|none|
|radiation_therapy_type|string|false|none|none|
|radiation_therapy_fractions|integer|false|none|none|
|radiation_therapy_dosage|integer|false|none|none|
|anatomical_site_irradiated|string|false|none|none|
|radiation_boost|boolean¦null|false|none|none|
|reference_radiation_treatment_id|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_treatment_id|string|false|none|none|

<h2 id="tocS_PatchedSampleRegistrationRequest">PatchedSampleRegistrationRequest</h2>

<a id="schemapatchedsampleregistrationrequest"></a>
<a id="schema_PatchedSampleRegistrationRequest"></a>
<a id="tocSpatchedsampleregistrationrequest"></a>
<a id="tocspatchedsampleregistrationrequest"></a>

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_sample_id|string|false|none|none|
|program_id|string|false|none|none|
|gender|string|false|none|none|
|sex_at_birth|string|false|none|none|
|specimen_tissue_source|string|false|none|none|
|tumour_normal_designation|string|false|none|none|
|specimen_type|string|false|none|none|
|sample_type|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_specimen_id|string|false|none|none|

<h2 id="tocS_PatchedSpecimenRequest">PatchedSpecimenRequest</h2>

<a id="schemapatchedspecimenrequest"></a>
<a id="schema_PatchedSpecimenRequest"></a>
<a id="tocSpatchedspecimenrequest"></a>
<a id="tocspatchedspecimenrequest"></a>

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|string|false|none|none|
|pathological_tumour_staging_system|string|false|none|none|
|pathological_t_category|string|false|none|none|
|pathological_n_category|string|false|none|none|
|pathological_m_category|string|false|none|none|
|pathological_stage_group|string|false|none|none|
|specimen_collection_date|string|false|none|none|
|specimen_storage|string|false|none|none|
|tumour_histological_type|string|false|none|none|
|specimen_anatomic_location|string|false|none|none|
|reference_pathology_confirmed_diagnosis|string|false|none|none|
|reference_pathology_confirmed_tumour_presence|string|false|none|none|
|tumour_grading_system|string|false|none|none|
|tumour_grade|string|false|none|none|
|percent_tumour_cells_range|string|false|none|none|
|percent_tumour_cells_measurement_method|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_primary_diagnosis_id|string|false|none|none|

<h2 id="tocS_PatchedSurgeryRequest">PatchedSurgeryRequest</h2>

<a id="schemapatchedsurgeryrequest"></a>
<a id="schema_PatchedSurgeryRequest"></a>
<a id="tocSpatchedsurgeryrequest"></a>
<a id="tocspatchedsurgeryrequest"></a>

```json
{
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": -2147483648,
  "tumour_width": -2147483648,
  "greatest_dimension_tumour": -2147483648,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": "string",
  "margin_types_not_involved": "string",
  "margin_types_not_assessed": "string",
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_type|string|false|none|none|
|surgery_site|string|false|none|none|
|surgery_location|string|false|none|none|
|tumour_length|integer¦null|false|none|none|
|tumour_width|integer¦null|false|none|none|
|greatest_dimension_tumour|integer¦null|false|none|none|
|tumour_focality|string|false|none|none|
|residual_tumour_classification|string|false|none|none|
|margin_types_involved|string|false|none|none|
|margin_types_not_involved|string|false|none|none|
|margin_types_not_assessed|string|false|none|none|
|lymphovascular_invasion|string|false|none|none|
|perineural_invasion|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_specimen_id|string|false|none|none|
|submitter_treatment_id|string|false|none|none|

<h2 id="tocS_PatchedTreatmentRequest">PatchedTreatmentRequest</h2>

<a id="schemapatchedtreatmentrequest"></a>
<a id="schema_PatchedTreatmentRequest"></a>
<a id="tocSpatchedtreatmentrequest"></a>
<a id="tocspatchedtreatmentrequest"></a>

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": "string",
  "is_primary_treatment": "string",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": -2147483648,
  "number_of_cycles": -2147483648,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|string|false|none|none|
|treatment_type|string|false|none|none|
|is_primary_treatment|string|false|none|none|
|treatment_start_date|string|false|none|none|
|treatment_end_date|string|false|none|none|
|treatment_setting|string|false|none|none|
|treatment_intent|string|false|none|none|
|days_per_cycle|integer¦null|false|none|none|
|number_of_cycles|integer¦null|false|none|none|
|response_to_treatment_criteria_method|string|false|none|none|
|response_to_treatment|string|false|none|none|
|program_id|string|false|none|none|
|submitter_donor_id|string|false|none|none|
|submitter_primary_diagnosis_id|string|false|none|none|

<h2 id="tocS_PrimaryDiagnosis">PrimaryDiagnosis</h2>

<a id="schemaprimarydiagnosis"></a>
<a id="schema_PrimaryDiagnosis"></a>
<a id="tocSprimarydiagnosis"></a>
<a id="tocsprimarydiagnosis"></a>

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": -2147483648,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|string|true|none|none|
|date_of_diagnosis|string|true|none|none|
|cancer_type_code|string|true|none|none|
|basis_of_diagnosis|string|true|none|none|
|lymph_nodes_examined_status|string|true|none|none|
|lymph_nodes_examined_method|string|true|none|none|
|number_lymph_nodes_positive|integer¦null|false|none|none|
|clinical_tumour_staging_system|string|true|none|none|
|clinical_t_category|string|true|none|none|
|clinical_n_category|string|true|none|none|
|clinical_m_category|string|true|none|none|
|clinical_stage_group|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|

<h2 id="tocS_PrimaryDiagnosisRequest">PrimaryDiagnosisRequest</h2>

<a id="schemaprimarydiagnosisrequest"></a>
<a id="schema_PrimaryDiagnosisRequest"></a>
<a id="tocSprimarydiagnosisrequest"></a>
<a id="tocsprimarydiagnosisrequest"></a>

```json
{
  "submitter_primary_diagnosis_id": "string",
  "date_of_diagnosis": "string",
  "cancer_type_code": "string",
  "basis_of_diagnosis": "string",
  "lymph_nodes_examined_status": "string",
  "lymph_nodes_examined_method": "string",
  "number_lymph_nodes_positive": -2147483648,
  "clinical_tumour_staging_system": "string",
  "clinical_t_category": "string",
  "clinical_n_category": "string",
  "clinical_m_category": "string",
  "clinical_stage_group": "string",
  "program_id": "string",
  "submitter_donor_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_primary_diagnosis_id|string|true|none|none|
|date_of_diagnosis|string|true|none|none|
|cancer_type_code|string|true|none|none|
|basis_of_diagnosis|string|true|none|none|
|lymph_nodes_examined_status|string|true|none|none|
|lymph_nodes_examined_method|string|true|none|none|
|number_lymph_nodes_positive|integer¦null|false|none|none|
|clinical_tumour_staging_system|string|true|none|none|
|clinical_t_category|string|true|none|none|
|clinical_n_category|string|true|none|none|
|clinical_m_category|string|true|none|none|
|clinical_stage_group|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|

<h2 id="tocS_Program">Program</h2>

<a id="schemaprogram"></a>
<a id="schema_Program"></a>
<a id="tocSprogram"></a>
<a id="tocsprogram"></a>

```json
{
  "program_id": "string",
  "name": "string",
  "created": "2019-08-24",
  "updated": "2019-08-24T14:15:22Z"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|name|string|true|none|none|
|created|string(date)|false|none|none|
|updated|string(date-time)|false|none|none|

<h2 id="tocS_ProgramRequest">ProgramRequest</h2>

<a id="schemaprogramrequest"></a>
<a id="schema_ProgramRequest"></a>
<a id="tocSprogramrequest"></a>
<a id="tocsprogramrequest"></a>

```json
{
  "program_id": "string",
  "name": "string",
  "created": "2019-08-24",
  "updated": "2019-08-24T14:15:22Z"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|program_id|string|true|none|none|
|name|string|true|none|none|
|created|string(date)|false|none|none|
|updated|string(date-time)|false|none|none|

<h2 id="tocS_Radiation">Radiation</h2>

<a id="schemaradiation"></a>
<a id="schema_Radiation"></a>
<a id="tocSradiation"></a>
<a id="tocsradiation"></a>

```json
{
  "id": 0,
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": -2147483648,
  "radiation_therapy_dosage": -2147483648,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|radiation_therapy_modality|string|true|none|none|
|radiation_therapy_type|string|true|none|none|
|radiation_therapy_fractions|integer|true|none|none|
|radiation_therapy_dosage|integer|true|none|none|
|anatomical_site_irradiated|string|true|none|none|
|radiation_boost|boolean¦null|false|none|none|
|reference_radiation_treatment_id|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_RadiationRequest">RadiationRequest</h2>

<a id="schemaradiationrequest"></a>
<a id="schema_RadiationRequest"></a>
<a id="tocSradiationrequest"></a>
<a id="tocsradiationrequest"></a>

```json
{
  "radiation_therapy_modality": "string",
  "radiation_therapy_type": "string",
  "radiation_therapy_fractions": -2147483648,
  "radiation_therapy_dosage": -2147483648,
  "anatomical_site_irradiated": "string",
  "radiation_boost": true,
  "reference_radiation_treatment_id": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|radiation_therapy_modality|string|true|none|none|
|radiation_therapy_type|string|true|none|none|
|radiation_therapy_fractions|integer|true|none|none|
|radiation_therapy_dosage|integer|true|none|none|
|anatomical_site_irradiated|string|true|none|none|
|radiation_boost|boolean¦null|false|none|none|
|reference_radiation_treatment_id|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_SampleRegistration">SampleRegistration</h2>

<a id="schemasampleregistration"></a>
<a id="schema_SampleRegistration"></a>
<a id="tocSsampleregistration"></a>
<a id="tocssampleregistration"></a>

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_sample_id|string|true|none|none|
|program_id|string|true|none|none|
|gender|string|true|none|none|
|sex_at_birth|string|true|none|none|
|specimen_tissue_source|string|true|none|none|
|tumour_normal_designation|string|true|none|none|
|specimen_type|string|true|none|none|
|sample_type|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string|true|none|none|

<h2 id="tocS_SampleRegistrationRequest">SampleRegistrationRequest</h2>

<a id="schemasampleregistrationrequest"></a>
<a id="schema_SampleRegistrationRequest"></a>
<a id="tocSsampleregistrationrequest"></a>
<a id="tocssampleregistrationrequest"></a>

```json
{
  "submitter_sample_id": "string",
  "program_id": "string",
  "gender": "string",
  "sex_at_birth": "string",
  "specimen_tissue_source": "string",
  "tumour_normal_designation": "string",
  "specimen_type": "string",
  "sample_type": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_sample_id|string|true|none|none|
|program_id|string|true|none|none|
|gender|string|true|none|none|
|sex_at_birth|string|true|none|none|
|specimen_tissue_source|string|true|none|none|
|tumour_normal_designation|string|true|none|none|
|specimen_type|string|true|none|none|
|sample_type|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string|true|none|none|

<h2 id="tocS_Specimen">Specimen</h2>

<a id="schemaspecimen"></a>
<a id="schema_Specimen"></a>
<a id="tocSspecimen"></a>
<a id="tocsspecimen"></a>

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|string|true|none|none|
|pathological_tumour_staging_system|string|true|none|none|
|pathological_t_category|string|true|none|none|
|pathological_n_category|string|true|none|none|
|pathological_m_category|string|true|none|none|
|pathological_stage_group|string|true|none|none|
|specimen_collection_date|string|true|none|none|
|specimen_storage|string|true|none|none|
|tumour_histological_type|string|true|none|none|
|specimen_anatomic_location|string|true|none|none|
|reference_pathology_confirmed_diagnosis|string|true|none|none|
|reference_pathology_confirmed_tumour_presence|string|true|none|none|
|tumour_grading_system|string|true|none|none|
|tumour_grade|string|true|none|none|
|percent_tumour_cells_range|string|true|none|none|
|percent_tumour_cells_measurement_method|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|

<h2 id="tocS_SpecimenRequest">SpecimenRequest</h2>

<a id="schemaspecimenrequest"></a>
<a id="schema_SpecimenRequest"></a>
<a id="tocSspecimenrequest"></a>
<a id="tocsspecimenrequest"></a>

```json
{
  "submitter_specimen_id": "string",
  "pathological_tumour_staging_system": "string",
  "pathological_t_category": "string",
  "pathological_n_category": "string",
  "pathological_m_category": "string",
  "pathological_stage_group": "string",
  "specimen_collection_date": "string",
  "specimen_storage": "string",
  "tumour_histological_type": "string",
  "specimen_anatomic_location": "string",
  "reference_pathology_confirmed_diagnosis": "string",
  "reference_pathology_confirmed_tumour_presence": "string",
  "tumour_grading_system": "string",
  "tumour_grade": "string",
  "percent_tumour_cells_range": "string",
  "percent_tumour_cells_measurement_method": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_specimen_id|string|true|none|none|
|pathological_tumour_staging_system|string|true|none|none|
|pathological_t_category|string|true|none|none|
|pathological_n_category|string|true|none|none|
|pathological_m_category|string|true|none|none|
|pathological_stage_group|string|true|none|none|
|specimen_collection_date|string|true|none|none|
|specimen_storage|string|true|none|none|
|tumour_histological_type|string|true|none|none|
|specimen_anatomic_location|string|true|none|none|
|reference_pathology_confirmed_diagnosis|string|true|none|none|
|reference_pathology_confirmed_tumour_presence|string|true|none|none|
|tumour_grading_system|string|true|none|none|
|tumour_grade|string|true|none|none|
|percent_tumour_cells_range|string|true|none|none|
|percent_tumour_cells_measurement_method|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|

<h2 id="tocS_Surgery">Surgery</h2>

<a id="schemasurgery"></a>
<a id="schema_Surgery"></a>
<a id="tocSsurgery"></a>
<a id="tocssurgery"></a>

```json
{
  "id": 0,
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": -2147483648,
  "tumour_width": -2147483648,
  "greatest_dimension_tumour": -2147483648,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": "string",
  "margin_types_not_involved": "string",
  "margin_types_not_assessed": "string",
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|id|integer|false|read-only|none|
|surgery_type|string|true|none|none|
|surgery_site|string|true|none|none|
|surgery_location|string|true|none|none|
|tumour_length|integer¦null|false|none|none|
|tumour_width|integer¦null|false|none|none|
|greatest_dimension_tumour|integer¦null|false|none|none|
|tumour_focality|string|true|none|none|
|residual_tumour_classification|string|true|none|none|
|margin_types_involved|string|true|none|none|
|margin_types_not_involved|string|true|none|none|
|margin_types_not_assessed|string|true|none|none|
|lymphovascular_invasion|string|true|none|none|
|perineural_invasion|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_SurgeryRequest">SurgeryRequest</h2>

<a id="schemasurgeryrequest"></a>
<a id="schema_SurgeryRequest"></a>
<a id="tocSsurgeryrequest"></a>
<a id="tocssurgeryrequest"></a>

```json
{
  "surgery_type": "string",
  "surgery_site": "string",
  "surgery_location": "string",
  "tumour_length": -2147483648,
  "tumour_width": -2147483648,
  "greatest_dimension_tumour": -2147483648,
  "tumour_focality": "string",
  "residual_tumour_classification": "string",
  "margin_types_involved": "string",
  "margin_types_not_involved": "string",
  "margin_types_not_assessed": "string",
  "lymphovascular_invasion": "string",
  "perineural_invasion": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_specimen_id": "string",
  "submitter_treatment_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|surgery_type|string|true|none|none|
|surgery_site|string|true|none|none|
|surgery_location|string|true|none|none|
|tumour_length|integer¦null|false|none|none|
|tumour_width|integer¦null|false|none|none|
|greatest_dimension_tumour|integer¦null|false|none|none|
|tumour_focality|string|true|none|none|
|residual_tumour_classification|string|true|none|none|
|margin_types_involved|string|true|none|none|
|margin_types_not_involved|string|true|none|none|
|margin_types_not_assessed|string|true|none|none|
|lymphovascular_invasion|string|true|none|none|
|perineural_invasion|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_specimen_id|string|true|none|none|
|submitter_treatment_id|string|true|none|none|

<h2 id="tocS_Treatment">Treatment</h2>

<a id="schematreatment"></a>
<a id="schema_Treatment"></a>
<a id="tocStreatment"></a>
<a id="tocstreatment"></a>

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": "string",
  "is_primary_treatment": "string",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": -2147483648,
  "number_of_cycles": -2147483648,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|string|true|none|none|
|treatment_type|string|true|none|none|
|is_primary_treatment|string|true|none|none|
|treatment_start_date|string|true|none|none|
|treatment_end_date|string|true|none|none|
|treatment_setting|string|true|none|none|
|treatment_intent|string|true|none|none|
|days_per_cycle|integer¦null|false|none|none|
|number_of_cycles|integer¦null|false|none|none|
|response_to_treatment_criteria_method|string|true|none|none|
|response_to_treatment|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|

<h2 id="tocS_TreatmentRequest">TreatmentRequest</h2>

<a id="schematreatmentrequest"></a>
<a id="schema_TreatmentRequest"></a>
<a id="tocStreatmentrequest"></a>
<a id="tocstreatmentrequest"></a>

```json
{
  "submitter_treatment_id": "string",
  "treatment_type": "string",
  "is_primary_treatment": "string",
  "treatment_start_date": "string",
  "treatment_end_date": "string",
  "treatment_setting": "string",
  "treatment_intent": "string",
  "days_per_cycle": -2147483648,
  "number_of_cycles": -2147483648,
  "response_to_treatment_criteria_method": "string",
  "response_to_treatment": "string",
  "program_id": "string",
  "submitter_donor_id": "string",
  "submitter_primary_diagnosis_id": "string"
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|submitter_treatment_id|string|true|none|none|
|treatment_type|string|true|none|none|
|is_primary_treatment|string|true|none|none|
|treatment_start_date|string|true|none|none|
|treatment_end_date|string|true|none|none|
|treatment_setting|string|true|none|none|
|treatment_intent|string|true|none|none|
|days_per_cycle|integer¦null|false|none|none|
|number_of_cycles|integer¦null|false|none|none|
|response_to_treatment_criteria_method|string|true|none|none|
|response_to_treatment|string|true|none|none|
|program_id|string|true|none|none|
|submitter_donor_id|string|true|none|none|
|submitter_primary_diagnosis_id|string|true|none|none|

<h2 id="tocS_moh_overview_schema_response">moh_overview_schema_response</h2>

<a id="schemamoh_overview_schema_response"></a>
<a id="schema_moh_overview_schema_response"></a>
<a id="tocSmoh_overview_schema_response"></a>
<a id="tocsmoh_overview_schema_response"></a>

```json
{
  "cohort_count": 0,
  "individual_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cohort_count|integer|true|none|none|
|individual_count|integer|true|none|none|

