Patients API
============

Data types endpoints
--------------------

**Individuals**

:code:`api/individuals` GET: list of individuals

:code:`api/individuals/{id}` GET: single individual

The following **filters** can be used:

- id (single or multiple ids can be sent): :code:`/api/individuals?id=10001&id=10002`

- alternate_ids (case-insensitive partial match): :code:`/api/individuals?alternate_ids=10002-23`

- sex (case-insensitive exact match): :code:`/api/individuals?sex=female`
  options: female, male, unknown_sex, other_sex

- karyotypic_sex (case-insensitive exact match): :code:`/api/individuals?karyotypic_sex=xx`
  options: unknown_karyotype, XX, XY, XO, XXY, XXX, XXYY, XXXY, XXXX, XYY, other_karyotype

- active status: :code:`/api/individuals?active=true`
  options: true, false

- deceased status: :code:`/api/individuals?deceased=false`
  options: true, false

- ethnicity (case-insensitive partial match): :code:`/api/individuals?ethnicity={value}`

- race (case-insensitive partial match): :code:`/api/individuals?race={value}`

- date_of_birth (range filter): :code:`/api/individuals?date_of_birth_after=1987-01-01&date_of_birth_before=1990-12-31`

- disease (case-insensitive partial match for disease term label or disease id represented by URI or CURIE):
  for example, a disease recorded as :code:`{"id": "SNOMED:840539006", "label": "COVID-19"}` can be searched

  1. by its label

  :code:`/api/individuals?disease=covid`

  or

  2. by its CURIE

  :code:`/api/individuals?disease=SNOMED:840539006`


- found_phenotypic_feature (case-insensitive partial match for phenotypic feature type label or
  id represented by URI or CURIE), finds all phenotypic feature with negated set to False:
  for example, a phenotypic feature  recorded as :code:`{"id": "HP:0000822", "label": "Hypertension"}` can be searched

  1. by its label

  :code:`/api/individuals?found_phenotypic_feature=hypertension`

  or

  2. by its CURIE

  :code:`/api/individuals?found_phenotypic_feature=HP:0000822`

- phenopackets__biosamples (single or multiple biosample ids), returns individuals linked to those biosamples:

  :code:`/api/individuals?phenopackets__biosamples=2615-01&phenopackets__biosamples=2390-11`

- phenopackets (single or multiple phenopacket ids): :code:`/api/individuals?phenopackets=10080&phenopackets=12045`

**Batch Individuals**

:code:`api/batch/individuals` POST: list of individuals

The following **body JSON options** can be used:

- format: case-sensitive, exact match: :code:`csv`
  options: csv, phenopackets, fhir, argo

- id: single or multiple ids can be provided as an array :code:`{"id": ["HP:0000822", "HP:0000823"]}`
