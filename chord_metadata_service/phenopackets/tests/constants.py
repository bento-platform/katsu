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


VALID_INDIVIDUAL_1 = {
    "id": "patient:1",
    "date_of_birth": "1967-01-01",
    "sex": "MALE"
}


VALID_INDIVIDUAL_2 = {
    "id": "patient:2",
    "date_of_birth": "1978-01-01",
    "sex": "FEMALE"
}


VALID_HTS_FILE = {
    "uri": "https://data.example/genomes/germline_wgs.vcf.gz",
    "description": "Matched normal germline sample",
    "hts_format": "VCF",
    "genome_assembly": "GRCh38",
    "individual_to_sample_identifiers": {
      "patient:1": "NA12345"
    },
    "extra_properties": {
        "comment": "test data"
    }
}


def valid_biosample_1(individual, procedure):
    return dict(
        id='biosample_id:1',
        individual=individual,
        sampled_tissue={
            "id": "UBERON_0001256",
            "label": "wall of urinary bladder"
        },
        description='This is a test biosample.',
        taxonomy={
            "id": "NCBITaxon:9606",
            "label": "Homo sapiens"
        },
        individual_age_at_collection='P52Y2M',
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
        is_control_sample=True
    )


def valid_biosample_2(individual, procedure):
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
        individual_age_at_collection='P52Y2M',
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
        negated=True,
        severity={
            "id": "HP: 0012825",
            "label": "Mild"
        },
        modifier=[
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
        },
        biosample=biosample,
        phenopacket=phenopacket
        )