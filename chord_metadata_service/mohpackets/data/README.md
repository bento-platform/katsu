# Synthetic Data for MoH Models

- `mockaroo_schemas`: blueprints for data generation
- `no_relationships_data`: raw data without relationships
- `synthetic_data`: generated data with relationships
- `fixtures`: synthetic data in Django format

## Loading Fixtures

Use the `loaddata` command:

```bash
fixtures_path="chord_metadata_service/mohpackets/data/small_dataset/fixtures"
fixtures_name=(Program Donor PrimaryDiagnosis Specimen SampleRegistration Treatment Chemotherapy HormoneTherapy Radiation Immunotherapy Surgery FollowUp Biomarker Comorbidity)
for fixture in ${fixtures_name}; do python manage.py loaddata $fixtures_path/$fixture.json; done
```

## Clean up data

If you need to clean up the data, run:

```bash
python manage.py flush
```

## Generating Data (Optional)

1. Create a [Mockaroo](https://www.mockaroo.com/) account
2. Use the blueprints in `mockaroo_schemas` to restore from backup
3. Make changes
4. Download the data as a JSON file, and put it in `no_relationships_data`
5. Run `convert.py` to set relationships and convert to fixtures:

```python
python chord_metadata_service/mohpackets/data/convert.py
```
