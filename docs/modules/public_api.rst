Public API
==========

There are several public APIs to return data overview and perform a search that returns only objects counts.
The implementation of public APIs relies on a project customized configuration file (config.json) that must be placed in the base directory.
Currently, there is an :code:`example.config.json` located  in :code:`/katsu/chord_metadata_service` directory which is set to be the project base directory.
The file can be copied, renamed to :code:`config.json` and modified.

The :code:`config.json` file contains fields that data providers would like to open for public access.
If the :code:`config.json` file is not set up/created it means there is no public data and no data will be available via these APIs.

Config file specification
-------------------------

The :code:`config.json` file follows jsonschema specifications: it includes fields from katsu data model, defines their type and other attributes that determine how the data from these fields will be presented in the public response.

**Jsonschema properties**:

- "overview" - an array defining the fields that will be queried for statistics to be displayed as charts and their layout in the overview panel
- "search" - an array defining the fields that can be queried by the user for a count and their grouping by section
- "fields" - configuration of the fields available for search or overview
- "rules" - global privacy rules enforced on the data exported or the queries allowed

**config.overview properties**

An array of:

- "section_title" (string) - title that will be displayed for the group of charts
- "charts" - array of:

  - "field" (string) - field id (from the :code:`config.fields` property), to get statistics from
  - "chart_type" (options: pie, bar) - defines the type of chart used to display the statistics

**config.search properties**

An array of:

- "section-title" (string) - title that will be displayed for the group of fields
- "fields" (string array) - Array of fields id (from the :code:`config.fields`)

**config.fields properties**:

A dictionary, keyed by field id of:

- "mapping" (string) - defines in a path like format, the mapping between the field and its object representation in the Django ORM. The first part is a reference to the model. The following is the "location" of the field relative to the model (might be nested or made accross joins). Example "individual/extra_properties/date_of_consent"
- "title" (string) - name that is displayed to the user
- "description" (string) - detailed description of the field, suitable for a tooltip
- "datatype" (options number, date, string) - defines the type of field
- "config" (dict) - a configuration object that defines the values or ranges that can be queried for this field. Depends on the datatype.

  - [datatype=number].config:

    - "bin-size" (number): bins width. Due to implementation limitations, must be an integer for now.
    - "minimum" (number): values lesser than minimum can't be queried
    - "maximum" (number): values greater than or equal to maximum can't be queried
    - "taper_left" (number): cutoff value for the first bin. Disabled when equals to ``minimum``
    - "taper_right" (number): cutoff value for the last bin. Disabled when equals to ``maximum``
    - "units" (string): unit that will be displayed to the user

  - [datatype=string].config:

    - "enum" (string array or ``null``): when set to null, the distinct values are extracted from the table content. When set as a list, only the values listed will be displayed to the user.

  - [datatype=date].config:

    - "bin-by" (options month): only one valid option implemented for now. Bin values according to the method defined.

**config.rules properties**:

- "count_threshold" (number): when a count for a given bin is below or equal to this value, 0 is returned instead (avoids leaking small cell counts)
- "max_query_parameters" (number): maximum number of fields that can be queried simultaneously for a count


Example of the config.json

.. code-block::

  {
    "overview": [
        {
            "section_title": "Demographics",
            "charts": [
                {"field": "age", "chart_type": "bar"},
                {"field": "sex", "chart_type": "pie"},
                {"field": "date_of_consent", "chart_type": "bar"},
                {"field": "mobility", "chart_type": "bar"},
                {"field": "lab_test_result_value", "chart_type": "bar"}
            ]
        },
        {
            "section_title": "Experiments",
            "charts": [
                {"field": "experiment_type", "chart_type": "pie"}
            ]
        }
    ],
    "search": [
        {
            "section_title": "Demographics",
            "fields": ["age", "sex", "date_of_consent", "lab_test_result_value"]
        }
    ],
    "fields": {
        "age": {
            "mapping": "individual/age_numeric",
            "title": "Age",
            "description": "Age at arrival",
            "datatype": "number",
            "config": {
                "bin_size": 10,
                "taper_left": 10,
                "taper_right": 100,
                "units": "years",
                "minimum": 0,
                "maximum": 100
            }
        },
        "sex": {
            "mapping": "individual/sex",
            "title": "Sex",
            "description": "Sex at birth",
            "datatype": "string",
            "config": {
                "enum": null
            }
        },
        "experiment_type": {
            "mapping": "experiment/experiment_type",
            "title": "Experiment Types",
            "description": "Types of experiments performed on a sample",
            "datatype": "string",
            "config": {
                "enum": ["DNA Methylation", "mRNA-Seq", "smRNA-Seq", "RNA-Seq", "WES", "Other"]
            }
        },
        "date_of_consent": {
            "mapping": "individual/extra_properties/date_of_consent",
            "title": "Verbal consent date",
            "description": "Date of initial verbal consent(participant, legal representative or tutor), yyyy-mm-dd",
            "datatype": "date",
            "config": {
                "bin_by": "month"
            }
        },
        "lab_test_result_value": {
            "mapping": "individual/extra_properties/lab_test_result_value",
            "title": "Lab Test Result",
            "description": "This acts as a placeholder for numeric values",
            "datatype": "number",
            "config": {
                "bin_size": 50,
                "taper_left": 50,
                "taper_right": 800,
                "minimum": 0,
                "maximum": 1000,
                "units": "mg/L"
            }
        }
    },
    "rules": {
        "count_threshold": 5,
        "max_query_parameters": 2
    }
  }


Public endpoints
----------------

The public APIs include the following endpoints:


1. :code:`/api/public_search_fields` GET: returns a json containing for each section of the search form, the list of fields that can be queried and the authorized values.

  Example of response

  .. code-block::

    {
      "sections": [
          {
              "section_title": "Demographics",
              "fields": [
                  {
                      "mapping": "individual/age_numeric",
                      "title": "Age",
                      "description": "Age at arrival",
                      "datatype": "number",
                      "config": {
                          "bin_size": 10,
                          "taper_left": 10,
                          "taper_right": 100,
                          "units": "years",
                          "minimum": 0,
                          "maximum": 100
                      },
                      "id": "age",
                      "options": [
                          "< 10",
                          "10-20",
                          "20-30",
                          "30-40",
                          "40-50",
                          "50-60",
                          "60-70",
                          "70-80",
                          "80-90",
                          "90-100"
                      ]
                  },
                  {
                      "mapping": "individual/sex",
                      "title": "Sex",
                      "description": "Sex at birth",
                      "datatype": "string",
                      "config": {
                          "enum": null
                      },
                      "id": "sex",
                      "options": [
                          "FEMALE",
                          "MALE"
                      ]
                  },
                  {
                      "mapping": "individual/extra_properties/date_of_consent",
                      "title": "Verbal consent date",
                      "description": "Date of initial verbal consent(participant, legal representative or tutor), yyyy-mm-dd",
                      "datatype": "date",
                      "config": {
                          "bin_by": "month"
                      },
                      "id": "date_of_consent",
                      "options": [
                          "Nov 2020",
                          "Dec 2021",
                          "Jan 2021",
                          "Feb 2021",
                          "Mar 2021",
                          "Apr 2021",
                          "May 2021",
                          "Jun 2021",
                          "Jul 2021",
                          "Aug 2021",
                          "Sep 2021",
                          "Oct 2021",
                          "Nov 2021",
                          "Dec 2022",
                          "Jan 2022"
                      ]
                  },
                  {
                      "mapping": "individual/extra_properties/lab_test_result_value",
                      "title": "Lab Test Result",
                      "description": "This acts as a placeholder for numeric values",
                      "datatype": "number",
                      "config": {
                          "bin_size": 50,
                          "taper_left": 50,
                          "taper_right": 800,
                          "minimum": 0,
                          "maximum": 1000,
                          "units": "mg/L"
                      },
                      "id": "lab_test_result_value",
                      "options": [
                          "< 50",
                          "50-100",
                          "100-150",
                          "150-200",
                          "200-250",
                          "250-300",
                          "300-350",
                          "350-400",
                          "400-450",
                          "450-500",
                          "500-550",
                          "550-600",
                          "600-650",
                          "650-700",
                          "700-750",
                          "750-800",
                          "≥ 800"
                      ]
                  }
              ]
          }
      ]
    }

   The response when public fields are not configured and config file is not provided: :code:`{"message": "No public fields configured."}`


2. :code:`/api/public_overview` GET: returns an overview that contains counts for each field of interest.

   The response when there is no public data available and config file is not provided: :code:`{"message": "No public data available."}`


3. :code:`/api/public`  GET: returns a count of all individuals in database.

   The response when there is no public data available and config file is not provided: :code:`{"message": "No public data available."}`

   The response when there is no enough data that passes the project-custom threshold: :code:`{"message": "Insufficient data available."}`


   When count is less or equal to a project's custom threshold returns message that insufficient data available.
   Accepts search filters on the fields that are specified in the :code:`config.json` file.
   Example of searches:

   - sex: e.g. :code:`/api/public?sex=female`

   - age: search by age range e.g. :code:`/api/public?age=20-30`

   - combined fields: e.g. :code:`/api/public?smoking=Non-smoker&covidstatus=positive`

   - date: e.g. :code:`/api/public?date_of_consent=Feb 2021`

   The accepted values for the field names and their content is limited to the ones listed in :code:`/api/public_search_fields`. Note that searches on categories (datatype as string) are case insensitive
