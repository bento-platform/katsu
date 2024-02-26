version 1.0

workflow experiments_extended_json {
    input {
        String directory
        File json_document
        String drs_url
        String katsu_url
        String project_dataset
        String access_token
        Boolean validate_ssl
    }

    call prepare_download_list {
        input:
            json_document = json_document,
            directory = directory
    }

    ## Calculate the size of the JSON document to determine if there are any URLs to download
    Int urls_json_size = ceil(size(prepare_download_list.urls_json, "Gi") * 8000)

    if (urls_json_size > 0) {
        call process_downloads {
            input:
                urls_json = prepare_download_list.urls_json
        }

        call prepare_for_download {
            input:
                json_document = prepare_download_list.urls_json
        }

        scatter (download_info in prepare_for_download.download_list) {
            call download_file {
                input:
                    url = download_info.url,
                    filename = download_info.filename,
                    directory = directory,
                    access_token = access_token,
                    validate_ssl = validate_ssl
            }
        }
    }

    call prepare_for_drs {
        input:
            json_download_list = prepare_download_list.urls_json,
            json_path_list = prepare_download_list.path_list,
            downloaded_files = download_file.downloaded_file
    }

    scatter (path in prepare_for_drs.consolidated_paths_for_drs) {
        call post_to_drs {
            input:
                file_path = path,
                drs_url = drs_url,
                project_dataset = project_dataset,
                token = access_token,
                validate_ssl = validate_ssl
        }
    }

    call write_drs_responses_to_file {
        input:
            drs_responses = post_to_drs.response_message
    }

    call parse_txt {
        input:
            txt_responses = write_drs_responses_to_file.results_post_drs
    }

    call update_experiment_json {
        input:
            json_document = json_document,
            processed_drs_responses = parse_txt.processed_drs_responses
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
        File download_list = prepare_download_list.urls_json
        File path_list = prepare_download_list.path_list
        Array[File]? downloaded_files = download_file.downloaded_file
        Array[String] consolidated_paths_for_drs = prepare_for_drs.consolidated_paths_for_drs
        Array[String] drs_responses = post_to_drs.response_message
        File results_post_drs = write_drs_responses_to_file.results_post_drs
        File processed_drs_responses = parse_txt.processed_drs_responses
        File final_updated_json = update_experiment_json.final_updated_json
    }
}

task prepare_download_list {
    input {
        File json_document
        String directory
    }
    command <<<
    python3 -c "
import json
import os

directory = '~{directory}'

with open('~{json_document}', 'r') as file:
    data = json.load(file)

# List of allowed protocols
allowed_protocols = ['http://', 'https://', 'ftp://', 'ftps://']

def is_allowed_protocol(url):
    return any(url.startswith(protocol) for protocol in allowed_protocols)

download_list = []
path_list = []
for experiment in data.get('experiments', []):
    for result in experiment.get('experiment_results', []):
        url = result.get('url', '')
        filename = result.get('filename', '')
        if url and is_allowed_protocol(url):
            download_info = {'url': url, 'filename': filename}
            download_list.append(download_info)
            # Process indices
            for index in result.get('indices', []):
                index_url = index.get('url', '')
                index_format = index.get('format', '')
                if index_url and is_allowed_protocol(index_url):
                    index_info = {'url': index_url, 'filename': filename + '.' + index_format.lower()}
                    download_list.append(index_info)
        else:
            file_found = False
            for root, dirs, files in os.walk(directory):
                if filename in files:
                    file_found = True
                    file_path = os.path.join(root, filename)
                    path_list.append({'filename': filename, 'url': file_path})
                    break
            if not file_found:
                print(f'File not found for {filename}')

with open('download_list.json', 'w') as outfile:
    json.dump(download_list, outfile, indent=4)

with open('path_list.json', 'w') as file:
    json.dump(path_list, file, indent=4)
    "
    >>>
    output {
        File urls_json = "download_list.json"
        File path_list = "path_list.json"
    }
}

task prepare_for_download {
    input {
        File json_document
    }

    command <<<
    python3 -c "
import json

with open('~{json_document}', 'r') as file:
    data = json.load(file)

download_list = [{'url': item['url'], 'filename': item['filename']} for item in data]

print(json.dumps(download_list))
    "
    >>>
    output {
         Array[Map[String, String]] download_list = read_json(stdout())
    }
}

task download_file {
    input {
        String url
        String filename
        String directory
        String access_token
        Boolean validate_ssl
    }

    command <<<
    curl -L "~{url}" -o "~{filename}" -H "Authorization: Bearer ~{access_token}"
    >>>

    output {
        File downloaded_file = '~{filename}'
    }
}

task prepare_for_drs {
    input {
        File json_download_list
        File json_path_list
        Array[File]? downloaded_files
    }

    command <<<
    python3 -c "
import json

# Convert the space-separated string of downloaded files into a Python list
downloaded_files = \"\"\"~{sep=' ' downloaded_files}\"\"\".split(' ')

with open('~{json_download_list}', 'r') as file:
    download_list = json.load(file)

with open('~{json_path_list}', 'r') as file:
    path_list = json.load(file)

consolidated_paths = downloaded_files[:]

consolidated_paths.extend([str(path['url']) for path in path_list])

# Filter out any empty strings from consolidated_paths before printing
filtered_paths = [path for path in consolidated_paths if path.strip()]

print(json.dumps(filtered_paths))

    "
    >>>
    output {
        Array[String] consolidated_paths_for_drs = read_json(stdout())
    }
}

task post_to_drs {
    input {
        File file_path
        String drs_url
        String project_dataset
        String token
        Boolean validate_ssl
    }
    command <<<
        project_id=$(python3 -c 'print("~{project_dataset}".split(":")[0])')
        dataset_id=$(python3 -c 'print("~{project_dataset}".split(":")[1])')
        curl ~{true="" false="-k" validate_ssl} \
            -X POST \
            -F "file=@~{file_path}" \
            -F "project_id=$project_id" \
            -F "dataset_id=$dataset_id" \
            -H "Authorization: Bearer ~{token}" \
            --fail-with-body \
            "~{drs_url}/ingest"
    >>>
    output {
        String response_message = read_string(stdout())
    }
}

task write_drs_responses_to_file {
    input {
        Array[String] drs_responses
    }

    command <<<
        for response in "~{sep=' ' drs_responses}"; do
            echo "$response"
        done > results_post_drs.txt
    >>>

    output {
        File results_post_drs = "results_post_drs.txt"
    }
}

task parse_txt {
    input {
        File txt_responses
    }

    command <<<
    python3 -c "
import json

def read_and_process_file(file_path):
    with open(file_path, 'r') as file:
        data = file.read().strip().replace('\n', '').split('} {')

    new_array = []
    for line in data:
        information = {'name': '', 'self_uri': ''}

        line = line.strip('{} ').replace('\'', '\"')
        parts = line.split(', ')
        for part in parts:
            key_value = part.split(':', 1)
            if len(key_value) == 2:
                key, value = key_value[0].strip(), key_value[1].strip().strip('\"')
                if 'name' in key:
                    information['name'] = value
                elif 'self_uri' in key:
                    information['self_uri'] = value
        new_array.append(information)

    with open('processed_drs_responses.json', 'w') as outfile:
        json.dump(new_array, outfile, indent=4)

read_and_process_file('~{txt_responses}')
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
import json

with open('~{json_document}', 'r') as file:
    data = json.load(file)

with open('~{processed_drs_responses}', 'r') as file:
    drs_data = json.load(file)

def construct_drs_name_for_index(filename, format):
    return filename + '.' + format.lower()

# Update the original JSON document with DRS URIs for both files and their indices
for experiment in data.get('experiments', []):
    for result in experiment.get('experiment_results', []):
        # Update primary file URL
        for drs_response in drs_data:
            if result['filename'] == drs_response['name']:
                result['url'] = drs_response['self_uri']
                break
        # Update indices URLs if present
        for index in result.get('indices', []):
            expected_drs_name = construct_drs_name_for_index(result['filename'], index['format'])
            for drs_response in drs_data:
                if expected_drs_name == drs_response['name']:
                    index['url'] = drs_response['self_uri']
                    break

with open('final_updated_json.json', 'w') as file:
    json.dump(data, file, indent=4)
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

task process_downloads {
    input {
        File urls_json
    }

    command <<<
        echo "Processing downloads listed in"
        # Placeholder for actual processing commands
    >>>

    output {
        String message = read_string(stdout())
    }
}