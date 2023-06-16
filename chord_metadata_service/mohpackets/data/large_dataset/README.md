# Large dataset relationships

This is a diagram of the synthetic relationships between the models in the dataset.

```mermaid
---
title: 5000 Donors and 10 Programs
---
graph LR;  
  Donor_1_500 --> Program_1;
  Donor_501_1000 --> Program_2;  
  Donor_1001_1500 --> Program_3;  
  Donor_1501_2000 --> Program_4;  
  Donor_2001_2500 --> Program_5;  
  Donor_2501_3000 --> Program_6;  
  Donor_3001_3500 --> Program_7;  
  Donor_3501_4000 --> Program_8;  
  Donor_4001_4500 --> Program_9;
  Donor_4501_5000 --> Program_10;    
 
```

---

```mermaid
---
title: 10000 PrimaryDiagnoses
---
graph LR;  
  PrimaryDiagnosis_1_1000 --> Donor_1_500 --> Program_1;
  PrimaryDiagnosis_1001_2000 --> Donor_501_1000 --> Program_2;  
  PrimaryDiagnosis_2001_3000 --> Donor_1001_1500 --> Program_3;  
  PrimaryDiagnosis_3001_4000 --> Donor_1501_2000 --> Program_4;  
  PrimaryDiagnosis_4001_5000 --> Donor_2001_2500 --> Program_5;  
  PrimaryDiagnosis_5001_6000 --> Donor_2501_3000 --> Program_6;  
  PrimaryDiagnosis_6001_7000 --> Donor_3001_3500 --> Program_7;  
  PrimaryDiagnosis_7001_8000 --> Donor_3501_4000 --> Program_8;  
  PrimaryDiagnosis_8001_9000 --> Donor_4001_4500 --> Program_9;
  PrimaryDiagnosis_9001_10000 --> Donor_4501_5000 --> Program_10;
```

---

```mermaid
---
title: 10000 Specimens
---
graph LR;  
  Specimen_1_1000 --> PrimaryDiagnosis_1_1000 --> Donor_1_500 --> Program_1;
  Specimen_1001_2000 --> PrimaryDiagnosis_1001_2000 --> Donor_501_1000 --> Program_2;
  Specimen_2001_3000 --> PrimaryDiagnosis_2001_3000 --> Donor_1001_1500 --> Program_3;
  Specimen_3001_4000 --> PrimaryDiagnosis_3001_4000 --> Donor_1501_2000 --> Program_4;
  Specimen_4001_5000 --> PrimaryDiagnosis_4001_5000 --> Donor_2001_2500 --> Program_5;
  Specimen_5001_6000 --> PrimaryDiagnosis_5001_6000 --> Donor_2501_3000 --> Program_6;
  Specimen_6001_7000 --> PrimaryDiagnosis_6001_7000 --> Donor_3001_3500 --> Program_7;
  Specimen_7001_8000 --> PrimaryDiagnosis_7001_8000 --> Donor_3501_4000 --> Program_8;
  Specimen_8001_9000 --> PrimaryDiagnosis_8001_9000 --> Donor_4001_4500 --> Program_9;
  Specimen_9001_10000 --> PrimaryDiagnosis_9001_10000 --> Donor_4501_5000 --> Program_10;
```

---

```mermaid
---
title: 10000 SampleRegistrations
---
graph LR;  
  SampleRegistration_1_1000 --> Specimen_1_1000 --> Donor_1_500 --> Program_1;
  SampleRegistration_1001_2000 --> Specimen_1001_2000 --> Donor_501_1000 --> Program_2;
  SampleRegistration_2001_3000 --> Specimen_2001_3000 --> Donor_1001_1500 --> Program_3;
  SampleRegistration_3001_4000 --> Specimen_3001_4000 --> Donor_1501_2000 --> Program_4;
  SampleRegistration_4001_5000 --> Specimen_4001_5000 --> Donor_2001_2500 --> Program_5;
  SampleRegistration_5001_6000 --> Specimen_5001_6000 --> Donor_2501_3000 --> Program_6;
  SampleRegistration_6001_7000 --> Specimen_6001_7000 --> Donor_3001_3500 --> Program_7;
  SampleRegistration_7001_8000 --> Specimen_7001_8000 --> Donor_3501_4000 --> Program_8;
  SampleRegistration_8001_9000 --> Specimen_8001_9000 --> Donor_4001_4500 --> Program_9;
  SampleRegistration_9001_10000 --> Specimen_9001_10000 --> Donor_4501_5000 --> Program_10;
  
```

---

```mermaid
---
title: 20000 Treatments
---
graph LR;  
  Treatment_1_2000 --> PrimaryDiagnosis_1_1000 --> Donor_1_500 --> Program_1;
  Treatment_2001_4000 --> PrimaryDiagnosis_1001_2000 --> Donor_501_1000 --> Program_2;
  Treatment_4001_6000 --> PrimaryDiagnosis_2001_3000 --> Donor_1001_1500 --> Program_3;
  Treatment_6001_8000 --> PrimaryDiagnosis_3001_4000 --> Donor_1501_2000 --> Program_4;
  Treatment_8001_10000 --> PrimaryDiagnosis_4001_5000 --> Donor_2001_2500 --> Program_5;
  Treatment_10001_12000 --> PrimaryDiagnosis_5001_6000 --> Donor_2501_3000 --> Program_6;
  Treatment_12001_14000 --> PrimaryDiagnosis_6001_7000 --> Donor_3001_3500 --> Program_7;
  Treatment_14001_16000 --> PrimaryDiagnosis_7001_8000 --> Donor_3501_4000 --> Program_8;
  Treatment_16001_18000 --> PrimaryDiagnosis_8001_9000 --> Donor_4001_4500 --> Program_9;
  Treatment_18001_20000 --> PrimaryDiagnosis_9001_10000 --> Donor_4501_5000 --> Program_10;

```

---

```mermaid
---
title: 4000 Chemotherapies
---
graph LR;  
  Chemotherapy_1_2000 --> Treatment_1_2000 --> Donor_1_500 --> Program_1;
  Chemotherapy_2001_4000 --> Treatment_2001_4000 --> Donor_501_1000 --> Program_2;
```

---

```mermaid
---
title: 4000 HormoneTherapies
---
graph LR;  
  HormoneTherapy_1_2000 --> Treatment_4001_6000 --> Donor_1001_1500 --> Program_3;  
  HormoneTherapy_2001_4000 --> Treatment_6001_8000 --> Donor_1501_2000 --> Program_4;  

```

---

```mermaid
---
title: 4000 Immunotherapies
---
graph LR;  
  Immunotherapy_1_2000 --> Treatment_8001_10000 -->  Donor_2001_2500 --> Program_5;  
  Immunotherapy_2001_4000 -->  Treatment_10001_12000 --> Donor_2501_3000 --> Program_6;  
```

---

```mermaid
---
title: 4000 Radiations
---
graph LR;  
  Radiation_1_2000 --> Treatment_12001_14000 --> Donor_3001_3500 --> Program_7;  
  Radiation_2001_4000 --> Treatment_14001_16000 --> Donor_3501_4000 --> Program_8;  
```

---

```mermaid
---
title: 4000 Surgeries
---
graph LR;  
  Surgery_1_2000 --> Treatment_16001_18000 --> Donor_4001_4500 --> Program_9;
  Surgery_2001_4000 --> Treatment_18001_20000 --> Donor_4501_5000 --> Program_10;  
```

---

```mermaid
---
title: 20000 FollowUps
---
graph LR;  
  FollowUp_1_2000 --> Treatment_1_2000 --> PrimaryDiagnosis_1_1000 --> Donor_1_500 --> Program_1;
  FollowUp_2001_4000 --> Treatment_2001_4000 --> PrimaryDiagnosis_1001_2000 --> Donor_501_1000 --> Program_2;
  FollowUp_4001_6000 --> Treatment_4001_6000 --> PrimaryDiagnosis_2001_3000 --> Donor_1001_1500 --> Program_3;
  FollowUp_6001_8000 --> Treatment_6001_8000 --> PrimaryDiagnosis_3001_4000 --> Donor_1501_2000 --> Program_4;
  FollowUp_8001_10000 --> Treatment_8001_10000 --> PrimaryDiagnosis_4001_5000 --> Donor_2001_2500 --> Program_5;
  FollowUp_10001_12000 --> Treatment_10001_12000 --> PrimaryDiagnosis_5001_6000 --> Donor_2501_3000 --> Program_6;
  FollowUp_12001_14000 --> Treatment_12001_14000 --> PrimaryDiagnosis_6001_7000 --> Donor_3001_3500 --> Program_7;
  FollowUp_14001_16000 --> Treatment_14001_16000 --> Donor_3501_4000 --> Program_8;
  FollowUp_16001_18000 --> PrimaryDiagnosis_8001_9000 --> Donor_4001_4500 --> Program_9;
  FollowUp_18001_20000 --> Donor_4501_5000 --> Program_10;

```

---

```mermaid
---
title: 18000 Biomarkers
---
graph LR;  
  Biomarker_1_2000 --> Donor_1_500 --> Program_1;
  Biomarker_2001_4000 --> PrimaryDiagnosis_1001_2000 --> Donor_501_1000 --> Program_2;
  Biomarker_4001_6000 --> Specimen_2001_3000 --> PrimaryDiagnosis_2001_3000 --> Donor_1001_1500 --> Program_3;
  Biomarker_6001_8000 --> Treatment_6001_8000 --> Specimen_3001_4000 --> PrimaryDiagnosis_3001_4000 --> Donor_1501_2000 --> Program_4;
  Biomarker_8001_10000 --> FollowUp_8001_10000 --> Treatment_8001_10000 --> Specimen_4001_5000 --> PrimaryDiagnosis_4001_5000 --> Donor_2001_2500 --> Program_5;
  Biomarker_10001_12000 --> FollowUp_10001_12000 --> Specimen_5001_6000 --> PrimaryDiagnosis_5001_6000 --> Donor_2501_3000 --> Program_6;
  Biomarker_12001_14000 --> FollowUp_12001_14000 --> Treatment_12001_14000 --> PrimaryDiagnosis_6001_7000 --> Donor_3001_3500 --> Program_7;
  Biomarker_14001_16000 --> FollowUp_14001_16000 --> Treatment_14001_16000 --> Specimen_7001_8000 --> Donor_3501_4000 --> Program_8;
  Biomarker_16001_18000 --> FollowUp_16001_18000 --> Treatment_16001_18000 --> Donor_4001_4500 --> Program_9;

```

---

```mermaid
---
title: 10000 Exposures
---
graph LR;  
  Exposure_1_1000 --> Donor_1_500 --> Program_1;
  Exposure_1001_2000 --> Donor_501_1000 --> Program_2;  
  Exposure_2001_3000 --> Donor_1001_1500 --> Program_3;  
  Exposure_3001_4000 --> Donor_1501_2000 --> Program_4;  
  Exposure_4001_5000 --> Donor_2001_2500 --> Program_5;  
  Exposure_5001_6000 --> Donor_2501_3000 --> Program_6;  
  Exposure_6001_7000 --> Donor_3001_3500 --> Program_7;  
  Exposure_7001_8000 --> Donor_3501_4000 --> Program_8;  
  Exposure_8001_9000 --> Donor_4001_4500 --> Program_9;
  Exposure_9001_10000 --> Donor_4501_5000 --> Program_10;
```

---

```mermaid
---
title: 10000 Comorbidities
---
graph LR;  
  Comorbidity_1_1000 --> Donor_1_500 --> Program_1;
  Comorbidity_1001_2000 --> Donor_501_1000 --> Program_2;  
  Comorbidity_2001_3000 --> Donor_1001_1500 --> Program_3;  
  Comorbidity_3001_4000 --> Donor_1501_2000 --> Program_4;  
  Comorbidity_4001_5000 --> Donor_2001_2500 --> Program_5;  
  Comorbidity_5001_6000 --> Donor_2501_3000 --> Program_6;  
  Comorbidity_6001_7000 --> Donor_3001_3500 --> Program_7;  
  Comorbidity_7001_8000 --> Donor_3501_4000 --> Program_8;  
  Comorbidity_8001_9000 --> Donor_4001_4500 --> Program_9;
  Comorbidity_9001_10000 --> Donor_4501_5000 --> Program_10;
```
