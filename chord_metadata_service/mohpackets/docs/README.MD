# About

This folder contains the schema and documentation for **MoH models**

## Katsu API Documentation

To view the API documentation, simply open [openapi.md](openapi.md) or [Redoc](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/docs/schema.json).

To generate the `schema.json` file, run the following command:

```bash
python manage.py export_openapi_schema --api chord_metadata_service.mohpackets.apis.core.api | python -m json.tool > chord_metadata_service/mohpackets/docs/schema.json
```

To generate the `openapi.md` file, install [widdershins](https://github.com/Mermade/widdershins) and then run the following command:

```bash
widdershins ./chord_metadata_service/mohpackets/docs/schema.json -o ./chord_metadata_service/mohpackets/docs/openapi.md -u ./chord_metadata_service/mohpackets/docs/widdershins/templates/openapi3 -c true --omitHeader true
```

This will create the openapi.md file with the updated documentation.

## Katsu MoH data model Documentation

To regenerate the `er_diagram.md` file, run the following from the commandline in the current directory: 

To update the model classes:
```bash
pip install pylint
pyreverse -o mmd ./models.py
```

To update the markdown file
```bash
python make_er_diagram.py
```
