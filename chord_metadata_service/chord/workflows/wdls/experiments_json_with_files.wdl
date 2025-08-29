version 1.0

workflow experiments_json_with_files {
    input {
        String directory
        File json_document
        String drs_url
        String katsu_url
        String project_dataset
        Boolean filter_out_vcf_files = false
        String access_token
        Boolean validate_ssl
    }

    call prepare_files_list {
        input:
            json_document = json_document,
            directory = directory,
            filter_out_vcf_files = filter_out_vcf_files
    }

    call prepare_for_drs {
        input:
            json_path_list = prepare_files_list.path_list,
    }

    scatter (path in prepare_for_drs.consolidated_paths_for_drs) {
        call post_to_drs {
            input:
                file_path = path,
                drs_url = drs_url,
                project_dataset = project_dataset,
                token = access_token,
                validate_ssl = validate_ssl,
                json_document = json_document
        }
    }

    call write_drs_responses_to_file {
        input:
            drs_responses = flatten(post_to_drs.response_message)
    }

    call parse_json {
        input:
            json_responses = write_drs_responses_to_file.results_post_drs
    }

    call update_experiment_json {
        input:
            json_document = json_document,
            processed_drs_responses = parse_json.processed_drs_responses
    }

    call ingest_task {
        input:
            json_document = update_experiment_json.final_updated_json,
            project_dataset = project_dataset,
            katsu_url = katsu_url,
            token = access_token,
            validate_ssl = validate_ssl
    }

    output {
        File download_list = prepare_files_list.path_list
        Array[String] consolidated_paths_for_drs = prepare_for_drs.consolidated_paths_for_drs
        Array[String] drs_responses = flatten(post_to_drs.response_message)
        File results_post_drs = write_drs_responses_to_file.results_post_drs
        File processed_drs_responses = parse_json.processed_drs_responses
        File final_updated_json = update_experiment_json.final_updated_json
    }
}

task prepare_files_list {
    input {
        File json_document
        String directory
        Boolean filter_out_vcf_files
    }
    command <<<
    python3 -c "
import json
import os

directory = '~{directory}'
filter_vcf = '~{filter_out_vcf_files}'

with open('~{json_document}', 'r') as file:
    data = json.load(file)

path_list = []
for experiment in data.get('experiments', []):
    for result in experiment.get('experiment_results', []):
        filename = result.get('filename', '')
        file_found = False
        is_vcf = filename.endswith('.vcf') or filename.endswith('.vcf.gz')

        if filter_vcf and is_vcf:
            continue

        for root, dirs, files in os.walk(directory):
            if filename in files:
                file_found = True
                file_path = os.path.join(root, filename)
                path_list.append({'filename': filename, 'path': file_path})
                break
        if not file_found:
            print(f'File not found for {filename}')

with open('path_list.json', 'w') as file:
    json.dump(path_list, file, indent=4)
    "
    >>>
    output {
        File path_list = "path_list.json"
    }
}

task prepare_for_drs {
    input {
        File json_path_list
    }

    command <<<
    python3 -c "
import json

with open('~{json_path_list}', 'r') as file:
    path_list = json.load(file)

consolidated_paths = [str(path['path']).strip() for path in path_list if str(path['path']).strip()]

print(json.dumps(consolidated_paths))

    "
    >>>
    output {
        Array[String] consolidated_paths_for_drs = read_json(stdout())
    }
}

task post_to_drs {
  input {
    File    file_path
    String  drs_url
    String  project_dataset
    String  token
    Boolean validate_ssl
    File    json_document
  }
  command <<<
    # Extract project_id and dataset_id
    project_id=$(python3 -c 'print("~{project_dataset}".split(":")[0])')
    dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')

    # Function to ingest a file into DRS
    ingest_to_drs() {
        local file=$1
        curl ~{true="" false="-k" validate_ssl} \
          -X POST \
          -F "file=@${file}" \
          -F "project_id=${project_id}" \
          -F "dataset_id=${dataset_id}" \
          -H "Authorization: Bearer ~{token}" \
          --fail-with-body \
          "~{drs_url}/ingest"
    }

    # Ingest the main file
    resp_main=$(ingest_to_drs "~{file_path}")
    echo "$resp_main" | jq -c

    # Index BAM and CRAM files
    if [[ "~{file_path}" =~ \.(bam|cram)$ ]]; then
      filename=$(basename "~{file_path}")
      index_ext=".bai"
      idx_fmt="BAI"
      [[ "~{file_path}" =~ \.cram$ ]] && { index_ext=".crai"; idx_fmt="CRAI"; }
        samtools index "~{file_path}" 1>/dev/null 2>&1
        resp_index=$(ingest_to_drs "~{file_path}${index_ext}")
        echo "$resp_index" | jq -c
    fi
  >>>
  output {
    Array[String] response_message = read_lines(stdout())
  }
}

task write_drs_responses_to_file {
    input {
        Array[String] drs_responses
    }

    command <<<
    python3 -c "
import json

temporary_file_drs_responses = '~{write_json(drs_responses)}'
with open(temporary_file_drs_responses, 'r') as f:
    lines = json.load(f)

valid_json_responses = []
for line in lines:
    line = line.strip()
    if not line:
        continue
    try:
        parsed = json.loads(line)
        valid_json_responses.append(parsed)
    except json.JSONDecodeError:
        pass

with open('results_post_drs.json', 'w') as outfile:
    json.dump(valid_json_responses, outfile, indent=2)
    "
    >>>

    output {
        File results_post_drs = "results_post_drs.json"
    }
}

task parse_json {
    input {
        File json_responses
    }

    command <<<
    python3 -c "
import json

def parse_drs_response(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    new_array = []
    for item in data:
        information = {
            'name': item.get('name', ''),
            'self_uri': item.get('self_uri', '')
        }
        new_array.append(information)

    with open('processed_drs_responses.json', 'w') as outfile:
        json.dump(new_array, outfile, indent=4)

parse_drs_response('~{json_responses}')
"
    >>>
    output {
        File processed_drs_responses = "processed_drs_responses.json"
    }
}

task update_experiment_json {
    input {
        File json_document
        File processed_drs_responses
    }
    command <<<
    python3 -c "
import json, os

with open('~{json_document}', 'r') as f:
    data = json.load(f)

with open('~{processed_drs_responses}', 'r') as f:
    drs_data = json.load(f)

def construct_index_basename(filename, fmt):
    return f'{filename}.{fmt.lower()}'

for experiment in data.get('experiments', []):
    for result in experiment.get('experiment_results', []):
        filename = result.get('filename', '')

        if 'indices' not in result or not isinstance(result['indices'], list):
            result['indices'] = []

        for drs_resp in drs_data:
            if os.path.basename(drs_resp.get('name', '')) == filename:
                result['url'] = drs_resp.get('self_uri')
                break

        new_index_format = None
        if filename.endswith('.bam'):
            new_index_format = 'BAI'
        elif filename.endswith('.cram'):
            new_index_format = 'CRAI'

        if new_index_format:
            index_basename = construct_index_basename(filename, new_index_format)

            for drs_resp in drs_data:
                existing_idx = None
                for idx in result['indices']:
                    if idx.get('format') == new_index_format:
                        existing_idx = idx
                        break

                if existing_idx:
                    existing_idx['url'] = drs_resp.get('self_uri')
                else:
                    result['indices'].append({
                        'format': new_index_format,
                        'url': drs_resp.get('self_uri')
                    })
                break

with open('final_updated_json.json', 'w') as f:
    json.dump(data, f, indent=4)
"
    >>>
    output {
        File final_updated_json = "final_updated_json.json"
    }
}

task ingest_task {
    input {
        File json_document
        String project_dataset
        String katsu_url
        String token
        Boolean validate_ssl
    }
    command <<<
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        RESPONSE=$(curl -X POST ~{true="" false="-k" validate_ssl} -s -w "%{http_code}" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ~{token}" \
            --data "@~{json_document}" \
            "~{katsu_url}/ingest/${dataset_id}/experiments_json")
        if [[ "${RESPONSE}" != "204" ]]
        then
            echo "Error: Metadata service replied with ${RESPONSE}" 1>&2  # to stderr
            exit 1
        fi
        echo ${RESPONSE}
    >>>

    output {
        File txt_output = stdout()
        File err_output = stderr()
    }
}
