version 1.0

workflow cbioportal {
    input {
        String project_dataset
        String katsu_url
        String drs_url
        String access_token
        Boolean validate_ssl
    }

    call dataset_id_from_project_dataset {
        input: project_dataset = project_dataset
    }

    call katsu_dataset_export {
        input: dataset_id = dataset_id_from_project_dataset.dataset_id,
               katsu_url = katsu_url,
               token = access_token,
               validate_ssl = validate_ssl
    }

    call get_maf {
        input: drs_url = drs_url,
               dataset_id = dataset_id_from_project_dataset.dataset_id,
               token = access_token,
               validate_ssl = validate_ssl,
               export_data = katsu_dataset_export.export_data
    }

    output {
        File export_data = get_maf.export_data_with_maf
    }
}

task dataset_id_from_project_dataset {
    input {
        String project_dataset
    }
    command <<<
        python3 -c 'print("~{project_dataset}".split(":")[1], end="")'
    >>>
    output {
        String dataset_id = read_string(stdout())
    }
}

task katsu_dataset_export {
    input {
        String dataset_id
        String katsu_url
        String token
        Boolean validate_ssl
    }

    # Enclosing command with curly braces {} causes issues with parsing in this
    # command block (tested with womtool-v78). Using triple angle braces made
    # interpolation more straightforward.
    command <<<
        # Export results; Katsu returns a .tar.gz file
        curl -X POST ~{true="" false="-k" validate_ssl} -s --fail-with-body \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ~{token}" \
            -d '{"format": "cbioportal", "object_type": "dataset", "object_id": "~{dataset_id}"}' \
            -o export.tar.gz \
            "~{katsu_url}/private/export"
    >>>

    output {
        File export_data = "export.tar.gz"
        File txt_output = stdout()
        File err_output = stderr()
    }
}

task get_maf {
    input {
        String drs_url
        String dataset_id
        String token
        Boolean validate_ssl
        File export_data
    }

    command <<<
        # Extract exported data
        tar -xzvf ~{export_data}

        # Write data_mutations_extended
        python <<CODE
        import json
        import requests
        import sys

        MAF_LIST = "export/maf_list.txt"
        MUTATION_DATA_FILE= "export/data_mutations_extended.txt"

        with open(MAF_LIST) as file_handle, \
            open(MUTATION_DATA_FILE, 'w') as mutation_file_handle:

            # Each line in maf_list contains the file uri
            no_file_processed_yet = True
            for i, maf_uri in enumerate(file_handle):

                # Request the MAF file from DRS
                object_id = maf_uri.split("/")[-1].rstrip()
                response = requests.get(
                    f"~{drs_url}/objects/{object_id}?internal_path=1",
                    headers={"Authorization": "Bearer ~{token}"},
                    verify=~{true="True" false="False" validate_ssl},
                )
                r = response.json()

                if len(r) == 0:
                    print(f"MAF file with id {object_id} not found", file=sys.stderr)
                    continue

                filtered_methods = filter(
                    lambda method: method["type"] == "file",
                    r["access_methods"]
                )
                maf_path = next(filtered_methods)["access_url"]["url"].replace("file://", "")

                with open(maf_path, "r") as maf_file_handle:
                    # first line of .maf file has the version number
                    # second line contains field names
                    # Both are skipped, unless it is the first file processed
                    start_line = 0 if no_file_processed_yet else 2

                    for line_no, line in enumerate(maf_file_handle):
                        if line_no < start_line:
                            continue
                        mutation_file_handle.write(line.rstrip() + "\n")

                    no_file_processed_yet = False


        CODE

        # Compress the final exported data, with MAFs
        tar -czf export_with_maf.tar.gz export
    >>>

    output {
        File export_data_with_maf = "export_with_maf.tar.gz"
    }
}
