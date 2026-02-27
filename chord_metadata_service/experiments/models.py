from django.contrib.postgres.indexes import GinIndex
from django.db import models
from django.db.models import CharField, JSONField
from django.contrib.postgres.fields import ArrayField
from chord_metadata_service.discovery.full_text_search import BaseFTSModel, ToFTSReprMixin
from chord_metadata_service.discovery.scopeable_model import (
    BaseScopeableModel,
    TOP_LEVEL_MODEL_SCOPE_FILTERS,
)
from chord_metadata_service.discovery.types import ModelScopeFilters
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.validators import (
    ontology_validator,
    base_extra_properties_validator,
)
from chord_metadata_service.phenopackets.models import Biosample

from . import descriptions as d
from .validators import file_index_list_validator

__all__ = ["Experiment", "ExperimentResult", "Instrument"]


# The experiment class here is primarily designed for *genomic* experiments - thus the need for a biosample ID. If, in
# the future, medical imaging or something which isn't sample-based is desired, it may be best to create a separate
# model for the desired purposes.


class Experiment(BaseScopeableModel, BaseFTSModel, IndexableMixin):
    """
    Class to store Experiment information. This model is primarily designed for genomic experiments; it is thus
    linked to a specific biosample.

    Experiments can be linked via a many-to-many relationship to ExperimentResults; many-to-many because a result
    may be derived from multiple experiments. Consider, for example, the results of a pairwise analysis derived from
    two Experiments, each of which was performed on a different Biosample.
    """

    class Meta:
        indexes = [
            GinIndex(name="exp_id_trgm_idx", fields=["id"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_desc_trgm_idx", fields=["description"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_study_type_trgm_idx", fields=["study_type"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_experiment_type_trgm_idx", fields=["experiment_type"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_molecule_trgm_idx", fields=["molecule"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_lib_strategy_trgm_idx", fields=["library_strategy"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_lib_source_trgm_idx", fields=["library_source"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_lib_selection_trgm_idx", fields=["library_selection"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_lib_layout_trgm_idx", fields=["library_layout"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_lib_id_trgm_idx", fields=["library_id"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_lib_extract_id_trgm_idx", fields=["library_extract_id"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_extract_proto_trgm_idx", fields=["extraction_protocol"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_protocol_url_trgm_idx", fields=["protocol_url"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="exp_ref_registry_id_trgm_idx", fields=["reference_registry_id"], opclasses=["gin_trgm_ops"]),
            BaseFTSModel.get_fts_extra_trgm_index("exp"),
        ]

    @staticmethod
    def get_scope_filters() -> ModelScopeFilters:
        return TOP_LEVEL_MODEL_SCOPE_FILTERS

    id = CharField(primary_key=True, max_length=200, help_text=rec_help(d.EXPERIMENT, "id"))
    # STUDY TYPE
    # ["Whole Genome Sequencing","Metagenomics","Transcriptome Analysis","Resequencing","Epigenetics",
    # "Synthetic Genomics","Forensic or Paleo-genomics","Gene Regulation Study","Cancer Genomics",
    # "Population Genomics","RNASeq","Pooled Clone Sequencing","Transcriptome Sequencing","Other"]
    study_type = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "study_type"),
    )
    # TYPE
    experiment_type = CharField(max_length=200, help_text=rec_help(d.EXPERIMENT, "experiment_type"))
    experiment_ontology = JSONField(
        blank=True,
        null=True,
        validators=[ontology_validator],
        help_text=rec_help(d.EXPERIMENT, "experiment_ontology"),
    )
    # MOLECULE
    molecule = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "molecule"),
    )
    molecule_ontology = JSONField(
        blank=True,
        null=True,
        validators=[ontology_validator],
        help_text=rec_help(d.EXPERIMENT, "molecule_ontology"),
    )
    # LIBRARY
    library_strategy = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "library_strategy"),
    )
    library_source = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "library_source"),
    )
    library_selection = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "library_selection"),
    )
    library_layout = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "library_layout"),
    )
    library_id = CharField(max_length=200, null=True, blank=True, help_text=rec_help(d.EXPERIMENT, "library_id"))
    library_extract_id = CharField(
        max_length=200, null=True, blank=True, help_text=rec_help(d.EXPERIMENT, "library_extract_id")
    )
    library_description = models.TextField(
        null=True, blank=True, help_text=rec_help(d.EXPERIMENT, "library_description")
    )
    extraction_protocol = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "extraction_protocol"),
    )
    reference_registry_id = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "reference_registry_id"),
    )
    qc_flags = ArrayField(
        CharField(max_length=200, help_text=rec_help(d.EXPERIMENT, "qc_flags")),
        blank=True,
        default=list,
    )
    insert_size = models.IntegerField(null=True, blank=True, help_text=rec_help(d.EXPERIMENT, "insert_size"))
    protocol_url = models.URLField(
        max_length=500, null=True, blank=True, help_text=rec_help(d.EXPERIMENT, "protocol_url")
    )
    # SAMPLE
    biosample = models.ForeignKey(
        Biosample,
        on_delete=models.CASCADE,
        related_name="experiments",
        help_text=rec_help(d.EXPERIMENT, "biosample"),
    )
    dataset = models.ForeignKey(
        "chord.Dataset",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="experiments",
    )  # TODO: Help text

    # EXPERIMENT RESULT
    #  - Many-to-many because experiment results can contain analyses involving multiple experiments,
    #    e.g., a pairwise analysis
    experiment_results = models.ManyToManyField(
        "experiments.ExperimentResult",
        blank=True,
        help_text=rec_help(d.EXPERIMENT, "experiment_results"),
        related_name="experiments",
    )
    # INSTRUMENT
    instrument = models.ForeignKey(
        "experiments.Instrument",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT, "instrument"),
        related_name="experiments",
    )
    # EXPERIMENT DESCRIPTION
    description = models.TextField(blank=True, null=True, help_text=rec_help(d.EXPERIMENT, "description"))
    # EXTRA
    extra_properties = JSONField(
        blank=True,
        default=dict,
        validators=[base_extra_properties_validator],
        help_text=rec_help(d.EXPERIMENT, "extra_properties"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------------------------------------------------------

    def get_fts_extra(self) -> tuple:
        # avoid circular 'dependencies' here - don't include biosample
        return (self.instrument,)

    def save(self, *args, **kwargs):
        self.populate_fts_extra()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)


class ExperimentResult(BaseScopeableModel, BaseFTSModel, IndexableMixin):
    class Meta:
        indexes = [
            GinIndex(name="expres_identifier_trgm_idx", fields=["identifier"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_description_trgm_idx", fields=["description"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_filename_trgm_idx", fields=["filename"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_url_trgm_idx", fields=["url"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_asm_id_trgm_idx", fields=["genome_assembly_id"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_file_format_trgm_idx", fields=["file_format"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_data_output_trgm_idx", fields=["data_output_type"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_usage_trgm_idx", fields=["usage"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_creation_date_trgm_idx", fields=["creation_date"], opclasses=["gin_trgm_ops"]),
            GinIndex(name="expres_created_by_trgm_idx", fields=["created_by"], opclasses=["gin_trgm_ops"]),
            BaseFTSModel.get_fts_extra_trgm_index("expres"),
        ]

    @staticmethod
    def get_scope_filters() -> ModelScopeFilters:
        return {
            "base_prefetch_related": ("experiments", "experiments__dataset"),
            "project": {
                "filter": "experiments__dataset__project_id",
            },
            "dataset": {
                "filter": "experiments__dataset_id",
            },
        }

    """ Class to represent information about analysis of sequencing data in a file format. """
    # TODO identifier assigned by lab (?)
    identifier = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "identifier"),
    )
    description = CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "description"),
    )
    filename = CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "filename"),
    )
    # URLs:
    #  - one file for the experiment result file proper
    url = CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "url"),
    )
    #  - an array of index file objects (e.g., FAI, Tabix, Tribble, BGZF), formatted like
    #    { "url": "...", "format": "FAI" | "TABIX" | "TRIBBLE " | ... }
    indices = JSONField(
        blank=True,
        default=list,
        validators=[file_index_list_validator],
        help_text=rec_help(d.EXPERIMENT_RESULT, "indices"),
    )

    genome_assembly_id = CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "genome_assembly_id"),
    )
    file_format = CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "file_format"),
    )
    data_output_type = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "data_output_type"),
    )
    usage = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "usage"),
    )
    creation_date = CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "creation_date"),
    )
    created_by = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "created_by"),
    )
    extra_properties = JSONField(
        blank=True,
        default=dict,
        validators=[base_extra_properties_validator],
        help_text=rec_help(d.EXPERIMENT_RESULT, "extra_properties"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # ------------------------------------------------------------------------------------------------------------------

    def save(self, *args, **kwargs):
        self.populate_fts_extra()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.identifier)


class Instrument(models.Model, IndexableMixin, ToFTSReprMixin):
    """Class to represent information about instrument used to perform a sequencing experiment."""

    # TODO identifier assigned by lab (?)
    identifier = CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text=rec_help(d.EXPERIMENT_RESULT, "identifier"),
    )
    device = CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=rec_help(d.INSTRUMENT, "device"),
    )
    device_ontology = JSONField(
        blank=True,
        null=True,
        validators=[ontology_validator],
        help_text=rec_help(d.INSTRUMENT, "device_ontology"),
    )
    description = CharField(
        max_length=500,
        blank=True,
        null=True,
        help_text=rec_help(d.INSTRUMENT, "description"),
    )
    extra_properties = JSONField(
        blank=True,
        default=dict,
        validators=[base_extra_properties_validator],
        help_text=rec_help(d.INSTRUMENT, "extra_properties"),
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    def fts_repr_values(self) -> tuple:
        return self.identifier, self.device, self.device_ontology, self.description, self.extra_properties
