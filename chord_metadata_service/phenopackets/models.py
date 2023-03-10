from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.models import IndexableMixin, BaseTimeStamp
from chord_metadata_service.restapi.schema_utils import validation_schema_list
from chord_metadata_service.restapi.validators import (
    JsonSchemaValidator,
    age_or_age_range_validator,
    ontology_validator,
    ontology_list_validator
)
from . import descriptions as d
from .schemas import (
    EXPRESSION_SCHEMA,
    EXTENSION_SCHEMA,
    ONE_OF_MEDICAL_ACTION,
    PHENOPACKET_EVIDENCE_SCHEMA,
    PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA,
    PHENOPACKET_MEASUREMENT_VALUE_SCHEMA,
    PHENOPACKET_UPDATE_SCHEMA,
    VCF_RECORD_SCHEMA, PHENOPACKET_PROCEDURE_SCHEMA, PHENOPACKET_MEASUREMENT_SCHEMA, PHENOPACKET_DISEASE_SCHEMA,
    PHENOPACKET_MEDICAL_ACTION_SCHEMA,
)
from ..restapi.schemas import TIME_ELEMENT_SCHEMA


#############################################################
#                                                           #
#                        Metadata                           #
#                                                           #
#############################################################


class MetaData(BaseTimeStamp):
    """
    Class to store structured definitions of the resources
    and ontologies used within the phenopacket

    FHIR: Metadata
    """

    created_by = models.CharField(max_length=200, blank=True, null=True, default=None, help_text=rec_help(d.META_DATA, "created_by"))
    submitted_by = models.CharField(max_length=200, blank=True, null=True, default=None, help_text=rec_help(d.META_DATA, "submitted_by"))
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
    onset = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=TIME_ELEMENT_SCHEMA)])
    resolution = JSONField(blank=True, null=True, validators=[
        JsonSchemaValidator(schema=TIME_ELEMENT_SCHEMA)])

    # evidence can stay here because evidence is given for an observation of PF
    # JSON schema to check evidence_code is present
    # FHIR: Condition.evidence
    evidence = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=PHENOPACKET_EVIDENCE_SCHEMA)],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "evidence"))
    biosample = models.ForeignKey(
        "Biosample", on_delete=models.CASCADE, blank=True, null=True, related_name='phenotypic_features')
    # Phenotypic features can be attached directly to phenopackets, rather than through biosamples
    phenopacket = models.ForeignKey(
        "Phenopacket", on_delete=models.CASCADE, blank=True, null=True, related_name='phenotypic_features')
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PHENOTYPIC_FEATURE, "extra_properties"))

    def __str__(self):
        return str(self.id)


class Procedure(BaseTimeStamp, IndexableMixin):
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
        JsonSchemaValidator(schema=TIME_ELEMENT_SCHEMA)])

    def __str__(self):
        return str(self.id)


class File(BaseTimeStamp, IndexableMixin):
    uri = models.URLField(primary_key=True, max_length=200, help_text=rec_help(d.FILE, "uri"))
    individual_to_file_identifiers = JSONField(blank=True, null=True,
                                               help_text=rec_help(d.FILE, "individual_to_file_identifiers"))
    file_attributes = JSONField(blank=True, null=True, help_text=rec_help(d.FILE, "file_attributes"))

    def __str__(self):
        return str(self.uri)

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


class Disease(BaseTimeStamp, IndexableMixin):
    """
    Class to represent a diagnosis and inference or hypothesis about the cause
    underlying the observed phenotypic abnormalities

    FHIR: Condition
    """

    term = JSONField(validators=[ontology_validator], help_text=rec_help(d.DISEASE, "term"))
    excluded = models.BooleanField(blank=True, null=True)
    onset = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=TIME_ELEMENT_SCHEMA)])
    resolution = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(schema=TIME_ELEMENT_SCHEMA)])
    disease_stage = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                              help_text=rec_help(d.DISEASE, "disease_stage"))
    clinical_tnm_finding = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                                     help_text=rec_help(d.DISEASE, "tnm_finding"))
    primary_site = JSONField(blank=True, null=True, validators=[ontology_validator])
    laterality = JSONField(blank=True, null=True, validators=[ontology_validator])
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
    derived_from_id = models.CharField(max_length=200, blank=True, help_text=rec_help(d.BIOSAMPLE, "derived_from_id"))
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.BIOSAMPLE, "description"))
    sampled_tissue = JSONField(validators=[ontology_validator], help_text=rec_help(d.BIOSAMPLE, "sampled_tissue"))
    sample_type = JSONField(blank=True, null=True, validators=[ontology_validator],
                            help_text=rec_help(d.BIOSAMPLE, "sample_type"))

    # phenotypic_features = models.ManyToManyField(PhenotypicFeature, blank=True,
    #   help_text='List of phenotypic abnormalities of the sample.')

    measurements = models.JSONField(blank=True, null=True,
                                    validators=[JsonSchemaValidator(PHENOPACKET_MEASUREMENT_SCHEMA)],
                                    help_text=rec_help(d.BIOSAMPLE, "measurements"))
    taxonomy = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.BIOSAMPLE, "taxonomy"))
    time_of_collection = JSONField(blank=True, null=True, validators=[JsonSchemaValidator(TIME_ELEMENT_SCHEMA)],
                                   help_text=rec_help(d.BIOSAMPLE, "time_of_collection"))

    histological_diagnosis = JSONField(
        blank=True, null=True, validators=[ontology_validator],
        help_text=rec_help(d.BIOSAMPLE, "histological_diagnosis"))
    # TODO: Lists?
    tumor_progression = JSONField(blank=True, null=True, validators=[ontology_validator],
                                  help_text=rec_help(d.BIOSAMPLE, "tumor_progression"))
    tumor_grade = JSONField(blank=True, null=True, validators=[ontology_validator],
                            help_text=rec_help(d.BIOSAMPLE, "tumor_grade"))
    pathological_stage = JSONField(blank=True, null=True, validators=[ontology_validator],
                                   help_text=rec_help(d.BIOSAMPLE, "pathological_stage"))
    diagnostic_markers = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                                   help_text=rec_help(d.BIOSAMPLE, "diagnostic_markers"))
    # CHECK! if Procedure instance is deleted Biosample instance is deleted too
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, help_text=rec_help(d.BIOSAMPLE, "procedure"))
    hts_files = models.ManyToManyField(
        HtsFile, blank=True, related_name='biosample_hts_files', help_text=rec_help(d.BIOSAMPLE, "hts_files"))
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
    value_id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.GENE_DESCRIPTOR, "value_id"))
    symbol = models.CharField(max_length=200, blank=True, help_text=rec_help(d.GENE_DESCRIPTOR, "symbol"))
    description = models.CharField(max_length=200, blank=True, help_text=rec_help(d.GENE_DESCRIPTOR, "description"))
    alternate_ids = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                               help_text=rec_help(d.GENE_DESCRIPTOR, "alternate_ids"))
    xrefs = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                       help_text=rec_help(d.GENE_DESCRIPTOR, "xrefs"))
    alternate_symbols = ArrayField(models.CharField(max_length=200, blank=True), blank=True, default=list,
                                   help_text=rec_help(d.GENE_DESCRIPTOR, "alternate_symbols"))
    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')

    def __str__(self) -> str:
        return str(self.value_id)


class VariationDescriptor(BaseTimeStamp):
    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.VARIANT_DESCRIPTOR, "id"))
    variation = models.JSONField(blank=True, null=True, help_text=rec_help(d.VARIANT_DESCRIPTOR, "variation"))
    label = models.CharField(blank=True, max_length=200, help_text=rec_help(d.VARIANT_DESCRIPTOR, "label"))
    description = models.CharField(blank=True, max_length=200, help_text=rec_help(d.VARIANT_DESCRIPTOR, "description"))
    gene_context = models.ForeignKey(GeneDescriptor, blank=True, null=True, on_delete=models.CASCADE,
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
    variation_descriptor = models.ForeignKey(VariationDescriptor, on_delete=models.CASCADE,
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
        ('UNKNOWN_STATUS', 'UNKNOWN_STATUS'),
        ('REJECTED', 'REJECTED'),
        ('CANDIDATE', 'CANDIDATE'),
        ('CONTRIBUTORY', 'CONTRIBUTORY'),
        ('CAUSATIVE', 'CAUSATIVE')
    )
    subject_or_biosample_id = models.CharField(
        max_length=200, blank=True, help_text="Id of the patient or biosample of the subject being interpreted")
    interpretation_status = models.CharField(max_length=200, choices=GENOMIC_INTERPRETATION_STATUS, default="UNKNOWN_STATUS",
                                             help_text='How the call of this GenomicInterpretation was interpreted.')

    # Corresponds to 'call' field in schema in case of GeneDescriptor
    gene_descriptor = models.ForeignKey(GeneDescriptor, on_delete=models.CASCADE, null=True,
                                        blank=True, help_text="Corresponds to 'call' field in schema in case of GeneDescriptor")
    # Corresponds to 'call' field in schema in case of VariantInterpretation
    variant_interpretation = models.ForeignKey(VariantInterpretation, on_delete=models.CASCADE, null=True,
                                               blank=True, help_text="Corresponds to 'call' field in schema in case of VariantInterpretation")

    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')

    def clean(self):
        if not (self.gene_descriptor or self.variant_interpretation):
            raise ValidationError('Either Gene or Variant must be specified')

    def __str__(self):
        return str(self.id)


class Diagnosis(BaseTimeStamp):
    """
    Class to refer to disease that is present in the individual analyzed

    FHIR: Condition
    """
    disease_ontology = models.JSONField(null=True, blank=True, validators=[ontology_validator])

    # required?
    genomic_interpretations = models.ManyToManyField(
        GenomicInterpretation, blank=True,
        help_text='The genomic elements assessed as being responsible for the disease.')
    extra_properties = JSONField(
        blank=True, null=True, help_text='Extra properties that are not supported by current schema')

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
    diagnosis = models.ForeignKey(Diagnosis, blank=True, null=True, on_delete=models.CASCADE, help_text='One or more diagnoses, if made.')
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

    measurements = models.JSONField(
        blank=True, null=True, validators=[JsonSchemaValidator(PHENOPACKET_MEASUREMENT_SCHEMA)])
    biosamples = models.ManyToManyField(Biosample, blank=True, help_text=rec_help(d.PHENOPACKET, "biosamples"))

    # NOTE: As of Phenopackets V2.0, genes and variants fields are replaced with interpretations
    interpretations = models.ManyToManyField(
        Interpretation, blank=True, help_text=rec_help(d.PHENOPACKET, "interpretations"))

    diseases = models.ManyToManyField(Disease, blank=True, help_text=rec_help(d.PHENOPACKET, "diseases"))

    medical_actions = models.JSONField(
        blank=True, null=True, validators=[JsonSchemaValidator(PHENOPACKET_MEDICAL_ACTION_SCHEMA)])

    # TODO: warn users that files will not be ingested in phenopackets

    # TODO OneToOneField
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, help_text=rec_help(d.PHENOPACKET, "meta_data"))
    table = models.ForeignKey("chord.Table", on_delete=models.CASCADE, blank=True, null=True)  # TODO: Help text
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PHENOPACKET, "extra_properties"))

    def __str__(self):
        return str(self.id)
