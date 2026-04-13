def valid_experiment(biosample, instrument=None, dataset=None, num_experiment=1):
    return {
        "id": f"experiment:{num_experiment}",
        "study_type": "Whole genome Sequencing",
        "experiment_type": "DNA Methylation Array",
        "experiment_ontology": {"id": "ontology:1", "label": "Ontology term 1"},
        "molecule": "total RNA",
        "molecule_ontology": {"id": "ontology:1", "label": "Ontology term 1"},
        "library_strategy": "Bisulfite-Seq",
        "library_source": "Genomic",
        "library_selection": "PCR",
        "library_layout": "Single",
        "library_id": f"lib_id_test-{num_experiment}",
        "library_extract_id": f"lib_extract_id_test-{num_experiment}",
        "insert_size": 350 + num_experiment,
        "description": f"Experimental design description for {num_experiment}",
        "protocol_url": f"http://protocols.io/view/protocol-{num_experiment}",
        "library_description": f"Library construction details for {num_experiment}",
        "extraction_protocol": "NGS",
        "reference_registry_id": "some_id",
        "qc_flags": ["flag 1", "flag 2"],
        "extra_properties": {"some_field": "value"},
        "biosample": biosample,
        "instrument": instrument,
        "dataset": dataset
    }


def valid_experiment_result(num_exp_res=1):
    return {
        "identifier": f"experiment_result:{num_exp_res}",
        "description": f"Test Experiment result {num_exp_res}",
        "filename": f"0{num_exp_res}.vcf.gz",
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
        "device": "Illumina",
        "description": "Test description 1",
        "extra_properties": {"date": "2021-06-21"}
    }
