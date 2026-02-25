from chord_metadata_service.patients.related_fields import INDIVIDUAL_SELECT_REL

BIOSAMPLE_PREFETCH = (
    "phenotypic_features",
    "experiments",
    "experiments__experiment_results",
    "experiments__instrument",
)

BIOSAMPLE_SELECT_REL = (
    "individual",
    "derived_from_id",
    "location_collected",
)

PHENOPACKET_PREFETCH = (
    *(f"biosamples__{p}" for p in BIOSAMPLE_PREFETCH),
    *(f"biosamples__{p}" for p in BIOSAMPLE_SELECT_REL),
    *(f"subject__{p}" for p in INDIVIDUAL_SELECT_REL),
    "meta_data__resources",
    "diseases",
    "phenotypic_features",
    "interpretations",
    "interpretations__diagnosis",
    "interpretations__diagnosis__genomic_interpretations",
    "interpretations__diagnosis__genomic_interpretations__biosample",
    "interpretations__diagnosis__genomic_interpretations__subject",
    "interpretations__diagnosis__genomic_interpretations__gene_descriptor",
    "interpretations__diagnosis__genomic_interpretations__variant_interpretation__variation_descriptor",
)

PHENOPACKET_SELECT_REL = (
    "dataset",
    "subject",
    "meta_data",
)
