version 1.0

workflow phenopackets_json {
    input {
        File json_document
        String access_token
        String project_dataset
        String katsu_url
        Boolean validate_ssl
    }

    call ingest_task {
        input:
            json_document = json_document,
            katsu_url = katsu_url,
            project_dataset = project_dataset,
            token = access_token,
            validate_ssl = validate_ssl
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
        Boolean validate_ssl
    }
    command <<<
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        RESPONSE=$(curl -X POST ~{true="" false="-k" validate_ssl} -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ~{token}" \
            --data "@~{json_document}" \
            "~{katsu_url}/ingest/${dataset_id}/phenopackets_json")
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
