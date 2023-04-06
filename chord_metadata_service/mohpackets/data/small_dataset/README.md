# Dataset relationships

This is a diagram of the relationships between the models in the dataset.

## Small dataset data

- 2 Programs
- 10 Donors
  - 1-6: program_1
  - 7-10: program_2

- 16 PrimaryDiagnosis
  - 1-3: donor_1 | program_1
  - 4-6: donor_2 | program_1
  - 7-8: donor_3 | program_1
  - 9-10: donor_4 | program_1
  - 11-12: donor_5_6 | program_1
  - 13-16: donor_7_10 | program_2

- 22 Specimen
  - 1-3: primary_diagnosis_1 | donor_1 | program_1
  - 4-6: primary_diagnosis_2 | donor_1 | program_1
  - 7-8: primary_diagnosis_3 | donor_1 | program_1
  - 9-10: primary_diagnosis_4 | donor_2 | program_1
  - 11-12: primary_diagnosis_5_6 | donor_2 | program_1
  - 13-14: primary_diagnosis_7_8 | donor_3 | program_1
  - 15-16: primary_diagnosis_9_10 | donor_4 | program_1
  - 17-18: primary_diagnosis_11_12 | donor_5_6 | program_1
  - 19-22: primary_diagnosis_13_16 | donor_7_10 | program_2

- 28 SampleRegistration
  - 1-3: specimen_1 | donor_1 | program_1
  - 4-6: specimen_2 | donor_1 | program_1
  - 7-8: specimen_3 | donor_1 | program_1
  - 9-10: specimen_4 | donor_1 | program_1
  - 11-12: specimen_5_6 | donor_1 | program_1
  - 13-14: specimen_7_8 | donor_1 | program_1
  - 15-16: specimen_9_10 | donor_2 | program_1
  - 17-18: specimen_11_12 | donor_2 | program_1
  - 19-20: specimen_13_14 | donor_3 | program_1
  - 21-22: specimen_15_16 | donor_4 | program_1
  - 23-24: specimen_17_18 | donor_5_6 | program_1
  - 25-28: specimen_19_22 | donor_7_10 | program_2

- 22 Treatment
  - 1-3: primary_diagnosis_1 | donor_1 | program_1
  - 4-6: primary_diagnosis_2 | donor_1 | program_1
  - 7-8: primary_diagnosis_3 | donor_1 | program_1
  - 9-10: primary_diagnosis_4 | donor_2 | program_1
  - 11-12: primary_diagnosis_5_6 | donor_2 | program_1
  - 13-14: primary_diagnosis_7_8 | donor_3 | program_1
  - 15-16: primary_diagnosis_9_10 | donor_4 | program_1
  - 17-18: primary_diagnosis_11_12 | donor_5_6 | program_1
  - 19-22: primary_diagnosis_13_16 | donor_7_10 | program_2

- 7 Chemotherapy
  - 1-3: treatment_1 | donor_1 | program_1
  - 4-5: treatment_2 | donor_1 | program_1
  - 6-7: treatment_3_4 | donor_1 | program_1

- 7 HormoneTherapy
  - 1-3: treatment_5 | donor_1 | program_1
  - 4-5: treatment_6 | donor_1 | program_1
  - 6-7: treatment_7_8 | donor_1 | program_1

- 5 Radiation
  - 1-2: treatment_9_10 | donor_2 | program_1
  - 3-4: treatment_11_12 | donor_2 | program_1
  - 5: treatment_13 | donor_3 | program_1

- 7 Immunotherapy
  - 1-3: treatment_14 | donor_3 | program_1
  - 4-5: treatment_15 | donor_4 | program_1
  - 6-7: treatment_16_17 | donor_4_5 | program_1

- 5 Surgery
  - 1: treatment_18 | specimen_18 | donor_6 | program_1
  - 2-5: treatment_19_22 | donor_7_10 | program_2

- 28 FollowUp
  - 1-3: treatment_1 | primary_diagnosis_1 | donor_1 | program_1
  - 4-6: treatment_2 | primary_diagnosis_1 | donor_1 | program_1
  - 7-8: treatment_3 | primary_diagnosis_1 | donor_1 | program_1
  - 9-10: treatment_4 | primary_diagnosis_2 | donor_1 | program_1
  - 11-12: treatment_5_6 | primary_diagnosis_2 | donor_1 | program_1
  - 13-14: treatment_7_8 | primary_diagnosis_3 | donor_1 | program_1
  - 15-16: treatment_9_10 | primary_diagnosis_4 | donor_2 | program_1
  - 17-18: treatment_11_12 | primary_diagnosis_5_6 | donor_2 | program_1
  - 19-20: treatment_13_14: primary_diagnosis_7_8 | donor_3 | program_1
  - 21-22: treatment_15_16: primary_diagnosis_9_10 | donor_4 | program_1
  - 23-24: treatment_17_18: primary_diagnosis_11_12 | donor_5_6 | program_1
  - 25-28: treatment_19_22: primary_diagnosis_13_16 | donor_7_10 | program_2

- 12 Biomarker
  - 1-3: follow_up_1 | specimen_1 | donor_1 | program_1
  - 4-6: follow_up_2 | donor_1 | program_1
  - 7-8: specimen_1 | treatment_1 | donor_1 | program_1
  - 9-10: treatment_2 | donor_1 | program_1
  - 11-11: primary_diagnosis_4 | donor_2 | program_1
  - 12-12: donor_3 | program_1

- 14 Comorbidity
  - 1-3: donor_1 | program_1
  - 4-6: donor_2 | program_1
  - 7-8: donor_3 | program_1
  - 9-10: donor_4 | program_1
  - 11-12: donor_5_6 | program_1
  - 13-14: donor_7_8 | program_2

```mermaid
---
title: 10 Donors and 2 Programs
---
graph LR;  
  Donor_1_6 --> Program_1;  
  Donor_7_10 --> Program_2;
```

```mermaid
---
title: 16 PrimaryDiagnosis
---
graph LR;  
  PrimaryDiagnosis_1_3 --> Donor_1 --> Program_1;  
  PrimaryDiagnosis_4_6 --> Donor_2 --> Program_1;  
  PrimaryDiagnosis_7_8 --> Donor_3 --> Program_1;  
  PrimaryDiagnosis_9_10 --> Donor_4 --> Program_1;
  PrimaryDiagnosis_11_12 --> Donor_5_6 --> Program_1;
  PrimaryDiagnosis_13_16 --> Donor_7_10 --> Program_2;
```

```mermaid
---
title: 22 Specimens
---
graph LR;  
  Specimen_1_3 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  Specimen_4_6 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1;  
  Specimen_7_8 --> PrimaryDiagnosis_3 --> Donor_1 --> Program_1;  
  Specimen_9_10 --> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;  
  Specimen_11_12 --> PrimaryDiagnosis_5_6 --> Donor_2 --> Program_1;  
  Specimen_13_14 --> PrimaryDiagnosis_7_8 --> Donor_3 --> Program_1;  
  Specimen_15_16 --> PrimaryDiagnosis_9_10 --> Donor_4 --> Program_1;  
  Specimen_17_18 --> PrimaryDiagnosis_11_12 --> Donor_5_6 --> Program_1;  
  Specimen_19_22 --> PrimaryDiagnosis_13_16 --> Donor_7_10 --> Program_2;
```

```mermaid
---
title: 28 SampleRegistration
---
graph LR;  
  SampleRegistration_1_3 --> Specimen_1 --> Donor_1 --> Program_1;  
  SampleRegistration_4_6 --> Specimen_2 --> Donor_1 --> Program_1;  
  SampleRegistration_7_8 --> Specimen_3 --> Donor_1 --> Program_1;  
  SampleRegistration_9_10 --> Specimen_4 --> Donor_1 --> Program_1;  
  SampleRegistration_11_12 --> Specimen_5_6 --> Donor_1 --> Program_1;  
  SampleRegistration_13_14 --> Specimen_7_8 --> Donor_1 --> Program_1;  
  SampleRegistration_15_16 --> Specimen_9_10 --> Donor_2 --> Program_1;  
  SampleRegistration_17_18 --> Specimen_11_12 --> Donor_2 --> Program_1;  
  SampleRegistration_19_20 --> Specimen_13_14 --> Donor_3 --> Program_1;  
  SampleRegistration_21_22 --> Specimen_15_16 --> Donor_4 --> Program_1;  
  SampleRegistration_23_24 --> Specimen_17_18 --> Donor_5_6 --> Program_1;  
  SampleRegistration_25_28 --> Specimen_19_22 --> Donor_7_10 --> Program_2;
```

```mermaid
---
title: 22 Treatment
---
graph LR;  
  Treatment_1_3 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  Treatment_4_6 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1;  
  Treatment_7_8 --> PrimaryDiagnosis_3 --> Donor_1 --> Program_1;  
  Treatment_9_10 --> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;  
  Treatment_11_12 --> PrimaryDiagnosis_5_6 --> Donor_2 --> Program_1;  
  Treatment_13_14 --> PrimaryDiagnosis_7_8 --> Donor_3 --> Program_1;  
  Treatment_15_16 --> PrimaryDiagnosis_9_10 --> Donor_4 --> Program_1;  
  Treatment_17_18 --> PrimaryDiagnosis_11_12 --> Donor_5_6 --> Program_1;  
  Treatment_19_22 --> PrimaryDiagnosis_13_16 --> Donor_7_10 --> Program_2;
```

```mermaid
---
title: 7 Chemotherapy
---
graph LR;  
  Chemotherapy_1_3 --> Treatment_1 --> Donor_1 --> Program_1;  
  Chemotherapy_4_5 --> Treatment_2 --> Donor_1 --> Program_1;  
  Chemotherapy_6_7 --> Treatment_3_4 --> Donor_1 --> Program_1;
```

```mermaid
---
title: 7 HormoneTherapy
---
graph LR;  
  HormoneTherapy_1_3 --> Treatment_5 --> Donor_1 --> Program_1;  
  HormoneTherapy_4_5 --> Treatment_6 --> Donor_1 --> Program_1;  
  HormoneTherapy_6_7 --> Treatment_7_8 --> Donor_1 --> Program_1;
```

```mermaid
---
title: 5 Radiation
---
graph LR;  
  Radiation_1_2 --> Treatment_9_10 --> Donor_2 --> Program_1;  
  Radiation_3_4 --> Treatment_11_12 --> Donor_2 --> Program_1;  
  Radiation_5 --> Treatment_13 --> Donor_3 --> Program_1;
```

```mermaid
---
title: 7 Immunotherapy
---
graph LR;  
  Immunotherapy_1_3 --> Treatment_14 --> Donor_3 --> Program_1;  
  Immunotherapy_4_5 --> Treatment_15 --> Donor_4 --> Program_1;  
  Immunotherapy_6_7 --> Treatment_16_17 --> Donor_4_5 --> Program_1;
```

```mermaid
---
title: 5 Surgery
---
graph LR;  
  Surgery_1_2 --> Treatment_18 --> Donor_6 --> Program_1;  
  Surgery_3_5 --> Treatment_19_22 --> Donor_7_10 --> Program_2;
```

```mermaid
---
title: 28 FollowUp
---
graph LR;  
  FollowUp_1_3 --> Treatment_1 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  FollowUp_4_6 --> Treatment_2 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  FollowUp_7_8 --> Treatment_3 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  FollowUp_9_10 --> Treatment_4 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1;  
  FollowUp_11_12 --> Treatment_5_6 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1;  
  FollowUp_13_14 --> Treatment_7_8 --> PrimaryDiagnosis_3 --> Donor_1 --> Program_1;  
  FollowUp_15_16 --> Treatment_9_10 --> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;  
  FollowUp_17_18 --> Treatment_11_12 --> PrimaryDiagnosis_5_6 --> Donor_2 --> Program_1;  
  FollowUp_19_20 --> Treatment_13_14 --> PrimaryDiagnosis_7_8 --> Donor_3 --> Program_1;  
  FollowUp_21_22 --> Treatment_15_16 --> PrimaryDiagnosis_9_10 --> Donor_4 --> Program_1;  
  FollowUp_23_24 --> Treatment_17_18 --> PrimaryDiagnosis_11_12 --> Donor_5_6 --> Program_1;  
  FollowUp_25_28 --> Treatment_19_22 --> PrimaryDiagnosis_13_16 --> Donor_7_10 --> Program_2;
```

```mermaid
---
title: 12 Biomarker
---
graph LR;  
  Biomarker_1_3 --> FollowUp_1 --> Specimen_1 --> Donor_1 --> Program_1;
  Biomarker_4_6 --> FollowUp_2 ----> Donor_1 --> Program_1;
  Biomarker_7_8 ---> Specimen_1 --> Treatment_1 --> Donor_1 --> Program_1;
  Biomarker_9_10 ----> Treatment_2 --> Donor_1 --> Program_1;
  Biomarker_11_11 ----> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;
  Biomarker_12_12 -----> Donor_3 --> Program_1;
```

```mermaid
---
title: 14 Comorbidity
---
graph LR;  
  Comorbidity_1_3 --> Donor_1 --> Program_1;  
  Comorbidity_4_6 --> Donor_2 --> Program_1;  
  Comorbidity_7_8 --> Donor_3 --> Program_1;  
  Comorbidity_9_10 --> Donor_4 --> Program_1;  
  Comorbidity_11_12 --> Donor_5_6 --> Program_1;  
  Comorbidity_13_14 --> Donor_7_8 --> Program_2;
```
