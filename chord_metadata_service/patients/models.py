from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField, ArrayField


#############################################################
#                                                           #
#                        Ontology                           #
#                                                           #
#############################################################


class Ontology(models.Model):
	""" Class to reperesent terms from ontologies
	e.g.
	{
	  "id": "HP:0001875",
	  "label": "Neutropenia"
	}
	"""

	ontology_id = models.CharField(max_length=200)
	label = models.CharField(max_length=200)

	class Meta:
		unique_together = ['ontology_id', 'label']

	def __str__(self):
		return str(ontology_id)

#############################################################


#############################################################
#                                                           #
#                        Variants                           #
#                                                           #
#############################################################


class Variant(models.Model):
	""" Class to describe candidate (individual ???) variants or diagnosed causative variants """
	# TODO
	ALLELE = (
	('hgvsAllele', 'hgvsAllele'),
	('vcfAllele', 'vcfAllele'),
	('spdiAllele', 'spdiAllele'),
	('iscnAllele', 'iscnAllele')
	)

	# {
	# "spdiAllele": {
	#   "id": "clinvar:13294"
	#   "seqId": "NC_000010.10",
	#   "position": 123256214,
	#   "deletedSequence": "T",
	#   "insertedSequence": "G"
	# },
	# "zygosity": {
	#   "id": "GENO:0000135",
	#   "label": "heterozygous"
	# }
	# }

	# CHECK! one allele per one variant
	allele_type = models.CharField(choices=ALLELE, max_length=200)
	# !!!!!!!!! CHECK
	allele = JSONField()
	zygosity = models.ForeignKey(Ontology, on_delete=models.SET_NULL, null=True)

	def __str__(self):
		return str(self.id)

# CHECK !!!

class HgvsAllele(models.Model):
	""" Class to describe an allele according to the nomenclature of the HGVC """

	hgvs_allele_id = models.CharField(max_length=200, blank=True)
	hgvs = models.CharField(max_length=200)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.id)


class VcfAllele(models.Model):
	""" Class to describe variants using Varian Call Format """

	vcf_allele_id = models.CharField(max_length=200, blank=True)
	genome_assembly = models.CharField(max_length=200)
	_chr = models.CharField(max_length=200)
	pos = models.IntegerField()
	re = models.CharField(max_length=200)
	alt = models.CharField(max_length=200)
	info = models.CharField(blank=True, max_length=500)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.id)


class SpdiAllele(models.Model):
	""" Class to describe variants using SPDI notation """

	spdi_allele_id = models.CharField(max_length=200, blank=True)
	seq_id = models.CharField(max_length=200)
	position = models.IntegerField()
	deleted_sequence = models.CharField(max_length=200)
	inserted_sequence = models.CharField(max_length=200)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.id)


class IscnAllele(models.Model):
	""" Class to describe cytogenetic anomalies according to the ISCN """

	iscn_allele_id = models.CharField(max_length=200, blank=True)
	iscn = models.CharField(max_length=200)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.id)


#############################################################


class PhenotypicFeature(models.Model):
	""" Class to describe a phenotype of an Individual """

	description = models.CharField(max_length=200, blank=True)
	# if Ontology deleted protect the PhenotypicFeature from deletion
	# and raise IntegrityError
	phenotype = models.ForeignKey(Ontology, on_delete=models.PROTECT,
		related_name='phenotypes')
	negated = models.BooleanField(default=False)
	# since severity is an optional, set value to null when Ontology deleted
	severity = models.ForeignKey(Ontology, on_delete=models.SET_NULL,
		null=True, related_name='severities')
	modifier = models.ManyToManyField(Ontology, blank=True,
		related_name='modifiers')
	onset = models.ForeignKey(Ontology, on_delete=models.SET_NULL,
		null=True, related_name='onsets')
	evidence = JSONField(blank=True, null=True)

	def __str__(self):
		return str(self.id)


class Procedure(models.Model):
	"""
	Class to represent a clinical procedure performed on an individual
	(subject) in oder to extract a biosample
	"""

	code = models.ForeignKey(Ontology, on_delete=models.PROTECT,
		related_name='codes')
	body_site = models.ForeignKey(Ontology, on_delete=models.SET_NULL,
		null=True, related_name='body_sites')

	def __str__(self):
		return str(self.id)


class HtsFile(models.Model):
	""" Class to link HTC files with data """
	HTS_FORMAT = (
	('UNKNOWN', 'UNKNOWN'),
	('SAM', 'SAM'),
	('BAM', 'BAM'),
	('CRAM', 'CRAM'),
	('VCF', 'VCF'),
	('BCF', 'BCF'),
	('GVCF', 'GVCF')
	)

	uri = models.URLField(max_length=200)
	description = models.CharField(max_length=200, blank=True)
	hts_format = models.CharField(choices=HTS_FORMAT, max_length=200)
	genome_assembly = models.CharField(max_length=200)
	# e.g.
	# "individualToSampleIdentifiers": {
	#   "patient23456": "NA12345"
	# }
	# the key is always unique ?
	individual_to_sample_identifiers = JSONField(blank=True, null=True)

	def __str__(self):
		return str(self.id)


class Gene(models.Model):
	""" Class to represent an identifier for a gene """

	# Gene id is unique
	gene_id = models.CharField(max_length=200, unique=True)
	# CURIE style?
	alternate_id = ArrayField(models.CharField(blank=True, max_length=200))
	symbol = models.CharField(max_length=200)

	def __str__(self):
		return str(self.id)


class Disease(models.Model):
	"""
	Class to represent a diagnosis and inference or hypothesis about the cause
	underlying the observed phenotypic abnoramalities
	"""

	term = models.ForeignKey(Ontology, on_delete=models.PROTECT,
		related_name='terms')
	# onset can be represented by Age or Ontology, recommended ontology is the HPO onset hierarchy
	# TODO think how to serialize it

	# "ageOfOnset": {
  	# "age": "P38Y7M"
  	# }
	age_of_onset = JSONField(blank=True, null=True)
	# "ageOfOnset": {
  	# "id": "HP:0003581",
  	# "label": "Adult onset"
  	# }
	age_of_onset_ontology = models.ForeignKey(Ontology, on_delete=models.SET_NULL,
		null=True, related_name='age_of_onset_ontologies')
	tumor_stage = models.ForeignKey(Ontology, on_delete=models.SET_NULL,
		null=True, related_name='tumor_stages')

	def __str__(self):
		return self.id


#############################################################
#                                                           #
#                        Metadata                           #
#                                                           #
#############################################################


class Resource(models.Model):
	"""
	Class to represent a description of an external resource
	used for referencing an object
	"""

	# resource_id e.g. "id": "uniprot"
	resource_id = models.CharField(max_length=200)
	name = models.CharField(max_length=200)
	namespace_prefix = models.CharField(max_length=200)
	url = models.URLField(max_length=200)
	version = models.CharField(max_length=200)
	iri_prefix = models.URLField(max_length=200)

	def __str__(self):
		return str(self.id)


class Update(models.Model):
	""" Class to store data about an update event to a metadata record """

	timestamp = models.DateTimeField(default=timezone.now)
	updated_by = models.CharField(max_length=200, blank=True)
	comment = models.TextField()

	def __str__(self):
		return str(self.id)


class ExternalReference(models.Model):
	""" Class to store information about an external reference """

	external_reference_id = models.CharField(max_length=200)
	description = JSONField(blank=True, null=True)

	def __str__(self):
		return str(self.id)


class MetaData(models.Model):
	"""
	Class to store structured definitions of the resources
	and ontologies used within the phenopacket
	"""

	# CHECK !!! created or submitted?
	created = models.DateTimeField(default=timezone.now)
	created_by = models.CharField(max_length=200)
	submitted_by = models.CharField(max_length=200, blank=True)
	# From specs:
	# The MetaData element MUST have one Resource element for each ontology or terminology whose
	# terms are used in the Phenopacket. For instance, if a MONDO term is used to specificy the disease
	# and HPO terms are used to specificy the phenotypes of a patient, then the MetaData element
	# MUST have one Resource element each for MONDO and HPO.
	# see example: https://phenopackets-schema.readthedocs.io/en/latest/metadata.html#rstmetadata
	resource = models.ManyToManyField(Resource)
	update = models.ManyToManyField(Update, blank=True)
	phenopacket_schema_version = models.CharField(max_length=200, blank=True)
	external_reference = models.ManyToManyField(ExternalReference, blank=True)

	def __str__(self):
		return str(self.id)


#############################################################


class Individual(models.Model):
	""" Class to store sensitive information about Patient"""

	SEX = (
	('UNKNOWN_SEX', 'UNKNOWN_SEX'),
	('FEMALE', 'FEMALE'),
	('MALE', 'MALE'),
	('OTHER_SEX', 'OTHER_SEX')
	)

	KARYOTYPIC_SEX = (
	('UNKNOWN_KARYOTYPE', 'UNKNOWN_KARYOTYPE'),
	('XX', 'XX'),
	('XY', 'XY'),
	('XO', 'XO'),
	('XXY', 'XXY'),
	('XXX', 'XXX'),
	('XXYY', 'XXYY'),
	('XXXY', 'XXXY'),
	('XXXX', 'XXXX'),
	('XYY', 'XYY'),
	('OTHER_KARYOTYPE', 'OTHER_KARYOTYPE'),
	)

	# GENDER = (
	# ('MALE', 'MALE'),
	# ('FEMALE', 'FEMALE'),
	# ('OTHER', 'OTHER'),
	# ('UNKNOWN', 'UNKNOWN')
	# )

	#id = models.AutoField(primary_key=True)
	# takes a list of CURIE
	individual_id = models.CharField(max_length=200)
	alternate_id = ArrayField(models.CharField(max_length=200), blank=True, null=True)
	date_of_birth = models.DateField(null=True, blank=True)
	# An ISO8601 string represent age
	age = models.CharField(max_length=200, blank=True)
	sex = models.CharField(choices=SEX, max_length=200,  blank=True, null=True)
	karyotypic_sex = models.CharField(choices=KARYOTYPIC_SEX, max_length=200, blank=True)
	# OntologyClass
	taxonomy = JSONField(blank=True, null=True)
	# FHIR fields how useful hey are?
	# active = models.BooleanField()
	# gender = models.CharField(choices=GENDER, max_length=200)
	# deceased = models.BooleanField()

	def __str__(self):
		return str(self.id)


class Biosample(models.Model):
	""" Class to describe a unit of biological material """

	biosample_id = models.CharField(max_length=200)
	# if Invividual instance is deleted Biosample instance is deleted too
	# CHECK if this rel must be a required
	individual = models.ForeignKey(Individual, on_delete=models.CASCADE, blank=True, null=True)
	description = models.CharField(max_length=200, blank=True)
	# OntologyClass
	sampled_tissue = JSONField()
	phenotypic_feature = models.ManyToManyField(PhenotypicFeature, blank=True)
	# OntologyClass
	taxonomy = JSONField(blank=True, null=True)
	# An ISO8601 string represent age
	individual_age_at_collection = models.CharField(max_length=200, blank=True)
	# all OntologyClass
	historical_diagnosis = JSONField(blank=True, null=True)
	tumor_progression = JSONField(blank=True, null=True)
	tumor_grade = JSONField(blank=True, null=True)
	diagnostic_marker = JSONField(blank=True, null=True)
	# CHECK! if Procedure instance is deleted Biosample instance is deleted too
	procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
	hts_file = models.ForeignKey(HtsFile, on_delete=models.CASCADE, blank=True, null=True)
	variant = models.ManyToManyField(Variant, blank=True)
	is_control_sample = models.BooleanField(default=False)

	def __str__(self):
		return str(self.id)


class Phenopacket(models.Model):
	""" Class to aggregate Patient's experiments data """

	phenopacket_id = models.CharField(max_length=200)
	# if Individual instance is deleted Phenopacket instance is deleted too
	# CHECK !!! Force as required?
	subject = models.ForeignKey(Individual, on_delete=models.CASCADE)
	# PhenotypicFeatures are present in Biosample, so can be accessed via Biosample instance
	phenotypic_feature = models.ManyToManyField(PhenotypicFeature, blank=True)
	biosample = models.ManyToManyField(Biosample, blank=True)
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE, blank=True, null=True)
	variant = models.ManyToManyField(Variant, blank=True)
	disease = models.ManyToManyField(Disease, blank=True)
	hts_file = models.ManyToManyField(HtsFile, blank=True)
	meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE)
	
	def __str__(self):
		return str(self.id)


#############################################################
#                                                           #
#                    Interpretation                         #
#                                                           #
#############################################################


class GenomicInterpretation(models.Model):
	"""
	Class to represent a statemenet about the contribution
	of a genomic element towards the observed phenotype
	"""

	GENOMIC_INTERPRETATION_STATUS = (
		('UNKNOWN', 'UNKNOWN'),
		('REJECTED', 'REJECTED'),
		('CANDIDATE', 'CANDIDATE'),
		('CAUSATIVE', 'CAUSATIVE')
		)
	status = models.CharField(choices=GENOMIC_INTERPRETATION_STATUS, max_length=200)
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE, to_field='gene_id',
		blank=True, null=True)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE,
		blank=True, null=True)


	def clean(self):
		if not (self.gene or self.variant):
			raise ValidationError('Either Gene or Variant must be specified')

	def __str__(self):
		return str(self.id)


class Diagnosis(models.Model):
	""" Class to refer to disease that is present in in the individual analyzed """

	disease = models.ForeignKey(Disease, on_delete=models.CASCADE)
	# required?
	genomic_interpretation = models.ManyToManyField(GenomicInterpretation, blank=True)

	def __str__(self):
		return str(self.id)


class Interpretation(models.Model):
	""" Class to represent the interpretation of a genomyc analysis """

	RESOLUTION_STATUS = (
		('UNKNOWN', 'UNKNOWN'),
		('SOLVED', 'SOLVED'),
		('UNSOLVED', 'UNSOLVED'),
		('IN_PROGRESS', 'IN_PROGRESS')
		)

	interpretation_id = models.CharField(max_length=200)
	resolution_status = models.CharField(choices=RESOLUTION_STATUS, max_length=200, blank=True)
	phenopacket = models.ForeignKey(Phenopacket, on_delete=models.CASCADE)
	# fetch disease via from phenopacket
	# diagnosis on one disease ? there can be many disease assosiated with phenopacket
	diagnosis = models.ManyToManyField(Diagnosis)
	meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE)

	def __str__(self):
		return str(self.id)
