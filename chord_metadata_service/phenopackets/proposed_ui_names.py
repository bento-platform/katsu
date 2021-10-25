# the file contains proposed UI names for complex phenopackets objects to simplify user experience when searching

PROPOSED_UI_NAMES_MAPPING = {
    "phenopacket": {
        "id": "id",
        "subject": {
            "id": {
                "path": "subject.id",
                "ui_name": "Subject ID"
            },
            "sex": {
                "path": "subject.sex",
                "ui_name": "Sex"
            },
            "karyotypic_sex": {
                "path": "subject.karyotypic_sex",
                "ui_name": "Karyotypic sex"
            },
            "taxonomy": {
                "path": "subject.taxonomy.label",
                "ui_name": "Taxonomy"
            }
        },
        "phenotypic_features": {
            "description": {
                "path": "phenotypic_features.[item].description",
                "ui_name": "Phenotypic feature description"
            },
            "type": {
                "path": "phenotypic_features.[item].type.label",
                "ui_name": "Phenotypic feature type"
            },
            "severity": {
                "path": "phenotypic_features.[item].severity.label",
                "ui_name": "Phenotypic feature severity"
            },
            "modifier": {
                "path": "phenotypic_features.[item].modifier.[item].label",
                "ui_name": "Phenotypic feature modifier"
            },
            "onset": {
                "path": "phenotypic_features.[item].onset.label",
                "ui_name": "Phenotypic feature onset"
            }
        },
        "biosamples": {
            "description": {
                "path": "biosamples.[item].description",
                "ui_name": "Biosample description"
            },
            "sampled_tissue": {
                "path": "biosamples.[item].sampled_tissue.label",
                "ui_name": "Sampled tissue"
            },
            "taxonomy": {
                "path": "biosamples.[item].taxonomy.label",
                "ui_name": "Biosample taxonomy"
            },
            "histological_diagnosis": {
                "path": "biosamples.[item].histological_diagnosis.label",
                "ui_name": "Biosample histological diagnosis"
            },
            "tumor_progression": {
                "path": "biosamples.[item].tumor_progression.label",
                "ui_name": "Tumor progression"
            },
            "tumor_grade": {
                "path": "biosamples.[item].tumor_grade.label",
                "ui_name": "Tumor grade"
            },
            "diagnostic_markers": {
                "path": "phenotypic_features.[item].diagnostic_markers.[item].label",
                "ui_name": "Diagnostic markers"
            },
            "procedure": {
                "path": "biosamples.[item].procedure.code.label",
                "ui_name": "Procedure"
            }
        },
        "genes": {
            "id": {
                "path": "genes.[item].id",
                "ui_name": "Gene ID"
            },
            "symbol": {
                "path": "genes.[item].symbol",
                "ui_name": "Gene symbol"
            }
        },
        "variants": {
            "zygosity": {
                "path": "variants.[item].zygosity.label",
                "ui_name": "Zygosity"
            }
        },
        "diseases": {
            "term": {
                "path": "diseases.[item].term.label",
                "ui_name": "Disease"
            },
            "disease_stage": {
                "path": "diseases.[item].disease_stage.[item].label",
                "ui_name": "Disease stage"
            },
            "tnm_finding": {
                "path": "diseases.[item].tnm_finding.[item].label",
                "ui_name": "TNM finding"
            },
        }
    }
}
