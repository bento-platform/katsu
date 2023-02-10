# About

This folder contains synthetic data for **MoH models**.

The **schemas** contains the blueprints to generate the data.

The **synthetic_data** folder contains the generated data.

The **fixtures** contains the mock data in Django format (converted from synthetic data).
## How to use

To generate synthetic data, you need to create a [Mockaroo](https://www.mockaroo.com/) account and use the blueprints in the schemas folder ("RESTORE FROM BACKUP...").

Then, generate the data and download it as a JSON file.

To convert the JSON file to Django fixtures, use the following command from the root folder:

```
python chord_metadata_service/mohpackets/data/convert.py
```

To load the fixtures into local database, you can use the following command from the root folder:
```
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Program.json chord_metadata_service/mohpackets/data/fixtures/Donor.json chord_metadata_service/mohpackets/data/fixtures/PrimaryDiagnosis.json chord_metadata_service/mohpackets/data/fixtures/Specimen.json chord_metadata_service/mohpackets/data/fixtures/SampleRegistration.json chord_metadata_service/mohpackets/data/fixtures/Treatment.json chord_metadata_service/mohpackets/data/fixtures/Chemotherapy.json chord_metadata_service/mohpackets/data/fixtures/HormoneTherapy.json chord_metadata_service/mohpackets/data/fixtures/Radiation.json chord_metadata_service/mohpackets/data/fixtures/Immunotherapy.json chord_metadata_service/mohpackets/data/fixtures/Surgery.json chord_metadata_service/mohpackets/data/fixtures/FollowUp.json chord_metadata_service/mohpackets/data/fixtures/Biomarker.json chord_metadata_service/mohpackets/data/fixtures/Comorbidity.json
```

or you can do it one by one in this order:
```
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Program.json 
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Donor.json 
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/PrimaryDiagnosis.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Specimen.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/SampleRegistration.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Treatment.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Chemotherapy.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/HormoneTherapy.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Radiation.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Immunotherapy.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Surgery.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/FollowUp.json
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Biomarker.json 
python manage.py loaddata chord_metadata_service/mohpackets/data/fixtures/Comorbidity.json
```

*Note:* To clean up data (this will **delete everything** in the database, not just MoH data)

```
python manage.py flush
```

## Small dataset data:
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
   - 13-16: donor_7_8_9_10 | program_2

 - 22 Specimen
   - 1-3: primary_diagnosis_1 | donor_1 | program_1
   - 4-6: primary_diagnosis_2 | donor_1 | program_1
   - 7-8: primary_diagnosis_3 | donor_1 | program_1
   - 9-10: primary_diagnosis_4 | donor_2 | program_1
   - 11-12: primary_diagnosis_5_6 | donor_2 | program_1
   - 13-14: primary_diagnosis_7_8 | donor_3 | program_1
   - 15-16: primary_diagnosis_9_10 | donor_4 | program_1
   - 17-18: primary_diagnosis_11_12 | donor_5_6 | program_1
   - 19-22: primary_diagnosis_13_14_15_16 | donor_7_8_9_10 | program_2
        
 - 28 SampleRegistration
   - 1-3: specimen_1 | primary_diagnosis_1 | donor_1 | program_1
   - 4-6: specimen_2 | primary_diagnosis_1 | donor_1 | program_1
   - 7-8: specimen_3 | primary_diagnosis_1 | donor_1 | program_1
   - 9-10: specimen_4 | primary_diagnosis_2 | donor_1 | program_1
   - 11-12: specimen_5_6 | primary_diagnosis_2 | donor_1 | program_1
   - 13-14: specimen_7_8 | primary_diagnosis_3 | donor_1 | program_1
   - 15-16: specimen_9_10 | primary_diagnosis_4 | donor_2 | program_1
   - 17-18: specimen_11_12 | primary_diagnosis_5_6 | donor_2 | program_1
   - 19-20: specimen_13_14 | primary_diagnosis_7_8 | donor_3 | program_1
   - 21-22: specimen_15_16 | primary_diagnosis_9_10 | donor_4 | program_1
   - 23-24: specimen_17_18 | primary_diagnosis_11_12 | donor_5_6 | program_1
   - 25-28: specimen_19_20_21_22 | primary_diagnosis_13_14_15_16 | donor_7_8_9_10 | program_2

 - 22 Treatment
    - 1-3: primary_diagnosis_1 | donor_1 | program_1
    - 4-6: primary_diagnosis_2 | donor_1 | program_1
    - 7-8: primary_diagnosis_3 | donor_1 | program_1
    - 9-10: primary_diagnosis_4 | donor_2 | program_1
    - 11-12: primary_diagnosis_5_6 | donor_2 | program_1
    - 13-14: primary_diagnosis_7_8 | donor_3 | program_1
    - 15-16: primary_diagnosis_9_10 | donor_4 | program_1
    - 17-18: primary_diagnosis_11_12 | donor_5_6 | program_1
    - 19-22: primary_diagnosis_13_14_15_16 | donor_7_8_9_10 | program_2

 - 7 Chemotherapy
    - 1-3: treatment_1 | primary_diagnosis_1 | donor_1 | program_1
    - 4-5: treatment_2 | primary_diagnosis_1 | donor_1 | program_1
    - 6-7: treatment_3_4 | primary_diagnosis_1_2 | donor_1 | program_1

 - 7 HormoneTherapy
   - 1-3: treatment_5 | primary_diagnosis_2 | donor_1 | program_1
   - 4-5: treatment_6 | primary_diagnosis_2 | donor_1 | program_1
   - 6-7: treatment_7_8 | primary_diagnosis_3 | donor_1 | program_1

 - 5 Radiation
   - 1-2: treatment_9_10 | primary_diagnosis_4 | donor_2 | program_1
   - 3-4: treatment_11_12 | primary_diagnosis_5_6 | donor_2 | program_1
   - 5: treatment_13 | primary_diagnosis_7 | donor_3 | program_1

 - 7 Immunotherapy
    - 1-3: treatment_14 | primary_diagnosis_8 | donor_3 | program_1
    - 4-5: treatment_15 | primary_diagnosis_9 | donor_4 | program_1
    - 6-7: treatment_16_17 | primary_diagnosis_10_11 | donor_4_5 | program_1

 - 5 Surgery (treatment_17_18_19_20 has 1, specimen_1_2 has 1)
   - 1: treatment_18 | primary_diagnosis_12 | donor_5 | program_1
   - 2-5: treatment_19_22 | primary_diagnosis_13_14_15_16 | donor_7_8_9_10 | program_2
- 
        
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
    - 25-28: treatment_19_22: primary_diagnosis_13_14_15_16 | donor_7_8_9_10 | program_2

 - 12 Biomarker
   - 1-3: follow_up_1 | treatment_1 | primary_diagnosis_1 | donor_1 | program_1
   - 4-6: follow_up_2 | treatment_1 | primary_diagnosis_1 | donor_1 | program_1
   - 7-8: follow_up_3 | treatment_1 | primary_diagnosis_1 | donor_1 | program_1
   - 9-10: follow_up_4 | treatment_2 | primary_diagnosis_1 | donor_1 | program_1
   - 11-12: follow_up_5_6 | treatment_2 | primary_diagnosis_1 | donor_1 | program_1

 - 14 Comorbidity
    - 1-3: donor_1 | program_1
    - 4-6: donor_2 | program_1
    - 7-8: donor_3 | program_1
    - 9-10: donor_4 | program_1
    - 11-12: donor_5_6 | program_1
    - 13-14: donor_7_8 | program_2