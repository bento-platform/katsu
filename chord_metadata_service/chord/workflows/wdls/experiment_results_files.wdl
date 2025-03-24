version 1.0

workflow experiment_results_files {
    input {
        Array[File] files
        String drs_url
        String project_dataset
        String access_token
        Boolean validate_ssl
    }

    scatter (file in files) {
        call post_to_drs {
            input:
                file_path       = file,
                drs_url         = drs_url,
                project_dataset = project_dataset,
                token           = access_token,
                validate_ssl    = validate_ssl
        }
    }

    output {
        Array[String] drs_responses = flatten(post_to_drs.response_message)
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
        # Handling index files
        handle_index_file() {
            local file_extension="$1"
            local index_extension="$2"

            index_file="~{file_path}${index_extension}"
            index_name=$(basename "$index_file")

            # Search for the index file in DRS
            search_resp=$(curl ~{true="" false="-k" validate_ssl} -s \
                -H "Authorization: Bearer ~{token}" \
                "~{drs_url}/search?name=${index_name}")

            # If the index is not found, create and upload it
            if ! echo "$search_resp" | grep -q "\"name\": \"${index_name}\""; then
                samtools index "~{file_path}"
                resp_index=$(curl ~{true="" false="-k" validate_ssl} \
                    -X POST \
                    -F "file=@${index_file}" \
                    -F "project_id=$project_id" \
                    -F "dataset_id=$dataset_id" \
                    -H "Authorization: Bearer ~{token}" \
                    --fail-with-body \
                    "~{drs_url}/ingest")
                echo "$resp_index"
            else
                echo "Index file '${index_name}' already in DRS. Skipped indexing and upload."
            fi
        }

        project_id=$(python3 -c 'print("~{project_dataset}".split(":")[0])')
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')

        resp_main=$(curl ~{true="" false="-k" validate_ssl} \
            -X POST \
            -F "file=@~{file_path}" \
            -F "project_id=$project_id" \
            -F "dataset_id=$dataset_id" \
            -H "Authorization: Bearer ~{token}" \
            --fail-with-body \
            "~{drs_url}/ingest")

        # Handle .bam or .cram files with their respective indices
        if [[ "~{file_path}" =~ \.bam$ ]]; then
            handle_index_file ".bam" ".bai"
        elif [[ "~{file_path}" =~ \.cram$ ]]; then
            handle_index_file ".cram" ".crai"
        fi

        echo "$resp_main"
    >>>

    output {
        Array[String] response_message = read_lines(stdout())
    }
}
