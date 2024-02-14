version 1.0

workflow experiments_update_json {
    input {
        String directory
        File json_document
        String drs_url
        String project_dataset
        String access_token
        Boolean validate_ssl
    }

    call update_json_paths {
        input:
            json_document = json_document,
            directory = directory
    }

    output {
        File updated_json = update_json_paths.updated_json
    }
}


task update_json_paths {
    input {
        File json_document
        String directory
    }
    command <<<
        python3 -c "
import json
import os

print('Starting script...')  # Debugging line
directory = '~{directory}'
print(f'Searching in directory: {directory}')  # Debugging line

# Load the input JSON
with open('~{json_document}', 'r') as json_file:
    data = json.load(json_file)

found_files = 0  # Debugging variable

names_list = []

for file_entry in data.get('files', []):
    file_name = file_entry['name']
    for root, dirs, files in os.walk(directory):
        print(f'Checking {root}...')  # Debugging line
        if file_name in files:
            file_path = os.path.join(root, file_name)
            names_list.append(file_path)
            file_entry['file_path'] = file_path
            print(f'Found {file_name} at {file_path}')  # Debugging line
            found_files += 1
            break

print(names_list)  # Debugging line

if found_files == 0:
    print('No files were updated.')  # Debugging line

# Write the updated JSON to a new file
with open('updated_json.json', 'w') as updated_json_file:
    json.dump(data, updated_json_file, indent=4)
"
    >>>
    output {
        File updated_json = "updated_json.json"
    }
}
