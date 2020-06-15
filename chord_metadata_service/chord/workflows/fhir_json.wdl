workflow fhir_json {
    File patients
    File? observations
    File? conditions
    File? specimens

    call identity_task {
        input: json_in = patients
    }

    call optional_fhir_json_task as ofjt1 {
        input: json_in = observations, file_name = "observations.json"
    }
    call optional_fhir_json_task as ofjt2 {
        input: json_in = conditions, file_name = "conditions.json"
    }
    call optional_fhir_json_task as ofjt3 {
        input: json_in = specimens, file_name = "specimens.json"
    }
}

task identity_task {
    File json_in

    command {
        true
    }

    output {
        File json_out = "${json_in}"
    }
}

task optional_fhir_json_task {
    File? json_in
    String file_name

    command <<<
        if [[ "${json_in}" = *"None"* ]]; then
          echo '*{"resourceType": "bundle", "entry": []}*' > "${file_name}";
        else
          echo "${json_in}" > "/chord/data/${file_name}" &&
          echo '*{"resourceType": "bundle", "entry": []}*' > "/chord/data/{file_name}_test.json";
          # mv "${json_in}" "${file_name}";
        fi
    >>>
    output {
        File json_out = "${file_name}"
    }
}
