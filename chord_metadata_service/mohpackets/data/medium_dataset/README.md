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
title: 1000 Chemotherapies
---
graph LR; 
  Chemotherapy_1_800 --> Treatment_1_80 --> Donor_1_40 --> Program_1;  
  Chemotherapy_801_960 --> Treatment_81_121 --> Donor_1_40 --> Program_1;  
  Chemotherapy_961_1000 --> Treatment_121_160 --> Donor_1_40 --> Program_1;
```

---

```mermaid
---
title: 1000 HormoneTherapies
---
graph LR;  
  HormoneTherapy_1_800 --> Treatment_161_240 --> Donor_1_40 --> Program_1;  
  HormoneTherapy_801_960 --> Treatment_241_280 --> Donor_1_40 --> Program_1;  
  HormoneTherapy_961_1000 --> Treatment_281_320 --> Donor_1_40 --> Program_1;
```

---

```mermaid
---
title: 1000 Immunotherapies
---
graph LR;  
  Immunotherapy_1_800 --> Treatment_321_400 --> Donor_1_40 --> Program_1;  
  Immunotherapy_801_960 --> Treatment_401_440 --> Donor_1_40 --> Program_1;  
  Immunotherapy_961_1000 --> Treatment_441_480 --> Donor_1_40 --> Program_1;
```

---

```mermaid
---
title: 280 Radiations
---
graph LR;  
  Radiation_1_160 --> Treatment_481_640 --> Donor_1_40 --> Program_1;
  Radiation_161_280 --> Treatment_641_760 --> Donor_41_70 --> Program_2;
```

---

```mermaid
---
title: 240 Surgeries
---
graph LR;  
  Surgery_1_150 --> Treatment_761_910 --> Donor_41_70 --> Program_2;
  Surgery_151_230 --> Treatment_911_990 --> Donor_71_90 --> Program_3;
  Surgery_231_240 --> Treatment_991_1000 --> Donor_91_100 --> Program_4;
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
title: 1000 Biomarkers
---
graph LR;  
  Biomarker_1_80 ------> Donor_1_40 --> Program_1;
  Biomarker_81_400 -----> PrimaryDiagnosis_1_160 --> Donor_1_40 --> Program_1;
  Biomarker_401_670 ----> Specimen_641_910 ---> Donor_41_70 --> Program_2;
  Biomarker_671_910 ---> Treatment_911_990 ----> Donor_71_90 --> Program_3;
  Biomarker_911_1000 --> FollowUp_991_1000 -----> Donor_91_100 --> Program_4;
```

---

```mermaid
---
title: 1000 Comorbidities
---
graph LR;  
  Exposure_1_600 --> Donor_1_40 --> Program_1;
  Exposure_601_900 --> Donor_41_70 --> Program_2; 
  Exposure_901_1000 --> Donor_91_100 --> Program_4; 
```

```mermaid
---
title: 1000 Exposures
---
graph LR;  
  Exposure_1_400 --> Donor_1_40 --> Program_1;
  Exposure_401_1000 --> Donor_41_70 --> Program_2; 
```
