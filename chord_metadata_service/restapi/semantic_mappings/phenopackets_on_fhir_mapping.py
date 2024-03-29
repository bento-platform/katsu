# All fixed values provided by Phenopackets on FHIR Mapping guide

PHENOPACKETS_ON_FHIR_MAPPING = {
    "individual": {
        "title": "Individual",
        "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/Individual",
        "birth_date": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-birthdate",
        "karyotypic_sex": {
            "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-karyotypic-sex",
            "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/karyotypic-sex"
        },
        "taxonomy": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-taxonomy"
    },
    "phenopacket": {
        "title": "Phenopacket",
        "code": {
            "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/document-type",
            "code": "phenopacket"
        },
        "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/Phenopacket",
        "phenotypic_features": {
            "title": "Phenotypic Features",
            "code": {
                "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/section-type",
                "version": "0.1.0",
                "code": "phenotypic-features",
                "display": "Phenotypic Features"
            }
        },
        "biosamples": {
            "title": "Biosamples",
            "code": {
                "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/section-type",
                "version": "0.1.0",
                "code": "biosamples",
                "display": "Biosamples"
            }
        },
        "variants": {
            "title": "Variants",
            "code": {
                "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/section-type",
                "version": "0.1.0",
                "code": "variants",
                "display": "Variants"
            }
        },
        "diseases": {
            "title": "Diseases",
            "code": {
                "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/section-type",
                "version": "0.1.0",
                "code": "diseases",
                "display": "Diseases"
            }
        }
    },
    "biosample": {
        "title": "Biosample",
        "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/Biosample",
        "time_of_collection":
            "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-time_of_collection",
        "histological_diagnosis":
            "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-histological-diagnosis",
        "tumor_progression": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-tumor-progression",
        "tumor_grade": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-tumor-grade",
        "diagnostic_markers": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-diagnostic-markers",
        "is_control_sample": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-control",
        "collected": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-collected"
    },
    "phenotypic_feature": {
        "title": "Phenotypic Feature",
        "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/PhenotypicFeature",
        "severity": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-severity",
        "modifiers": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-modifier",
        "onset": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-onset",
        "evidence": {
            "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/evidence",
            # fixed value
            "evidence_code": "evidenceCode"
        }
    },
    "external_reference": {
        "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/external-reference",
        # fixed values
        "id_url": "id",
        "description_url": "description"
    },
    "disease": {
        "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/Disease",
        "onset": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/disease-onset",
        "disease_stage": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/disease-tumor-stage",
    }
}
