workflow mcode_fhir_json {
    File json_document

    call copy_task {
        input: json_document_in = json_document
    }

    output {
        File json_document_out = copy_task.json_document
    }
}

task copy_task {
    File json_document_in
    command {
        cp "${json_document_in}" ingest.json
    }
    output {
        File json_document = "ingest.json"
    }
}
