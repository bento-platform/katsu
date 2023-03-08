# About

This folder contains the schema and documentation for **MoH models**

To view the API documentation, you can simply open [openapi.md](openapi.md) or [Redoc](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/CanDIG/katsu/develop/chord_metadata_service/mohpackets/docs/schema.yml). If you need to generate the `schema.yml` file, run the command below:

```bash
python manage.py spectacular --file ./chord_metadata_service/mohpackets/docs/schema.yml --validate --fail-on-warn
```

Then to generate `openapi.md` file, you'll need to install `widdershins` first and then run the following command:

```bash
widdershins ./chord_metadata_service/mohpackets/docs/schema.yml -o ./chord_metadata_service/mohpackets/docs/openapi.md -u ./chord_metadata_service/mohpackets/docs/widdershins/templates/openapi3 -c true --omitHeader true
```
