Phenopackets API endpoints
======================

Data types endpoints
--------------------

**Phenotypic features**

:code:`api/phenotypicfeatures` GET: list of phenotypic features

:code:`api/phenotypicfeatures/{id}` GET: single phenotypic feature

The following **filters** can be applied:

- id (exact match, single): :code:`/api/phenotypicfeatures?id=112002`

- negated: :code:`/api/phenotypicfeatures?negated=No`
  options: Unknown, Yes, No

- description (case-insensitive partial match): :code:`/api/phenotypicfeatures?description=test`

- type (case-insensitive partial match): :code:`/api/phenotypicfeatures?type=hypertension`
  or :code:`/api/phenotypicfeatures?type=HP:0000822`

- severity (case-insensitive partial match): :code:`/api/phenotypicfeatures?severity=mild`
  or :code:`/api/phenotypicfeatures?severity=HP:0012825`

- onset (case-insensitive partial match): :code:`/api/phenotypicfeatures?onset=adult`
  or :code:`/api/phenotypicfeatures?onset=HP:0003581`

- evidence (case-insensitive partial match): :code:`/api/phenotypicfeatures?evidence=author statement`
  or :code:`/api/phenotypicfeatures?evidence=ECO:0006017`

- extra_properties (case-insensitive partial match): :code:`/api/phenotypicfeatures?extra_properties=test`

- extra_properties_datatype (ONLY if "datatype" is present in extra_properties, case-insensitive partial match):
  :code:`/api/phenotypicfeatures?extra_properties_datatype=comorbidities`

- individual (single or multiple individuals ids separated by comma), returns all phenotypic features for listed individuals:
  :code:`/api/phenotypicfeatures?individual=10001,10002`

- biosample (single), returns phenotypic features that are related to a specified biosample:
  :code:`/api/phenotypicfeatures?biosample=2615-01`

- phenopacket (single), returns phenotypic features that are related to a specified phenopacket:
  :code:`/api/phenotypicfeatures?phenopacket=20110`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/phenotypicfeatures?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/phenotypicfeatures?authorized_datasets=dataset_1,dataset_2`


**Procedures**

:code:`api/procedures` GET: list of phenotypic features

:code:`api/procedures/{id}` GET: single phenotypic feature

The following **filters** can be applied:

- id (exact match, single): :code:`/api/procedures?id=112002`

- code (case-insensitive partial match): :code:`/api/procedures?code=punch biopsy`
  or :code:`/api/procedures?code=NCIT:C28743`

- body_site (case-insensitive partial match): :code:`/api/procedures?body_site=skin of forearm`
  or :code:`/api/procedures?body_site=UBERON:0003403`

- biosample (single), returns procedure that was performed on a specified biosample:
  :code:`/api/procedures?biosample=2615-01`

- extra_properties (case-insensitive partial match): :code:`/api/procedures?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/procedures?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/procedures?authorized_datasets=dataset_1,dataset_2`


**HTS Files**

:code:`api/htsfiles` GET: list of HTS files

:code:`api/htsfiles/{uri}` GET: single HTS files

The following **filters** can be applied:

- uri (exact match, single): :code:`/api/htsfiles?uri=drs://data/10001.vcf.gz`

- description (case-insensitive partial match): :code:`/api/htsfiles?description=test`

- hts_format (case-insensitive exact match): :code:`/api/htsfiles?hts_format=VCF`
  options: UNKNOWN, SAM, BAM, CRAM, VCF, BCF, GVCF

- genome_assembly (case-insensitive exact match): :code:`/api/htsfiles?genome_assembly=GRCh37`

- extra_properties (case-insensitive partial match): :code:`/api/htsfiles?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/htsfiles?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/htsfiles?authorized_datasets=dataset_1,dataset_2`


**Genes**

:code:`api/genes` GET: list of Genes

:code:`api/genes/{id}` GET: single Gene

The following **filters** can be applied:

- id (single, exact match), takes an official identifier of the gene according to HGNC:
  :code:`/api/genes?id=HGNC:347`

- symbol (single, exact match), takes an official symbol of the gene according to HGNC:
  :code:`/api/genes?symbol=ETF1`

- extra_properties (case-insensitive partial match): :code:`/api/genes?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/genes?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/genes?authorized_datasets=dataset_1,dataset_2`


**Variants**

:code:`api/variants` GET: list of Variants

:code:`api/variants/{id}` GET: single Variants

The following **filters** can be applied:

- id (single, exact match), takes an official identifier of the gene according to HGNC:
  :code:`/api/variants?id=HGNC:347`

- allele_type (single, case-insensitive exact match): :code:`/api/variants?allele_type=spdiAllele`

- zygosity (case-insensitive partial match): :code:`/api/variants?zygosity=heterozygous`
  or :code:`/api/variants?zygosity=GENO:0000135`

- extra_properties (case-insensitive partial match): :code:`/api/variants?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/variants?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/variants?authorized_datasets=dataset_1,dataset_2`


**Diseases**

:code:`api/diseases` GET: list of Diseases

:code:`api/diseases/{id}` GET: single Disease

The following **filters** can be applied:

- id (single, exact match), disease id in Katsu database: :code:`/api/diseases?id=1`

- term (case-insensitive partial match): :code:`/api/diseases?term=COVID-19`
  or :code:`/api/diseases?term=SNOMED:840539006`

- extra_properties (case-insensitive partial match): :code:`/api/diseases?extra_properties=test`

- extra_properties_datatype (ONLY if "datatype" is present in extra_properties, case-insensitive partial match):
  :code:`/api/diseases?extra_properties_datatype=comorbidities`

- extra_properties_comorbidities_group (ONLY if "comorbidities_group" is present in extra_properties, case-insensitive partial match):
  :code:`/api/diseases?extra_properties_comorbidities_group=common`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/diseases?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/diseases?authorized_datasets=dataset_1,dataset_2`













