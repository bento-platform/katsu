workflow cbioportal {
    String dataset_id
    String chord_url
    String run_dir
    String one_time_token
    String one_time_token_host
    String? temp_token = ""
    String? temp_token_host = ""

    call katsu_dataset_export {
        input: dataset_id = dataset_id,
               chord_url = chord_url,
               run_dir = run_dir,
               one_time_token = one_time_token,
               one_time_token_host = one_time_token_host
    }

    call get_maf {
        input: temp_token = temp_token,
               temp_token_host = temp_token_host,
               chord_url = chord_url,
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
    String chord_url
    String run_dir
    String one_time_token
    String one_time_token_host

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
            -H "Content-Type: application/json" -H "Host: ${one_time_token_host}" -H "X-OTT: ${one_time_token}" \
            -d '{"format": "cbioportal", "object_type": "dataset", "object_id": "${dataset_id}", "output_path": "${run_dir}"}' \
            "${chord_url}/api/metadata/private/export")
        
        if [ $RESPONSE != "204" ]
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
    String temp_token
    String temp_token_host
    String chord_url
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

        headers = {"Host": "${temp_token_host}", "X-TT": "${temp_token}"} if "${temp_token}" else {}

        MAF_LIST = "${run_dir}/export/${dataset_id}/maf_list.tsv"
        MUTATION_DATA_FILE= "${run_dir}/export/${dataset_id}/data_mutations_extended.txt"
        CASE_FILE = "${run_dir}/export/${dataset_id}/case_lists/case_list_sequenced.txt"

        # TODO: replae this when MAF files can be inferred from experimental_results data
        case_list = set()  # sample ids that have a maf file associated with

        with open(MAF_LIST) as file_handle, \
            open(MUTATION_DATA_FILE, 'wb') as mutation_file_handle:

            # Each line in maf_list begins with the file name
            nb_files_processed = 0
            for i, line in enumerate(file_handle):

                ### REMOVE THIS ####
                ### TESTING ONLY ####
                if i > 10: break

                fields = line.split()
                maf_file = fields[0]

                # Ask DRS for the maf file URI
                # TODO: for now infer maf filename from vcf file names
                # TODO: change the logic when MAF files are added to the 
                # experiment_results in the metadata service
                drs_url = f"${chord_url}/api/drs/search?fuzzy_name={maf_file}.maf"
                response = requests.get(drs_url, headers=headers, verify=False)
                r = response.json()
                
                if (len(r) == 0):
                    print(f"maf file {maf_file} not found")
                    continue

                case_list.add(fields[1])

                # Extract DRS generated URL
                # The following code breaks due to a bug in the DRS url generation
                # See: issue #1085 in bento redmine repo
                # Until it is fixed, urls must be generated "manually" assuming
                # the http access is available for the given file.
                # method = next(filter(
                #     lambda method: method['type'] == 'http',
                #     r[0]['access_methods']
                # ), None)
                # if method is None:
                #     print(f"No suitable access method found for maf file {maf_file}")
                #     continue

                # Get the file from DRS and append its content to the mutation file
                drs_object_url = f"${chord_url}/api/drs/objects/{r[0]['id']}/download"
                response = requests.get(drs_object_url,
                    headers=headers,
                    verify=False,
                    stream=True
                )
                for line_no, chunk in enumerate(response.iter_lines(chunk_size=4096)):
                    # first line of .maf file has the version number
                    # second line contains field names
                    # Both are skipped, unless it is the first file processed
                    if line_no < 2 and nb_files_processed > 0:
                        continue

                    mutation_file_handle.write(chunk + b"\n")

                nb_files_processed += 1

        # Append to the case_list file, the list of sample ids associated with
        # mutation data
        with open(CASE_FILE, 'a') as file_handle:
            file_handle.write('case_list_ids: ' + '\t'.join(case_list))

        CODE
    >>>

    output {
        File txt_output_maf = stdout()
        File err_output_maf = stderr()
    }
}
