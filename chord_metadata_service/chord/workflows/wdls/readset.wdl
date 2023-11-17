version 1.0

workflow readset {
    input {
        Array[File] readset_files
        String drs_url
        String project_dataset
        String access_token
    }

    scatter(file in readset_files) {
        call post_to_drs {
            input:
                file_path = file,
                drs_url = drs_url,
                project_dataset = project_dataset,
                token = access_token
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
        String project_dataset
        String token
    }
    command {
        project_id=$(python3 -c 'print("~{project_dataset}".split(":")[0])')
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        curl -k -X POST \
             -F "file=@~{file_path}" \
             -F "project_id=$project_id" \
             -F "dataset_id=$dataset_id" \
             -H "Authorization: Bearer ~{token}" \
             "~{drs_url}/ingest"
    }
    output {
        String response_message = read_string(stdout())
    }
}
