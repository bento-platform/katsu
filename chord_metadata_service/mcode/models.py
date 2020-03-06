from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.phenopackets.models import Gene
from django.core.exceptions import ValidationError


################################# Genomics #################################

class GeneticVariantTested(models.Model, IndexableMixin):
    """
    The class records an alteration in the most common DNA nucleotide sequence.
    """

    # TODO Discuss: Connection to Gene from Phenopackets
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the genetic variant tested.')
    gene_studied = models.ForeignKey(Gene, blank=True, null=True,
                                     help_text='A gene targeted for mutation analysis, '
                                               'identified in HUGO Gene Nomenclature Committee (HGNC) notation. ')
    method = JSONField(blank=True, null=True, help_text='An ontology or controlled vocabulary term to indetify '
                                                        'the method used to perform the genetic test. '
                                                        'Accepted value set: NCIT')
    variant_tested_identifier = JSONField(blank=True, null=True,
                                         help_text='The variation ID assigned by HGVS, for example, '
                                                   '360448 is the identifier for NM_005228.4(EGFR):c.-237A>G '
                                                   '(single nucleotide variant in EGFR).')
    variant_tested_hgvs_name = ArrayField(models.CharField(max_length=200), blank=True, null=True,
                                         help_text='Symbolic representation of the variant used in HGVS, for example, '
                                         'NM_005228.4(EGFR):c.-237A>G for HVGS variation ID 360448.')
    variant_tested_description = models.CharField(max_length=200, blank=True,
                                                 help_text='Description of the variant.')
    data_value = JSONField(blank=True, null=True,
                           help_text='An ontology or controlled vocabulary term to indetify '
                                     'positive or negative value for the mutation. Accepted value set: SNOMED CT.')

    def __str__(self):
        return str(self.id)

    def clean(self):
        if not (self.variant_tested_identifier or self.variant_tested_hgvs_name or self.variant_tested_description):
            raise ValidationError('At least one element out of the following must be reported: '
                                  'Variant Tested Identifier, Variant Tested HGVS Name, and Variant Tested Description')


class GeneticVariantFound(models.Model, IndexableMixin):
    """
    The class records whether a single discrete variant tested is present
    or absent (denoted as positive or negative respectively).
    """

    # TODO Discuss: Connection to Gene from Phenopackets
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the genetic variant found.')
    method = JSONField(blank=True, null=True, help_text='An ontology or controlled vocabulary term to indetify '
                                                        'the method used to perform the genetic test. '
                                                        'Accepted value set: NCIT')

    variant_found_identifier = JSONField(blank=True, null=True,
                                         help_text='The variation ID assigned by HGVS, for example, 360448 is the identifier '
                                                   'for NM_005228.4(EGFR):c.-237A>G (single nucleotide variant in EGFR). '
                                                   'Accepted value set: ClinVar.')
    variant_found_hgvs_name = ArrayField(models.CharField(max_length=200), blank=True, null=True,
                                        help_text='Symbolic representation of the variant used in HGVS, '
                                                    'for example, NM_005228.4(EGFR):c.-237A>G for HVGS variation ID 360448.')
    variant_found_description = models.CharField(max_length=200, blank=True,
                                                 help_text='Description of the variant.')
    genomic_source_class = JSONField(blank=True, null=True,
                                     help_text='An ontology or controlled vocabulary term to indetify '
                                               'the genomic class of the specimen being analyzed.')

    def __str__(self):
        return str(self.id)

    def clean(self):
        if not (self.variant_found_identifier or self.variant_found_hgvs_name or self.variant_found_description):
            raise ValidationError('At least one element out of the following must be reported: '
                                  'Variant Found Identifier, Variant Found HGVS Name, and Variant Found Description')


class GenomicsReport(models.Model, IndexableMixin):
    """
    Genetic Analysis Summary
    """

    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the genetics report.')
    test_name = JSONField(help_text='An ontology or controlled vocabulary term to identify the laboratory test.'
                                    'Accepted value sets: LOINC, GTR')
    performing_ogranization_name = models.CharField(max_length=200, blank=True,
                                                    help_text='The name of the organization '
                                                              'producing the genomics report.')
    specimen_type = JSONField(blank=True, null=True,
                              help_text='An ontology or controlled vocabulary term to indetify the type of '
                                        'material the specimen contains or consists of.'
                                        'Accepted value set: HL7 Version 2 and Specimen Type.')
    genetic_variant_tested = models.ManyToManyField(GeneticVariantTested, blank=True, null=True,
                                                    help_text='A test for a specific mutation on a particular gene.')
    genetic_variant_found = models.ManyToManyField(GeneticVariantFound, blank=True, null=True,
                                                   help_text='Records an alteration in the most common DNA '
                                                             'nucleotide sequence.')

    def __str__(self):
        return str(self.id)
