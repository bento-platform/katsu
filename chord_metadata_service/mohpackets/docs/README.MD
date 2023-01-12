# About

This folder contains the schema and documentation for **MoH models**

To view the API documentation, you can simply open [openapi.md](openapi.md). If you need to generate the `schema.yml` file, run the command below:

```bash
python manage.py spectacular --file ./chord_metadata_service/mohpackets/docs/schema.yml --validate --fail-on-warn
```

For the `openapi.md` file, you'll need to install `widdershins` first and then run the following command:

```bash
widdershins ./chord_metadata_service/mohpackets/docs/schema.yml -o ./chord_metadata_service/mohpackets/docs/openapi.md -c true -u ./chord_metadata_service/mohpackets/docs/widdershins/templates/openapi3
```

Alternatively, you can also view the documentation in Redoc by using the following Docker command:

```bash
docker run -it --rm -p 8080:80 \
  -v $(pwd)/chord_metadata_service/mohpackets/docs/schema.yml:/usr/share/nginx/html/schema.yml \
  -e SPEC_URL=schema.yml redocly/redoc
```

Once you run it, you can access the documentation by visiting `localhost:8080` in your web browser.
