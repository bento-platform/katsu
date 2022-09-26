workflow vcf2maf {
    String chord_url
    String drs_url
    String metadata_url
    String one_time_token_metadata_ingest
    String temp_token_drs
    String auth_host
    String dataset_id
    String dataset_name
    String vep_cache_dir
    String run_dir

    # Defaults (see: https://github.com/openwdl/wdl/blob/main/versions/1.0/SPEC.md#declared-inputs-defaults-and-overrides)
    String vep_species = "Homo_sapiens"     # ensembl syntax

    call katsu_dataset_export_vcf {
        input:  dataset_name = dataset_name,
                drs_url  = drs_url,
                metadata_url = metadata_url
    }

    call vcf_2_maf {
        input:
            vcf_files = katsu_dataset_export_vcf.vcf_files,
            vep_species = vep_species,
            vep_cache_dir = vep_cache_dir,
            drs_url = drs_url,
            temp_token_drs = temp_token_drs,
            auth_host = auth_host,
            run_dir = run_dir
    }

    call katsu_update_experiment_results_with_maf {
        input:  dataset_id = dataset_id,
                experiment_results_json = katsu_dataset_export_vcf.experiment_results_json,
                maf_list = vcf_2_maf.maf_list,
                metadata_url  = metadata_url,
                one_time_token_metadata_ingest = one_time_token_metadata_ingest,
                auth_host = auth_host,
                run_dir = run_dir
    }

    output {
        Array[File] maf = vcf_2_maf.out
    }
}

task katsu_dataset_export_vcf {
    #>>>>>> task inputs <<<<<<
    String dataset_name
    String drs_url
    String metadata_url

    # Enclosing command with curly braces {} causes issues with parsing in this
    # command block (tested with womtool-v78). Using triple angle braces made
    # interpolation more straightforward. According to specs, this should
    # restrict to ~{} syntax instead of ${} for string interpolation, which is
    # accepted by womtools but is not recognized by toil runner...
    command <<<
        python <<CODE
        import json
        import requests
        import sys

        # Query Katsu for experiment results as VCF files
        # Note: it is not possible to get the corresponding experiments at
        # this step due to the many to many relationship between these objects.

        # Beware: results are paginated! 10,000 is supposedly big enough
        # (actually the upper limit)
        # TODO: handle pagination, i.e. if the `next` property is set, loop
        # over the pages of results
        metadata_url = "${metadata_url}/api/experimentresults?datasets=${dataset_name}&file_format=vcf&page_size=20"
        response = requests.get(metadata_url, verify=False)
        r = response.json()

        if r["count"] == 0:
            sys.exit("No VCF file to convert from dataset ${dataset_name}")

        # Process each VCF from the results
        vcf_dict = dict()   # vcf processed keyed by filename
        with open("vcf_files.tsv", "w") as file_handle:

            for result in r["results"]:
                vcf = result["filename"]

                # In case of duplicates, skip. This happens with the synthetic demo
                # dataset.
                if vcf in vcf_dict:
                    continue

                # TODO add a default global parameter for when genome_assembly_id
                # is not defined on experiment results records.
                assembly_id = result.get("genome_assembly_id", "GRCh37")

                # Query DRS with the filename to get the absolute file path in
                # DRS for processing.
                drs_url = f"${drs_url}/search?name={vcf}&internal_path=1"
                response = requests.get(drs_url, verify=False)
                if not response.ok:
                    continue
                drs_resp = response.json()

                if len(drs_resp) == 0:
                    print(f"VCF file {vcf} not found")
                    continue

                filtered_methods = filter(
                    lambda method: method["type"] == "file", drs_resp[0]["access_methods"]
                )
                location = next(filtered_methods)["access_url"]["url"].replace("file://", "")
                file_handle.write(f"{location}\t{assembly_id}\t{vcf}\n")

                vcf_dict[vcf] = result

        # save the JSON
        with open("experiment_results.json", "w") as file_handle:
            json.dump(vcf_dict, file_handle)

        CODE
    >>>

    output {
        File vcf_files = "vcf_files.tsv"
        File experiment_results_json = "experiment_results.json"
        File txt_output = stdout()
        File err_output = stderr()
    }
}


task vcf_2_maf {
    File vcf_files
    String vep_species
    String vep_cache_dir
    String drs_url
    String temp_token_drs
    String auth_host
    String run_dir

    # workaround for var interpolation. Syntax ${} confuses wdl parsers
    # between wdl level interpolation and shell string interpolation.
    String dollar = "$"

    # Enclosing command with curly braces {} causes issues with parsing in this
    # command block (tested with womtool-v78). Using triple angle braces made
    # interpolation more straightforward. According to specs, this should
    # restrict to ~{} syntax instead of ${} for string interpolation, which is
    # accepted by womtools but is not recognized by toil runner...
    command <<<
        # This task also produces a .tsv file containing the list of MAF files
        # that have been computed and their uri in DRS

        # Generate TSV file header
        echo -e "vcf\tmaf\turi" > maf.list.tsv

        # Loop through list of VCF files
        cat ${vcf_files} | while read -r g_vcf assembly_id orig_vcf_filename
        do
            # prepare file names
            export vcf_file_name=$(basename ${dollar}{orig_vcf_filename})
            filtered_vcf=$(echo ${dollar}{vcf_file_name} | sed 's/\(.*\.\)vcf\.gz/\1filtered\.vcf/')
            export maf=${run_dir}/${dollar}{vcf_file_name}.maf

            # filter out variants that are homozyguous and identical to assemby ref.
            bcftools view -i 'GT[*]="alt"' ${dollar}{g_vcf} > ${dollar}{filtered_vcf}

            # even if VEP is in the path, vcf2maf script requires a valid path or it
            # defaults to a conda based path hard coded in the perl script (!)
            VEP_PATH=$(dirname $(which vep))

            # extract VEP version from the executable help page
            #(pattern is like: "  ensembl-vep          : 105.0")
            VEP_ENSEMBL_VERSION=$(vep --help | grep "ensembl-vep" | grep -o "[0-9]*" | head -1)

            # Find the location of the reference assembly FASTA file for VEP
            VEP_CACHE_PATH_SPECIES=$(echo ${vep_species} | tr '[:upper:]' '[:lower:]')
            REF_FASTA_PATH=${vep_cache_dir}/${dollar}{VEP_CACHE_PATH_SPECIES}/${dollar}{VEP_ENSEMBL_VERSION}_${dollar}{assembly_id}

            # The name of the FASTA file used as a reference can not be infered
            # consistently from primitives: GRCh37 assembly has not been updated since
            # ensembl version 75. We rely on the file actually present in the
            # cache directory
            # (pattern is like: "Homo_sapiens.GRCh37.75.dna.toplevel.fa.gz")
            REF_FASTA_TOPLEVEL=$(ls ${dollar}{REF_FASTA_PATH} | grep "toplevel" | head -1)

            # Get the sample ID from the VCF file header.
            # Here it is assumed that only one sample is present in the file.
            # TODO: check output and syntax if multiple samples are present.
            SAMPLE_ID=$(bcftools query -l ${dollar}{g_vcf})

            perl /opt/vcf2maf.pl \
                --input-vcf ${dollar}{filtered_vcf} \
                --output-maf ${dollar}{maf} \
                --vep-data ${vep_cache_dir} \
                --ref-fasta ${dollar}{REF_FASTA_PATH}/${dollar}{REF_FASTA_TOPLEVEL} \
                --vep-path ${dollar}{VEP_PATH} \
                --tumor-id ${dollar}{SAMPLE_ID}

            # Store the maf file in DRS and register its uri
            python -c '
        import json
        import requests
        import os
        import sys

        params = {
            "path": os.environ["maf"],
            "deduplicate": True
        }

        drs_url = "${drs_url}/private/ingest"
        try:
            response = requests.post(
                drs_url,
                headers={"Host": "${auth_host}", "X-TT": "${temp_token_drs}"} if "${temp_token_drs}" else {},
                json=params,
                verify=False
            )
            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            msg = e.response.json() if hasattr(e, "response") else ""
            sys.exit(f"An error occured during DRS ingestion ({msg})")

        r = response.json()
        uri = r["self_uri"]

        with open("maf.list.tsv", "a") as maf_list_fh:
            maf_list_fh.write(
                os.environ["vcf_file_name"] + "\t" + os.path.basename(params["path"]) + "\t" + uri + "\n"
            )

        '
        done

        echo "end loop" >> /tmp/dump.tsv

    >>>

    output {
        Array[File] out = glob("*.maf")
        File maf_list = "maf.list.tsv"
        File txt_output = stdout()
        File err_output = stderr()
    }

}


task katsu_update_experiment_results_with_maf {
    #>>>>>> task inputs <<<<<<
    String dataset_id
    String metadata_url
    String one_time_token_metadata_ingest
    String auth_host
    String run_dir
    File experiment_results_json
    File maf_list

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
        python <<CODE

        import csv
        import json
        import requests
        from datetime import date
        from os import path

        vcf_dict = dict()
        with open("${experiment_results_json}") as file_handle:
            vcf_dict = json.load(file_handle)

        maf_exp_res_list = []
        with open("${maf_list}") as file_handle:
            tsv_reader = csv.DictReader(file_handle, delimiter="\t")

            for row in tsv_reader:
                vcf_file_name = row["vcf"]
                if vcf_file_name not in vcf_dict:
                    continue

                vcf_props = vcf_dict[vcf_file_name]
                maf_exp_res_list.append({
                    "identifier": f"{vcf_props['identifier']}-MAF",
                    "description": "MAF file",
                    "filename": row["maf"],
                    "file_format": "MAF",
                    "data_output_type": "Derived data",
                    "usage": "downloaded",
                    "creation_date": date.today().isoformat(),
                    "created_by": "Bento",
                    "genome_assembly_id": vcf_props["genome_assembly_id"],
                    "extra_properties": {
                        "uri": row['uri'],
                        "derived_from": vcf_props["identifier"]
                    }
                })

        EXPERIMENT_RESULTS_JSON = path.join("${run_dir}", "experiment_results_maf.json")
        with open(EXPERIMENT_RESULTS_JSON, "w") as file_handle:
            json.dump(maf_exp_res_list, file_handle)

        # Ingest metadata about MAF files into Katsu
        # The following passes an absolute path to the current working directory.
        # As Katsu has the /wes/tmp/ volume mounted with the same path
        # internally, direct access to the file is guaranteed.

        headers = (
            {"Host": "${auth_host}", "X-OTT": "${one_time_token_metadata_ingest}"}
            if "${one_time_token_metadata_ingest}"
            else {}
        )

        metadata_url = f"${metadata_url}/private/ingest"
        data = {
            "table_id": "FROM_DERIVED_DATA",
            "workflow_id": "maf_derived_from_vcf_json",
            "workflow_outputs": {
                "json_document": path.abspath(EXPERIMENT_RESULTS_JSON)
            },
            "workflow_params": {
                "derived_from_data_type": "experiment_result"
            }
        }
        response = requests.post(metadata_url, headers=headers, json=data, verify=False)
        response.raise_for_status()

        CODE
    >>>

    output {
        File experiment_results_maf_json = "experiment_results_maf.json"
        # File txt_output = stdout()
        # File err_output = stderr()
    }
}
