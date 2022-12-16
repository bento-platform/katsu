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