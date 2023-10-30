# Individual schemas for validation of JSONField values
import json
import jsonschema
from pathlib import Path
from chord_metadata_service.patients.schemas import INDIVIDUAL_SCHEMA
from chord_metadata_service.resources.schemas import RESOURCE_SCHEMA
from chord_metadata_service.restapi.schemas import (
    AGE,
    AGE_RANGE,
    EXTRA_PROPERTIES_SCHEMA,
    ONTOLOGY_CLASS,
    TIME_INTERVAL, TIME_ELEMENT_SCHEMA,
)
from chord_metadata_service.restapi.schema_utils import (
    DATE_TIME,
    DRAFT_07,
    SCHEMA_STRING_FORMATS,
    SCHEMA_TYPES,
    array_of,
    base_type,
    enum_of,
    named_one_of,
    base_schema_uri,
    sub_schema_uri,
    string_with_format,
    describe_schema, get_schema_base_path
)

from . import descriptions


__all__ = [
    "PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA",
    "PHENOPACKET_UPDATE_SCHEMA",
    "PHENOPACKET_META_DATA_SCHEMA",
    "PHENOPACKET_EVIDENCE_SCHEMA",
    "PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA",
    "PHENOPACKET_GENE_SCHEMA",
    "PHENOPACKET_HTS_FILE_SCHEMA",
    "PHENOPACKET_BIOSAMPLE_SCHEMA",
    "PHENOPACKET_DISEASE_ONSET_SCHEMA",
    "PHENOPACKET_DISEASE_SCHEMA",
    "PHENOPACKET_SCHEMA",
    "PHENOPACKET_PROCEDURE_SCHEMA",
    "PHENOPACKET_QUANTITY_SCHEMA",
    "PHENOPACKET_TYPED_QUANTITY_SCHEMA",
    "PHENOPACKET_VALUE_SCHEMA",
    "PHENOPACKET_COMPLEX_VALUE_SCHEMA",
    "PHENOPACKET_MEASUREMENT_VALUE_SCHEMA",
    "PHENOPACKET_MEASUREMENT_SCHEMA",
    "PHENOPACKET_TREATMENT",
    "PHENOPACKET_RADIATION_THERAPY",
    "PHENOPACKET_THERAPEUTIC_REGIMEN",
    "PHENOPACKET_MEDICAL_ACTION_SCHEMA",
    "PHENOPACKET_REF_RESOLVER",
    "VRS_VARIATION_SCHEMA"
]

base_path = get_schema_base_path(Path(__file__).parent.name)
base_uri = base_schema_uri(base_path)


with open("chord_metadata_service/vrs/schema/vrs.json", "r") as file:
    vrs_schema_definitions = json.load(file)
    file.close()


PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "external_reference"),
    "title": "External reference schema",
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "reference": base_type(SCHEMA_TYPES.STRING),
        "description": base_type(SCHEMA_TYPES.STRING)
    }
}, descriptions.EXTERNAL_REFERENCE)

PHENOPACKET_UPDATE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "update"),
    "title": "Updates schema",
    "type": "object",
    "properties": {
        "timestamp": DATE_TIME,
        "updated_by": base_type(SCHEMA_TYPES.STRING),
        "comment": base_type(SCHEMA_TYPES.STRING)
    },
    "additionalProperties": False,
    "required": ["timestamp", "comment"],
}, descriptions.UPDATE)


# noinspection PyProtectedMember
PHENOPACKET_META_DATA_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "meta_data"),
    "type": "object",
    "properties": {
        "created": DATE_TIME,
        "created_by": base_type(SCHEMA_TYPES.STRING),
        "submitted_by": base_type(SCHEMA_TYPES.STRING),
        "resources": array_of(RESOURCE_SCHEMA),
        "updates": array_of(PHENOPACKET_UPDATE_SCHEMA),
        "phenopacket_schema_version": base_type(SCHEMA_TYPES.STRING),
        "external_references": array_of(PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA),
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
}, descriptions.META_DATA)

PHENOPACKET_EVIDENCE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "evidence"),
    "title": "Evidence schema",
    "type": "object",
    "properties": {
        "evidence_code": ONTOLOGY_CLASS,
        "reference": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
    },
    "additionalProperties": False,
    "required": ["evidence_code"],
}, descriptions.EVIDENCE)


PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "phenotypic_feature"),
    "type": "object",
    "properties": {
        "description": base_type(SCHEMA_TYPES.STRING),
        "type": ONTOLOGY_CLASS,
        "excluded": base_type(SCHEMA_TYPES.BOOLEAN),
        "severity": ONTOLOGY_CLASS,
        "modifiers": array_of(ONTOLOGY_CLASS),
        "onset": TIME_ELEMENT_SCHEMA,
        "resolution": TIME_ELEMENT_SCHEMA,
        "evidence": array_of(PHENOPACKET_EVIDENCE_SCHEMA),
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
}, descriptions.PHENOTYPIC_FEATURE)

# TODO: search
PHENOPACKET_GENE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "gene"),
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "alternate_ids": array_of(base_type(SCHEMA_TYPES.STRING)),
        "symbol": base_type(SCHEMA_TYPES.STRING),
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "symbol"]
}, descriptions.GENE)

PHENOPACKET_HTS_FILE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "hts_file"),
    "type": "object",
    "properties": {
        "uri": string_with_format(SCHEMA_STRING_FORMATS.URI),
        "description": base_type(SCHEMA_TYPES.STRING),
        "hts_format": enum_of(["SAM", "BAM", "CRAM", "VCF", "BCF", "GVCF", "FASTQ", "UNKNOWN"]),
        "genome_assembly": base_type(SCHEMA_TYPES.STRING),
        "individual_to_sample_identifiers": base_type(SCHEMA_TYPES.OBJECT),
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    }
}, descriptions.HTS_FILE)


PHENOPACKET_PROCEDURE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "procedure"),
    "title": "Procedure schema",
    "type": "object",
    "properties": {
        "code": ONTOLOGY_CLASS,
        "body_site": ONTOLOGY_CLASS,
        "performed": TIME_ELEMENT_SCHEMA
    },
    "required": ["code"],
}, descriptions=descriptions.PROCEDURE)

REFERENCE_RANGE_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "reference_range"),
    "title": "Reference range schema",
    "type": "object",
    "properties": {
        "unit": ONTOLOGY_CLASS,
        "low": base_type(SCHEMA_TYPES.NUMBER),
        "high": base_type(SCHEMA_TYPES.NUMBER)
    },
    "required": ["unit", "low", "high"]
}

PHENOPACKET_QUANTITY_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "quantity"),
    "title": "Quantity schema",
    "type": "object",
    "properties": {
        "unit": ONTOLOGY_CLASS,
        "value": base_type(SCHEMA_TYPES.NUMBER),
        "reference_range": REFERENCE_RANGE_SCHEMA
    },
    "required": ["unit", "value"]
}

PHENOPACKET_TYPED_QUANTITY_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "typed_quantity"),
    "title": "Quantity schema",
    "type": "object",
    "properties": {
        "type": ONTOLOGY_CLASS,
        "quantity": PHENOPACKET_QUANTITY_SCHEMA
    },
    "required": ["type", "quantity"]
}

PHENOPACKET_VALUE_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "value"),
    "title": "Value schema",
    "type": "object",
    "oneOf": [
        named_one_of("quantity", PHENOPACKET_QUANTITY_SCHEMA),
        named_one_of("ontology_class", ONTOLOGY_CLASS)
    ]
}

PHENOPACKET_COMPLEX_VALUE_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "complex_value"),
    "title": "Complex value schema",
    "type": "object",
    "properties": {
        "typed_quantities": array_of(PHENOPACKET_TYPED_QUANTITY_SCHEMA)
    },
    "required": ["typed_quantities"]
}

PHENOPACKET_MEASUREMENT_VALUE_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "measurement_value"),
    "title": "Measurement value schema",
    "type": "object",
    "oneOf": [
        named_one_of("value", PHENOPACKET_VALUE_SCHEMA),
        named_one_of("complex_value", PHENOPACKET_COMPLEX_VALUE_SCHEMA)
    ]
}

PHENOPACKET_MEASUREMENT_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "measurement"),
    "title": "Measurement schema",
    "type": "object",
    "properties": {
        "description": base_type(SCHEMA_TYPES.STRING),
        "assay": ONTOLOGY_CLASS,
        "time_observed": TIME_ELEMENT_SCHEMA,
        "procedure": PHENOPACKET_PROCEDURE_SCHEMA
    },
    "oneOf": [
        named_one_of("value", PHENOPACKET_VALUE_SCHEMA),
        named_one_of("complex_value", PHENOPACKET_COMPLEX_VALUE_SCHEMA)
    ],
    "required": ["assay"]
}

FILE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "file"),
    "title": "Phenopacket file schema",
    "description": "The File message allows a Phenopacket to link the structured phenotypic data it "
    + "contains to external files which can be used to inform analyses.",
    "type": "object",
    "properties": {
        "uri": base_type(SCHEMA_TYPES.STRING),
        "undividual_to_file_identifiers": base_type(SCHEMA_TYPES.OBJECT),
        "file_attributes": base_type(SCHEMA_TYPES.OBJECT)
    }
}, {})

# noinspection PyProtectedMember
PHENOPACKET_BIOSAMPLE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "biosample"),
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "individual_id": base_type(SCHEMA_TYPES.STRING),
        "derived_from_id": base_type(SCHEMA_TYPES.STRING),
        "description": base_type(SCHEMA_TYPES.STRING),
        "sampled_tissue": ONTOLOGY_CLASS,
        "sample_type": ONTOLOGY_CLASS,
        "phenotypic_features": array_of(PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA),
        "measurements": array_of(PHENOPACKET_MEASUREMENT_SCHEMA),
        "taxonomy": ONTOLOGY_CLASS,
        "time_of_collection": TIME_ELEMENT_SCHEMA,
        "histological_diagnosis": ONTOLOGY_CLASS,
        "tumor_progression": ONTOLOGY_CLASS,
        "tumor_grade": ONTOLOGY_CLASS,
        "pathological_stage": ONTOLOGY_CLASS,
        "pathological_tnm_finding": array_of(ONTOLOGY_CLASS),
        "diagnostic_markers": array_of(ONTOLOGY_CLASS),
        "procedure": PHENOPACKET_PROCEDURE_SCHEMA,
        "files": array_of(FILE_SCHEMA),
        "material_sample": ONTOLOGY_CLASS,
        "sample_processing": ONTOLOGY_CLASS,
        "sample_storage": ONTOLOGY_CLASS,

        # Extended fields
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id"],
}, descriptions.BIOSAMPLE)


PHENOPACKET_DISEASE_ONSET_SCHEMA = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "disease_onset"),
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "anyOf": [
        AGE,
        AGE_RANGE,
        ONTOLOGY_CLASS
    ]
}

PHENOPACKET_DISEASE_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "disease"),
    "title": "Disease schema",
    "type": "object",
    "properties": {
        "term": ONTOLOGY_CLASS,
        "excluded": base_type(SCHEMA_TYPES.BOOLEAN),
        "onset": TIME_ELEMENT_SCHEMA,
        "resolution": TIME_ELEMENT_SCHEMA,
        "disease_stage": array_of(ONTOLOGY_CLASS),
        "clinical_tnm_finding": array_of(ONTOLOGY_CLASS),
        "primary_site": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["term"],
}, descriptions.DISEASE)

DOSE_INTERVAL = {
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "dose_interval"),
    "title": "Phenopacket dose interval for treatment",
    "description": "Represents the dose intervals of a treatment.",
    "type": "object",
    "properties": {
        "quantity": PHENOPACKET_QUANTITY_SCHEMA,
        "schedule_frequency": ONTOLOGY_CLASS,
        "interval": TIME_INTERVAL
    },
    "required": ["quantity", "schedule_frequency", "interval"]
}

PHENOPACKET_TREATMENT = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "treatment"),
    "title": "Phenopacket treatment",
    "description": "Represents a treatment with an agent, such as a drug.",
    "type": "object",
    "properties": {
        "agent": ONTOLOGY_CLASS,
        "route_of_administration": ONTOLOGY_CLASS,
        "dose_intervals": array_of(DOSE_INTERVAL),
        "drug_type": enum_of([
            "UNKNOWN_DRUG_TYPE",
            "PRESCRIPTION",
            "EHR_MEDICATION_LIST",
            "ADMINISTRATION_RELATED_TO_PROCEDURE"
        ]),
        "cumulative_dose": PHENOPACKET_QUANTITY_SCHEMA
    },
    "required": ["agent"]
}, {})  # TODO: add description

PHENOPACKET_RADIATION_THERAPY = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "radiation_therapy"),
    "title": "Phenopacket radiation therapy",
    "description": "Radiation therapy (or radiotherapy) uses ionizing radiation, generally as part of cancer "
                   "treatment to control or kill malignant cells.",
    "type": "object",
    "properties": {
        "modality": ONTOLOGY_CLASS,
        "body_site": ONTOLOGY_CLASS,
        "dosage": base_type(SCHEMA_TYPES.INTEGER),
        "fractions": base_type(SCHEMA_TYPES.INTEGER)
    },
    "required": ["modality", "body_site", "dosage", "fractions"]
}, {})

PHENOPACKET_THERAPEUTIC_REGIMEN = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "therapeutic_regimen"),
    "title": "Phenopacket therapeutic regimen",
    "description": "This element represents a therapeutic regimen which will involve a specified set of treatments "
                   "for a particular condition.",
    "type": "object",
    "properties": {
        "start_time": TIME_ELEMENT_SCHEMA,
        "end_time": TIME_ELEMENT_SCHEMA,
        "status": enum_of(["UNKNOWN_STATUS", "STARTED", "COMPLETED", "DISCONTINUED"])
    },
    "oneOf": [
        named_one_of("ontology_class", ONTOLOGY_CLASS),
        named_one_of("external_reference", PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA)
    ],
    "required": ["status"]
}, {})

ONE_OF_MEDICAL_ACTION = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "one_of_medical_actions"),
    "title": "Supported Phenopacket medical actions",
    "description": "One-of schema for supported medical action schemas",
    "type": "object",
    "oneOf": [
        named_one_of("procedure", PHENOPACKET_PROCEDURE_SCHEMA),
        named_one_of("treatment", PHENOPACKET_TREATMENT),
        named_one_of("radiation_therapy", PHENOPACKET_RADIATION_THERAPY),
        named_one_of("therapeutic_regimen", PHENOPACKET_THERAPEUTIC_REGIMEN)
    ]
}, {})  # TODO: describe

PHENOPACKET_MEDICAL_ACTION_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "medical_action"),
    "title": "Phenopacket medical action schema",
    "description": "Describes a medical action",
    "type": "object",
    "properties": {
        "treatment_target": ONTOLOGY_CLASS,
        "treatment_intent": ONTOLOGY_CLASS,
        "response_to_treatment": ONTOLOGY_CLASS,
        "adverse_events": array_of(ONTOLOGY_CLASS),
        "treatment_termination_reason": ONTOLOGY_CLASS
    },
    "oneOf": [
        named_one_of("procedure", PHENOPACKET_PROCEDURE_SCHEMA),
        named_one_of("treatment", PHENOPACKET_TREATMENT),
        named_one_of("radiation_therapy", PHENOPACKET_RADIATION_THERAPY),
        named_one_of("therapeutic_regimen", PHENOPACKET_THERAPEUTIC_REGIMEN)
    ]
}, descriptions=descriptions.MEDICAL_ACTION)


GENE_DESCRIPTOR = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "gene_descriptor"),
    "title": "Gene descriptor schema",
    "description": "Schema used to describe genes",
    "type": "object",
    "properties": {
        "value_id": base_type(SCHEMA_TYPES.STRING),
        "symbol": base_type(SCHEMA_TYPES.STRING),
        "description": base_type(SCHEMA_TYPES.STRING),
        "alternate_ids": array_of(base_type(SCHEMA_TYPES.STRING)),
        "xrefs": array_of(base_type(SCHEMA_TYPES.STRING)),
        "alternate_symbols": array_of(base_type(SCHEMA_TYPES.STRING)),
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["value_id", "symbol"]
}, descriptions=descriptions.GENE_DESCRIPTOR)


EXPRESSION_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "expression"),
    "title": "Expression schema",
    "description": "Enables description of an object based on a nomenclature",
    "type": "object",
    "properties": {
        "syntax": base_type(SCHEMA_TYPES.STRING),
        "value": base_type(SCHEMA_TYPES.STRING),
        "version": base_type(SCHEMA_TYPES.STRING)
    },
    "required": ["syntax", "value"]
}, descriptions=descriptions.EXPRESSION)


EXTENSION_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "extension"),
    "title": "Extension schema",
    "description": "The Extension class provides a means to extend descriptions with other attributes unique to a "
                   "content provider",
    "type": "object",
    "properties": {
        "name": base_type(SCHEMA_TYPES.STRING),
        "value": base_type(SCHEMA_TYPES.STRING)
    },
    "required": ["name", "value"]
}, {})

VCF_RECORD_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "vcf_record"),
    "title": "VCF record schema",
    "description": "This element is used to describe variants using the Variant Call Format.",
    "type": "object",
    "properties": {
        "genome_assembly": base_type(SCHEMA_TYPES.STRING),
        "chrom": base_type(SCHEMA_TYPES.STRING),
        "pos": base_type(SCHEMA_TYPES.INTEGER),
        "id": base_type(SCHEMA_TYPES.STRING),
        "ref": base_type(SCHEMA_TYPES.STRING),
        "alt": base_type(SCHEMA_TYPES.STRING),
        "qual": base_type(SCHEMA_TYPES.STRING),
        "filter": base_type(SCHEMA_TYPES.STRING),
        "info": base_type(SCHEMA_TYPES.STRING)
    },
    "required": ["genome_assembly", "chrom", "pos", "ref", "alt"]
}, descriptions=descriptions.VCF_RECORD)


VARIANT_DESCRIPTOR = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "variant_descriptor"),
    "title": "Variant descriptor schema",
    "description": "Schema used to describe variants",
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "variation": {
            "$ref": "#/definitions/Variation"
        },
        "label": base_type(SCHEMA_TYPES.STRING),
        "description": base_type(SCHEMA_TYPES.STRING),
        "gene_context": GENE_DESCRIPTOR,
        "expressions": array_of(EXPRESSION_SCHEMA),
        "vcf_record": VCF_RECORD_SCHEMA,
        "xrefs": array_of(base_type(SCHEMA_TYPES.STRING)),
        "alternate_labels": array_of(base_type(SCHEMA_TYPES.STRING)),
        "extensions": array_of(EXTENSION_SCHEMA),
        "molecule_context": base_type(SCHEMA_TYPES.STRING),
        "structural_type": ONTOLOGY_CLASS,
        "vrs_ref_allele_seq": base_type(SCHEMA_TYPES.STRING),
        "allelic_state": ONTOLOGY_CLASS
    },
    "required": ["id"]
}, descriptions=descriptions.VARIANT_DESCRIPTOR)


PHENOPACKET_VARIANT_INTERPRETATION = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "variant_interpretation"),
    "title": "Phenopacket variant interpretation schema",
    "description": "This element represents the interpretation of a variant according to the American College of "
                   "Medical Genetics (ACMG) guidelines.",
    "type": "object",
    "properties": {
        "acmg_pathogenicity_classification": enum_of(["NOT_PROVIDED", "BENIGN", "LIKELY_BENIGN",
                                                      "UNCERTAIN_SIGNIFICANCE", "LIKELY_PATHOGENIC", "PATHOGENIC"]),
        "therapeutic_actionability": enum_of(["UNKNOWN_ACTIONABILITY", "NOT_ACTIONABLE", "ACTIONABLE"]),
        "variation_descriptor": VARIANT_DESCRIPTOR
    },
    "required": ["acmg_pathogenicity_classification", "therapeutic_actionability", "variation_descriptor"]
}, descriptions=descriptions.VARIANT_INTERPRETATION)


PHENOPACKET_GENOMIC_INTERPRETATION = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "genomic_interpretation"),
    "title": "Phenopacket genomic interpretation schema",
    "description": "Describes the interpretation for an individual variant or gene",
    "type": "object",
    "properties": {
        "subject_or_biosample_id": base_type(SCHEMA_TYPES.STRING),
        "interpretation_status": enum_of(["UNKNOWN_STATUS", "REJECTED", "CANDIDATE", "CONTRIBUTORY", "CAUSATIVE"]),
    },
    "oneOf": [
        named_one_of("gene_descriptor", GENE_DESCRIPTOR),
        named_one_of("variant_interpretation", PHENOPACKET_VARIANT_INTERPRETATION)
    ],
    "required": ["subject_or_biosample_id", "interpretation_status"]
}, descriptions.GENOMIC_INTERPRETATION)


PHENOPACKET_DIAGNOSIS_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "diagnosis"),
    "title": "Phenopacket diagnosis schema",
    "description": "Refers to a disease and its genomic interpretations",
    "type": "object",
    "properties": {
        "disease": ONTOLOGY_CLASS,
        "genomic_interpretations": array_of(PHENOPACKET_GENOMIC_INTERPRETATION)
    },
    "required": ["disease"]
}, descriptions=descriptions.DIAGNOSIS)

PHENOPACKET_INTERPRETATION_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "interpretation"),
    "title": "Phenopacket interpretation schema",
    "description": "This message intends to represent the interpretation of a genomic analysis, such as the report "
                   "from a diagnostic laboratory.",
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "progress_status": enum_of([
            "UNKNOWN_PROGRESS",
            "IN_PROGRESS",
            "COMPLETED",
            "SOLVED",
            "UNSOLVED"
        ]),
        "diagnosis": PHENOPACKET_DIAGNOSIS_SCHEMA,
        "summary": base_type(SCHEMA_TYPES.STRING),
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "progress_status"]
}, descriptions=descriptions.INTERPRETATION)

PHENOPACKET_SCHEMA = describe_schema({
    "$schema": DRAFT_07,
    "$id": sub_schema_uri(base_uri, "phenopacket"),
    "title": "Phenopacket schema",
    "description": "Schema for metadata service datasets",
    "type": "object",
    "properties": {
        "id": base_type(SCHEMA_TYPES.STRING),
        "subject": INDIVIDUAL_SCHEMA,
        "phenotypic_features": array_of(PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA),
        "measurements": array_of(PHENOPACKET_MEASUREMENT_SCHEMA),
        "biosamples": array_of(PHENOPACKET_BIOSAMPLE_SCHEMA),
        "interpretations": array_of(PHENOPACKET_INTERPRETATION_SCHEMA),
        "diseases": array_of(PHENOPACKET_DISEASE_SCHEMA),
        "medical_actions": array_of(PHENOPACKET_MEDICAL_ACTION_SCHEMA),
        "files": array_of(FILE_SCHEMA),
        "meta_data": PHENOPACKET_META_DATA_SCHEMA,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "meta_data"],
}, descriptions.PHENOPACKET)

from referencing import Registry, Resource
VRS_REF_RESOURCE = Resource(contents=vrs_schema_definitions, specification=DRAFT_07)
VRS_REF_REGISTRY = Registry().with_resource(
    uri=sub_schema_uri(base_uri, "vrs"),
    resource=VRS_REF_RESOURCE,
)

# For efficient validation of VRS
PHENOPACKET_REF_RESOLVER: jsonschema.RefResolver = jsonschema.RefResolver.from_schema({
    **PHENOPACKET_SCHEMA,
    "definitions": vrs_schema_definitions.get("definitions")
})

_, VRS_VARIATION_SCHEMA = PHENOPACKET_REF_RESOLVER.resolve("#/definitions/Variation")
