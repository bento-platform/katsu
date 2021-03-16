from django.db import models
from django.db.models import CharField
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.validators import ontology_list_validator, key_value_validator
from chord_metadata_service.phenopackets.models import Biosample
import chord_metadata_service.experiments.descriptions as d


__all__ = ["Experiment"]


# The experiment class here is primarily designed for *genomic* experiments - thus the need for a biosample ID. If, in
# the future, medical imaging or something which isn't sample-based is desired, it may be best to create a separate
# model for the desired purposes.


class Experiment(models.Model, IndexableMixin):
    """ Class to store Experiment information """

    id = CharField(primary_key=True, max_length=200, help_text=rec_help(d.EXPERIMENT, 'id'))
    experiment_type = CharField(max_length=200, help_text=rec_help(d.EXPERIMENT, 'experiment_type'))
    experiment_ontology = JSONField(blank=True, default=list, validators=[ontology_list_validator],
                                    help_text=rec_help(d.EXPERIMENT, 'experiment_ontology'))
    molecule = CharField(max_length=200, blank=True, null=True, help_text=rec_help(d.EXPERIMENT, 'molecule'))
    molecule_ontology = JSONField(blank=True, default=list, validators=[ontology_list_validator],
                                  help_text=rec_help(d.EXPERIMENT, 'molecule_ontology'))
    library_strategy = CharField(max_length=200, blank=True, null=True,
                                 help_text=rec_help(d.EXPERIMENT, 'library_strategy'))
    extraction_protocol = CharField(max_length=200, blank=True, null=True,
                                    help_text=rec_help(d.EXPERIMENT, 'extraction_protocol'))
    file_location = CharField(max_length=500, blank=True, null=True,
                              help_text=rec_help(d.EXPERIMENT, 'file_location'))
    reference_registry_id = CharField(max_length=200, blank=True, null=True,
                                      help_text=rec_help(d.EXPERIMENT, 'reference_registry_id'))
    qc_flags = ArrayField(CharField(max_length=200, help_text=rec_help(d.EXPERIMENT, 'qc_flags')),
                          blank=True, default=list)
    extra_properties = JSONField(blank=True, default=dict, validators=[key_value_validator],
                                 help_text=rec_help(d.EXPERIMENT, 'extra_properties'))
    biosample = models.ForeignKey(Biosample, on_delete=models.CASCADE, help_text=rec_help(d.EXPERIMENT, 'biosample'))
    table = models.ForeignKey("chord.Table", on_delete=models.CASCADE, blank=True, null=True)  # TODO: Help text

    def __str__(self):
        return str(self.id)
