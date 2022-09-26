workflow cbioportal {
    String dataset_id
    String chord_url
    String run_dir
    String one_time_token
    String one_time_token_host

    call katsu_dataset_export {
        input: dataset_id = dataset_id,
               chord_url = chord_url,
               run_dir = run_dir,
               one_time_token = one_time_token,
               one_time_token_host = one_time_token_host
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
        Array[File] data_txt = glob("export/${dataset_id}/*.txt")
        File txt_output = stdout()
        File err_output = stderr()
    }
}
