# Medium dataset relationships

This is a diagram of the synthetic relationships between the models in the dataset.

```mermaid
---
title: 100 Donors and 4 Programs
---
graph LR;  
  Donor_1_40 --> Program_1;  
  Donor_41_70 --> Program_2;
  Donor_71_90 --> Program_3;
  Donor_91_100 --> Program_4;
```

---

```mermaid
---
title: 300 PrimaryDiagnoses
---
graph LR;  
  PrimaryDiagnosis_1_160 --> Donor_1_40 --> Program_1;
  PrimaryDiagnosis_161_250 --> Donor_41_70 --> Program_2;
  PrimaryDiagnosis_251_290 --> Donor_71_90 --> Program_3;
  PrimaryDiagnosis_291_300 --> Donor_91_100 --> Program_4; 
```

---

```mermaid
---
title: 1000 Specimens
---
graph LR;  
  Specimen_1_640 --> PrimaryDiagnosis_1_160 --> Donor_1_40 --> Program_1;
  Specimen_641_910 --> PrimaryDiagnosis_161_250 --> Donor_41_70 --> Program_2; 
  Specimen_911_990 --> PrimaryDiagnosis_251_290 --> Donor_71_90 --> Program_3;
  Specimen_991_1000 --> PrimaryDiagnosis_291_300 --> Donor_91_100 --> Program_4; 

```

---

```mermaid
---
title: 1000 SampleRegistrations
---
graph LR;  
  SampleRegistration_1_640 --> Specimen_1_640 --> Donor_1_40 --> Program_1;
  SampleRegistration_641_910 --> Specimen_641_910 --> Donor_41_70 --> Program_2; 
  SampleRegistration_911_990 --> Specimen_911_990 --> Donor_71_90 --> Program_3;
  SampleRegistration_991_1000 --> Specimen_991_1000 --> Donor_91_100 --> Program_4; 
```

---

```mermaid
---
title: 1000 Treatments
---
graph LR;  
  Treatment_1_640 --> PrimaryDiagnosis_1_160 --> Donor_1_40 --> Program_1;
  Treatment_641_910 --> PrimaryDiagnosis_161_250 --> Donor_41_70 --> Program_2; 
  Treatment_911_990 --> PrimaryDiagnosis_251_290 --> Donor_71_90 --> Program_3;
  Treatment_991_1000 --> PrimaryDiagnosis_291_300 --> Donor_91_100 --> Program_4; 
```

---

```mermaid
---
title: 560 Chemotherapies
---
graph LR;  
  Chemotherapy_1_360 --> Treatment_1_120 --> Donor_1_40 --> Program_1;  
  Chemotherapy_361_440 --> Treatment_121_200 --> Donor_1_40 --> Program_1;  
  Chemotherapy_441_560 --> Treatment_201_320 --> Donor_1_40 --> Program_1;
```

---

```mermaid
---
title: 560 HormoneTherapies
---
graph LR;  
  HormoneTherapy_1_360 --> Treatment_321_440 --> Donor_1_40 --> Program_1;  
  HormoneTherapy_361_440 --> Treatment_441_520 --> Donor_1_40 --> Program_1;  
  HormoneTherapy_441_560 --> Treatment_521_640 --> Donor_1_40 --> Program_1;  

```

---

```mermaid
---
title: 540 Immunotherapies
---
graph LR;  
  Immunotherapy_1_270 --> Treatment_641_730 --> Donor_41_70 --> Program_2;
  Immunotherapy_271_450 --> Treatment_731_820 --> Donor_41_70 --> Program_2;
  Immunotherapy_451_540 --> Treatment_821_910 --> Donor_41_70 --> Program_2;
```

---

```mermaid
---
title: 80 Radiations
---
graph LR;  
  Radiation_1_80 --> Treatment_911_990 --> Donor_71_90 --> Program_3;
```

---

```mermaid
---
title: 10 Surgeries
---
graph LR;  
  Surgery_1_10 --> Treatment_991_1000 --> Donor_91_100 --> Program_4; 
```

---

```mermaid
---
title: 1000 FollowUps
---
graph LR;  
  FollowUp_1_640 --> Treatment_1_640 --> PrimaryDiagnosis_1_160 --> Donor_1_40 --> Program_1;
  FollowUp_641_910 --> Treatment_641_910 --> PrimaryDiagnosis_161_250 --> Donor_41_70 --> Program_2; 
  FollowUp_911_990 --> Treatment_911_990 --> PrimaryDiagnosis_251_290 --> Donor_71_90 --> Program_3;
  FollowUp_991_1000 --> Treatment_991_1000 --> PrimaryDiagnosis_291_300 --> Donor_91_100 --> Program_4; 
```

---

```mermaid
---
title: 750 Biomarkers
---
graph LR;  
  Biomarker_1_640 --> FollowUp_1_640 --> Specimen_1_640 --> Donor_1_40 --> Program_1;
  Biomarker_641_720 ---> PrimaryDiagnosis_251_290 --> Donor_71_90 --> Program_3;
  Biomarker_721_750 ----> Donor_91_100 --> Program_4; 
```

---

```mermaid
---
title: 250 Comorbidities
---
graph LR;  
  Comorbidity_1_160 --> Donor_1_40 --> Program_1;
  Comorbidity_161_250 --> Donor_41_70 --> Program_2;
```

```mermaid
---
title: 220 Exposures
---
graph LR;  
  Exposure_1_160 --> Donor_1_40 --> Program_1;
  Exposure_161_220 --> Donor_71_90 --> Program_3;
```
