Resources API
=============

Data types endpoints
--------------------

**Resources**

:code:`api/resources` GET: list of resources

:code:`api/resources/{id}` GET: single resource

The following **filters** can be used:

- name (single, case-insensitive, partial match): :code:`/api/resources?name=NCBI Taxonomy`

- namespace_prefix (single, case-insensitive, exact match): :code:`/api/resources?namespace_prefix=NCBITaxon`

- url (single, case-insensitive, exact match): :code:`/api/resources?url=http://purl.obolibrary.org/obo/ncbitaxon.owl`

- iri_prefix (single, case-insensitive, exact match): :code:`/api/resources?url=http://purl.obolibrary.org/obo/NCBITaxon_`
