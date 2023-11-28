from typing import Optional
from django.apps import apps
from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from chord_metadata_service.restapi.models import BaseTimeStamp, IndexableMixin, SchemaType, BaseExtraProperties
from chord_metadata_service.restapi.schemas import TIME_ELEMENT_SCHEMA
from chord_metadata_service.restapi.validators import JsonSchemaValidator, ontology_validator
from .values import PatientStatus, Sex, KaryotypicSex


class VitalStatus(BaseTimeStamp, IndexableMixin):

    VITAL_STATUS = PatientStatus.as_django_values()
    status = models.CharField(choices=VITAL_STATUS, max_length=200, blank=True, null=False)
    time_of_death = models.JSONField(blank=True, null=True,
                                     validators=[JsonSchemaValidator(TIME_ELEMENT_SCHEMA)],
                                     help_text="Should be left blank if patient not known to be deceased")
    cause_of_death = JSONField(blank=True, null=True, validators=[ontology_validator],
                               help_text='Should be left blank if patient not known to be deceased')
    survival_time_in_days = models.IntegerField(blank=True, null=True, help_text="Number of days the patient was alive"
                                                                                 " after their primary diagnosis")


class Individual(BaseExtraProperties, BaseTimeStamp, IndexableMixin):
    """ Class to store demographic information about an Individual (Patient) """

    @property
    def schema_type(self) -> SchemaType:
        return SchemaType.INDIVIDUAL

    def get_project_id(self) -> Optional[str]:
        if not self.phenopackets.count():
            # Need to wait for phenopacket to exist
            return None
        model = apps.get_model("chord.Project")
        try:
            project = model.objects.get(datasets=self.phenopackets.first().dataset_id)
        except model.DoesNotExist:
            return None
        return project.identifier

    SEX = Sex.as_django_values()
    KARYOTYPIC_SEX = KaryotypicSex.as_django_values()

    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for the individual.')
    # TODO check for CURIE
    alternate_ids = ArrayField(models.CharField(max_length=200), blank=True, null=True,
                               help_text='A list of alternative identifiers for the individual.')
    date_of_birth = models.DateField(null=True, blank=True, help_text='A timestamp either exact or imprecise.')

    # Computed at ingestion
    age_numeric = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True,
                                      help_text='The age of the individual as number.')
    age_unit = models.CharField(max_length=50, blank=True, help_text='The unit for measuring age.')

    time_at_last_encounter = models.JSONField(blank=True, null=True,
                                              validators=[JsonSchemaValidator(TIME_ELEMENT_SCHEMA)],
                                              help_text="TimeElement of the patient when last encountered.")

    vital_status = models.OneToOneField(VitalStatus, blank=True, null=True, on_delete=models.CASCADE,
                                        help_text="The vital status of the individual e.g. whether they are alive or"
                                                  " the time and cause of death")

    sex = models.CharField(choices=SEX, max_length=200, blank=True, null=True,
                           help_text='Observed apparent sex of the individual.')
    karyotypic_sex = models.CharField(choices=KARYOTYPIC_SEX, max_length=200, default=KaryotypicSex.UNKNOWN_KARYOTYPE,
                                      help_text='The karyotypic sex of the individual.')
    taxonomy = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text='Ontology resource representing the species (e.g., NCBITaxon:9615).')

    # FHIR specific
    active = models.BooleanField(default=False, help_text='Whether this patient\'s record is in active use.')
    deceased = models.BooleanField(default=False, help_text='Indicates if the individual is deceased or not.')

    # extra
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')

    def __str__(self):
        return str(self.id)
