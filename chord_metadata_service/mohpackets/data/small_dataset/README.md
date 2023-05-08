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
title: 22 Treatments
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

---

```mermaid
---
title: 7 Chemotherapies
---
graph LR;  
  Chemotherapy_1_3 --> Treatment_1 --> Donor_1 --> Program_1;  
  Chemotherapy_4_5 --> Treatment_2 --> Donor_1 --> Program_1;  
  Chemotherapy_6_7 --> Treatment_3_4 --> Donor_1 --> Program_1;
```

---

```mermaid
---
title: 7 HormoneTherapies
---
graph LR;  
  HormoneTherapy_1_3 --> Treatment_5 --> Donor_1 --> Program_1;  
  HormoneTherapy_4_5 --> Treatment_6 --> Donor_1 --> Program_1;  
  HormoneTherapy_6_7 --> Treatment_7_8 --> Donor_1 --> Program_1;
```

---

```mermaid
---
title: 5 Radiations
---
graph LR;  
  Radiation_1_2 --> Treatment_9_10 --> Donor_2 --> Program_1;  
  Radiation_3_4 --> Treatment_11_12 --> Donor_2 --> Program_1;  
  Radiation_5 --> Treatment_13 --> Donor_3 --> Program_1;
```

---

```mermaid
---
title: 7 Immunotherapies
---
graph LR;  
  Immunotherapy_1_3 --> Treatment_14 --> Donor_3 --> Program_1;  
  Immunotherapy_4_5 --> Treatment_15 --> Donor_4 --> Program_1;  
  Immunotherapy_6_7 --> Treatment_16_17 --> Donor_4_5 --> Program_1;
```

---

```mermaid
---
title: 5 Surgeries
---
graph LR;  
  Surgery_1_2 --> Treatment_18 --> Donor_6 --> Program_1;  
  Surgery_3_5 --> Treatment_19_22 --> Donor_7_10 --> Program_2;
```

---

```mermaid
---
title: 28 FollowUps
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

---

```mermaid
---
title: 12 Biomarkers
---
graph LR;  
  Biomarker_1_3 --> FollowUp_1 --> Specimen_1 --> Donor_1 --> Program_1;
  Biomarker_4_6 --> FollowUp_2 ----> Donor_1 --> Program_1;
  Biomarker_7_8 ---> Specimen_1 --> Treatment_1 --> Donor_1 --> Program_1;
  Biomarker_9_10 ----> Treatment_2 --> Donor_1 --> Program_1;
  Biomarker_11_11 ----> PrimaryDiagnosis_4 --> Donor_2 --> Program_1;
  Biomarker_12_12 -----> Donor_3 --> Program_1;
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
