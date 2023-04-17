# Medium dataset relationships

This is a diagram of the synthetic relationships between the models in the dataset.

```mermaid
---
title: 1000 Donors and 10 Programs
---
graph LR;  
  Donor_1_100 --> Program_1;
  Donor_100_200 --> Program_2;  
  Donor_200_300 --> Program_3;  
  Donor_300_400 --> Program_4;  
  Donor_400_500 --> Program_5;  
  Donor_500_600 --> Program_6;  
  Donor_600_700 --> Program_7;  
  Donor_700_800 --> Program_8;  
  Donor_800_900 --> Program_9;
  Donor_900_1000 --> Program_10;    
 
```

---

```mermaid
---
title: 2000 PrimaryDiagnoses
---
graph LR;  
  PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  PrimaryDiagnosis_200_400 --> Donor_100_200 --> Program_2;  
  PrimaryDiagnosis_400_600 --> Donor_200_300 --> Program_3;  
  PrimaryDiagnosis_600_800 --> Donor_300_400 --> Program_4;  
  PrimaryDiagnosis_800_1000 --> Donor_400_500 --> Program_5;  
  PrimaryDiagnosis_1000_1200 --> Donor_500_600 --> Program_6;  
  PrimaryDiagnosis_1200_1400 --> Donor_600_700 --> Program_7;  
  PrimaryDiagnosis_1400_1600 --> Donor_700_800 --> Program_8;  
  PrimaryDiagnosis_1600_1800 --> Donor_800_900 --> Program_9;
  PrimaryDiagnosis_1800_2000 --> Donor_900_1000 --> Program_10;  
```

---

```mermaid
---
title: 2000 Specimens
---
graph LR;  
  Specimen_1_200 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  Specimen_200_400 --> PrimaryDiagnosis_200_400 --> Donor_100_200 --> Program_2;  
  Specimen_400_600 --> PrimaryDiagnosis_400_600 --> Donor_200_300 --> Program_3;  
  Specimen_600_800 --> PrimaryDiagnosis_600_800 --> Donor_300_400 --> Program_4;  
  Specimen_800_1000 --> PrimaryDiagnosis_800_1000 --> Donor_400_500 --> Program_5;  
  Specimen_1000_1200 --> PrimaryDiagnosis_1000_1200 --> Donor_500_600 --> Program_6;  
  Specimen_1200_1400 --> PrimaryDiagnosis_1200_1400 --> Donor_600_700 --> Program_7;  
  Specimen_1400_1600 --> PrimaryDiagnosis_1400_1600 --> Donor_700_800 --> Program_8;  
  Specimen_1600_1800 --> PrimaryDiagnosis_1600_1800 --> Donor_800_900 --> Program_9;
  Specimen_1800_2000 --> PrimaryDiagnosis_1800_2000 --> Donor_900_1000 --> Program_10;  

```

---

```mermaid
---
title: 2000 SampleRegistrations
---
graph LR;  
  SampleRegistration_1_200 --> Specimen_1_200 --> Donor_1_100 --> Program_1;
  SampleRegistration_200_400 --> Specimen_200_400 --> Donor_100_200 --> Program_2;  
  SampleRegistration_400_600 --> Specimen_400_600 --> Donor_200_300 --> Program_3;  
  SampleRegistration_600_800 --> Specimen_600_800 --> Donor_300_400 --> Program_4;  
  SampleRegistration_800_1000 --> Specimen_800_1000 --> Donor_400_500 --> Program_5;  
  SampleRegistration_1000_1200 --> Specimen_1000_1200 --> Donor_500_600 --> Program_6;  
  SampleRegistration_1200_1400 --> Specimen_1200_1400 --> Donor_600_700 --> Program_7;  
  SampleRegistration_1400_1600 --> Specimen_1400_1600 --> Donor_700_800 --> Program_8;  
  SampleRegistration_1600_1800 --> Specimen_1600_1800 --> Donor_800_900 --> Program_9;
  SampleRegistration_1800_2000 --> Specimen_1800_2000 --> Donor_900_1000 --> Program_10;  
```

---

```mermaid
---
title: 4000 Treatments
---
graph LR;  
  Treatment_1_400 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  Treatment_400_800 --> PrimaryDiagnosis_200_400 --> Donor_100_200 --> Program_2;  
  Treatment_800_1200 --> PrimaryDiagnosis_400_600 --> Donor_200_300 --> Program_3;  
  Treatment_1200_1600 --> PrimaryDiagnosis_600_800 --> Donor_300_400 --> Program_4;  
  Treatment_1600_2000 --> PrimaryDiagnosis_800_1000 --> Donor_400_500 --> Program_5;  
  Treatment_2000_2400 --> PrimaryDiagnosis_1000_1200 --> Donor_500_600 --> Program_6;  
  Treatment_2400_2800 --> PrimaryDiagnosis_1200_1400 --> Donor_600_700 --> Program_7;  
  Treatment_2800_3200 --> PrimaryDiagnosis_1400_1600 --> Donor_700_800 --> Program_8;  
  Treatment_3200_3600 --> PrimaryDiagnosis_1600_1800 --> Donor_800_900 --> Program_9;
  Treatment_3600_4000 --> PrimaryDiagnosis_1800_2000 --> Donor_900_1000 --> Program_10;  
```

---

```mermaid
---
title: 800 Chemotherapies
---
graph LR;  
  Chemotherapy_1_400 -->  Treatment_1_400 --> Donor_1_100 --> Program_1;
  Chemotherapy_400_800 -->  Treatment_400_800 --> Donor_100_200 --> Program_2; 
```

---

```mermaid
---
title: 800 HormoneTherapies
---
graph LR;  
  HormoneTherapy_1_400 --> Treatment_800_1200 --> Donor_200_300 --> Program_3;  
  HormoneTherapy_400_800 --> Treatment_1200_1600 --> Donor_300_400 --> Program_4;  

```

---

```mermaid
---
title: 800 Immunotherapies
---
graph LR;  
  Immunotherapy_1_400 --> Treatment_1600_2000 -->  Donor_400_500 --> Program_5;  
  Immunotherapy_400_800 -->  Treatment_2000_2400 --> Donor_500_600 --> Program_6;  
```

---

```mermaid
---
title: 800 Radiations
---
graph LR;  
  Radiation_1_400 --> Treatment_2400_2800 --> Donor_600_700 --> Program_7;  
  Radiation_400_800 --> Treatment_2800_3200 --> Donor_700_800 --> Program_8;  
```

---

```mermaid
---
title: 800 Surgeries
---
graph LR;  
  Surgery_1_400 --> Treatment_3200_3600 --> Donor_800_900 --> Program_9;
  Surgery_400_800 --> Treatment_3600_4000 --> Donor_900_1000 --> Program_10;  
```

---

```mermaid
---
title: 4000 FollowUps
---
graph LR;  
  FollowUp_1_400 --> Treatment_1_400 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  FollowUp_400_800 --> Treatment_400_800 --> PrimaryDiagnosis_200_400 --> Donor_100_200 --> Program_2;  
  FollowUp_800_1200 --> Treatment_800_1200 --> PrimaryDiagnosis_400_600 --> Donor_200_300 --> Program_3;  
  FollowUp_1200_1600 --> Treatment_1200_1600 --> PrimaryDiagnosis_600_800 --> Donor_300_400 --> Program_4;  
  FollowUp_1600_2000 --> Treatment_1600_2000 --> PrimaryDiagnosis_800_1000 --> Donor_400_500 --> Program_5;  
  FollowUp_2000_2400 --> Treatment_2000_2400 --> PrimaryDiagnosis_1000_1200 --> Donor_500_600 --> Program_6;  
  FollowUp_2400_2800 --> Treatment_2400_2800 --> PrimaryDiagnosis_1200_1400 --> Donor_600_700 --> Program_7;  
  FollowUp_2800_3200 --> Treatment_2800_3200 ---> Donor_700_800 --> Program_8;  
  FollowUp_3200_3600 ---> PrimaryDiagnosis_1600_1800 --> Donor_800_900 --> Program_9;
  FollowUp_3600_4000 ----> Donor_900_1000 --> Program_10;  
```

---

```mermaid
---
title: 3600 Biomarkers
---
graph LR;  
  Biomarker_1_400 --> FollowUp_1_400 --> Treatment_1_400 --> PrimaryDiagnosis_1_200 --> Donor_1_100 --> Program_1;
  Biomarker_400_800 --> Treatment_400_800--> PrimaryDiagnosis_200_400 --> Donor_100_200 --> Program_2;  
  Biomarker_800_1200 --> PrimaryDiagnosis_400_600 --> Donor_200_300 --> Program_3;  
  Biomarker_1200_1600 --> Donor_300_400 --> Program_4;  
  Biomarker_1600_2000 --> FollowUp_1600_2000 --> Treatment_1600_2000 --> Donor_400_500 --> Program_5;  
  Biomarker_2000_2400 --> Treatment_2000_2400 --> Donor_500_600 --> Program_6;  
  Biomarker_2400_2800 --> Specimen_1200_1400 --> PrimaryDiagnosis_1200_1400 --> Donor_600_700 --> Program_7;  
  Biomarker_2800_3200 --> Specimen_1400_1600  --> Donor_700_800 --> Program_8;  
  Biomarker_3200_3600 --> FollowUp_3200_3600--> Treatment_3200_3600 --> Specimen_1600_1800 --> PrimaryDiagnosis_1600_1800 --> Donor_800_900 --> Program_9;
```

---

```mermaid
---
title: 1000 Comorbidities
---
graph LR;  
  Comorbidity_1_200 --> Donor_1_100 --> Program_1;
  Comorbidity_200_400 --> Donor_100_200 --> Program_2;  
  Comorbidity_400_600 --> Donor_200_300 --> Program_3;  
  Comorbidity_600_800 --> Donor_300_400 --> Program_4;  
  Comorbidity_800_1000 --> Donor_400_500 --> Program_5;  
```
