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


from chord_metadata_service.patients.descriptions import INDIVIDUAL
from chord_metadata_service.resources.descriptions import RESOURCE
from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES, ontology_class


# If description and help are specified separately, the Django help text differs from the schema description. Otherwise,
# the data type is a string which fills both roles.

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
            "description": "ISO8601 UTC timestamp specifying when when this update occurred.",
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
    "description": "A representation of the evidence for an assertion, such as an observation of a phenotypic feature.",
    "properties": {
        "evidence_code": ontology_class("that represents the evidence type"),
        "reference": EXTERNAL_REFERENCE,
        **EXTRA_PROPERTIES
    }
}


def phenotypic_feature(subject="a subject or biosample"):
    return {
        "description": f"A description of a phenotype that characterizes {subject} of a Phenopacket.",
        "properties": {
            "description": "Human-readable text describing the phenotypic feature; NOT for structured text.",
            "type": ontology_class("which describes the phenotype"),
            "excluded": "Whether the feature is present (false) or absent (true, feature is excluded); default false.",
            "severity": ontology_class("that describes the severity of the condition"),
            "modifiers": {
                "description": "A list of ontology terms that provide more expressive / precise descriptions of a "
                               "phenotypic feature, including e.g. positionality or external factors.",
                "items": ontology_class("that expounds on the phenotypic feature")
            },
            "onset": "Age or time at which the feature was first observed.",
            "evidence": {
                "description": "One or more pieces of evidence that specify how the phenotype was determined.",
                "items": EVIDENCE,
            },
            **EXTRA_PROPERTIES
        }
    }


PHENOTYPIC_FEATURE = phenotypic_feature()


PROCEDURE = {
    "description": "A description of a clinical procedure performed on a subject in order to extract a biosample.",
    "properties": {
        "code": ontology_class("that represents a clinical procedure performed on a subject"),
        "body_site": ontology_class("that is specified when it is not possible to represent the procedure with a "
                                    "single ontology class"),
        "performed": "Age/time when the procedure was performed",
        **EXTRA_PROPERTIES
    }
}


FILE = {
    "description": "A link to a High-Throughput Sequencing (HTS) data file.",
    "properties": {
        "uri": "A valid URI to the file",
        "individual_to_file_identifiers": ("The mapping between the Individual.id or Biosample.id to any "
                                           "identifier in the file."),
        "file_attributes": "A map of attributes pertaining to the file or its contents.",
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

GENE_DESCRIPTOR = {
    "description": "This element represents an identifier for a gene, using the Gene Descriptor from the VRSATILE "
                   "Framework.",
    "properties": {
        "value_id": "Official identifier of the gene. REQUIRED.",
        "symbol": "Official gene symbol. REQUIRED.",
        "description": "A free-text description of the gene",
        "alternate_ids": "Alternative identifier(s) of the gene",
        "xrefs": "Related concept IDs (e.g. gene ortholog IDs) may be placed in xrefs",
        "alternate_symbols": "Alternative symbol(s) of the gene",
        **EXTRA_PROPERTIES}}

ALLELE = {
    "properties": {
        "id": "An arbitrary identifier.",
        "hgvs": "",
        "genome_assembly": "The reference genome identifier e.g. GRCh38.",
        "chr": "A chromosome identifier e.g. chr2 or 2.",
        "pos": "The 1-based genomic position e.g. 134327882.",
        "ref": "The reference base(s).",
        "alt": "The alternate base(s).",
        "info": "Relevant parts of the INFO field.",
        "seq_id": "Sequence ID, e.g. Seq1.",
        "position": "Position , a 0-based coordinate for where the Deleted Sequence starts, e.g. 4.",
        "deleted_sequence": "Deleted sequence , sequence for the deletion, can be empty, e.g. A",
        "inserted_sequence": "Inserted sequence , sequence for the insertion, can be empty, e.g. G",
        "iscn": "E.g. t(8;9;11)(q12;p24;p12)."
    }
}

EXPRESSION = {
    "description": ("The Expression class is designed to enable descriptions based on a specified"
                    " nomenclature or syntax for representing an object. Common examples of expressions"
                    " for the description of molecular variation include the HGVS and ISCN nomenclatures."),
    "properties": {
        "syntax": "A name for the expression syntax. REQUIRED.",
        "value": "The concept expression as a string. REQUIRED.",
        "version": "An optional version of the expression syntax."
    }
}
VCF_RECORD = {
    "description": ("This element is used to describe variants using the Variant Call Format, which is in near "
                    "universal use for exome, genome, and other Next-Generation-Sequencing-based variant calling."
                    " It is an appropriate option to use for variants reported according to their chromosomal "
                    "location as derived from a VCF file."),
    "properties": {
        "genome_assembly": "Identifier for the genome assembly used to call the allele. REQUIRED.",
        "chrom": "Chromosome or contig identifier. REQUIRED.",
        "pos": "The reference position, with the 1st base having position 1. REQUIRED.",
        "id": "Identifier: Semicolon-separated list of unique identifiers where available. If this is a dbSNP variant "
              "thers number(s) should be used.",
        "ref": "Reference base. REQUIRED.",
        "alt": "Alternate base. REQUIRED.",
        "qual": "Quality: Phred-scaled quality score for the assertion made in ALT.",
        "filter": "Filter status: PASS if this position has passed all filters.",
        "info": "Additional information: Semicolon-separated series of additional information fields"
    }
}

VARIANT_DESCRIPTOR = {
    "description": ("Variation Descriptors are part of the VRSATILE framework, a set of conventions extending"
                    " the GA4GH Variation Representation Specification (VRS)."),
    "properties": {
        "id": "Descriptor ID; MUST be unique within document. REQUIRED.",
        "variation": "The VRS Variation object",
        "label": "A primary label for the variation",
        "description": "A free-text description of the variation",
        "gene_context": GENE_DESCRIPTOR,
        "expressions": {
            "description": "",
            "items": EXPRESSION
        },
        "vcf_record": {
            "description": "",
            "items": VCF_RECORD
        },
        "xrefs": "List of CURIEs representing associated concepts. Allele registry, ClinVar, or other related IDs "
                 "should be included as xrefs",
        "alternate_labels": "Common aliases for a variant, e.g. EGFR vIII, are alternate labels",
        "extensions": "List of resource-specific Extensions needed to describe the variation",
        "molecule_context": "The molecular context of the vrs variation.",
        "structural_type": "The structural variant type associated with this variant, such as a substitution, "
                           "deletion, or fusion.",
        "vrs_ref_allele_seq": "A Sequence corresponding to a “ref allele”, describing the sequence expected at a "
                              "SequenceLocation reference.",
        "allelic_state": ("The zygosity of the variant as determined in all of the samples represented"
                          "in this Phenopacket is represented using a list of terms taken from the Genotype Ontology "
                          "(GENO)."),
    }
}

VARIANT_INTERPRETATION = {
    "description": ("This element represents the interpretation of a variant according to the American College of "
                    " Medical Genetics (ACMG) variant interpretation guidelines."),
    "properties": {
        "acmg_pathogenicity_classification": "one of the five ACMG pathogenicity categories, or NOT_PROVIDED. The "
                                             "default is NOT_PROVIDED",
        "therapeutic_actionability": "The therapeutic actionability of the variant, default is UNKNOWN_ACTIONABILITY",
        "variant": VARIANT_DESCRIPTOR
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


BIOSAMPLE = {
    "description": ("A unit of biological material from which the substrate molecules (e.g. genomic DNA, RNA, "
                    "proteins) for molecular analyses are extracted, e.g. a tissue biopsy. Biosamples may be shared "
                    "among several technical replicates or types of experiments."),
    "properties": {
        "id": "Unique arbitrary, researcher-specified identifier for the biosample.",
        "individual_id": "Identifier for the individual this biosample was sampled from.",
        "derived_from_id": "id of the biosample from which the current biosample was derived (if applicable)",
        "description": "Human-readable, unstructured text describing the biosample or providing additional "
                       "information.",
        "sampled_tissue": ontology_class("describing the tissue from which the specimen was collected. The use of "
                                         "UBERON is recommended"),
        "sample_type": "type of material, e.g., RNA, DNA, Cultured cells",
        "phenotypic_features": {
            "description": "A list of phenotypic features / abnormalities of the sample.",
            "items": phenotypic_feature("a biosample")
        },
        "measurements": "List of measurements of the sample",
        "taxonomy": ontology_class("specified when more than one organism may be studied. It is advised that codes"
                                   "from the NCBI Taxonomy resource are used, e.g. NCBITaxon:9606 for humans"),
        "time_of_collection": "Age of the proband at the time the sample was taken.",
        "histological_diagnosis": ontology_class("representing a refinement of the clinical diagnosis. Normal samples "
                                                 "could be tagged with NCIT:C38757, representing a negative finding"),
        "tumor_progression": ontology_class("representing if the specimen is from a primary tumour, a metastasis, or a "
                                            "recurrence. There are multiple ways of representing this using ontology "
                                            "terms, and the terms chosen will have a specific meaning that is "
                                            "application specific"),
        "tumor_grade": ontology_class("representing the tumour grade. This should be a child term of NCIT:C28076 "
                                      "(Disease Grade Qualifier) or equivalent"),
        "pathological_stage": ontology_class("Pathological stage, if applicable."),
        "diagnostic_markers": {
            "description": "A list of ontology terms representing clinically-relevant bio-markers.",
            "items": ontology_class("representing a clinically-relevant bio-marker. Most of the assays, such as "
                                    "immunohistochemistry (IHC), are covered by the NCIT ontology under the "
                                    "sub-hierarchy NCIT:C25294 (Laboratory Procedure), e.g. NCIT:C68748 "
                                    "(HER2/Neu Positive), or NCIT:C131711 Human Papillomavirus-18 Positive)")
        },
        "procedure": PROCEDURE,
        "variants": {
            "description": "A list of variants determined to be present in the biosample.",
            "items": VARIANT
        },
        "is_control_sample": "Whether the sample is being used as a normal control.",
        **EXTRA_PROPERTIES
    }
}

MEASUREMENT = {
    "description": ("The measurement element is used to record individual measurements. "
                    "It can capture quantitative, ordinal (e.g., absent/present), or categorical measurements."),
    "properties": {
        "assay": "OntologyClass that describes the assay used to produce the measurement. REQUIRED.",
        "description": "Human-readable, unstructured text describing the measurement or providing additional "
                       "information.",
        "measurement_value": "Result of the measurement",
        "time_observed": "Time at which measurement was performed. RECOMMENDED.",
        "procedure": "Clinical procdure performed to acquire the sample used for the measurement",
        **EXTRA_PROPERTIES
    }
}

MEDICAL_ACTION = {
    "description": ("This element describes medications, procedures, other actions taken for clinical management."
                    " The element is a list of options."),
    "properties": {
        "action": "One of a list of medical actions. REQUIRED.",
        "treatment_target": "The condition or disease that this treatment was intended to address",
        "treatment_intent": "Whether the intention of the treatment was curative, palliative…",
        "response_to_treatment": "How the patient responded to the treatment",
        "adverse_events": {
            "description": "Any adverse effects experienced by the patient attributed to the treatment",
            "items": ontology_class("Any adverse effects experienced by the patient attributed to the treatment")
        },
        "treatment_termination_reason": "The reason that the treatment was stopped."
    }
}

INTERPRETATION = {
    "description": ("This message intends to represent the interpretation of a genomic analysis,"
                    " such as the report from a diagnostic laboratory."),
    "properties": {
        "id": "Arbitrary identifier. REQUIRED.",
        "progress_status": "The current resolution status. REQUIRED.",
        "diagnosis": "The diagnosis, if made.",
        "summary": "Additional data about this interpretation",
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
            "items": phenotypic_feature("the proband")
        },
        "biosamples": {
            "description": "Samples (e.g. biopsies) taken from the individual, if any.",
            "items": BIOSAMPLE
        },
        "interpretations": {
            "description": "Interpretations related to this phenopacket",
            "items": INTERPRETATION
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
        "measurements": {
            "description": "Measurements performed in the proband",
            "items": MEASUREMENT
        },
        "medical_actions": {
            "description": "Medical actions performed",
            "items": MEDICAL_ACTION
        },
        "meta_data": META_DATA,
        **EXTRA_PROPERTIES
    }
}

AGE = {
    "description": ("The Age element allows the age of the subject to be encoded in several"
                    " different ways that support different use cases. Age is encoded as ISO8601 duration."),
    "properties": {
        "iso8601duration": "An ISO8601 string represent age"
    }
}

AGE_RANGE = {
    "description": "The AgeRange element is intended to be used when the age of a subject is represented by a bin, "
                   "e.g., 5-10 years.",
    "properties": {
        "start": AGE,
        "end": AGE
    }
}

GENOMIC_INTERPRETATION = {
    "description": ("This element is used as a component of the Interpretation element, and describes"
                    " the interpretation for an individual variant or gene."),
    "properties": {
        "subject_or_biosample_id": "The id of the patient or biosample that is the subject being interpreted.",
        "interpretation_status": "Status of the interpretation.",
        "call": {
            "oneOf": [
                GENE_DESCRIPTOR,
                VARIANT_INTERPRETATION
            ]
        }
    }
}

DIAGNOSIS = {
    "description": ("The diagnosis element is meant to refer to the disease that is inferred to be present in the"
                    " individual or family being analyzed."),
    "properties": {
        "disease": DISEASE,
        "genomic_interpretations": {
            "description": "The genomic elements assessed as being responsible for the disease or empty.",
            "items": GENOMIC_INTERPRETATION
        }
    }
}
