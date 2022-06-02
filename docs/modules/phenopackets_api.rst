Phenopackets API
================

Data types endpoints
--------------------

**Phenotypic features**

:code:`api/phenotypicfeatures` GET: list of phenotypic features

:code:`api/phenotypicfeatures/{id}` GET: single phenotypic feature

The following **filters** can be applied:

- id (exact match, single): :code:`/api/phenotypicfeatures?id=112002`

- negated: :code:`/api/phenotypicfeatures?negated=false`
  options: true, false

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

- id (single, exact match):
  :code:`/api/variants?id=100`

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


**Biosamples**

:code:`api/biosamples` GET: list of Biosamples

:code:`api/biosamples/{id}` GET: single Biosample

The following **filters** can be applied:

- id (single, exact match): :code:`/api/biosamples?id=1`

- description (case-insensitive partial match): :code:`/api/biosamples?description=test`

- sampled_tissue (case-insensitive partial match): :code:`/api/biosamples?sampled_tissue=urinary bladder`
  or :code:`/api/biosamples?sampled_tissue=UBERON:0001256`

- taxonomy (case-insensitive partial match): :code:`/api/biosamples?taxonomy=homo sapiens`
  or :code:`/api/biosamples?taxonomy=NCBITaxon:9606`

- histological_diagnosis (case-insensitive partial match): :code:`/api/biosamples?histological_diagnosis=negative finding`
  or :code:`/api/biosamples?histological_diagnosis=NCIT:C38757`

- tumor_progression (case-insensitive partial match): :code:`/api/biosamples?tumor_progression=primary neoplasm`
  or :code:`/api/biosamples?tumor_progression=NCIT:C8509`

- tumor_grade (case-insensitive partial match): :code:`/api/biosamples?tumor_grade=healed`
  or :code:`/api/biosamples?tumor_grade=NCIT:C41133`

- individual (single, exact match, biosample must be related to Individual via ForeignKey not via Phenopacket):
  :code:`/api/biosamples?individual=10001`

- procedure (single, exact match, searches by procedure id): :code:`/api/biosamples?procedure=1`

- is_control_sample: :code:`/api/biosamples?is_control_sample=false`
  options: true, false

- extra_properties (case-insensitive partial match): :code:`/api/biosamples?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/biosamples?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/biosamples?authorized_datasets=dataset_1,dataset_2`


**Phenopackets**

:code:`api/phenopackets` GET: list of Phenopackets

:code:`api/phenopackets/{id}` GET: single Phenopacket

The following **filters** can be applied:

- id (single, exact match): :code:`/api/phenopackets?id=12000`

- subject (single, exact match), returns all phenopackets for a single individual: :code:`/api/phenopackets?subject=10001`

- disease (case-insensitive partial match): :code:`/api/phenopackets?disease=COVID-19`
  or :code:`/api/phenopackets?disease=SNOMED:840539006`

- found_phenotypic_feature (case-insensitive partial match): :code:`/api/phenopackets?found_phenotypic_feature=hypertension`
  or :code:`/api/phenopackets?found_phenotypic_feature=HP:0000822`

- biosamples (single or multiple, exact match), takes biosample id, returns phenopacket(s) containing specified biosample(s):
  :code:`/api/phenopackets?biosamples=2231-20&biosamples=1289-21`

- genes (single or multiple, exact match), returns phenopacket(s) containing specified gene(s):
  :code:`/api/phenopackets?genes=HGNC:347`

- variants (single or multiple, exact match), returns phenopacket(s) containing specified variant(s):
  :code:`/api/phenopackets?variants=100&variants=101`

- hts_files (single or multiple, exact match), returns phenopacket(s) containing specified hts_file(s):
  :code:`/api/phenopackets?hts_files=drs://data/10001.vcf.gz&hts_files=drs://data/10002.vcf.gz`

- extra_properties (case-insensitive partial match): :code:`/api/phenopackets?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/phenopackets?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/phenopackets?authorized_datasets=dataset_1,dataset_2`


**Genomic Interpretations**

:code:`api/genomicinterpretations` GET: list of Genomic Interpretations

:code:`api/genomicinterpretations/{id}` GET: single Genomic Interpretation

The following **filters** can be applied:

- id (single, exact match): :code:`/api/genomicinterpretations?id=1`

- gene (single, exact match): :code:`/api/genomicinterpretations?gene=HGNC:347`

- variant (single, exact match): :code:`/api/genomicinterpretations?variant=100`

- status (case-insensitive, exact match): :code:`/api/genomicinterpretations?status=causative`
  options: Unknown, Rejected, Candidate, Causative

- extra_properties (case-insensitive partial match): :code:`/api/genomicinterpretations?extra_properties=test`


**Diagnoses**

:code:`api/diagnoses` GET: list of Diagnoses

:code:`api/diagnoses/{id}` GET: single Diagnosis

The following **filters** can be applied:

- id (single, exact match): :code:`/api/diagnoses?id=1`

- disease_type (case-insensitive partial match): :code:`/api/diagnoses?disease_type=COVID-19`
  or :code:`/api/diagnoses?disease_type=SNOMED:840539006`

- extra_properties (case-insensitive partial match): :code:`/api/diagnoses?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/diagnoses?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/diagnoses?authorized_datasets=dataset_1,dataset_2`


**Interpretations**

:code:`api/interpretations` GET: list of Interpretations

:code:`api/interpretations/{id}` GET: single Interpretation

The following **filters** can be applied:

- id (single, exact match): :code:`/api/interpretations?id=1`

- resolution_status (case-insensitive, exact match): :code:`/api/interpretations?resolution_status=causative`
  options: Unknown, Solved, Unsolved, In_progress

- phenopacket (single, exact match, searches by phenopacket id),
  returns all interpretations made for a specified phenopacket: :code:`/api/interpretations?phenopacket=12000`

- extra_properties (case-insensitive partial match): :code:`/api/interpretations?extra_properties=test`

- datasets (single or multiple list of datasets titles separated by comma):
  :code:`/api/interpretations?datasets=dataset_1,dataset_2`

- authorized_datasets (single or multiple list of authorized datasets titles separated by comma):
  :code:`/api/interpretations?authorized_datasets=dataset_1,dataset_2`
