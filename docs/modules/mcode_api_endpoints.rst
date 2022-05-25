mCODE API endpoints
======================

Data types endpoints
--------------------

**All data elements**

:code:`api/{data element plural form}` GET: list of objects

:code:`api/{data element plural form}/{id}` GET: single object

The following **filters** can be applied:

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/{data element plural form}?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/{data element plural form}?authorized_datasets=dataset_1,dataset_2`

**Example**

:code:`api/geneticspecimens` GET: list of Genetic Specimens

:code:`api/geneticspecimens/{id}` GET: single Genetic Specimen

GET single object:

:code:`api/geneticspecimens/100-1`

Filtering:

:code:`/api/geneticspecimens?datasets=dataset_1,dataset_2`
