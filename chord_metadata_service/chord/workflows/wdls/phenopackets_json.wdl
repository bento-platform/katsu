version 1.0

workflow phenopackets_json {
    input {
        File json_document
        String secret__access_token
        String run_dir
        String project_id
        String dataset_id
        String katsu_url
    }

    call ingest_task {
        input:
            json_document = json_document,
            katsu_url = katsu_url,
            dataset_id = dataset_id,
            token = secret__access_token
    }

    output {
        File stdout = ingest_task.txt_output
        File stderr = ingest_task.err_output
    }
}

task ingest_task {
    input {
        File json_document
        String katsu_url
        String dataset_id
        String token
    }
    command <<<
        RESPONSE=$(curl -X POST -k -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ~{token}" \
            --data "@~{json_document}" \
            "~{katsu_url}/ingest/~{dataset_id}/phenopackets_json")
        if [[ "${RESPONSE}" != "204" ]]
        then
            echo "Error: Metadata service replied with ${RESPONSE}" 1>&2  # to stderr
            exit 1
        fi
        echo ${RESPONSE}
    >>>

    output {
        File txt_output = stdout()
        File err_output = stderr()
    }
}
