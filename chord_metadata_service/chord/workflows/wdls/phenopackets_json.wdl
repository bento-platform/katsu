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
            service_url = service_url,
            dataset_id = dataset_id,
            token = secret__access_token
    }

    output {
        File json_document_out = copy_task.json_document
        File stdout = ingest_task.txt_output
        File stderr = ingest_task.err_output
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
        String dataset_id
        String token
    }
    command <<<
        RESPONSE=$(curl -X POST -k -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -H "Authorization: ~{token}" \
            --data "@~{json_document}" \
            "~{service_url}/ingest/~{dataset_id}/phenopackets_json")
        if [ "${RESPONSE}" != "204" ]
        then
            echo "Error: Metadata service replied with HTTP code ${RESPONSE}" 1>&2  # to stderr
            exit 1
        fi
        echo ${RESPONSE}
    >>>

    output {
        File txt_output = stdout()
        File err_output = stderr()
    }
}
