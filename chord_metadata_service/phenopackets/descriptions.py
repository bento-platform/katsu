# Portions of this text copyright (c) 2019-2020 the Canadian Centre for Computational Genomics; licensed under the
# GNU Lesser General Public License version 3.

# Portions of this text (c) 2019 Julius OB Jacobsen, Peter N Robinson, Christopher J Mungall; taken from the
# Phenopackets documentation: https://phenopackets-schema.readthedocs.io
# Licensed under the BSD 3-Clause License:
#   BSD 3-Clause License
#
#   Portions Copyright (c) 2018, PhenoPackets
#   All rights reserved.
#
#   Redistribution and use in source and binary forms, with or without
#   modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice, this
#     list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * Neither the name of the copyright holder nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
#   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#   DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#   FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#   DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#   SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#   CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#   OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#   OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


def describe_schema(schema, descriptions):
    if schema is None:
        return {}  # TODO: If none is specified, should we still annotate it?

    if descriptions is None:
        return schema

    schema_description = (descriptions.get("description", None)
                          if isinstance(descriptions, dict) else descriptions)
    schema_help = (descriptions.get("help", descriptions.get("description", None))
                   if isinstance(descriptions, dict) else descriptions)

    new_schema = schema.copy()

    if schema_description is not None:
        new_schema["description"] = schema_description

    if schema_help is not None:
        new_schema["help"] = schema_help

    if all((schema["type"] == "object", "properties" in schema, isinstance(descriptions, dict),
            "properties" in descriptions)):
        new_schema["properties"] = {p: describe_schema(schema["properties"].get(p, None),
                                                       descriptions["properties"]) for p in schema["properties"]}

    elif all((schema["type"] == "array", "items" in schema, isinstance(descriptions, dict), "items" in descriptions)):
        new_schema["items"] = describe_schema(schema["items"], descriptions["items"])

    return new_schema


def get_help(description):
    if isinstance(description, str):
        return description

    elif "help" in description:
        return description["help"]

    return description["description"]


def rec_help(description, *args):
    if len(args) == 0:
        return get_help(description)

    elif args[0] == "[item]":
        return rec_help(description["items"], *args[1:])

    return rec_help(description["properties"][args[0]], *args[1:])


EXTRA_PROPERTIES = {"extra_properties": {
    # This isn't in the JSON schema, so no description needed
    "help": "Extra properties that are not supported by current schema."
}}


def ontology_class(purpose=""):
    padded_purpose = f" {purpose}" if purpose.strip() != "" else ""
    return {
        "description": f"An ontology term{padded_purpose}",
        "properties": {
            "id": f"A CURIE-style identifier (e.g. HP:0001875) for an ontology term{padded_purpose}.",
            "label": f"A human readable class name for an ontology term{padded_purpose}."
        }
    }


# If description and help are specified separately, the Django help text differs from the schema description. Otherwise,
# the data type is a string which fills both roles.

RESOURCE = {
    "description": "A description of an external resource used for referencing an object.",
    "properties": {
        "id": {
            "description": "Unique researcher-specified identifier for the resource.",
            "help": "For OBO ontologies, the value of this string MUST always be the official OBO ID, which is always "
                    "equivalent to the ID prefix in lower case. For other resources use the prefix in "
                    "identifiers.org."
        },
        "name": {
            "description": "Human-readable name for the resource.",
            "help": "The full name of the resource or ontology referred to by the id element."
        },
        "namespace_prefix": "Prefix for objects from this resource. In the case of ontology resources, this should be "
                            "the CURIE prefix.",
        "url": "Resource URL. In the case of ontologies, this should be an OBO or OWL file. Other resources should "
               "link to the official or top-level url.",
        "version": "The version of the resource or ontology used to make the annotation.",
        "iri_prefix":  "The IRI prefix, when used with the namespace prefix and an object ID, should resolve the term "
                       "or object from the resource in question.",
        **EXTRA_PROPERTIES
    }
}

EXTERNAL_REFERENCE = {
    "description": "An encoding of information about a reference to an external resource.",
    "properties": {
        "id": "An application-specific identifier. It is RECOMMENDED that this is a CURIE that uniquely identifies the "
              "evidence source when combined with a resource; e.g. PMID:123456 with a resource `pmid`. It could also "
              "be a URI or other relevant identifier.",
        "description": "An application-specific free-text description.",
        **EXTRA_PROPERTIES
    }
}

UPDATE = {
    "description": "An update event for a record (e.g. a phenopacket.)",
    "properties": {
        "timestamp": {
            "description": "ISO8601 timestamp specifying when when this update occurred.",
            "help": "Timestamp specifying when when this update occurred.",
        },
        "updated_by": "Information about the person/organization/network that performed the update.",
        "comment": "Free-text comment about the changes made and/or the reason for the update.",
        **EXTRA_PROPERTIES
    }
}

META_DATA = {
    "description": "A structured definition of the resources and ontologies used within a phenopacket.",
    "properties": {
        "created": {
            "description": "ISO8601 timestamp specifying when when this object was created.",
            "help": "Timestamp specifying when when this object was created.",
        },
        "created_by": "Name of the person who created the phenopacket.",
        "submitted_by": "Name of the person who submitted the phenopacket.",
        "resources": {
            "description": "A list of resources or ontologies referenced in the phenopacket",
            "items": RESOURCE
        },
        "updates": {
            "description": "A list of updates to the phenopacket.",
            "items": UPDATE
        },
        "phenopacket_schema_version": "Schema version of the current phenopacket.",
        "external_references": {
            "description": "A list of external (non-resource) references.",
            "items": EXTERNAL_REFERENCE
        },
        **EXTRA_PROPERTIES
    }
}

EVIDENCE = {
    "description": "A representation for the evidence for an assertion such as an observation of a phenotypic feature.",
    "properties": {
        "evidence_code": ontology_class("that represents the evidence type"),
        "reference": EXTERNAL_REFERENCE,
        **EXTRA_PROPERTIES
    }
}

PHENOTYPIC_FEATURE = {
    "description": "A description of a phenotype that characterizes a subject or biosample of a Phenopacket.",
    "properties": {
        "description": "Human-readable text describing the phenotypic feature; NOT for structured text.",
        "type": ontology_class("which describes the phenotype"),
        "negated": "Whether the feature is present (false) or absent (true, feature is negated); default is false.",
        "severity": ontology_class("that describes the severity of the condition"),
        "modifier": {  # TODO: Plural?
            "description": "A list of ontology terms that provide more expressive / precise descriptions of a "
                           "phenotypic feature, including e.g. positionality or external factors.",
            "items": ontology_class("that expounds on the phenotypic feature")
        },
        "onset": ontology_class("that describes the age at which the phenotypic feature was first noticed or "
                                "diagnosed, e.g. HP:0003674"),
        "evidence": {
            "description": "One or more pieces of evidence that specify how the phenotype was determined.",
            "items": EVIDENCE,
        },
        **EXTRA_PROPERTIES
    }
}

PROCEDURE = {
    "description": "A description of a clinical procedure performed on a subject in order to extract a biosample.",
    "properties": {
        "code": ontology_class("that represents a clinical procedure performed on a subject"),
        "body_site": ontology_class("that is specified when it is not possible to represent the procedure with a "
                                    "single ontology class"),
        **EXTRA_PROPERTIES
    }
}

HTS_FILE = {
    "description": "A link to a High-Throughput Sequencing (HTS) data file.",
    "properties": {
        "uri": "A valid URI to the file",
        "description": "Human-readable text describing the file.",
        "hts_format": "The file's format; one of SAM, BAM, CRAM, VCF, BCF, GVCF, FASTQ, or UNKNOWN.",
        "genome_assembly": "Genome assembly ID for the file, e.g. GRCh38.",
        "individual_to_sample_identifiers": ("Mapping between individual or biosample IDs and the sample identifier in "
                                             "the HTS file."),
        **EXTRA_PROPERTIES
    }
}

GENE = {
    "description": "A representation of an identifier for a gene.",
    "properties": {
        "id": "Official identifier of the gene. It SHOULD be a CURIE identifier with a prefix used by the official "
              "organism gene nomenclature committee, e.g. HGNC:347 for humans.",
        "alternate_ids": {
            "description": "A list of identifiers for alternative resources where the gene is used or catalogued.",
            "items": "An alternative identifier from a resource where the gene is used or catalogued."
        },
        "symbol": "A gene's official gene symbol as designated by the organism's gene nomenclature committee, e.g. "
                  "ETF1 from the HUGO Gene Nomenclature committee.",
        **EXTRA_PROPERTIES
    }
}

VARIANT = {
    "description": "A representation used to describe candidate or diagnosed causative variants.",  # TODO: GA4GH VR
    "properties": {
        "allele": "The variant's corresponding allele",  # TODO: Allele data structure
        "zygosity": ontology_class("taken from the Genotype Ontology (GENO) representing the zygosity of the variant"),
        **EXTRA_PROPERTIES
    }
}

DISEASE = {
    "description": "A representation of a diagnosis, i.e. an inference or hypothesis about the cause underlying the "
                   "observed phenotypic abnormalities.",
    "properties": {
        "term": ontology_class("that represents the disease. It's recommended that one of the OMIM, Orphanet, or MONDO "
                               "ontologies is used for rare human diseases"),
        "onset": "A representation of the age of onset of the disease",  # TODO: Onset data structure
        "disease_stage": {
            "description": "A list of terms representing the disease stage. Elements should be derived from child "
                           "terms of NCIT:C28108 (Disease Stage Qualifier) or equivalent hierarchy from another "
                           "ontology.",
            "items": ontology_class("that represents the disease stage. Terms should be children of NCIT:C28108 "
                                    "(Disease Stage Qualifier) or equivalent hierarchy from another ontology"),
        },
        "tnm_finding": {
            "description": "A list of terms representing the tumour TNM score. Elements should be derived from child "
                           "terms of NCIT:C48232 (Cancer TNM Finding) or equivalent hierarchy from another "
                           "ontology.",
            "items": ontology_class("that represents the TNM score. Terms should be children of NCIT:C48232 "
                                    "(Cancer TNM Finding) or equivalent hierarchy from another ontology")
        },
        **EXTRA_PROPERTIES
    }
}

AGE = {
    "description": "An ISO8601 duration string (e.g. P40Y10M05D for 40 years, 10 months, 5 days) representing an age "
                   "of a subject.",
    "help": "Age of a subject."
}

AGE_NESTED = {
    "description": AGE["description"],
    "properties": {
        "age": AGE
    }
}

BIOSAMPLE = {
    "description": ("A unit of biological material from which the substrate molecules (e.g. genomic DNA, RNA, "
                    "proteins) for molecular analyses are extracted, e.g. a tissue biopsy. Biosamples may be shared "
                    "among several technical replicates or types of experiments."),
    "properties": {
        "id": "Unique arbitrary, researcher-specified identifier for the biosample.",
        "individual_id": "Identifier for the individual this biosample was sampled from.",
        "description": "Human-readable, unstructured text describing the biosample or providing additional "
                       "information.",
        "sampled_tissue": ontology_class("describing the tissue from which the specimen was collected. The use of "
                                         "UBERON is recommended"),
        "phenotypic_features": {
            "description": "A list of phenotypic features / abnormalities of the sample.",
            "items": PHENOTYPIC_FEATURE
        },
        "taxonomy": ontology_class("specified when more than one organism may be studied. It is advised that codes"
                                   "from the NCBI Taxonomy resource are used, e.g. NCBITaxon:9606 for humans"),
        "individual_age_at_collection": None,  # TODO: oneOf
        "histological_diagnosis": ontology_class("representing a refinement of the clinical diagnosis. Normal samples "
                                                 "could be tagged with NCIT:C38757, representing a negative finding"),
        "tumor_progression": ontology_class("representing if the specimen is from a primary tumour, a metastasis, or a "
                                            "recurrence. There are multiple ways of representing this using ontology "
                                            "terms, and the terms chosen will have a specific meaning that is "
                                            "application specific."),
        "tumor_grade": ontology_class("representing the tumour grade. This should be a child term of NCIT:C28076 "
                                      "(Disease Grade Qualifier) or equivalent"),
        "diagnostic_markers": {
            "description": "A list of ontology terms representing clinically-relevant bio-markers.",
            "items": ontology_class("representing a clinically-relevant bio-marker. Most of the assays, such as "
                                    "immunohistochemistry (IHC), are covered by the NCIT ontology under the "
                                    "sub-hierarchy NCIT:C25294 (Laboratory Procedure), e.g. NCIT:C68748 "
                                    "(HER2/Neu Positive), or NCIT:C131711 Human Papillomavirus-18 Positive).")
        },
        "procedure": PROCEDURE,
        "hts_files": {
            "description": "A list of HTS files derived from the biosample.",
            "items": HTS_FILE
        },
        "variants": {
            "description": "A list of variants determined to be present in the biosample.",
            "items": VARIANT
        },
        "is_control_sample": "Whether the sample is being used as a normal control.",
        **EXTRA_PROPERTIES
    }
}

# TODO: This is part of another app
INDIVIDUAL = {
    "description": "A subject of a phenopacket, representing either a human (typically) or another organism.",
    "properties": {
        # Phenopackets / shared
        "id": "A unique researcher-specified identifier for an individual.",
        "alternate_ids": {
            "description": "A list of alternative identifiers for an individual.",
            "items": "One of possibly many alternative identifiers for an individual."
        },
        "date_of_birth": "A timestamp representing an individual's date of birth; either exactly or imprecisely.",
        "age": None,  # TODO: Age or AgeRange
        "sex": "The phenotypic sex of an individual, as would be determined by a midwife or physician at birth.",
        "karyotypic_sex": "The karyotypic sex of an individual.",
        "taxonomy": ontology_class("specified when more than one organism may be studied. It is advised that codes"
                                   "from the NCBI Taxonomy resource are used, e.g. NCBITaxon:9606 for humans"),

        # FHIR-specific
        "active": "Whether a patient's record is in active use.",
        "deceased": "Whether a patient is deceased.",

        # mCode-specific
        "race": "A code for a person's race (mCode).",
        "ethnicity": "A code for a person's ethnicity (mCode).",

        **EXTRA_PROPERTIES
    }
}

PHENOPACKET = {
    "description": "An anonymous phenotypic description of an individual or biosample with potential genes of interest "
                   "and/or diagnoses. The concept has multiple use-cases.",
    "properties": {
        "id": "Unique, arbitrary, researcher-specified identifier for the phenopacket.",
        "subject": INDIVIDUAL,  # TODO: Just phenopackets-specific components of individual?
        "phenotypic_features": {
            "description": "A list of phenotypic features observed in the proband.",
            "items": PHENOTYPIC_FEATURE
        },  # TODO: Not present in model?
        "biosamples": {
            "description": "Samples (e.g. biopsies) taken from the individual, if any.",
            "items": BIOSAMPLE
        },
        "genes": {
            "description": "Genes deemed to be relevant to the case; application-specific.",
            "items": GENE
        },
        "variants": {
            "description": "A list of variants identified in the proband.",
            "items": VARIANT
        },
        "diseases": {
            "description": "A list of diseases diagnosed in the proband.",
            "items": DISEASE
        },
        "hts_files": {
            "description": "A list of HTS files derived from the individual.",
            "items": HTS_FILE
        },
        "meta_data": META_DATA,
        **EXTRA_PROPERTIES
    }
}

# TODO: Mutually recursive, use functions
# DIAGNOSIS
# GENOMIC_INTERPRETATION
