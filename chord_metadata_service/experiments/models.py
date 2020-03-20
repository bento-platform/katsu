from django.db import models
from django.core.validators import RegexValidator
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.restapi.models import IndexableMixin


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
        ('polyA RNA', 'polyA RNA')
        ('cytoplasmic RNA', 'cytoplasmic RNA')
        ('nuclear RNA', 'nuclear RNA')
        ('small RNA', 'small RNA')
        ('genomic DNA', 'genomic DNA')
        ('protein', 'protein')
        ('other', 'other')
    )

    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for the individual.')

    # FIXME(validate qc_flags.max_length)
    # FIXME(validate experiment_ontology_curie.max_length)
    # FIXME(validate molecule_ontology_curie.max_length)

    reference_registry_id = models.CharField(max_length=30, null=True, blank=True, help_text='The IHEC EpiRR ID for this dataset, only for IHEC Reference Epigenome datasets. Otherwise leave empty.')
    qc_flags = models.CharField(max_length=30, null=True, blank=True, help_text='Any quanlity control observations can be noted here. This field can be omitted if empty')
    experiment_type = models.CharField(max_length=30, null=True, blank=True, help_text="(Controlled Vocabulary) The assay target (e.g. ‘DNA Methylation’, ‘mRNA-Seq’, ‘smRNA-Seq’, 'Histone H3K4me1').")
    experiment_ontology_curie = models.CharField(max_length=30, null=True, blank=True,
            validators=[RegexValidator(regex="^[A-Za-z]*:[A-Za-z0-9]*")],
            help_text="(Ontology: OBI) links to experiment ontology information.")
    molecule_ontology_curie = models.CharField(max_length=30, null=True, blank=True,
            validators=[RegexValidator(regex="^[A-Za-z]*:[A-Za-z0-9]*")],
            help_text="(Ontology: SO) links to molecule ontology information.")
    molecule = models.CharField(choices=MOLECULE, max_length=20, null=True, blank=True,
            help_text="(Controlled Vocabulary) The type of molecule that was extracted from the biological material. Include one of the following: total RNA, polyA RNA, cytoplasmic RNA, nuclear RNA, small RNA, genomic DNA, protein, or other.")

    library_strategy = models.CharField(choices=LIBRARY_STRATEGY, max_length=25, null=False, blank=False,
            help_text="(Controlled Vocabulary) The assay used. These are defined within the SRA metadata specifications with a controlled vocabulary (e.g. ‘Bisulfite-Seq’, ‘RNA-Seq’, ‘ChIP-Seq’). For a complete list, see https://www.ebi.ac.uk/ena/submit/reads-library-strategy.")

    def __str__(self):
        return str(self.id)
