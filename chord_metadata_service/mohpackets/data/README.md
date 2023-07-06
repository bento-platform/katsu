# Synthetic Data for MoH Models

This folder contains the necessary tools to generate synthetic data. Each dataset is organized into the following subfolders:

- `mockaroo_schemas`: contains the blueprints needed to generate data using the Mockaroo service.
- `no_relationships_data`: generated mock data that doesn't include any relationships.
- `synthetic_data`: assigned relationships data, can be used for ingestion.

## Create Fixtures

Run the following command and choose the dataset you want to generate fixtures for:

```python
python chord_metadata_service/mohpackets/data/convert.py
```

## Load Fixtures

Run the following commands (change the `fixtures_path` variable to the dataset you want to load):

```bash
fixtures_path="chord_metadata_service/mohpackets/data/small_dataset/fixtures"
python manage.py loaddata $fixtures_path/fixtures.json -v 3
```

## Clean up data

To start again, use:

```bash
python manage.py flush
```

## Customize and Generate the Data Yourself

If you want to modify the mock data to your preferences, you can follow these steps:

1. Create a [Mockaroo](https://www.mockaroo.com/) account
2. Load the blueprints from `mockaroo_schemas`
3. Make changes
4. Download the data as a JSON file, and put it in `no_relationships_data`
5. Modify `relationships.json` if needed
6. Run `convert.py` to generate the final data

*NOTE*: The synthetic data provided is intended for frontend testing. For other types of testing purposes, it is recommended to create your own data to ensure accuracy.
