Public API
==========

There are several public APIs to return data overview and perform a search that returns only objects count.
The implementation of public APIs relies on a project customized configuration file (config.json) that must be placed in the base directory.
Currently, there is an :code:`example.config.json` located  in :code:`/katsu/chord_metadata_service` directory which is set to be the project base directory.
The file can be copied, renamed to :code:`config.json` and modified.

The :code:`config.json` file contains fields that data providers would like to open for public access.
If the :code:`config.json` file is not set up/created it means there is no public data and no data will be available via these APIs.

Config file specification
-------------------------

The :code:`config.json` file follows jsonschema specifications: it includes fields from katsu data model, defines their type and other attributes that determine how the data from these fields will be presented in the public response.

**Jsonschema properties**:

- "type" - defines a data type for this field, e.g. "number" or "string" (katsu's config accepts only number and string types)
- "format" - defines a string format, e.g. "date" to record date in the format of "2021-12-31"
- "enum" - defines a list of options for this field
- "title" - field's user-friendly name
- "description" - field's description

**Custom properties**:

- "bin_size" (number) - defines a bin size for numeric fields (where "type" is set to "number"), by default bin size is set to 10
- "queryable" (true/false) - defines if the field should be included in search, if set to false the field will only be shown as a chart
- "is_range" (true/false) - defines if this field can  be searched using range search (e.g.min value and max value)
- "chart" (options: pie, bar)-  defines a type of the chart to be used to visualize the data
- "taper_left" and "taper_right" (number) - defines the cut offs for the data to be shown in charts
- "units" (string) - defines unit value for numeric fields (e.g. "years", "mg/L")
- "minimum" (number) - defines the minimum value in this field
- "maximum" (number) - defines the maximum value in this field

Example of the config.json

.. code-block::

    {
      "age": {
        "type": "number",
        "title": "Age",
        "bin_size": 10,
        "is_range": true,
        "queryable": true,
        "taper_left": 40,
        "taper_right": 60,
        "units": "years",
        "minimum": 0,
        "description": "Age at arrival"
      },
      "sex": {
        "type": "string",
        "enum": [
          "Male",
          "Female"
        ],
        "title": "Sex",
        "queryable": true,
        "description": "Sex at birth"
      },
      "extra_properties": {
        "date_of_consent": {
          "type": "string",
          "format": "date",
          "title": "Verbal consent date",
          "chart": "bar",
          "queryable": true,
          "description": "Date of initial verbal consent(participant, legal representative or tutor), yyyy-mm-dd"
        }
      }
    }


Public endpoints
----------------

The public APIs include the following endpoints:


1. :code:`/api/public_search_fields` GET: returns :code:`config.json` contents in a form of jsonschema.

   The response when public fields are not configured and config file is not provided: :code:`{"message": "No public fields configured."}`


2. :code:`/api/public_overview` GET: returns an overview that contains counts for each field of interest.

   The response when there is no public data available and config file is not provided: :code:`{"message": "No public data available."}`


3. :code:`/api/public`  GET: returns a count of all individuals in database.

   The response when there is no public data available and config file is not provided: :code:`{"message": "No public data available."}`

   The response when there is no enough data that passes the project-custom threshold: :code:`{"message": "Insufficient data available."}`


   When count is less or equal to a project's custom threshold returns message that insufficient data available.
   Accepts search filters on the fields that are specified in the :code:`config.json` file and set to "queryable".
   Currently, the following filters are written for the Individual model:

   - sex: e.g. :code:`/api/public?sex=female`

   - age: search by age ranges e.g. :code:`/api/public?age_range_min=20&age_range_max=30`

   - extra_properties: e.g. :code:`/api/public?extra_properties=[{"smoking": "Non-smoker"},{"covidstatus": "positive"}]`


   The :code:`extra_properties` is a JSONField without a schema.
   To allow searching content in this field the nested fields have to be added to the config file (see the config file example above).
   The query string must contain a list of objects where each object has a key-value pair representing a nested field name and a search value.


   Examples of extra properties searches:

   Search for items that have a type of string:

   .. code-block::

    /api/public?extra_properties=[{"smoking": "Non-smoker"},{"death_dc": "deceased"},{"covidstatus": "positive"}]


   Search for items that contain date ranges:

   .. code-block::

    /api/public?extra_properties=[{"date_of_consent": {"after": "2020-03-01", "before": "2021-05-01"}}]


   Search for items that contain numeric ranges:

   .. code-block::

    /api/public?extra_properties=[{"lab_test_result_value": {"rangeMin": 5, "rangeMax": 900}}]

   Examples of combining extra properties search with other fields:

   .. code-block::

    /api/public?sex=female&extra_properties=[{"covidstatus": "positive"}]
