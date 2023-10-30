version 1.0

workflow document {
    input {
        Array[File] document_files
        String run_dir
        String drs_url
        String project_id
        String dataset_id
        String secret__access_token
    }

    scatter(file in document_files) {
        call post_to_drs {
            input:
                file_path = file,
                drs_url = drs_url,
                project_id = project_id,
                dataset_id = dataset_id,
                token = secret__access_token
        }
    }

    output {
        Array[String] drs_responses = post_to_drs.response_message
    }
}

task post_to_drs {
    input {
        File file_path
        String drs_url
        String project_id
        String dataset_id
        String token
    }
    command {
        curl -k -X POST \
             -F "file=@~{file_path}" \
             -F "project_id=~{project_id}" \
             -F "dataset_id=~{dataset_id}" \
             -H "Authorization: Bearer ~{token}" \
             "~{drs_url}/ingest"
    }
    output {
        String response_message = read_string(stdout())
    }
}
