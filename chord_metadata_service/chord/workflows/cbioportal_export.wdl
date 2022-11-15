workflow cbioportal {
    String dataset_id
    String run_dir
    String metadata_url
    String drs_url

    call katsu_dataset_export {
        input: dataset_id = dataset_id,
               run_dir = run_dir,
               metadata_url = metadata_url
    }

    call get_maf {
        input: drs_url = drs_url,
               dataset_id = dataset_id,
               run_dir = run_dir
    }

    output {
        Array[File] cbio = katsu_dataset_export.data_txt
        File stdout = katsu_dataset_export.txt_output
        File stderr = katsu_dataset_export.err_output
    }
}

task katsu_dataset_export {
    #>>>>>> task inputs <<<<<<
    String dataset_id
    String metadata_url
    String run_dir

    #>>>>>> task constants <<<<<
    # workaround for var interpolation. Syntax ${} confuses wdl parsers
    # between wdl level interpolation and shell string interpolation.
    String dollar = "$"

    # Enclosing command with curly braces {} causes issues with parsing in this
    # command block (tested with womtool-v78). Using triple angle braces made
    # interpolation more straightforward. According to specs, this should
    # restrict to ~{} syntax instead of ${} for string interpolation, which is
    # accepted by womtools but is not recognized by toil runner...
    command <<<
        # Export results at export_path and returns http code 200 in case of success
        RESPONSE=$(curl -X POST -k -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -d '{"format": "cbioportal", "object_type": "dataset", "object_id": "${dataset_id}", "output_path": "${run_dir}"}' \
            "${metadata_url}/private/export")

        if [ "${dollar}{RESPONSE}" != "204" ]
        then
            echo "Error: Metadata service replied with HTTP code ${dollar}{RESPONSE}" 1>&2  # to stderr
            exit 1
        fi
        echo ${dollar}{RESPONSE}
    >>>

    output {
        Array[File] data_txt = glob("${run_dir}/export/${dataset_id}/*.txt")
        File txt_output = stdout()
        File err_output = stderr()
    }
}

task get_maf {
    #>>>>>>> task inputs <<<<<<<
    String drs_url
    String run_dir
    String dataset_id

    #>>>>>> task constants <<<<<
    # workaround for var interpolation. Syntax ${} confuses wdl parsers
    # between wdl level interpolation and shell string interpolation.
    String dollar = "$"

    command <<<
        python <<CODE
        import json
        import requests

        work_dir = "${run_dir}/export/${dataset_id}"
        MAF_LIST = f"{work_dir}/maf_list.txt"
        MUTATION_DATA_FILE= f"{work_dir}/data_mutations_extended.txt"

        with open(MAF_LIST) as file_handle, \
            open(MUTATION_DATA_FILE, 'w') as mutation_file_handle:

            # Each line in maf_list contains the file uri
            no_file_processed_yet = True
            for i, maf_uri in enumerate(file_handle):

                # Request from DRS the maf file absolute local path
                object_id = maf_uri.split("/")[-1].rstrip()
                drs_object_url = f"${drs_url}/objects/{object_id}?internal_path=1"
                response = requests.get(drs_object_url, verify=False)
                r = response.json()

                if (len(r) == 0):
                    print(f"maf file with id {object_id} not found")
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
    >>>

    output {
        File txt_output_maf = stdout()
        File err_output_maf = stderr()
    }
}