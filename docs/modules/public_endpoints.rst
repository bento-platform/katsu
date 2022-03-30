Public endpoints
================

There are several public APIs to perform a search that returns only objects count.
The implementation of public APIs relies on a project customized configuration file (config.json) that must be placed into base directory.
Currently, there is an :code:`example.config.json` located  in :code:`/katsu/chord_metadata_service` directory which is set to be the project base directory.
The file can be copied, renamed to :code:`config.json` and modified.

Config file specification
-------------------------

The config.json file follows jsonschema specifications: it includes a field from the current Phenopackets data model, defines it's type and other attributes that determine how the data from this field will be presented in the public response.

**Jsonschema properties**:

- "type" - defines a data type for this field, e.g. "number" or "string"
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


Public APIs
-------------------------

Coming soon...