from django.db import models
from django.db.models import CharField, JSONField
from django.contrib.postgres.fields import ArrayField
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.validators import ontology_list_validator, key_value_validator
from chord_metadata_service.phenopackets.models import Biosample
import chord_metadata_service.experiments.descriptions as d

__all__ = ["Experiment", "ExperimentResult", "Instrument"]


# The experiment class here is primarily designed for *genomic* experiments - thus the need for a biosample ID. If, in
# the future, medical imaging or something which isn't sample-based is desired, it may be best to create a separate
# model for the desired purposes.


class Experiment(models.Model, IndexableMixin):
    """ Class to store Experiment information """

    id = CharField(primary_key=True, max_length=200, help_text=rec_help(d.EXPERIMENT, "id"))
    # STUDY TYPE
    # ["Whole Genome Sequencing","Metagenomics","Transcriptome Analysis","Resequencing","Epigenetics",
    # "Synthetic Genomics","Forensic or Paleo-genomics","Gene Regulation Study","Cancer Genomics",
    # "Population Genomics","RNASeq","Pooled Clone Sequencing","Transcriptome Sequencing","Other"]
    study_type = CharField(max_length=200, blank=True, null=True, help_text=rec_help(d.EXPERIMENT, "study_type"))
    # TYPE
    experiment_type = CharField(max_length=200, help_text=rec_help(d.EXPERIMENT, "experiment_type"))
    experiment_ontology = JSONField(blank=True, default=list, validators=[ontology_list_validator],
                                    help_text=rec_help(d.EXPERIMENT, "experiment_ontology"))
    # MOLECULE
    molecule = CharField(max_length=200, blank=True, null=True, help_text=rec_help(d.EXPERIMENT, "molecule"))
    molecule_ontology = JSONField(blank=True, default=list, validators=[ontology_list_validator],
                                  help_text=rec_help(d.EXPERIMENT, "molecule_ontology"))
    # LIBRARY
    library_strategy = CharField(max_length=200, blank=True, null=True,
                                 help_text=rec_help(d.EXPERIMENT, "library_strategy"))
    library_source = CharField(max_length=200, blank=True, null=True,
                               help_text=rec_help(d.EXPERIMENT, "library_source"))
    library_selection = CharField(max_length=200, blank=True, null=True,
                                  help_text=rec_help(d.EXPERIMENT, "library_selection"))
    library_layout = CharField(max_length=200, blank=True, null=True,
                               help_text=rec_help(d.EXPERIMENT, "library_layout"))
    extraction_protocol = CharField(max_length=200, blank=True, null=True,
                                    help_text=rec_help(d.EXPERIMENT, "extraction_protocol"))
    reference_registry_id = CharField(max_length=200, blank=True, null=True,
                                      help_text=rec_help(d.EXPERIMENT, "reference_registry_id"))
    qc_flags = ArrayField(CharField(max_length=200, help_text=rec_help(d.EXPERIMENT, "qc_flags")),
                          blank=True, default=list)
    # SAMPLE
    biosample = models.ForeignKey(Biosample, on_delete=models.CASCADE, help_text=rec_help(d.EXPERIMENT, "biosample"))
    table = models.ForeignKey("chord.Table", on_delete=models.CASCADE, blank=True, null=True)  # TODO: Help text
    # EXPERIMENT RESULT
    experiment_results = models.ManyToManyField("ExperimentResult", blank=True,
                                                help_text=rec_help(d.EXPERIMENT, "experiment_results"))
    # INTSRUMENT
    instrument = models.ForeignKey("Instrument", blank=True, null=True, on_delete=models.CASCADE,
                                   help_text=rec_help(d.EXPERIMENT, "instrument"))
    # EXTRA
    extra_properties = JSONField(blank=True, default=dict, validators=[key_value_validator],
                                 help_text=rec_help(d.EXPERIMENT, "extra_properties"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class ExperimentResult(models.Model, IndexableMixin):
    """ Class to represent information about analysis of sequencing data in a file format. """
    # TODO identifier assigned by lab (?)
    identifier = CharField(max_length=200, blank=True, null=True,
                           help_text=rec_help(d.EXPERIMENT_RESULT, "identifier"))
    description = CharField(max_length=500, blank=True, null=True,
                            help_text=rec_help(d.EXPERIMENT_RESULT, "description"))
    filename = CharField(max_length=500, blank=True, null=True,
                         help_text=rec_help(d.EXPERIMENT_RESULT, "filename"))
    genome_assembly_id = CharField(max_length=50, blank=True, null=True,
                                   help_text=rec_help(d.EXPERIMENT_RESULT, "genome_assembly_id"))
    file_format = CharField(max_length=50, blank=True, null=True,
                            help_text=rec_help(d.EXPERIMENT_RESULT, "file_format"))
    data_output_type = CharField(max_length=200, blank=True, null=True,
                                 help_text=rec_help(d.EXPERIMENT_RESULT, "data_output_type"))
    usage = CharField(max_length=200, blank=True, null=True,
                      help_text=rec_help(d.EXPERIMENT_RESULT, "usage"))
    creation_date = CharField(max_length=500, blank=True, null=True,
                              help_text=rec_help(d.EXPERIMENT_RESULT, "creation_date"))
    created_by = CharField(max_length=200, blank=True, null=True,
                           help_text=rec_help(d.EXPERIMENT_RESULT, "created_by"))
    extra_properties = JSONField(blank=True, default=dict, validators=[key_value_validator],
                                 help_text=rec_help(d.EXPERIMENT_RESULT, "extra_properties"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.identifier)


class Instrument(models.Model, IndexableMixin):
    """ Class to represent information about instrument used to perform a sequencing experiment. """

    # TODO identifier assigned by lab (?)
    identifier = CharField(max_length=200, blank=True, null=True,
                           help_text=rec_help(d.EXPERIMENT_RESULT, "identifier"))
    platform = CharField(max_length=200, blank=True, null=True, help_text=rec_help(d.INSTRUMENT, "platform"))
    description = CharField(max_length=500, blank=True, null=True, help_text=rec_help(d.INSTRUMENT, "description"))
    model = CharField(max_length=500, blank=True, null=True, help_text=rec_help(d.INSTRUMENT, "model"))
    extra_properties = JSONField(blank=True, default=dict, validators=[key_value_validator],
                                 help_text=rec_help(d.INSTRUMENT, "extra_properties"))
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
