
<h1 id="moh-service-api">MoH Service API v1.0.0</h1>

This is the RESTful API for the MoH Service.

# Authentication

- HTTP Authentication, scheme: basic

* API Key (cookieAuth)
    - Parameter Name: **sessionid**, in: cookie. 

* API Key (tokenAuth)
    - Parameter Name: **Authorization**, in: header. Token-based authentication with required prefix "Token"

<h1 id="moh-service-api-biomarkers">biomarkers</h1>

## biomarkers_list

<a id="opIdbiomarkers_list"></a>

`GET /moh/v1/discovery/biomarkers/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="biomarkers_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-chemotherapies">chemotherapies</h1>

## chemotherapies_list

<a id="opIdchemotherapies_list"></a>

`GET /moh/v1/discovery/chemotherapies/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="chemotherapies_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-comorbidities">comorbidities</h1>

## comorbidities_list

<a id="opIdcomorbidities_list"></a>

`GET /moh/v1/discovery/comorbidities/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="comorbidities_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-donors">donors</h1>

## donors_list

<a id="opIddonors_list"></a>

`GET /moh/v1/discovery/donors/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="donors_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-follow_ups">follow_ups</h1>

## follow_ups_list

<a id="opIdfollow_ups_list"></a>

`GET /moh/v1/discovery/follow_ups/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="follow_ups_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-hormone_therapies">hormone_therapies</h1>

## hormone_therapies_list

<a id="opIdhormone_therapies_list"></a>

`GET /moh/v1/discovery/hormone_therapies/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="hormone_therapies_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-immunotherapies">immunotherapies</h1>

## immunotherapies_list

<a id="opIdimmunotherapies_list"></a>

`GET /moh/v1/discovery/immunotherapies/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="immunotherapies_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-overview">overview</h1>

## overview_cancer_type_count_retrieve

<a id="opIdoverview_cancer_type_count_retrieve"></a>

`GET /moh/v1/discovery/overview/cancer_type_count`

MoH cancer types count

> Example responses

> 200 Response

```json
{
  "cancer_type_count": 0
}
```

## overview_cohort_count_retrieve

<a id="opIdoverview_cohort_count_retrieve"></a>

`GET /moh/v1/discovery/overview/cohort_count`

MoH cohorts count

> Example responses

> 200 Response

```json
{
  "cohort_count": 0
}
```

## overview_diagnosis_age_count_retrieve

<a id="opIdoverview_diagnosis_age_count_retrieve"></a>

`GET /moh/v1/discovery/overview/diagnosis_age_count`

MoH Diagnosis age count

> Example responses

> 200 Response

```json
{
  "age_range_count": 0
}
```

## overview_gender_count_retrieve

<a id="opIdoverview_gender_count_retrieve"></a>

`GET /moh/v1/discovery/overview/gender_count`

MoH gender count

> Example responses

> 200 Response

```json
{
  "gender_count": 0
}
```

## overview_individual_count_retrieve

<a id="opIdoverview_individual_count_retrieve"></a>

`GET /moh/v1/discovery/overview/individual_count`

MoH individuals count

> Example responses

> 200 Response

```json
{
  "individual_count": 0
}
```

## overview_patients_per_cohort_retrieve

<a id="opIdoverview_patients_per_cohort_retrieve"></a>

`GET /moh/v1/discovery/overview/patients_per_cohort`

MoH patients per cohort count

> Example responses

> 200 Response

```json
{
  "patients_per_cohort_count": 0
}
```

## overview_treatment_type_count_retrieve

<a id="opIdoverview_treatment_type_count_retrieve"></a>

`GET /moh/v1/discovery/overview/treatment_type_count`

MoH Treatments type count

> Example responses

> 200 Response

```json
{
  "treatment_type_count": 0
}
```

<h1 id="moh-service-api-primary_diagnoses">primary_diagnoses</h1>

## primary_diagnoses_list

<a id="opIdprimary_diagnoses_list"></a>

`GET /moh/v1/discovery/primary_diagnoses/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="primary_diagnoses_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-radiations">radiations</h1>

## radiations_list

<a id="opIdradiations_list"></a>

`GET /moh/v1/discovery/radiations/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="radiations_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-sample_registrations">sample_registrations</h1>

## sample_registrations_list

<a id="opIdsample_registrations_list"></a>

`GET /moh/v1/discovery/sample_registrations/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="sample_registrations_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-specimens">specimens</h1>

## specimens_list

<a id="opIdspecimens_list"></a>

`GET /moh/v1/discovery/specimens/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="specimens_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-surgeries">surgeries</h1>

## surgeries_list

<a id="opIdsurgeries_list"></a>

`GET /moh/v1/discovery/surgeries/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="surgeries_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

<h1 id="moh-service-api-treatments">treatments</h1>

## treatments_list

<a id="opIdtreatments_list"></a>

`GET /moh/v1/discovery/treatments/`

This mixin should be used for viewsets that need to expose
discovery information about the donor they represent.

Methods
-------
list(request, *args, **kwargs)
    Returns a response that contains the number of unique donors in the
    queryset.

<h3 id="treatments_list-parameters">Parameters</h3>

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
{
  "discovery_donor": 0
}
```

# Schemas

<h2 id="tocS_Discovery">Discovery</h2>

<a id="schemadiscovery"></a>
<a id="schema_Discovery"></a>
<a id="tocSdiscovery"></a>
<a id="tocsdiscovery"></a>

```json
{
  "discovery_donor": 0
}

```

This serializer is used to return the discovery_donor.
It also override the list serializer to a single object

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|discovery_donor|integer|true|none|none|

<h2 id="tocS_moh_overview_cancer_type_count_response">moh_overview_cancer_type_count_response</h2>

<a id="schemamoh_overview_cancer_type_count_response"></a>
<a id="schema_moh_overview_cancer_type_count_response"></a>
<a id="tocSmoh_overview_cancer_type_count_response"></a>
<a id="tocsmoh_overview_cancer_type_count_response"></a>

```json
{
  "cancer_type_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cancer_type_count|integer|true|none|none|

<h2 id="tocS_moh_overview_cohort_count_response">moh_overview_cohort_count_response</h2>

<a id="schemamoh_overview_cohort_count_response"></a>
<a id="schema_moh_overview_cohort_count_response"></a>
<a id="tocSmoh_overview_cohort_count_response"></a>
<a id="tocsmoh_overview_cohort_count_response"></a>

```json
{
  "cohort_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|cohort_count|integer|true|none|none|

<h2 id="tocS_moh_overview_diagnosis_age_count_response">moh_overview_diagnosis_age_count_response</h2>

<a id="schemamoh_overview_diagnosis_age_count_response"></a>
<a id="schema_moh_overview_diagnosis_age_count_response"></a>
<a id="tocSmoh_overview_diagnosis_age_count_response"></a>
<a id="tocsmoh_overview_diagnosis_age_count_response"></a>

```json
{
  "age_range_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|age_range_count|integer|true|none|none|

<h2 id="tocS_moh_overview_gender_count_response">moh_overview_gender_count_response</h2>

<a id="schemamoh_overview_gender_count_response"></a>
<a id="schema_moh_overview_gender_count_response"></a>
<a id="tocSmoh_overview_gender_count_response"></a>
<a id="tocsmoh_overview_gender_count_response"></a>

```json
{
  "gender_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|gender_count|integer|true|none|none|

<h2 id="tocS_moh_overview_individual_count_response">moh_overview_individual_count_response</h2>

<a id="schemamoh_overview_individual_count_response"></a>
<a id="schema_moh_overview_individual_count_response"></a>
<a id="tocSmoh_overview_individual_count_response"></a>
<a id="tocsmoh_overview_individual_count_response"></a>

```json
{
  "individual_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|individual_count|integer|true|none|none|

<h2 id="tocS_moh_overview_patient_per_cohort_response">moh_overview_patient_per_cohort_response</h2>

<a id="schemamoh_overview_patient_per_cohort_response"></a>
<a id="schema_moh_overview_patient_per_cohort_response"></a>
<a id="tocSmoh_overview_patient_per_cohort_response"></a>
<a id="tocsmoh_overview_patient_per_cohort_response"></a>

```json
{
  "patients_per_cohort_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|patients_per_cohort_count|integer|true|none|none|

<h2 id="tocS_moh_overview_treatment_type_count_response">moh_overview_treatment_type_count_response</h2>

<a id="schemamoh_overview_treatment_type_count_response"></a>
<a id="schema_moh_overview_treatment_type_count_response"></a>
<a id="tocSmoh_overview_treatment_type_count_response"></a>
<a id="tocsmoh_overview_treatment_type_count_response"></a>

```json
{
  "treatment_type_count": 0
}

```

### Properties

|Name|Type|Required|Restrictions|Description|
|---|---|---|---|---|
|treatment_type_count|integer|true|none|none|

