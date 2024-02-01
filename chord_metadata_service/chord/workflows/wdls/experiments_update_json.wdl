version 1.0

workflow document {
    input {
        Array[File] document_files
        File experimentJson
        String drs_url
        String project_dataset
        String access_token
        Boolean validate_ssl
    }

    scatter(file in document_files) {
        call post_to_drs {
            input:
                file_path = file,
                drs_url = drs_url,
                project_dataset = project_dataset,
                token = access_token,
                validate_ssl = validate_ssl
        }
    }

    call update_json {
        input:
            drs_uris = post_to_drs.response_message,
            experimentJson = experimentJson
    }

    output {
        Array[String] drs_responses = post_to_drs.response_message
        File updatedExperimentJson = update_json.updatedJson
    }
}

task post_to_drs {
    input {
        File file_path
        String drs_url
        String project_dataset
        String token
        Boolean validate_ssl
    }

    command <<<
        project_id=$(python3 -c 'print("~{project_dataset}".split(":")[0])')
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        curl ~{true="" false="-k" validate_ssl} \
            -X POST \
            -F "file=@~{file_path}" \
            -F "project_id=$project_id" \
            -F "dataset_id=$dataset_id" \
            -H "Authorization: Bearer ~{token}" \
            --fail-with-body \
            "~{drs_url}/ingest"
    >>>
    output {
        String response_message = read_string(stdout())
    }
}

task update_json {
    input {
        Array[String] drs_uris
        File experimentJson
    }

    command <<<
        python3 <<CODE
        import json

        with open("~{experimentJson}") as f:
            data = json.load(f)

        # Assuming the JSON structure and updating it with DRS URIs
        for i, uri in enumerate(~{drs_uris}):
            # Modify below line to fit the JSON structure
            data["results"][i]["url"] = uri

        with open("updated_experiment.json", "w") as f:
            json.dump(data, f, indent=4)
        CODE
    >>>
    output {
        File updatedJson = "updated_experiment.json"
    }
}