version 1.0

workflow experiment_results_drs {
    input {
        String drs_url
        String katsu_url
        String project_dataset
        String access_token
        Boolean validate_ssl
    }

    call fetch_drs_objects {
        input:
            drs_url = drs_url,
            project_dataset = project_dataset,
            access_token = access_token,
            validate_ssl = validate_ssl
    }

    call associate_experiment_results_with_drs_objects {
        input:
            katsu_url = katsu_url,
            access_token = access_token,
            validate_ssl = validate_ssl,
            drs_json = fetch_drs_objects.response_json
    }

    output {
        File experiment_result_updates = associate_experiment_results_with_drs_objects.experiment_result_updates
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
        File response_json = stdout()
    }
}

task associate_experiment_results_with_drs_objects {
    input {
        String katsu_url
        String access_token
        Boolean validate_ssl
        File drs_json
    }
    command <<<
    python3 -c "
        import json
        import requests

        INDEX_SUFFIXES = {
            '.bai': 'BAI',
            '.crai': 'CRAI',
            '.csi': 'CSI',
            '.gzi': 'BGZF',
            '.tbi': 'TABIX',
        }

        updates = []

        with open('~{drs_json}') as fh:
            drs_records = json.load(fh)

        drs_uris_and_created_by_filename = {}
        for r in drs_records:
            name = r['name']
            rec = (r['self_uri'], r['created_time'])
            if name in drs_uris_and_created_by_filename:
                # for multiple, tie-break one with most recent timestamp!
                if rec[1] >= drs_uris_and_created_by_filename[name][1]:
                    drs_uris_and_created_by_filename[name] = rec
            else:
                drs_uris_and_created_by_filename[name] = rec

        er_url = '~{katsu_url}/api/experimentresults?project=${project_id}&dataset=${dataset_id}&has_url=False'
        auth_headers = {'Authorization': 'Bearer ~{access_token}'}
        verify_ssl = ~{true="True" false="False" validate_ssl}

        while er_url is not None:
            print('fetching experiment results page', er_url)
            experiment_results = requests.get(er_url, headers=auth_headers, verify=verify_ssl).json()

            for er in experiment_results['results']:
                f = er['filename']
                if not f:
                    continue

                update = {}
                if f in drs_uris_and_created_by_filename:
                    update['url'] = drs_uris_and_created_by_filename[f][0]
                elif any((f + s) in drs_uris_and_created_by_filename for s in INDEX_SUFFIXES.keys()):
                    pass  # TODO

                if update:
                    er_id = er['id']
                    print('updating experiment result', er_id, update)
                    requests.patch(
                        f'~{katsu_url}/api/experimentresults/{er_id}',
                        json=update,
                        headers=auth_headers,
                        verify=verify_ssl,
                    )

                    updates.append({'id': er_id, 'patch': update})

            # go to next page of results:
            er_url = experiment_results['next']

        with open('./experiment_result_updates.json', 'w') as fh:
            json.dump(updates, fh)

"
    >>>
    output {
        File experiment_result_updates = "experiment_result_updates.json"
        File task_stdout = stdout()
        File task_stderr = stderr()
    }
}
