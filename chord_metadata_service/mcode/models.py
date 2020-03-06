from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.phenopackets.models import Gene
from chord_metadata_service.patients.models import Individual
from django.core.exceptions import ValidationError

#TODO MOVE all help_text in sep doc

################################# Genomics #################################


class GeneticVariantTested(models.Model, IndexableMixin):
    """
    Class  to record an alteration in the most common DNA nucleotide sequence.
    """

    # TODO Discuss: Connection to Gene from Phenopackets
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the genetic variant tested.')
    gene_studied = models.ForeignKey(Gene, blank=True, null=True, on_delete=models.SET_NULL,
                                     help_text='A gene targeted for mutation analysis, '
                                               'identified in HUGO Gene Nomenclature Committee (HGNC) notation.')
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
    Class to record whether a single discrete variant tested is present
    or absent (denoted as positive or negative respectively).
    """

    # TODO Discuss: Connection to Gene from Phenopackets
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the genetic variant found.')
    method = JSONField(blank=True, null=True, help_text='An ontology or controlled vocabulary term to indetify '
                                                        'the method used to perform the genetic test. '
                                                        'Accepted value set: NCIT')

    variant_found_identifier = JSONField(blank=True, null=True,
                                         help_text='The variation ID assigned by HGVS, for example, 360448 is the'
                                                   ' identifier for NM_005228.4(EGFR):c.-237A>G (single nucleotide '
                                                   'variant in EGFR). Accepted value set: ClinVar.')
    variant_found_hgvs_name = ArrayField(models.CharField(max_length=200), blank=True, null=True,
                                         help_text='Symbolic representation of the variant used in HGVS, for example, '
                                                   'NM_005228.4(EGFR):c.-237A>G for HVGS variation ID 360448.')
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


################################# Labs/Vital #################################


class LabsVital(models.Model, IndexableMixin):
    """
    Class  to record tests performed on patient.
    """

    # TODO the data value should be in form of Quantity datatype - ADD json schema for Quantity
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the labs/vital tests.')
    individual = models.ForeignKey(Individual, on_delete=models.CASCADE,
                                   help_text='The individual who is the subject of the tests.')
    body_height = JSONField(help_text='The patient\'s height.')
    body_weight = JSONField(help_text='The patient\'s weight.')
    cbc_with_auto_differential_panel = ArrayField(models.CharField(max_length=200), blank=True, null=True,
                                                  help_text='Reference to a laboratory observation in the CBC with'
                                                            ' Auto Differential Panel test. ')
    comprehensive_metabolic_2000 = ArrayField(models.CharField(max_length=200), blank=True, null=True,
                                              help_text='Reference to a laboratory observation in the CMP 2000 test.')
    blood_pressure_diastolic = JSONField(blank=True, null=True,
                                         help_text='The blood pressure after the contraction of the heart while the '
                                                   'chambers of the heart refill with blood, when the pressure is lowest.')
    blood_pressure_systolic = JSONField(blank=True, null=True,
                                        help_text='The blood pressure during the contraction of the left '
                                                  'ventricle of the heart, when blood pressure is at its highest.')
    #TODO Ontology or Quantity or Ratio (?)
    tumor_marker_test = JSONField(help_text='An ontology or controlled vocabulary term to indetify tumor marker test.')

    def __str__(self):
        return str(self.id)

    def clean(self):
        if not (self.blood_pressure_diastolic or self.blood_pressure_systolic):
            raise ValidationError('At least one of the following must be reported: Systolic Blood Pressure or'
                                  'Diastolic Blood Pressure.')


################################# Treatment #################################

###### Procedure ######

class CancerRelatedProcedure(models.Model, IndexableMixin):
    """
    Class to represent radiological treatment or surgical action addressing a cancer condition.
    """

    PROCEDURE_TYPES = (
        ('radiation', 'radiation'),
        ('surgical', 'surgical')
    )
    #TODO Ontology class
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the procedure.')
    procedure_type = models.CharField(choices=PROCEDURE_TYPES, help_text='Type of cancer related procedure: '
                                                                         'radion or surgical procedure.')
    #Ontology
    code = JSONField(help_text='Code for the procedure performed.')
    #DateTime or Ontology
    occurence_time_or_period = JSONField(help_text='The date/time that a procedure was performed.')
    #List of Ontologies
    target_body_site = ArrayField(JSONField(null=True, blank=True), blank=True, null=True,
                                  help_text='The body location(s) where the procedure was performed.')
    #Ontology
    treatment_intent = JSONField(blank=True, null=True, help_text='The purpose of a treatment.')

    def __str__(self):
        return str(self.id)

###### Medication Statement ######

class MedicationStatement(models.Model, IndexableMixin):
    """
    Class to record the use of a medication.
    """

    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the medication statement.')
    medication_code = JSONField(help_text='A code for medication. Accepted code systems:'
                                          'Medication Clinical Drug (RxNorm) and other.')
    # List of Ontologies
    termination_reason = ArrayField(JSONField(null=True, blank=True), blank=True, null=True,
                                  help_text='A code explaining unplanned or premature termination of a course of'
                                            'medication. Accepted ontologies: SNOMED CT.')
    #Ontology
    treatment_intent = JSONField(blank=True, null=True, help_text='The purpose of a treatment.'
                                                                  'Accepted ontologies: SNOMED CT.')
    start_date = models.DateTimeField(blank=True, null=True, help_text='The start date/time of the medication.')
    end_date = models.DateTimeField(blank=True, null=True, help_text='The end date/time of the medication.')
    date_time = models.DateTimeField(blank=True, null=True, help_text='The date/time the medication was administered.')

    def __str__(self):
        return str(self.id)


class CancerCondition(models.Model, IndexableMixin):
    """
    Class to record the history of primary or secondary cancer conditions.
    """
    CANCER_CONDITION_TYPE = (
        ('primary', 'primary'),
        ('secondary', 'secondary')
    )
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the cancer condition.')
    condition_type = models.CharField(choices=CANCER_CONDITION_TYPE,
                                      help_text='Cancer condition type: primary or secondary.')
    body_location_code = ArrayField(JSONField(null=True, blank=True), blank=True, null=True,
                                  help_text='Code for the body location, optionally pre-coordinating laterality '
                                            'or direction. Accepted ontologies: SNOMED CT, ICD-O-3 and others.')
    clinical_status = JSONField(blank=True, null=True,
                                help_text='A flag indicating whether the condition is active '
                                          'or inactive, recurring, in remission, or resolved (as of the last update '
                                          'of the Condition). Accepted code system: '
                                          'http://terminology.hl7.org/CodeSystem/condition-clinical')
    condition_code = JSONField(help_text='A code describing the type of primary or secondary malignant '
                                         'neoplastic disease.')
    date_of_diagnosis = models.DateTimeField(blank=True, null=True,
                                             help_text='The date the disease was first clinically recognized with '
                                                       'sufficient certainty, regardless of whether it was fully '
                                                       'characterized at that time.')
    histology_morphology_behavior = JSONField(blank=True, null=True,
                                              help_text='A description of the morphologic and behavioral '
                                                        'characteristics of the cancer. Accepted ontologies:'
                                                        'SNOMED CT, ICD-O-3 and others.')

    def __str__(self):
        return str(self.id)


class TNMStaging(models.Model, IndexableMixin):
    """
    Class to describe the spread of cancer in a patient’s body.
    """
    id = models.CharField(primary_key=True, max_length=200,
                          help_text='An arbitrary identifier for the TNM staging.')
    #TODO Extended Ontology class: stage group - required and staging system - not required
    clinical_stage_group = JSONField(help_text='The extent of the cancer in the body, according to the TNM '
                                               'classification system. Accepted ontologies: SNOMED CT, AJCC and others.')
    clinical_primary_tumor_category = JSONField(help_text='Category of the primary tumor, based on its size and '
                                                          'extent, assessed prior to surgery, based on evidence '
                                                          'such as physical examination, imaging, and/or biopsy.'
                                                          'Accepted ontologies: SNOMED CT, AJCC and others.')
    clinical_regional_nodes_category = JSONField(help_text='Category of the presence or absence of metastases in '
                                                           'regional lymph nodes, assessed using tests that are '
                                                           'done before surgery. Accepted ontologies: '
                                                           'SNOMED CT, AJCC and others.')
    clinical_distant_metastases_category = JSONField(help_text='Category describing the presence or absence of '
                                                               'metastases in remote anatomical locations, assessed '
                                                               'using tests that are done before surgery. '
                                                               'Accepted ontologies: SNOMED CT, AJCC and others.')
    pathologic_stage_group = JSONField(help_text='The extent of the cancer in the body, according to the TNM '
                                                 'classification system, based on examination of tissue samples '
                                                 'removed during surgery, in addition to physical examination and '
                                                 'imaging and potentially, other prognostic factors. '
                                                 'Accepted ontologies: SNOMED CT, AJCC and others.')
    pathologic_primary_tumor_category = JSONField(help_text='Category describing the primary tumor, based on its '
                                                            'size and extent, assessed through pathologic analysis '
                                                            'of a tumor specimen. Accepted ontologies: SNOMED CT, '
                                                            'AJCC and others.')
    pathologic_regional_nodes_category = JSONField(help_text='Category describing the presence or absence of '
                                                             'metastases in regional lymph nodes, assessed through '
                                                             'pathologic analysis of a specimen. Accepted ontologies: '
                                                             'SNOMED CT, AJCC and others.')
    pathologic_distant_metastases_category = JSONField(help_text='Category describing the presence or absence of '
                                                                 'metastases in remote anatomical locations, assessed '
                                                                 'through pathologic analysis of a specimen. '
                                                                 'Accepted ontologies: SNOMED CT, AJCC and others.')

    def __str__(self):
        return str(self.id)
