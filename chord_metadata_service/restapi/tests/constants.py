INVALID_INGEST_BODY = {
    "dataset_id": "62b5fc67-d925-4409-bb59-e1e9a1ef10af",
    "patients": "patients_file",
    "metadata": {
        "test": "required created_by is not present"
    }
}


INVALID_FHIR_BUNDLE_1 = {
    "resourceType": "NotBundle",
    "entry": [
        {
            "test": "required resource is not present"
        }
    ]
}
