from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField, ArrayField


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

	individual_id = models.CharField(primary_key=True, max_length=200)
	# TODO check for CURIE
	alternate_ids = ArrayField(models.CharField(max_length=200), blank=True, null=True)
	date_of_birth = models.DateField(null=True, blank=True)
	# An ISO8601 string represent age
	age = models.CharField(max_length=200, blank=True)
	sex = models.CharField(choices=SEX, max_length=200,  blank=True, null=True)
	karyotypic_sex = models.CharField(choices=KARYOTYPIC_SEX, max_length=200, blank=True)
	taxonomy = JSONField(blank=True, null=True)
	# FHIR specific
	active = models.BooleanField(default=False)
	deceased = models.BooleanField(default=False)
	address_postal_code = models.CharField(max_length=200, blank=True)
	# mCode specific
	race = models.CharField(max_length=200, blank=True)
	ethnicity = models.CharField(max_length=200, blank=True)

	def __str__(self):
		return str(self.individual_id)
