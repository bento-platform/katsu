# Synthetic Data for MoH Models

This folder contains the necessary tools to generate synthetic data. Each dataset is organized into the following subfolders:

- `mockaroo_schemas`: contains the blueprints needed to generate data using the Mockaroo service.
- `no_relationships_data`: generated from mockaroo that doesn't include any relationships.
- `synthetic_data`: assigned relationships data, can be used for ingest APIs.

## To load data

```python
python chord_metadata_service/mohpackets/data/data_loader.py
```

## To clean up data

```python
python manage.py flush
```

## Customize and Generate the Data Yourself

If you want to modify the mock data to your preferences, you can follow these steps:

1. Create a [Mockaroo](https://www.mockaroo.com/) account
2. Load the blueprints from `mockaroo_schemas`
3. Make changes
4. Download the data as a JSON file, and put it in `no_relationships_data`
5. Modify `relationships.json` if needed
6. Run `data_converter.py` to generate the final data

*NOTE*: The synthetic data provided here is intended for frontend testing, and the logic is not strictly enforced. For other types of testing purposes, it is recommended to create your own data to ensure accuracy.
