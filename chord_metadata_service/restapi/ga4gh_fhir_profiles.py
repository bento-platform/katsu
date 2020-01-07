# Allf fixed values provided by Pheno_FHIR Mapping guide
# TODO split by some logic
GA4GH_FHIR_PROFILES = {
    "individual-age": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-age",
    "individual-karyotypic-sex": {
        "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-karyotypic-sex",
        "coding_system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/karyotypic-sex"
    },
    "individual-taxonomy": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-taxonomy",
    "biosample-individual-age-at-collection": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-individual-age-at-collection",
    "histological_diagnosis": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-histological-diagnosis",
    "tumor_progression": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-tumor-progression",
    "tumor_grade": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-tumor-grade",
    "diagnostic_markers": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-diagnostic-markers",
    "is_control_sample": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-control",
    "severity": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-severity",
    "modifier": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-modifier",
    "onset": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-onset",
    "evidence": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/evidence",
    "reference": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/external-reference",
    # GA4GH guide provides hardcoded values
    "evidence_code": "evidenceCode",
    "extension_id_url": "id",
    "extension_description_url": "description",
    "document_reference_status": "current",
    "hts_file": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/HtsFile",
    "genome_assembly": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/htsfile-genome-assembly",
    # FHIR
    "region_studied": "http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/region-studied",
    "disease-onset": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/disease-onset",
    "disease-tumor-stage": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/disease-tumor-stage",
    # fixed values for sections in phenopacket-composition
    # TODO split
    "phenopacket": {
        "title": "Phenopacket",
        "code": {
            "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/document-type",
            "code": "phenopacket"
        }
    },

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
    },
    "hts_files": {
        "title": "HTS Files",
        "code": {
            "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/section-type",
            "version": "0.1.0",
            "code": "hts-files",
            "display": "HTS Files"
        }
    }
}


HL7_GENOMICS_REPORTING = {
    "observation_component_gene_studied": {
        "system": "https://loinc.org",
        "id": "48018-6",
        "label": "Gene studied [ID]"
    },
    "HGNC": "https://www.genenames.org/",
    "variant": "http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/variant",
    "observation_component_variant": {
        "system": "https://loinc.org",
        "id": "81300-6",
        "label": "Structural variant [Length]"
    }
}