version 1.0

workflow experiments_json {
    input {
        File json_document
        String run_dir
        String project_id
        String dataset_id
        String katsu_url
        String secret__access_token
    }

    call ingest_task {
        input:
            json_document = json_document,
            katsu_url = katsu_url,
            dataset_id = dataset_id,
            token = secret__access_token,
            ingest_report = "~{run_dir}/ingest_report.json"
    }

    output {
        File stdout = ingest_task.txt_output
        File stderr = ingest_task.err_output
        File ingest_report = ingest_task.ingest_report
    }
}

task ingest_task {
    input {
        File json_document
        String katsu_url
        String dataset_id
        String token
        String ingest_report
    }
    command <<<
        RESPONSE=$(curl -X POST -k -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ~{token}" \
            --data "@~{json_document}" \
            -o "~{ingest_report}" \
            "~{katsu_url}/ingest/~{dataset_id}/experiments_json" | jq)

        if [[ "${RESPONSE}" != true ]]
        then
            echo "Error: Metadata service replied with ${RESPONSE}" 1>&2  # to stderr
            exit 1
        fi
        echo ${RESPONSE}
    >>>

    output {
        File txt_output = stdout()
        File err_output = stderr()
        File ingest_report = "~{ingest_report}"
    }
}
