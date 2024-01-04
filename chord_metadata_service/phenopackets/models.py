from typing import Optional
from django.apps import apps
from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.resources.models import Resource
from chord_metadata_service.restapi.description_utils import rec_help
from chord_metadata_service.restapi.schema_utils import validation_schema_list
from chord_metadata_service.restapi.models import IndexableMixin, BaseExtraProperties, SchemaType, BaseTimeStamp
from chord_metadata_service.restapi.validators import (
    JsonSchemaValidator,
    ontology_validator,
    ontology_list_validator
)
from . import descriptions as d
from .schemas import (
    EXPRESSION_SCHEMA,
    EXTENSION_SCHEMA,
    PHENOPACKET_EVIDENCE_SCHEMA,
    PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA,
    PHENOPACKET_UPDATE_SCHEMA,
    VCF_RECORD_SCHEMA,
    PHENOPACKET_MEASUREMENT_SCHEMA,
    PHENOPACKET_MEDICAL_ACTION_SCHEMA,
)
from .validators import vrs_variation_validator
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

    created_by = models.CharField(max_length=200, blank=True, null=True, default=None,
                                  help_text=rec_help(d.META_DATA, "created_by"))
    submitted_by = models.CharField(max_length=200, blank=True, null=True, default=None,
                                    help_text=rec_help(d.META_DATA, "submitted_by"))
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
    excluded = models.BooleanField(default=False, help_text=rec_help(d.PHENOTYPIC_FEATURE, "excluded"))
    severity = JSONField(blank=True, null=True, validators=[ontology_validator],
                         help_text=rec_help(d.PHENOTYPIC_FEATURE, "severity"))
    modifiers = JSONField(blank=True, null=True, validators=[ontology_list_validator],
                          help_text=rec_help(d.PHENOTYPIC_FEATURE, "modifiers"))
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


class Biosample(BaseExtraProperties, BaseTimeStamp, IndexableMixin):
    """
    Class to describe a unit of biological material

    FHIR: Specimen
    """

    id = models.CharField(primary_key=True, max_length=200, help_text=rec_help(d.BIOSAMPLE, "id"))
    # if Individual instance is deleted Biosample instance is deleted too
    individual = models.ForeignKey(
        Individual, on_delete=models.CASCADE, blank=True, null=True, related_name="biosamples",
        help_text=rec_help(d.BIOSAMPLE, "individual_id"))
    derived_from_id = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True, related_name="derived_biosamples",
        help_text=rec_help(d.BIOSAMPLE, "derived_from_id"))
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
    procedure = models.JSONField(blank=True, null=True, help_text=rec_help(d.BIOSAMPLE, "procedure"))
    is_control_sample = models.BooleanField(default=False, help_text=rec_help(d.BIOSAMPLE, "is_control_sample"))
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.BIOSAMPLE, "extra_properties"))

    def __str__(self):
        return str(self.id)

    @property
    def get_sample_tissue_data(self):
        return {
            'reference': {
                'reference': self.sampled_tissue.get('id'),
                'display': self.sampled_tissue.get('label'),
            },
        }

    @property
    def schema_type(self) -> SchemaType:
        return SchemaType.BIOSAMPLE

    def get_project_id(self) -> Optional[str]:
        model = apps.get_model("phenopackets.Phenopacket")
        if len(phenopackets := model.objects.filter(biosamples__id=self.id)) < 1:
            return None
        return phenopackets.first().get_project_id()


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
    variation = models.JSONField(blank=True, null=True, help_text=rec_help(d.VARIANT_DESCRIPTOR, "variation"),
                                 validators=[vrs_variation_validator])
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
    # Acmg pathogenicity classification choices
    NOT_PROVIDED = 'NOT_PROVIDED'
    BENIGN = 'BENIGN'
    LIKELY_BENIGN = 'LIKELY_BENIGN'
    UNCERTAIN_SIGNIFICANCE = 'UNCERTAIN_SIGNIFICANCE'
    LIKELY_PATHOGENIC = 'LIKELY_PATHOGENIC'
    PATHOGENIC = 'PATHOGENIC'
    VARIANT_INTERPRETATION_STATUS = (
        (NOT_PROVIDED, 'Not provided'),
        (BENIGN, 'Benign'),
        (LIKELY_BENIGN, 'Likely benign'),
        (UNCERTAIN_SIGNIFICANCE, 'Uncertain significance'),
        (LIKELY_PATHOGENIC, 'Likely pathogenic'),
        (PATHOGENIC, 'Pathogenic')
    )

    # Therapeutic actionability choices
    UNKNOWN_ACTIONABILITY = 'UNKNOWN_ACTIONABILITY'
    NOT_ACTIONABLE = 'NOT_ACTIONABLE'
    ACTIONABLE = 'ACTIONABLE'
    THERAPEUTIC_ACTIONABILITY_CHOICES = (
        (UNKNOWN_ACTIONABILITY, 'Unknown actionability'),
        (NOT_ACTIONABLE, 'Not actionable'),
        (ACTIONABLE, 'Actionable'),
    )
    acmg_pathogenicity_classification = models.CharField(max_length=200, choices=VARIANT_INTERPRETATION_STATUS,
                                                         default='NOT_PROVIDED',
                                                         help_text=rec_help(d.VARIANT_INTERPRETATION,
                                                                            "acmg_pathogenicity_classification"))
    therapeutic_actionability = models.CharField(max_length=200, choices=THERAPEUTIC_ACTIONABILITY_CHOICES,
                                                 default='UNKNOWN_ACTIONABILITY',
                                                 help_text=rec_help(d.VARIANT_INTERPRETATION,
                                                                    "therapeutic_actionability"))
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
    UNKNOWN_STATUS = 'UNKNOWN_STATUS'
    REJECTED = 'REJECTED'
    CANDIDATE = 'CANDIDATE'
    CONTRIBUTORY = 'CONTRIBUTORY'
    CAUSATIVE = 'CAUSATIVE'
    GENOMIC_INTERPRETATION_STATUS = (
        (UNKNOWN_STATUS, 'Unknown status'),
        (REJECTED, 'Rejected'),
        (CANDIDATE, 'Candidate'),
        (CONTRIBUTORY, 'Contributory'),
        (CAUSATIVE, 'Causative')
    )
    # 'subject_or_biosample_id' is returned by the serializer

    # Corresponds to 'subject_or_biosample_id' if it matches an Individual
    subject = models.ForeignKey(
        Individual, on_delete=models.CASCADE, null=True, blank=True, related_name="genomic_interpretations")
    # Corresponds to 'subject_or_biosample_id' if it matches a Biosample
    biosample = models.ForeignKey(
        Biosample, on_delete=models.CASCADE, null=True, blank=True, related_name="genomic_interpretations")

    interpretation_status = models.CharField(max_length=200, choices=GENOMIC_INTERPRETATION_STATUS,
                                             default="UNKNOWN_STATUS",
                                             help_text='How the call of this GenomicInterpretation was interpreted.')

    # Corresponds to 'call' field in schema in case of GeneDescriptor
    gene_descriptor = models.ForeignKey(GeneDescriptor, on_delete=models.CASCADE, null=True, blank=True,
                                        help_text="Corresponds to 'call' field in schema in case of GeneDescriptor")
    # Corresponds to 'call' field in schema in case of VariantInterpretation
    variant_interpretation = models.ForeignKey(VariantInterpretation, on_delete=models.CASCADE, null=True, blank=True,
                                               help_text="Corresponds to 'call' field in schema in case of "
                                                         "VariantInterpretation")

    extra_properties = JSONField(blank=True, null=True,
                                 help_text='Extra properties that are not supported by current schema')

    def clean(self):
        if not (self.gene_descriptor or self.variant_interpretation):
            raise ValidationError('Either Gene or Variant must be specified')
        if not (self.subject or self.biosample):
            raise ValidationError('The subject_or_biosample_id must point to a Biosample or a Subject.')

    def __str__(self):
        return str(self.id)


class Diagnosis(BaseTimeStamp):
    """
    Class to refer to disease that is present in the individual analyzed

    FHIR: Condition
    """
    id = models.CharField(primary_key=True, max_length=200,
                          help_text="Unique ID, uses the parent Interpretation's id when ingesting.")
    disease = models.JSONField(null=True, blank=True, validators=[ontology_validator])
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
    UNKNOWN_PROGRESS = "UNKNOWN_PROGRESS"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    SOLVED = "SOLVED"
    UNSOLVED = "UNSOLVED"
    PROGRESS_STATUS = [
        (UNKNOWN_PROGRESS, 'Unknown Progress'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
        (SOLVED, 'Solved'),
        (UNSOLVED, 'Unsolved'),
    ]

    id = models.CharField(primary_key=True, max_length=200, help_text='An arbitrary identifier for the interpretation.')
    progress_status = models.CharField(choices=PROGRESS_STATUS, max_length=200, blank=True,
                                       help_text='The current status of work on the case.')
    diagnosis = models.OneToOneField(Diagnosis, blank=True, null=True, on_delete=models.CASCADE,
                                     help_text='The diagnosis, if made.')
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

class Phenopacket(BaseExtraProperties, BaseTimeStamp, IndexableMixin):
    """
    Class to aggregate Individual's experiments data

    FHIR: Composition
    """

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["id", "dataset_id"], name="unique_pheno_dataset")
        ]

    @property
    def schema_type(self) -> SchemaType:
        return SchemaType.PHENOPACKET

    def get_project_id(self) -> Optional[str]:
        model = apps.get_model("chord.Project")
        try:
            project = model.objects.get(datasets=self.dataset)
            return project.identifier
        except ObjectDoesNotExist:
            return None

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

    # TODO OneToOneField
    meta_data = models.ForeignKey(MetaData, on_delete=models.CASCADE, help_text=rec_help(d.PHENOPACKET, "meta_data"))
    dataset = models.ForeignKey("chord.Dataset", on_delete=models.CASCADE, blank=True, null=True)  # TODO: Help text
    extra_properties = JSONField(blank=True, null=True, help_text=rec_help(d.PHENOPACKET, "extra_properties"))

    def __str__(self):
        return str(self.id)
