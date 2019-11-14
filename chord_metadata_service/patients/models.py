from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from .index import IndividualIndex
from django.db.models.signals import post_save
from django.dispatch import receiver


class Individual(models.Model):
	""" Class to store demographic information about an Individual (Patient) """

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

	individual_id = models.CharField(primary_key=True, max_length=200,
		help_text='An arbitrary identifier for the individual.')
	# TODO check for CURIE
	alternate_ids = ArrayField(models.CharField(max_length=200),
		blank=True, null=True,
		help_text='A list of alternative identifiers for the individual.')
	date_of_birth = models.DateField(null=True, blank=True,
		help_text='A timestamp either exact or imprecise.')
	# An ISO8601 string represent age
	age = models.CharField(max_length=200, blank=True,
		help_text='The age or age range of the individual.')
	sex = models.CharField(choices=SEX, max_length=200,  blank=True, null=True,
		help_text='Observed apparent sex of the individual.')
	karyotypic_sex = models.CharField(choices=KARYOTYPIC_SEX, max_length=200,
		blank=True, null=True, help_text='The karyotypic sex of the individual.')
	taxonomy = JSONField(blank=True, null=True, help_text='Ontology resource '
		'representing the species (e.g., NCBITaxon:9615).')
	# FHIR specific
	active = models.BooleanField(default=False,
		help_text='Whether this patient\'s record is in active use.')
	deceased = models.BooleanField(default=False,
		help_text='Indicates if the individual is deceased or not.')
	address_postal_code = models.CharField(max_length=200, blank=True,
		help_text='Postal code for area.')
	# mCode specific
	race = models.CharField(max_length=200, blank=True,
		help_text='A code for the person\'s race.')
	ethnicity = models.CharField(max_length=200, blank=True,
		help_text='A code for the person\'s ethnicity.')

	def __str__(self):
		return str(self.individual_id)

	def indexing(self):
		# mapping model fields to index fields
		obj = IndividualIndex(
			meta={'id': self.individual_id},
			alternate_ids=self.alternate_ids,
			date_of_birth=self.date_of_birth,
			age=self.age,
			sex=self.sex,
			karyotypic_sex=self.karyotypic_sex,
			taxonomy=self.taxonomy,
			active=self.active,
			deceased=self.deceased
			)
		obj.save(index='metadata')
		return obj.to_dict(include_meta=True)


# add to index on post_save signal
@receiver(post_save, sender=Individual)
def index_individual(sender, instance, **kwargs):
    instance.indexing()
