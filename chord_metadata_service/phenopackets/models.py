from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.models import IndexableMixin
from chord_metadata_service.restapi.schema_utils import validation_schema_list
from chord_metadata_service.restapi.validators import (
    JsonSchemaValidator,
    age_or_age_range_validator,
    ontology_validator,
    ontology_list_validator
)
from . import descriptions as d
from .schemas import (
    ALLELE_SCHEMA,
    EXPRESSION_SCHEMA,
    EXTENSION_SCHEMA,
    ONE_OF_MEDICAL_ACTION,
    PHENOPACKET_DISEASE_ONSET_SCHEMA,
    PHENOPACKET_EVIDENCE_SCHEMA,
    PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA,
    PHENOPACKET_MEASUREMENT_VALUE_SCHEMA,
    PHENOPACKET_TIME_ELEMENT_SCHEMA,
    PHENOPACKET_UPDATE_SCHEMA,
    VCF_RECORD_SCHEMA,
)


#############################################################
#                                                           #
#                        Metadata                           #
#                                                           #
#############################################################

class BaseTimeStamp(models.Model):
    """
    Abstract django model class for tables that should have
    columns for 'created' and 'updated' timestamps.
    Use in inheritance.
    """
    created = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Abstract prevents the creation of a _TimeStamp table
        abstract = True


class MetaData(models.Model):
    """
    Class to store structured definitions of the resources
    and ontologies used within the phenopacket

    FHIR: Metadata
    """

    created = models.DateTimeField(default=timezone.now, help_text=rec_help(d.META_DATA, "created"))
    created_by = models.CharField(max_length=200, help_text=rec_help(d.META_DATA, "created_by"))
    submitted_by = models.CharField(max_length=200, blank=True, help_text=rec_help(d.META_DATA, "submitted_by"))
    resources = models.ManyToManyField(Resource, help_text=rec_help(d.META_DATA, "resources"))
    updates = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(
                        schema=validation_schema_list(PHENOPACKET_UPDATE_SCHEMA), formats=['date-time'])],
                        help_text=rec_help(d.META_DATA, "updates"))
    phenopacket_schema_version = models.CharField(max_length=200, blank=True,
                                                  help_text='Schema version of the current phenopacket.')
    external_references = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(
                                    schema=validation_schema_list(PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA))],
                                    help_text=rec_help(d.META_DATA, "external_references"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.META_DATA, "extra_properties"))
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)


#############################################################


#############################################################
#                                                           #
#                  Phenotypic information                   #
#                                                           #
#############################################################


class PhenotypicFeature(BaseTimeStamp, IndexableMixin):
    """
    Class to describe a phenotype of an Individual

    FHIR: Condition or Observation
    """

    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.PHENOTYPIC_FEATURE, "description"))
    pftype = JSONField(verbose_name='type', validators=[ontology_validator],
                       help_text=rec_help(d.PHENOTYPIC_FEATURE, "type"))
    excluded = models.BooleanField(default=False, help_text=rec_help(d.PHENOTYPIC_FEATURE, "negated"))
    severity = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "severity"))
    modifier = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "modifier"))
    onset = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=PHENOPACKET_TIME_ELEMENT_SCHEMA)])
    resolution = JSONField(blank=True, null=True, validators=[
                           JsonSchemaValidator(schema=PHENOPACKET_TIME_ELEMENT_SCHEMA)])

    # evidence can stay here because evidence is given for an observation of PF
    # JSON schema to check evidence_code is present
    # FHIR: Condition.evidence
    evidence = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=PHENOPACKET_EVIDENCE_SCHEMA)],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "evidence"))
    biosample = models.ForeignKey(
        "Biosample", on_delete=models.SET_NULL, blank=True, null=True, related_name='phenotypic_features')
    phenopacket = models.ForeignKey(
        "Phenopacket", on_delete=models.SET_NULL, blank=True, null=True, related_name='phenotypic_features')
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PHENOTYPIC_FEATURE, "extra_properties"))

    def __str__(self):
        return str(self.id)


class Procedure(models.Model):
    """
    Class to represent a clinical procedure performed on an individual
    (subject) in order to extract a biosample

    FHIR: Procedure
    """

    code = JSONField(validators=[ontology_validator], help_text=rec_help(d.PROCEDURE, "code"))
    body_site = JSONField(blank=True, null=True, validators=[ontology_validator],
                          help_text=rec_help(d.PROCEDURE, "body_site"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PROCEDURE, "extra_properties"))
    performed = JSONField(blank=True, null=True, validators=[
                          JsonSchemaValidator(schema=PHENOPACKET_TIME_ELEMENT_SCHEMA)])

    def __str__(self):
        return str(self.id)


class Measurement(models.Model):
    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for a given measurement')
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.MEASUREMENT, "description"))
    assay = JSONField(verbose_name='assay', validators=[ontology_validator],
                      help_text=rec_help(d.MEASUREMENT, "assay"))
    measurement_value = models.JSONField(blank=True, null=True, validators=[
                                         JsonSchemaValidator(PHENOPACKET_MEASUREMENT_VALUE_SCHEMA)])
    time_observed = JSONField(blank=True, null=True, validators=[
                              JsonSchemaValidator(schema=PHENOPACKET_TIME_ELEMENT_SCHEMA)])
    procedure = models.ForeignKey(Procedure, on_delete=models.DO_NOTHING,
                                  help_text='Clinical procdure performed to acquire the sample used for the measurement')

    def __str__(self):
        return str(self.id)


class MedicalAction(models.Model):
    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for a medical action')
    action = models.JSONField(blank=True, null=True, validators=[JsonSchemaValidator(ONE_OF_MEDICAL_ACTION)])
    treatment_target = models.JSONField(validators=[ontology_validator])
    treatment_intent = models.JSONField(validators=[ontology_validator])
    response_to_treatment = models.JSONField(validators=[ontology_validator])
    adverse_events = models.JSONField(validators=[ontology_list_validator])
    treatment_termination_reason = models.JSONField(validators=[ontology_validator])

    def __str__(self) -> str:
        return str(self.id)


class HtsFile(BaseTimeStamp, IndexableMixin):
    """
    Class to link HTC files with data

    FHIR: DocumentReference
    """

    HTS_FORMAT = (
        ('UNKNOWN', 'UNKNOWN'),
        ('SAM', 'SAM'),
        ('BAM', 'BAM'),
        ('CRAM', 'CRAM'),
        ('VCF', 'VCF'),
        ('BCF', 'BCF'),
        ('GVCF', 'GVCF'),
    )
    uri = models.URLField(primary_key=True, max_length=200, help_text=rec_help(d.HTS_FILE, "uri"))
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.HTS_FILE, "description"))
    hts_format = models.CharField(max_length=200, choices=HTS_FORMAT, help_text=rec_help(d.HTS_FILE, "hts_format"))
    genome_assembly = models.CharField(max_length=200, help_text=rec_help(d.HTS_FILE, "genome_assembly"))
    # e.g.
    # "individualToSampleIdentifiers": {
    #   "patient23456": "NA12345"
    # TODO how to perform this validation, ensure the patient id is the correct one?
    individual_to_sample_identifiers = JSONField(
        blank=True, null=True, help_text=rec_help(d.HTS_FILE, "individual_to_sample_identifiers"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.HTS_FILE, "extra_properties"))

    def __str__(self):
        return str(self.uri)


class Gene(BaseTimeStamp):
    """
    Class to represent an identifier for a gene

    FHIR: ?
    Draft extension for Gene is in development
    where Gene defined via class CodeableConcept
    """

    # Gene id is unique
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.GENE, "id"))
    # CURIE style? Yes!
    alternate_ids = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                               help_text=rec_help(d.GENE, "alternate_ids"))
    symbol = models.CharField(max_length=200, help_text=rec_help(d.GENE, "symbol"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.GENE, "extra_properties"))

    def __str__(self):
        return str(self.id)


class Variant(BaseTimeStamp):
    """
    Class to describe Individual variants or diagnosed causative variants

    FHIR: Observation ?
    Draft extension for Variant is in development
    """

    ALLELE = (
        ('hgvsAllele', 'hgvsAllele'),
        ('vcfAllele', 'vcfAllele'),
        ('spdiAllele', 'spdiAllele'),
        ('iscnAllele', 'iscnAllele'),
    )
    allele_type = models.CharField(max_length=200, choices=ALLELE, help_text="One of four allele types.")
    allele = JSONField(validators=[JsonSchemaValidator(schema=ALLELE_SCHEMA)],
                       help_text=rec_help(d.VARIANT, "allele"))
    zygosity = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.VARIANT, "zygosity"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.VARIANT, "extra_properties"))

    def __str__(self):
        return str(self.id)


class Disease(BaseTimeStamp, IndexableMixin):
    """
    Class to represent a diagnosis and inference or hypothesis about the cause
    underlying the observed phenotypic abnormalities

    FHIR: Condition
    """

    term = JSONField(validators=[ontology_validator], help_text=rec_help(d.DISEASE, "term"))
    # "ageOfOnset": {
    # "age": "P38Y7M"
    # }
    # OR
    # "ageOfOnset": {
    # "id": "HP:0003581",
    # "label": "Adult onset"
    # }
    onset = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=PHENOPACKET_TIME_ELEMENT_SCHEMA)])
    disease_stage = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                              help_text=rec_help(d.DISEASE, "disease_stage"))
    tnm_finding = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                            help_text=rec_help(d.DISEASE, "tnm_finding"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.DISEASE, "extra_properties"))

    def __str__(self):
        return str(self.id)


class Biosample(BaseTimeStamp, IndexableMixin):
    """
    Class to describe a unit of biological material

    FHIR: Specimen
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.BIOSAMPLE, "id"))
    # if Individual instance is deleted Biosample instance is deleted too
    individual = models.ForeignKey(
        Individual, on_delete=models.CASCADE, blank=True, null=True, related_name="biosamples",
        help_text=rec_help(d.BIOSAMPLE, "individual_id"))
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.BIOSAMPLE, "description"))
    sampled_tissue = JSONField(validators=[ontology_validator], help_text=rec_help(d.BIOSAMPLE, "sampled_tissue"))
    # phenotypic_features = models.ManyToManyField(PhenotypicFeature, blank=True,
    #   help_text='List of phenotypic abnormalities of the sample.')
    taxonomy = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.BIOSAMPLE, "taxonomy"))
    # An ISO8601 string represent age
    individual_age_at_collection = JSONField(blank=True, null=True, validators=[age_or_age_range_validator],
                                             help_text=rec_help("individual_age_at_collection"))
    histological_diagnosis = JSONField(
        blank=True, null=True, validators=[ontology_validator],
        help_text=rec_help(d.BIOSAMPLE, "histological_diagnosis"))
    # TODO: Lists?
    tumor_progression = JSONField(blank=True, null=True, validators=[ontology_validator],
                                  help_text=rec_help(d.BIOSAMPLE, "tumor_progression"))
    tumor_grade = JSONField(blank=True, null=True, validators=[ontology_validator],
                            help_text=rec_help(d.BIOSAMPLE, "tumor_grade"))
    diagnostic_markers = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                                   help_text=rec_help(d.BIOSAMPLE, "diagnostic_markers"))
    # CHECK! if Procedure instance is deleted Biosample instance is deleted too
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, help_text=rec_help(d.BIOSAMPLE, "procedure"))
    hts_files = models.ManyToManyField(
        HtsFile, blank=True, related_name='biosample_hts_files', help_text=rec_help(d.BIOSAMPLE, "hts_files"))
    variants = models.ManyToManyField(Variant, blank=True, help_text=rec_help(d.BIOSAMPLE, "variants"))
    is_control_sample = models.BooleanField(default=False, help_text=rec_help(d.BIOSAMPLE, "is_control_sample"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.BIOSAMPLE, "extra_properties"))

    def __str__(self):
        return str(self.id)

    @property
    def get_sample_tissue_data(self):
        return {'reference': {
            'reference': self.sampled_tissue.get('id'),
            'display': self.sampled_tissue.get('label')
        }
        }


#############################################################
#                                                           #
#                    Interpretation                         #
#                                                           #
#############################################################

class GeneDescriptor(BaseTimeStamp):
    # Corresponds to GeneDescriptor.value_id field in schema
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.GENE_DESCRIPTOR, "value_id"))
    symbol = models.CharField(max_length=200, blank=True, help_text=rec_help(d.GENE_DESCRIPTOR, "symbol"))
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.GENE_DESCRIPTOR, "description"))
    alternate_ids = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                               help_text=rec_help(d.GENE_DESCRIPTOR, "alternate_ids"))
    xrefs = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                       help_text=rec_help(d.GENE_DESCRIPTOR, "xrefs"))
    alternate_symbols = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                                   help_text=rec_help(d.GENE_DESCRIPTOR, "alternate_symbols"))

    def __str__(self) -> str:
        return str(self.id)


class VariantDescriptor(BaseTimeStamp):
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.VARIANT_DESCRIPTOR, "id"))
    variation = models.JSONField(blank=True, null=True, help_text=rec_help(d.VARIANT_DESCRIPTOR, "variation"))
    label = models.CharField(blank=True, max_length=200, help_text=rec_help(d.VARIANT_DESCRIPTOR, "label"))
    description = models.CharField(blank=True, max_length=200, help_text=rec_help(d.VARIANT_DESCRIPTOR, "description"))
    gene_context = models.ForeignKey(GeneDescriptor, blank=True, on_delete=models.CASCADE,
                                     help_text=rec_help(d.VARIANT_DESCRIPTOR, "gene_context"))
    expressions = models.JSONField(blank=True, null=True, validators=[JsonSchemaValidator(EXPRESSION_SCHEMA)],
                                   help_text=rec_help(d.VARIANT_DESCRIPTOR, "expressions"))
    vcf_record = models.JSONField(blank=True, null=True, validators=[JsonSchemaValidator(VCF_RECORD_SCHEMA)])
    xrefs = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                       help_text=rec_help(d.VARIANT_DESCRIPTOR, "xrefs"))
    alternate_labels = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                                  help_text=rec_help(d.VARIANT_DESCRIPTOR, "alternate_labels"))
    extensions = ArrayField(models.JSONField(blank=True, null=True, validators=[JsonSchemaValidator(EXTENSION_SCHEMA)]),
                            blank=True, default=list, help_text=rec_help(d.VARIANT_DESCRIPTOR, "extensions"))
    molecule_context = models.CharField(max_length=200, blank=True,
                                        help_text=rec_help(d.VARIANT_DESCRIPTOR, "molecule_context"))
    structural_type = models.JSONField(blank=True, null=True, validators=[ontology_validator],
                                       help_text=rec_help(d.VARIANT_DESCRIPTOR, "structural_type"))
    vrs_ref_allele_seq = models.CharField(max_length=200, blank=True,
                                          help_text=rec_help(d.VARIANT_DESCRIPTOR, "vrs_ref_allele_seq"))
    allelic_state = models.JSONField(blank=True, null=True, validators=[
                                     ontology_validator], help_text=rec_help(d.VARIANT_DESCRIPTOR, "allelic_state"))

    def __str__(self) -> str:
        return str(self.id)


class VariantInterpretation(BaseTimeStamp):
    VARIANT_INTERPRETATION_STATUS = (
        ('NOT_PROVIDED', 'NOT_PROVIDED'),
        ('BENIGN', 'BENIGN'),
        ('LIKELY_BENIGN', 'LIKELY_BENIGN'),
        ('UNCERTAIN_SIGNIFICANCE', 'UNCERTAIN_SIGNIFICANCE'),
        ('LIKELY_PATHOGENIC', 'LIKELY_PATHOGENIC'),
        ('PATHOGENIC', 'PATHOGENIC')
    )
    THERAPEUTIC_ACTIONABILITY_CHOICES = (
        ('UNKNOWN_ACTIONABILITY', 'UNKNOWN_ACTIONABILITY'),
        ('NOT_ACTIONABLE', 'NOT_ACTIONABLE'),
        ('ACTIONABLE', 'ACTIONABLE'),
    )

    acmg_pathogenicity_classification = models.CharField(max_length=200, choices=VARIANT_INTERPRETATION_STATUS, default='NOT_PROVIDED',
                                                         help_text=rec_help(d.VARIANT_INTERPRETATION, "acmg_pathogenicity_classification"))
    therapeutic_actionability = models.CharField(max_length=200, choices=THERAPEUTIC_ACTIONABILITY_CHOICES, default='UNKNOWN_ACTIONABILITY',
                                                 help_text=rec_help(d.VARIANT_INTERPRETATION, "therapeutic_actionability"))
    variant = models.ForeignKey(VariantDescriptor, on_delete=models.CASCADE,
                                help_text=rec_help(d.VARIANT_INTERPRETATION, "variant"))

    def __str__(self) -> str:
        return str(self.id)


class GenomicInterpretation(BaseTimeStamp):
    """
    Class to represent a statement about the contribution
    of a genomic element towards the observed phenotype

    FHIR: Observation
    """

    GENOMIC_INTERPRETATION_STATUS = (
        ('UNKNOWN', 'UNKNOWN'),
        ('REJECTED', 'REJECTED'),
        ('CANDIDATE', 'CANDIDATE'),
        ('CONTRIBUTORY', 'CONTRIBUTORY'),
        ('CAUSATIVE', 'CAUSATIVE')
    )
    subject_or_biosample_id = models.CharField(
        max_length=200, blank=True, help_text="Id of the patient or biosample of the subject being interpreted")
    interpretation_status = models.CharField(max_length=200, choices=GENOMIC_INTERPRETATION_STATUS,
                                             help_text='How the call of this GenomicInterpretation was interpreted.')

    # Corresponds to 'call' field in schema in case of GeneDescriptor
    gene_descriptor = models.ForeignKey(GeneDescriptor, on_delete=models.CASCADE,
                                        blank=True, help_text="Corresponds to 'call' field in schema in case of GeneDescriptor")
    # Corresponds to 'call' field in schema in case of VariantInterpretation
    variant_interpretation = models.ForeignKey(VariantInterpretation, on_delete=models.CASCADE,
                                               blank=True, help_text="Corresponds to 'call' field in schema in case of VariantInterpretation")

    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')

    def clean(self):
        if not (self.gene or self.variant):
            raise ValidationError('Either Gene or Variant must be specified')

    def __str__(self):
        return str(self.id)


class Diagnosis(BaseTimeStamp):
    """
    Class to refer to disease that is present in the individual analyzed

    FHIR: Condition
    """

    disease = models.ForeignKey(Disease, on_delete=models.CASCADE, help_text='The diagnosed condition.')
    # required?
    genomic_interpretations = models.ManyToManyField(
        GenomicInterpretation, blank=True,
        help_text='The genomic elements assessed as being responsible for the disease.')
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')

    def __str__(self):
        return str(self.id)


class Interpretation(BaseTimeStamp):
    """
    Class to represent the interpretation of a genomic analysis

    FHIR: DiagnosticReport
    """

    PROGRESS_STATUS = (
        ('UNKNOWN_PROGRESS', 'UNKNOWN_PROGRESS'),
        ('IN_PROGRESS', 'IN_PROGRESS'),
        ('COMPLETED', 'COMPLETED'),
        ('SOLVED', 'SOLVED'),
        ('UNSOLVED', 'UNSOLVED'),
    )

    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for the interpretation.')
    progress_status = models.CharField(choices=PROGRESS_STATUS, max_length=200, blank=True,
                                       help_text='The current status of work on the case.')
    diagnosis = models.ManyToManyField(Diagnosis, help_text='One or more diagnoses, if made.')
    summary = models.CharField(max_length=200, blank=True, help_text='Free text summary of the interpretation.')
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')

    def __str__(self):
        return str(self.id)


#############################################################
#                                                           #
#                    Phenopacket                            #
#                                                           #
#############################################################

class Phenopacket(BaseTimeStamp, IndexableMixin):
    """
    Class to aggregate Individual's experiments data

    FHIR: Composition
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.PHENOPACKET, "id"))
    # if Individual instance is deleted Phenopacket instance is deleted too
    # CHECK !!! Force as required?
    subject = models.ForeignKey(
        Individual, on_delete=models.CASCADE, related_name="phenopackets",
        help_text=rec_help(d.PHENOPACKET, "subject"))
    # PhenotypicFeatures are present in Biosample, so can be accessed via Biosample instance
    # phenotypic_features = models.ManyToManyField(PhenotypicFeature, blank=True,
    #   help_text='Phenotypic features observed in the proband.')
    measurements = models.ManyToManyField(Measurement, blank=True, help_text=rec_help(d.PHENOPACKET, "measurements"))
    biosamples = models.ManyToManyField(Biosample, blank=True, help_text=rec_help(d.PHENOPACKET, "biosamples"))

    # NOTE: As of Phenopackets V2.0, genes and variants fields are replaced with interpretations
    interpretations = models.ManyToManyField(
        Interpretation, blank=True, help_text=rec_help(d.PHENOPACKET, "interpretations"))

    diseases = models.ManyToManyField(Disease, blank=True, help_text=rec_help(d.PHENOPACKET, "diseases"))
    medical_actions = models.ManyToManyField(
        MedicalAction, blank=True, help_text=rec_help(d.PHENOPACKET, "medical_actions"))
    # TODO: do we keep files referenced in phenopackets? Already tracked by experiments
    # hts_files = models.ManyToManyField(HtsFile, blank=True, help_text=rec_help(d.PHENOPACKET, "hts_files"))
    # TODO OneToOneField
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, help_text=rec_help(d.PHENOPACKET, "meta_data"))
    table = models.ForeignKey("chord.Table", on_delete=models.CASCADE, blank=True, null=True)  # TODO: Help text
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PHENOPACKET, "extra_properties"))

    def __str__(self):
        return str(self.id)
