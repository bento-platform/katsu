version 1.0

workflow experiment_results_drs {
    input {
        String drs_url
        String katsu_url
        String project_dataset
        String access_token
        Boolean validate_ssl
    }

    call fetch_experiment_results {
        input:
            katsu_url = katsu_url,
            project_dataset = project_dataset,
            access_token = access_token,
            validate_ssl = validate_ssl
    }

    call fetch_drs_objects {
        input:
            drs_url = drs_url,
            project_dataset = project_dataset,
            access_token = access_token,
            validate_ssl = validate_ssl
    }
}

task fetch_experiment_results {
    input {
        String katsu_url
        String project_dataset
        String access_token
        Boolean validate_ssl
    }
    command <<<
        project_id=$(python3 -c 'print("~{project_dataset}".split(":")[0])')
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        curl ~{true="" false="-k" validate_ssl} \
            -X GET \
            -H "Authorization: Bearer ~{access_token}" \
            --fail-with-body \
            "~{katsu_url}/api/experimentresults?project=${project_id}&dataset=${dataset_id}&has_url=False"
    >>>
    output {

    }
}

task fetch_drs_objects {
    input {
        String drs_url
        String project_dataset
        String access_token
        String validate_ssl
    }
    command <<<
        project_id=$(python3 -c 'print("~{project_dataset}".split(":")[0])')
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        curl ~{true="" false="-k" validate_ssl} \
            -X GET \
            -H "Authorization: Bearer ~{access_token}" \
            --fail-with-body \
            "~{drs_url}/search?project=${project_id}&dataset=${dataset_id}"
    >>>
    output {

    }
}

task associate_experiment_results_with_drs_objects {
    input {}
    command {} # TODO: associate files & indices
    output {}
}
