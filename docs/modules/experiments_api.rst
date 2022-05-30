Experiments API
===============

Data types endpoints
--------------------

**Experiments**

:code:`api/experiments` GET: list of Experiments

:code:`api/experiments/{id}` GET: single Experiment

The following **filters** can be applied:

- id (exact match, single): :code:`/api/experiments?id=100`

- reference_registry_id (single, case-sensitive, exact match): :code:`/api/experiments?reference_registry_id=RR10015`

- study_type (single, case-insensitive, partial match): :code:`/api/experiments?study_type=genomics`

- experiment_type (single, case-insensitive, partial match): :code:`/api/experiments?experiment_type=wes`

- molecule (single, case-insensitive, partial match): :code:`/api/experiments?molecule=protein`

- library_strategy (single, case-insensitive, partial match): :code:`/api/experiments?library_strategy=wes`

- library_source (single, case-insensitive, partial match): :code:`/api/experiments?library_source=genomic`

- library_selection (single, case-insensitive, partial match): :code:`/api/experiments?library_selection=random`

- library_layout (single, case-insensitive, partial match): :code:`/api/experiments?library_layout=single`

- extraction_protocol (single, case-insensitive, partial match): :code:`/api/experiments?extraction_protocol=exome capture`

- biosample (single, exact match), takes biosample id, returns all experimentsrelated to a specified biosample:
  :code:`/api/experiments?biosample=1005`

- extra_properties (case-insensitive, partial match): :code:`/api/experiments?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/experiments?datasets=dataset_1,dataset_2`


**Experiment Results**

:code:`api/experimentresults` GET: list of Experiment Results

:code:`api/experimentresults/{id}` GET: single Experiment Result

The following **filters** can be applied:

- identifier (single, exact match): :code:`/api/experimentresults?identifier=RN-1001`

- description (single, case-insensitive, partial match): :code:`/api/experimentresults?description=test`

- filename (single, case-insensitive, partial match): :code:`/api/experimentresults?filename=1001_rnaseq.bw`

- genome_assembly_id (single, case-insensitive, exact match): :code:`/api/experimentresults?genome_assembly_id=GRCh37`
  options: GRCh37, GRCh38, GRCm38, GRCm39

- file_format (single, case-insensitive, exact match): :code:`/api/experimentresults?file_format=VCF`

- data_output_type (single, case-insensitive, partial match): :code:`/api/experimentresults?data_output_type=raw data`

- usage (single, case-insensitive, partial match): :code:`/api/experimentresults?usage=visualized`

- created_by (single, case-insensitive, partial match): :code:`/api/experimentresults?created_by=Admin`

- extra_properties (case-insensitive, partial match): :code:`/api/experimentresults?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/experimentresults?datasets=dataset_1,dataset_2`
