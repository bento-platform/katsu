from django.db import models
from django.db.models import CharField
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.validators import JsonSchemaValidator
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS_LIST, KEY_VALUE_OBJECT
import chord_metadata_service.experiments.descriptions as d

ontologyListValidator = JsonSchemaValidator(ONTOLOGY_CLASS_LIST)
keyValueValidator     = JsonSchemaValidator(KEY_VALUE_OBJECT)

class Experiment(models.Model, IndexableMixin):
    """ Class to store Experiment information """

    LIBRARY_STRATEGY = (
        ('DNase-Hypersensitivity', 'DNase-Hypersensitivity'),
        ('ATAC-seq', 'ATAC-seq'),
        ('NOME-Seq', 'NOME-Seq'),
        ('Bisulfite-Seq', 'Bisulfite-Seq'),
        ('MeDIP-Seq', 'MeDIP-Seq'),
        ('MRE-Seq', 'MRE-Seq'),
        ('ChIP-Seq', 'ChIP-Seq'),
        ('RNA-Seq', 'RNA-Seq'),
        ('miRNA-Seq', 'miRNA-Seq'),
        ('WGS', 'WGS'),
    )

    MOLECULE = (
        ('total RNA', 'total RNA'),
        ('polyA RNA', 'polyA RNA'),
        ('cytoplasmic RNA', 'cytoplasmic RNA'),
        ('nuclear RNA', 'nuclear RNA'),
        ('small RNA', 'small RNA'),
        ('genomic DNA', 'genomic DNA'),
        ('protein', 'protein'),
        ('other', 'other'),
    )

    id = CharField(primary_key=True, max_length=200, help_text=rec_help(d.EXPERIMENT, 'id'))

    reference_registry_id = CharField(max_length=30, null=True, blank=True, help_text=rec_help(d.EXPERIMENT, 'reference_registry_id'))
    qc_flags = ArrayField(CharField(max_length=100, help_text=rec_help(d.EXPERIMENT, 'qc_flags')), null=True, default=list)
    experiment_type = CharField(max_length=30, null=True, blank=True, help_text=rec_help(d.EXPERIMENT, 'experiment_type'))
    experiment_ontology = JSONField(null=True, blank=True, validators=[ontologyListValidator], help_text=rec_help(d.EXPERIMENT, 'experiment_ontology'))
    molecule_ontology = JSONField(null=True, blank=True, validators=[ontologyListValidator], help_text=rec_help(d.EXPERIMENT, 'molecule_ontology'))
    molecule = CharField(choices=MOLECULE, max_length=20, null=True, blank=True, help_text=rec_help(d.EXPERIMENT, 'molecule'))

    library_strategy = CharField(choices=LIBRARY_STRATEGY, max_length=25, null=False, blank=False, help_text=rec_help(d.EXPERIMENT, 'library_strategy'))

    other_fields = JSONField(blank=True, null=True, validators=[keyValueValidator], help_text=rec_help(d.EXPERIMENT, 'other_fields'))

    def __str__(self):
        return str(self.id)
