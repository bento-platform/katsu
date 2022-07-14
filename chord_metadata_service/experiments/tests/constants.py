def valid_experiment(biosample, instrument=None, table=None, num_experiment=1):
    return {
        "id": f"experiment:{num_experiment}",
        "study_type": "Whole genome Sequencing",
        "experiment_type": "Chromatin Accessibility",
        "experiment_ontology": [{"id": "ontology:1", "label": "Ontology term 1"}],
        "molecule": "total RNA",
        "molecule_ontology": [{"id": "ontology:1", "label": "Ontology term 1"}],
        "library_strategy": "Bisulfite-Seq",
        "library_source": "Genomic",
        "library_selection": "PCR",
        "library_layout": "Single",
        "extraction_protocol": "NGS",
        "reference_registry_id": "some_id",
        "qc_flags": ["flag 1", "flag 2"],
        "extra_properties": {"some_field": "value"},
        "biosample": biosample,
        "instrument": instrument,
        "table": table
    }


def valid_experiment_result():
    return {
        "identifier": "experiment_result:1",
        "description": "Test Experiment result 1",
        "filename": "01.vcf.gz",
        "file_format": "VCF",
        "data_output_type": "Derived data",
        "usage": "download",
        "creation_date": "2021-06-28",
        "created_by": "admin",
        "extra_properties": {"target": "None"}
    }


def valid_instrument():
    return {
        "identifier": "instrument:01",
        "platform": "Illumina",
        "description": "Test description 1",
        "model": "Illumina HiSeq 4000",
        "extra_properties": {"date": "2021-06-21"}
    }
