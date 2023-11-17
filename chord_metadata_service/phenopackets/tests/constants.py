VALID_PROCEDURE_1 = {
    "code": {
        "id": "NCIT:C28743",
        "label": "Punch Biopsy"
    },
    "body_site": {
        "id": "UBERON:0003403",
        "label": "skin of forearm"
    }
}

VALID_PROCEDURE_2 = {
    "code": {
        "id": "NCIT:C28743",
        "label": "Punch Biopsy"
    },
    "body_site": {
        "id": "UBERON:0004263",
        "label": "upper arm skin"
    }
}

VALID_META_DATA_1 = {
    "created_by": "David Lougheed",
    "submitted_by": "David Lougheed"
}

VALID_META_DATA_2 = {"created_by": "Victor Rocheleau",
                     "submitted_by": "Victor Rocheleau",
                     "external_references": [{"id": "DOI:10.1016/j.jaccas.2020.04.001",
                                              "reference": "PMID:32292915",
                                              "description": "The Imperfect Cytokine Storm: Severe COVID-19 With ARDS "
                                                             "in a Patient on Durable LVAD Support"}],
                     "updates": [{"timestamp": "2018-06-10T10:59:06Z",
                                  "updated_by": "Julius J.",
                                  "comment": "added phenotypic features to individual patient:1"}],
                     "phenopacket_schema_version": "2.0"}

VALID_INDIVIDUAL_1 = {
    "id": "patient:1",
    "date_of_birth": "1967-01-01",
    "sex": "MALE",
    "time_at_last_encounter": {
        "age": {
            "iso8601duration": "P45Y"
        }
    },
    "extra_properties": {
        "education": "Bachelor's Degree"
    }
}

VALID_INDIVIDUAL_2 = {
    "id": "patient:2",
    "date_of_birth": "1978-01-01",
    "sex": "FEMALE",
    "time_at_last_encounter": {
        "age_range": {
            "start": {
                "age": {
                    "iso8601duration": "P30Y"
                }
            },
            "end": {
                "age": {
                    "iso8601duration": "P35Y"
                }
            }
        }
    }
}

VALID_GENE_1 = {
    "id": "HGNC:347",
    "alternate_ids": ["ensembl:ENSRNOG00000019450", "ncbigene:307503"],
    "symbol": "ETF1",
    "extra_properties": {
        "comment": "test data"
    }
}

INVALID_GENE_2 = {
    "id": "HGNC:347",
    "alternate_ids": "ensembl:ENSRNOG00000019450",
    "symbol": "ETF1",
    "extra_properties": {
        "comment": "test data"
    }
}

DUPLICATE_GENE_2 = {
    "id": "HGNC:347",
    "symbol": "DYI"
}

VALID_GENE_DESCRIPTOR_1 = {
    "value_id": "HGNC:347",
    "symbol": "ETF1",
    "alternate_ids": ["ensembl:ENSRNOG00000019450", "ncbigene:307503"],
    "extra_properties": {
        "comment": "test data"
    }
}

VALID_VARIANT_1 = {
    "allele_type": "spdiAllele",
    "allele": {
        "id": "clinvar:13294",
        "seq_id": "NC_000010.10",
        "position": 123256214,
        "deleted_sequence": "T",
        "inserted_sequence": "G"
    },
    "zygosity": {
        "id": "NCBITaxon:9606",
        "label": "human"
    },
    "extra_properties": {
        "comment": "test data"
    }
}

VALID_VARIANT_2 = {
    "allele_type": "spdiAllele",
    "spdiAllele": {
        "id": "clinvar:13294",
        "seq_id": "NC_000010.10",
        "position": 123256214,
        "deleted_sequence": "T",
        "inserted_sequence": "G"
    },
    "zygosity": {
        "id": "NCBITaxon:9606",
        "label": "human"
    },
    "extra_properties": {
        "comment": "test data"
    }
}

VALID_VARIANT_3 = {
    "location": {
        "interval": {
            "end": {
                "type": "Number",
                "value": 44908822
            },
            "start": {
                "type": "Number",
                "value": 44908821
            },
            "type": "SequenceInterval"
        },
        "sequence_id": "ga4gh:SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
        "type": "SequenceLocation"
    },
    "state": {
        "sequence": "T",
        "type": "SequenceState"
    },
    "type": "Allele"
}

VALID_ALLELE = {
    "location": {
        "interval": {
            "end": {
                "type": "Number",
                "value": 44908822
            },
            "start": {
                "type": "Number",
                "value": 44908821
            },
            "type": "SequenceInterval"
        },
        "sequence_id": "ga4gh:SQ.IIB53T8CNeJJdUqzn9V_JnRtQadwWCbl",
        "type": "SequenceLocation"
    },
    "state": {
        "sequence": "T",
        "type": "SequenceState"
    },
    "type": "Allele"
}

VALID_VARIANT_DESCRIPTOR = {
    "id": "clinvar:13294",
    "expressions": [{
        "syntax": "hgvs",
        "value": "NM_001848.2:c.877G\u003eA"
    }],
    "allelic_state": {
        "id": "GENO:0000135",
        "label": "heterozygous"
    }
}

VALID_DISEASE_ONTOLOGY = {
    "id": "OMIM:164400",
    "label": "Spinocerebellar ataxia 1"
}

VALID_DISEASE_1 = {
    "term": {
        "id": "OMIM:164400",
        "label": "Spinocerebellar ataxia 1"
    },
    "excluded": "False",
    "onset": {
        "age": {
            "iso8601duration": "P25Y3M2D"
        }
    },
    "resolution": {
        "age": {
            "iso8601duration": "P28Y3M2D"
        }
    },
    "disease_stage": [
        {
            "id": "NCIT:C48233",
            "label": "Cancer TNM Finding by Site"
        }
    ],
    "clinical_tnm_finding": [
        {
            "id": "NCIT:C28091",
            "label": "Gleason Score 7"
        }
    ],
    "extra_properties": {
        "comment": "test data"
    }
}

INVALID_DISEASE_2 = {
    "term": {
        "id": "OMIM:164400",
        "label": "Spinocerebellar ataxia 1"
    },
    "onset": {
        "age": "P55Y3M2D"
    },
    "disease_stage": [
        {
            "id": "NCIT:C28091"
        }
    ],
    "extra_properties": {
        "comment": "test data"
    }
}

VALID_MEASUREMENT_1 = {
    "assay": {
        "id": "NCIT:C113237",
        "label": "Absolute Blood Lymphocyte Count"
    },
    "value": {
        "quantity": {
            "unit": {
                "id": "NCIT:C67245",
                "label": "Thousand Cells"
            },
            "value": 1.4,
            "referenceRange": {
                "unit": {
                    "id": "NCIT:C67245",
                    "label": "Thousand Cells"
                },
                "low": 1.0,
                "high": 4.5
            }
        }
    },
    "timeObserved": {
        "interval": {
            "start": "2019-09-01T00:00:00Z",
            "end": "2020-03-01T00:00:00Z"
        }
    }
}

VALID_MEASUREMENT_2 = {
    "assay": {
        "id": "LOINC:26474-7",
        "label": "Lymphocytes [#/volume] in Blood"
    },
    "value": {
        "quantity": {
            "unit": {
                "id": "NCIT:C67245",
                "label": "Thousand Cells"
            },
            "value": 0.7,
            "referenceRange": {
                "unit": {
                    "id": "NCIT:C67245",
                    "label": "Thousand Cells"
                },
                "low": 1.0,
                "high": 4.5
            }
        }
    },
    "timeObserved": {
        "timestamp": "2020-03-20T00:00:00Z"
    }
}

VALID_MEDICAL_ACTIONS = [
    {
        "procedure": {
            "code": {
                "id": "NCIT:C80473",
                "label": "Left Ventricular Assist Device"
            },
            "performed": {
                "timestamp": "2016-01-01T00:00:00Z"
            }
        }
    },
    {
        "treatment": {
            "agent": {
                "id": "NCIT:C722",
                "label": "Oxygen"
            },
            "routeOfAdministration": {
                "id": "NCIT:C38284",
                "label": "Nasal Route of Administration"
            },
            "doseIntervals": [
                {
                    "quantity": {
                        "unit": {
                            "id": "NCIT:C67388",
                            "label": "Liter per Minute"
                        },
                        "value": 2.0
                    },
                    "scheduleFrequency": {
                        "id": "NCIT:C125004",
                        "label": "Once Daily"
                    },
                    "interval": {
                        "start": "2020-03-20T00:00:00Z",
                        "end": "2020-03-22T00:00:00Z"
                    }
                },
                {
                    "quantity": {
                        "unit": {
                            "id": "NCIT:C67388",
                            "label": "Liter per Minute"
                        },
                        "value": 50.0
                    },
                    "scheduleFrequency": {
                        "id": "NCIT:C125004",
                        "label": "Once Daily"
                    },
                    "interval": {
                        "start": "2020-03-22T00:00:00Z",
                        "end": "2020-03-23T00:00:00Z"
                    }
                }
            ]
        }
    }
],

VALID_GENOMIC_INTERPRETATION = {
    "subjectOrBiosampleId": "proband A",
    "interpretationStatus": "CAUSATIVE",
    "variantInterpretation": {
        "acmgPathogenicityClassification": "PATHOGENIC",
        "therapeuticActionability": "ACTIONABLE",
        "variationDescriptor": {
            "id": "variant_descriptor-id",
            "variation": {
                "copyNumber": {
                    "derivedSequenceExpression": {
                        "location": {
                            "sequenceId": "refseq:NC_000013.14",
                            "sequenceInterval": {
                                "startNumber": {
                                    "value": "25981249"
                                },
                                "endNumber": {
                                    "value": "61706822"
                                }
                            }
                        },
                        "reverseComplement": False
                    },
                    "number": {
                        "value": "1"
                    }
                }
            },
            "extensions": [{
                "name": "mosaicism",
                "value": "40.0%"
            }],
            "moleculeContext": "unspecified_molecule_context"
        }
    }
}


def valid_phenopacket(subject, meta_data):
    return dict(
        id='phenopacket:1',
        subject=subject,
        meta_data=meta_data
    )


def valid_biosample_1(individual, procedure=VALID_PROCEDURE_1):
    return dict(
        id='biosample_id:1',
        individual_id=individual,
        description='This is a test biosample.',
        sampled_tissue={
            "id": "UBERON_0001256",
            "label": "wall of urinary bladder"
        },
        taxonomy={
            "id": "NCBITaxon:9606",
            "label": "Homo sapiens"
        },
        time_of_collection={
            "age": {
                "iso8601duration": "P45Y"
            }
        },
        histological_diagnosis={
            "id": "NCIT:C39853",
            "label": "Infiltrating Urothelial Carcinoma"
        },
        tumor_progression={
            "id": "NCIT:C84509",
            "label": "Primary Malignant Neoplasm"
        },
        tumor_grade={
            "id": "NCIT:C48766",
            "label": "pT2b Stage Finding"
        },
        diagnostic_markers=[
            {
                "id": "NCIT:C49286",
                "label": "Hematology Test"
            },
            {
                "id": "NCIT:C15709",
                "label": "Genetic Testing"
            }
        ],
        procedure=procedure,
    )


def valid_biosample_2(individual, procedure=VALID_PROCEDURE_2):
    return dict(
        id='biosample_id:2',
        individual=individual,
        sampled_tissue={
            "id": "UBERON_0001256",
            "label": "urinary bladder"
        },
        description='This is a test biosample.',
        taxonomy={
            "id": "NCBITaxon:9606",
            "label": "Homo sapiens"
        },
        time_of_collection={
            "age": {
                "iso8601duration": "P45Y"
            }
        },
        histological_diagnosis={
            "id": "NCIT:C39853",
            "label": "Infiltrating Urothelial Carcinoma"
        },
        tumor_progression={
            "id": "NCIT:C3677",
            "label": "Benign Neoplasm"
        },
        tumor_grade={
            "id": "NCIT:C48766",
            "label": "pT2b Stage Finding"
        },
        diagnostic_markers=[
            {
                "id": "NCIT:C49286",
                "label": "Hematology Test"
            },
            {
                "id": "NCIT:C15709",
                "label": "Genetic Testing"
            }
        ],
        procedure=procedure,
        is_control_sample=True
    )


def valid_phenotypic_feature(biosample=None, phenopacket=None):
    return dict(
        description='This is a test phenotypic feature',
        pftype={
            "id": "HP:0000520",
            "label": "Proptosis"
        },
        excluded=True,
        severity={
            "id": "HP: 0012825",
            "label": "Mild"
        },
        modifiers=[
            {
                "id": "HP: 0012825 ",
                "label": "Mild"
            },
            {
                "id": "HP: 0012823 ",
                "label": "Semi-mild"
            }
        ],
        onset={
            "ontology_class": {
                "id": "HP:0003577",
                "label": "Congenital onset"
            }
        },
        evidence={
            "evidence_code": {
                "id": "ECO:0006017",
                "label": "Author statement from published clinical study used in manual assertion"
            },
            "reference": {
                "id": "PMID:30962759",
                "description": "Recurrent Erythema Nodosum in a Child with a SHOC2 Gene Mutation"
            }
        },
        extra_properties={
            "comment": "test data",
            "datatype": "symptom"
        },
        biosample=biosample,
        phenopacket=phenopacket
    )


def invalid_phenotypic_feature():
    return dict(
        description='This is a test phenotypic feature',
        excluded=True,
        severity={
            "id": "HP: 0012825",
            "label": "Mild"
        },
        modifiers=[
            {
                "label": "Mild"
            },
            {
                "id": "HP: 0012823 "
            }
        ],
        onset={
            "id": "HP:0003577",
            "label": "Congenital onset"
        },
        evidence={
            "evidence_code": {
                "id": "ECO:0006017",
                "label": "Author statement from published clinical study used in manual assertion"
            },
            "reference": {
                "id": "PMID:30962759",
                "description": "Recurrent Erythema Nodosum in a Child with a SHOC2 Gene Mutation"
            }
        },
        extra_properties={
            "comment": "test data"
        }
    )


def valid_variant_interpretation(variant_descriptor, acmg_class="NOT_PROVIDED",
                                 therapeutic_actionability="UNKNOWN_ACTIONABILITY"):
    return dict(
        acmg_pathogenicity_classification=acmg_class,
        therapeutic_actionability=therapeutic_actionability,
        variation_descriptor=variant_descriptor
    )


def valid_variant_descriptor(gene_descriptor):
    return dict(
        **VALID_VARIANT_DESCRIPTOR,
        gene_context=gene_descriptor
    )


def valid_genomic_interpretation(gene_descriptor=None, variant_interpretation=None):
    base = dict(
        interpretation_status='CANDIDATE',
        extra_properties={
            "comment": "test data"
        }
    )
    if gene_descriptor:
        base = dict(
            **base,
            gene_descriptor=gene_descriptor
        )
    if variant_interpretation:
        base = dict(
            **base,
            variant_interpretation=variant_interpretation
        )
    return base


def valid_diagnosis(disease):
    return dict(
        disease_ontology=disease,
        extra_properties={
            "comment": "test data"
        }
    )


def valid_interpretation(diagnosis):
    return dict(
        id='interpretation:1',
        progress_status='IN_PROGRESS',
        diagnosis=diagnosis,
        summary="Test interpretation",
        extra_properties={
            "comment": "test data"
        }
    )
