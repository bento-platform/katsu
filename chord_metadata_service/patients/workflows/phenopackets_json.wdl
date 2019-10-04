workflow phenopackets_json {
    File json_document

    call identity_task {
        input: json_document = json_document
    }
}

task identity_task {
    File json_document
    command {
        true
    }
    output {
        File json_document = json_document
    }
}
