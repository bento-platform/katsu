version 1.0

workflow experiments_json {
    input {
        File json_document
        String project_dataset
        String katsu_url
        String access_token
    }

    call ingest_task {
        input:
            json_document = json_document,
            katsu_url = katsu_url,
            project_dataset = project_dataset,
            token = access_token
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
        String project_dataset
        String token
    }
    command <<<
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1]))'))
        RESPONSE=$(curl -X POST -k -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ~{token}" \
            --data "@~{json_document}" \
            "~{katsu_url}/ingest/${dataset_id}/experiments_json")
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
