version 1.0

workflow phenopackets_json {
    input {
        File json_document
        String secret__access_token
        String run_dir
        String project_id
        String dataset_id
        String service_url
    }

    call copy_task {
        input: json_document_in = json_document
    }

    call ingest_task {
        input:
            json_document = copy_task.json_document,
            service_url = service_url
    }

    output {
        File json_document_out = copy_task.json_document
    }
}

task copy_task {
    input {
        File json_document_in
    }
    command {
        cp "~{json_document_in}" ingest.json
    }
    output {
        File json_document = "ingest.json"
    }
}

task ingest_task {
    input {
        File json_document
        String service_url
    }
    command {
        echo '${service_url}'
    }
}
