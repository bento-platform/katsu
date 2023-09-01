# Small dataset relationships

This is a diagram of the synthetic relationships between the models in the dataset.

```mermaid
---
title: 10 Donors and 2 Programs
---
graph LR;  
  Donor_1_6 --> Program_1;  
  Donor_7_10 --> Program_2;
```

---

```mermaid
---
title: 16 PrimaryDiagnoses
---
graph LR;  
  PrimaryDiagnosis_1_3 --> Donor_1 --> Program_1;  
  PrimaryDiagnosis_4_6 --> Donor_2 --> Program_1;  
  PrimaryDiagnosis_7_8 --> Donor_3 --> Program_1;  
  PrimaryDiagnosis_9_10 --> Donor_4 --> Program_1;
  PrimaryDiagnosis_11_12 --> Donor_5_6 --> Program_1;
  PrimaryDiagnosis_13_16 --> Donor_7_10 --> Program_2;
```

---

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

---

```mermaid
---
title: 28 SampleRegistrations
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

---

```mermaid
---
title: 25 Treatments
---
graph LR;  
  Treatment_1_3 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  Treatment_4_6 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1;  
  Treatment_7_9 --> PrimaryDiagnosis_3 --> Donor_1 --> Program_1;  
  Treatment_10_11 --> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;  
  Treatment_12_13 --> PrimaryDiagnosis_5 --> Donor_2 --> Program_1;  
  Treatment_14_15 --> PrimaryDiagnosis_6 --> Donor_2 --> Program_1; 
  Treatment_16_17 --> PrimaryDiagnosis_7_8 --> Donor_3 --> Program_1;  
  Treatment_18_19 --> PrimaryDiagnosis_9_10 --> Donor_4 --> Program_1;  
  Treatment_20_21 --> PrimaryDiagnosis_11_12 --> Donor_5_6 --> Program_1;  
  Treatment_22_25 --> PrimaryDiagnosis_13_16 --> Donor_7_10 --> Program_2;
```

---

```mermaid
---
title: 15 Chemotherapies
---
graph LR;  
  Chemotherapy_1_3 --> Treatment_1 --> Donor_1 --> Program_1;  
  Chemotherapy_4_6 --> Treatment_2 --> Donor_1 --> Program_1;  
  Chemotherapy_7_9 --> Treatment_3 --> Donor_1 --> Program_1;
  Chemotherapy_10_11 --> Treatment_4 --> Donor_1 --> Program_1;
  Chemotherapy_12_13 --> Treatment_5 --> Donor_1 --> Program_1;
  Chemotherapy_14_15 --> Treatment_6_7 --> Donor_1 --> Program_1;
```

---

```mermaid
---
title: 14 HormoneTherapies
---
graph LR;  
  HormoneTherapy_1_3 --> Treatment_8 --> Donor_1 --> Program_1;  
  HormoneTherapy_4_6 --> Treatment_9 --> Donor_1 --> Program_1;  
  HormoneTherapy_7_9 --> Treatment_10 --> Donor_2 --> Program_1;  
  HormoneTherapy_10_11 --> Treatment_11 --> Donor_2 --> Program_1;  
  HormoneTherapy_12_13 --> Treatment_12 --> Donor_2 --> Program_1;  
  HormoneTherapy_14 --> Treatment_13 --> Donor_2 --> Program_1;   
```

---

```mermaid
---
title: 11 Immunotherapies
---
graph LR;  
  Immunotherapy_1_3 --> Treatment_14 --> Donor_2 --> Program_1; 
  Immunotherapy_4_6 --> Treatment_15 --> Donor_2 --> Program_1;  
  Immunotherapy_7_8 --> Treatment_16 --> Donor_3 --> Program_1;  
  Immunotherapy_9_10 --> Treatment_17 --> Donor_3 --> Program_1;  
  Immunotherapy_11 --> Treatment_18 --> Donor_4 --> Program_1;   
```

---

```mermaid
---
title: 4 Radiations
---
graph LR;  
  Radiation_1_3 --> Treatment_19_21 --> Donor_4_6 --> Program_1;  
  Radiation_4 --> Treatment_22 --> Donor_7 --> Program_2; 
```

---

```mermaid
---
title: 3 Surgeries
---
graph LR;  
  Surgery_1_3 --> Treatment_23_25 --> Donor_8_10 --> Program_2;  
```

---

```mermaid
---
title: 34 FollowUps
---
graph LR;  
  FollowUp_1_3 --> Treatment_1 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  FollowUp_4_6 --> Treatment_2 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  FollowUp_7_9 --> Treatment_3 --> PrimaryDiagnosis_1 --> Donor_1 --> Program_1;  
  FollowUp_10_11 --> Treatment_4 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1; 
  FollowUp_12_13 --> Treatment_5 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1; 
  FollowUp_14_15 --> Treatment_6 --> PrimaryDiagnosis_2 --> Donor_1 --> Program_1; 
  FollowUp_16_18 --> Treatment_7_9 --> PrimaryDiagnosis_3 --> Donor_1 --> Program_1;
  FollowUp_19_20 --> Treatment_10_11 --> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;  
  FollowUp_21_22 --> Treatment_12_13 --> PrimaryDiagnosis_5 --> Donor_2 --> Program_1;  
  FollowUp_23_24 --> Treatment_14_15 --> PrimaryDiagnosis_6 --> Donor_2 --> Program_1; 
  FollowUp_25_26 --> Treatment_16_17 --> PrimaryDiagnosis_7_8 --> Donor_3 --> Program_1;  
  FollowUp_27_28 --> Treatment_18_19 --> PrimaryDiagnosis_9_10 --> Donor_4 --> Program_1;  
  FollowUp_29_30 --> Treatment_20_21 --> PrimaryDiagnosis_11_12 --> Donor_5_6 --> Program_1;  
  FollowUp_31_34 --> Treatment_22_25 --> PrimaryDiagnosis_13_16 --> Donor_7_10 --> Program_2;
```

---

```mermaid
---
title: 15 Biomarkers
---
graph LR;  
  Biomarker_1_5 ------> Donor_1 --> Program_1;
  Biomarker_6_9 -----> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;
  Biomarker_10_12 ----> Specimen_13 ---> Donor_3 --> Program_1;
  Biomarker_13_14 ---> Treatment_15 ----> Donor_4 --> Program_1;
  Biomarker_15 --> FollowUp_31 -----> Donor_7 --> Program_2;
```

---

```mermaid
---
title: 14 Comorbidities
---
graph LR;  
  Comorbidity_1_3 --> Donor_1 --> Program_1;  
  Comorbidity_4_6 --> Donor_2 --> Program_1;  
  Comorbidity_7_8 --> Donor_3 --> Program_1;  
  Comorbidity_9_10 --> Donor_4 --> Program_1;  
  Comorbidity_11_12 --> Donor_5_6 --> Program_1;  
  Comorbidity_13_14 --> Donor_7_8 --> Program_2;
```

---

```mermaid
---
title: 8 Exposures
---
graph LR;  
  Exposure_1_3 --> Donor_1 --> Program_1;  
  Exposure_4_5 --> Donor_2 --> Program_1;
  Exposure_6 --> Donor_3 --> Program_1;    
  Exposure_7_8 --> Donor_7_8 --> Program_2;
```
