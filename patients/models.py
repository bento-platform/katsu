from django.db import models
from django.conf import settings
from django.utils import timezone


#############################################################
#                                                           #
#                        Variants                           #
#                                                           #
#############################################################


class Variant(models.Model):
	""" Class to describe candidate (individual ???) variants or diagnosed causative variants """
	# TODO
	ALLELE = (
	('HgvsAllele', 'HgvsAllele'),
	('VcfAllele', 'VcfAllele'),
	('SpdiAllele', 'SpdiAllele'),
	('IscnAllele', 'IscnAllele')
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
	allele = models.TextField()
	zygosity = models.TextField(blank=True)

	def __str__(self);
		return self.id

# CHECK !!!

class HgcvAllele(models.Model):
	""" Class to describe an allele according to the nomenclature of the HGVC """

	hgvs = models.CharField(max_length=200)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self):
		return self.id


class VcfAllele(models.Model):
	""" Class to describe variants using Varian Call Format """

	genome_assembly = models.CharField(max_length=200)
	_chr = models.CharField(max_length=200)
	pos = models.IntegerField()
	re = models.CharField(max_length=200)
	alt = models.CharField(max_length=200)
	info = models.CharField(blank=True, max_length=200)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self);
	return self.id


class SpdiAllele(models.Model):
	""" Class to describe variants using SPDI notation """

	seq_id = models.CharField(max_length=200)
	position = models.IntegerField()
	deleted_sequence = models.CharField(max_length=200)
	inserted_sequence = models.CharField(max_length=200)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self):
		return self.id


class IscnAllele(models.Model):
	""" Class to describe cytogenetic anomalies according to the ISCN """

	iscn = models.CharField(max_length=200)
	variant = models.ForeignKey(Variant, on_delete=models.CASCADE)

	def __str__(self):
		return self.id


#############################################################


class PhenotypicFeature(models.Model):
	""" Class to describe a phenotype of an Individual """

	description = models.CharField(max_length=200, blank=True)
	# JsonField
	phenotype = models.TextField()
	negated = models.BooleanField(default=False)
	severity = models.TextField(blank=True)
	modifier = models.TextField(blank=True)
	onset = models.TextField(blank=True)
	evidence = models.TextField(blank=True)

	def __str__(self):
		return self.id


class Procedure(models.Model):
	"""
	Class to represent a clinical procedure performed on an individual
	(subject) in oder to extract a biosample
	"""

	code = models.TextField()
	body_site = models.TextField(blank=True)

	def __str__(self):
		return self.id


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
	individual_to_sample_identifiers = models.TextField(blank=True)

	def __str__(self):
		return self.id


class Gene(models.Model):
	""" Class to represent an identifier for a gene """

	alternate_ids = models.TextField(balnk=True)
	symbol = models.CharField(max_length=200)

	def __str__(self):
		return self.id


class Disease(models.Model):
	"""
	Class to represent a diagnosis and inference or hypothesis about the cause
	underlying the observed phenotypic abnoramalities
	"""

	term = models.TextField()
	onset = models.TextField(blank=True)
	tumor_stage = models.TextField(blank=True)

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

	name = models.CharField(max_length=200)
	namespace_prefix = models.CharField(max_length=200)
	url = models.URLField(max_length=200)
	version = models.CharField(max_length=200)
	iri_prefix = models.URLField(max_length=200)

	def __str__(self):
		return self.id


class Update(models.Model):
	""" Class to store data about an update event to a metadata record """

	timestamp = models.DateTimeField(default=timezone.now)
	updated_by = models.CharField(max_length=200, blank=True)
	comment = models.TextField()

	def __str__(self):
		return self.id


class ExternalResource(models.Model):
	""" Class to store information about an external resource """

	description = models.TextField(blank=True)

	def __str__(self):
		return self.id


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
	update = models.ManyToManyField(Update, blank=True, null=True)
	phenopacket_schema_version = models.CharField(max_length=200, blank=True)
	external_references = models.ManyToManyField(ExternalResource, blank=True, null=True)

	def __str__(self):
		return self.id


#############################################################


class Individual(models.Model):
	""" Class to store sensitive information about Patient"""
	UNKNOWN_SEX = 0
	FEMALE = 1
	MALE = 2
	OTHER_SEX = 3
	SEX = (
	(UNKNOWN_SEX, 'UNKNOWN_SEX'),
	(FEMALE, 'FEMALE'),
	(MALE, 'MALE'),
	(OTHER_SEX, 'OTHER_SEX')
	)

	# TODO
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
	alternate_ids = models.TextField(blank=True)
	date_of_birth = models.DateField(null=True, blank=True)
	# An ISO8601 string represent age
	age = models.CharField(max_length=200, blank=True)
	sex = models.IntegerField(choices=SEX, max_length=200,  blank=True, null=True)
	karyotypic_sex = models.CharField(choices=KARYOTYPIC_SEX, max_length=200, blank=True)
	# for now
	taxonomy = models.TextField(blank=True)
	# FHIR fields how useful hey are?
	# active = models.BooleanField()
	# gender = models.CharField(choices=GENDER, max_length=200)
	# deceased = models.BooleanField()

	def __str__(self):
		return self.id


class Biosample(models.Model):
	""" Class to describe a unit of biological material """

	# if Invividual instance is deleted Biosample instance is deleted too
	# CHECK if this rel must be a required
	individual = models.ForeignKey(Individual, on_delete=models.CASCADE, blank=True, null=True)
	description = models.CharField(max_length=200, blank=True)
	sampled_tissue = models.TextField()
	phenotypic_feature = models.ManyToManyField(PhenotypicFeature, blank=True, null=True)
	taxonomy = models.TextField(blank=True)
	# An ISO8601 string represent age
	individual_age_at_collection = models.CharField(max_length=200, blank=True)
	historical_diagnosis = models.TextField(blank=True)
	tumor_progression = models.TextField(blank=True)
	tumor_grade = models.TextField(blank=True)
	diagnostic_marker = models.TextField(blank=True)
	# CHECK! if Procedure instance is deleted Biosample instance is deleted too
	procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE)
	hts_file = models.ForeignKey(HtsFile, on_delete=models.CASCADE, blank=True, null=True)
	variant = models.ManyToManyField(Variant, blank=True, null=True)
	is_control_sample = models.BooleanField(default=False)

	def __str__(self);
		return self.id


class Phenopacket(models.Model):
	""" Class to aggregate Patient's experiments data """

	# if Individual instance is deleted Phenopacket instance is deleted too
	# CHECK !!! Force as required?
	subject = models.ForeignKey(Individual, on_delete=models.CASCADE)
	# PhenotypicFeatures are present in Biosample, so can be accessed via Biosample instance
	phenotypic_feature = models.ManyToManyField(PhenotypicFeature, blank=True, null=True)
	biosample = models.ManyToManyField(Biosample, blank=True, null=True)
	gene = models.ForeignKey(Gene, on_delete=models.CASCADE, blank=True, null=True)
	variant = models.ManyToManyField(Variant, blank=True, null=True)
	disease = models.ManyToManyField(Disease, blank=True, null=True)
	hts_file = models.ManyToManyField(HtsFile, blank=True, null=True)
	meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.id
