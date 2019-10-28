from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField, ArrayField


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

	# id = models.AutoField(primary_key=True)
	individual_id = models.CharField(primary_key=True, max_length=200)
	# TODO check for CURIE
	alternate_ids = ArrayField(models.CharField(max_length=200), blank=True, null=True)
	date_of_birth = models.DateField(null=True, blank=True)
	# An ISO8601 string represent age
	age = models.CharField(max_length=200, blank=True)
	sex = models.CharField(choices=SEX, max_length=200,  blank=True, null=True)
	karyotypic_sex = models.CharField(choices=KARYOTYPIC_SEX, max_length=200, blank=True)
	# OntologyClass
	# taxonomy = JSONField(blank=True, null=True)
	# FHIR fields how useful hey are?
	# active = models.BooleanField()
	# gender = models.CharField(choices=GENDER, max_length=200)
	# deceased = models.BooleanField()

	def __str__(self):
		return str(self.individual_id)

