version 1.0

workflow experiments_json {
    input {
        File json_document
        String project_dataset
        String katsu_url
        String access_token
        Boolean validate_ssl
    }

    call ingest_task {
        input:
            json_document = json_document,
            katsu_url = katsu_url,
            project_dataset = project_dataset,
            token = access_token,
            validate_ssl = validate_ssl,
            # ingest_report = "~{run_dir}/ingest_report.json"
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
        String project_dataset
        String token
        # String ingest_report
        Boolean validate_ssl
    }

    # TODO: add ingest report to outputs
    # -o "~{ingest_report}" \
    command <<<
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        RESPONSE=$(curl -X POST ~{true="" false="-k" validate_ssl} -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ~{token}" \
            --data "@~{json_document}" \
            "~{katsu_url}/ingest/${dataset_id}/experiments_json")
        if [[ "${RESPONSE}" != "201" ]]
        then
            echo "Error: Metadata service replied with ${RESPONSE}" 1>&2  # to stderr
            exit 1
        fi
        echo ${RESPONSE}
    >>>

    output {
        File txt_output = stdout()
        File err_output = stderr()
        # File ingest_report = "~{ingest_report}"
    }
}
