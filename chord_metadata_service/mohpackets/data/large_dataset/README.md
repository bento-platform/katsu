# Large dataset relationships

This is a diagram of the synthetic relationships between the models in the dataset.

```mermaid
---
title: 1000 Donors and 10 Programs
---
graph LR;  
  Donor_1_100 --> Program_1;
  Donor_101_200 --> Program_2;  
  Donor_201_300 --> Program_3;  
  Donor_301_400 --> Program_4;  
  Donor_401_500 --> Program_5;  
  Donor_501_600 --> Program_6;  
  Donor_601_700 --> Program_7;  
  Donor_701_800 --> Program_8;  
  Donor_801_900 --> Program_9;
  Donor_901_1000 --> Program_10;    
 
```

---

```mermaid
---
title: 2000 PrimaryDiagnoses
---
graph LR;  
  PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  PrimaryDiagnosis_201_400 --> Donor_101_200 --> Program_2;  
  PrimaryDiagnosis_401_600 --> Donor_201_300 --> Program_3;  
  PrimaryDiagnosis_601_800 --> Donor_301_400 --> Program_4;  
  PrimaryDiagnosis_801_1000 --> Donor_401_500 --> Program_5;  
  PrimaryDiagnosis_1001_1200 --> Donor_501_600 --> Program_6;  
  PrimaryDiagnosis_1201_1400 --> Donor_601_700 --> Program_7;  
  PrimaryDiagnosis_1401_1600 --> Donor_701_800 --> Program_8;  
  PrimaryDiagnosis_1601_1800 --> Donor_801_900 --> Program_9;
  PrimaryDiagnosis_1801_2000 --> Donor_901_1000 --> Program_10;  
```

---

```mermaid
---
title: 2000 Specimens
---
graph LR;  
  Specimen_1_200 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  Specimen_201_400 --> PrimaryDiagnosis_201_400 --> Donor_101_200 --> Program_2;  
  Specimen_401_600 --> PrimaryDiagnosis_401_600 --> Donor_201_300 --> Program_3;  
  Specimen_601_800 --> PrimaryDiagnosis_601_800 --> Donor_301_400 --> Program_4;  
  Specimen_801_1000 --> PrimaryDiagnosis_801_1000 --> Donor_401_500 --> Program_5;  
  Specimen_1001_1200 --> PrimaryDiagnosis_1001_1200 --> Donor_501_600 --> Program_6;  
  Specimen_1201_1400 --> PrimaryDiagnosis_1201_1400 --> Donor_601_700 --> Program_7;  
  Specimen_1401_1600 --> PrimaryDiagnosis_1401_1600 --> Donor_701_800 --> Program_8;  
  Specimen_1601_1800 --> PrimaryDiagnosis_1601_1800 --> Donor_801_900 --> Program_9;
  Specimen_1801_2000 --> PrimaryDiagnosis_1801_2000 --> Donor_901_1000 --> Program_10;  

```

---

```mermaid
---
title: 2000 SampleRegistrations
---
graph LR;  
  SampleRegistration_1_200 --> Specimen_1_200 --> Donor_1_100 --> Program_1;
  SampleRegistration_201_400 --> Specimen_201_400 --> Donor_101_200 --> Program_2;  
  SampleRegistration_401_600 --> Specimen_401_600 --> Donor_201_300 --> Program_3;  
  SampleRegistration_601_800 --> Specimen_601_800 --> Donor_301_400 --> Program_4;  
  SampleRegistration_801_1000 --> Specimen_801_1000 --> Donor_401_500 --> Program_5;  
  SampleRegistration_1001_1200 --> Specimen_1001_1200 --> Donor_501_600 --> Program_6;  
  SampleRegistration_1201_1400 --> Specimen_1201_1400 --> Donor_601_700 --> Program_7;  
  SampleRegistration_1401_1600 --> Specimen_1401_1600 --> Donor_701_800 --> Program_8;  
  SampleRegistration_1601_1800 --> Specimen_1601_1800 --> Donor_801_900 --> Program_9;
  SampleRegistration_1801_2000 --> Specimen_1801_2000 --> Donor_901_1000 --> Program_10;  
```

---

```mermaid
---
title: 4000 Treatments
---
graph LR;  
  Treatment_1_400 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  Treatment_401_800 --> PrimaryDiagnosis_201_400 --> Donor_101_200 --> Program_2;  
  Treatment_801_1200 --> PrimaryDiagnosis_401_600 --> Donor_201_300 --> Program_3;  
  Treatment_1201_1600 --> PrimaryDiagnosis_601_800 --> Donor_301_400 --> Program_4;  
  Treatment_1601_2000 --> PrimaryDiagnosis_801_1000 --> Donor_401_500 --> Program_5;  
  Treatment_2001_2400 --> PrimaryDiagnosis_1001_1200 --> Donor_501_600 --> Program_6;  
  Treatment_2401_2800 --> PrimaryDiagnosis_1201_1400 --> Donor_601_700 --> Program_7;  
  Treatment_2801_3200 --> PrimaryDiagnosis_1401_1600 --> Donor_701_800 --> Program_8;  
  Treatment_3201_3600 --> PrimaryDiagnosis_1601_1800 --> Donor_801_900 --> Program_9;
  Treatment_3601_4000 --> PrimaryDiagnosis_1801_2000 --> Donor_901_1000 --> Program_10;  
```

---

```mermaid
---
title: 800 Chemotherapies
---
graph LR;  
  Chemotherapy_1_400 -->  Treatment_1_400 --> Donor_1_100 --> Program_1;
  Chemotherapy_401_800 -->  Treatment_401_800 --> Donor_101_200 --> Program_2; 
```

---

```mermaid
---
title: 800 HormoneTherapies
---
graph LR;  
  HormoneTherapy_1_400 --> Treatment_801_1200 --> Donor_201_300 --> Program_3;  
  HormoneTherapy_401_800 --> Treatment_1201_1600 --> Donor_301_400 --> Program_4;  

```

---

```mermaid
---
title: 800 Immunotherapies
---
graph LR;  
  Immunotherapy_1_400 --> Treatment_1601_2000 -->  Donor_401_500 --> Program_5;  
  Immunotherapy_401_800 -->  Treatment_2001_2400 --> Donor_501_600 --> Program_6;  
```

---

```mermaid
---
title: 800 Radiations
---
graph LR;  
  Radiation_1_400 --> Treatment_2401_2800 --> Donor_601_700 --> Program_7;  
  Radiation_401_800 --> Treatment_2801_3200 --> Donor_701_800 --> Program_8;  
```

---

```mermaid
---
title: 800 Surgeries
---
graph LR;  
  Surgery_1_400 --> Treatment_3201_3600 --> Donor_801_900 --> Program_9;
  Surgery_401_800 --> Treatment_3601_4000 --> Donor_901_1000 --> Program_10;  
```

---

```mermaid
---
title: 4000 FollowUps
---
graph LR;  
  FollowUp_1_400 --> Treatment_1_400 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  FollowUp_401_800 --> Treatment_401_800 --> PrimaryDiagnosis_201_400 --> Donor_101_200 --> Program_2;  
  FollowUp_801_1200 --> Treatment_801_1200 --> PrimaryDiagnosis_401_600 --> Donor_201_300 --> Program_3;  
  FollowUp_1201_1600 --> Treatment_1201_1600 --> PrimaryDiagnosis_601_800 --> Donor_301_400 --> Program_4;  
  FollowUp_1601_2000 --> Treatment_1601_2000 --> PrimaryDiagnosis_801_1000 --> Donor_401_500 --> Program_5;  
  FollowUp_2001_2400 --> Treatment_2001_2400 --> PrimaryDiagnosis_1001_1200 --> Donor_501_600 --> Program_6;  
  FollowUp_2401_2800 --> Treatment_2401_2800 --> PrimaryDiagnosis_1201_1400 --> Donor_601_700 --> Program_7;  
  FollowUp_2801_3200 --> Treatment_2801_3200 ---> Donor_701_800 --> Program_8;  
  FollowUp_3201_3600 ---> PrimaryDiagnosis_1601_1800 --> Donor_801_900 --> Program_9;
  FollowUp_3601_4000 ----> Donor_901_1000 --> Program_10;  
```

---

```mermaid
---
title: 3600 Biomarkers
---
graph LR;  
  Biomarker_1_400 --> FollowUp_1_400 --> Treatment_1_400 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  Biomarker_401_800 --> Treatment_401_800--> PrimaryDiagnosis_201_400 --> Donor_101_200 --> Program_2;  
  Biomarker_801_1200 --> PrimaryDiagnosis_401_600 --> Donor_201_300 --> Program_3;  
  Biomarker_1201_1600 --> Donor_301_400 --> Program_4;  
  Biomarker_1601_2000 --> FollowUp_1601_2000 --> Treatment_1601_2000 --> Donor_401_500 --> Program_5;  
  Biomarker_2001_2400 --> Treatment_2001_2400 --> Donor_501_600 --> Program_6;  
  Biomarker_2401_2800 --> Specimen_1201_1400 --> PrimaryDiagnosis_1201_1400 --> Donor_601_700 --> Program_7;  
  Biomarker_2801_3200 --> Specimen_1401_1600  --> Donor_701_800 --> Program_8;  
  Biomarker_3201_3600 --> FollowUp_3201_3600--> Treatment_3201_3600 --> Specimen_1601_1800 --> PrimaryDiagnosis_1601_1800 --> Donor_801_900 --> Program_9;
```

---

```mermaid
---
title: 1000 Comorbidities
---
graph LR;  
  Comorbidity_1_200 --> Donor_1_100 --> Program_1;
  Comorbidity_201_400 --> Donor_101_200 --> Program_2;  
  Comorbidity_401_600 --> Donor_201_300 --> Program_3;  
  Comorbidity_601_800 --> Donor_301_400 --> Program_4;  
  Comorbidity_801_1000 --> Donor_401_500 --> Program_5;  
```
