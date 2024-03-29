workflow fhir_json {
    File patients
    File? observations
    File? conditions
    File? specimens

    call copy_task {
        input: json_in = patients, out_name = "patients.json"
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

task copy_task {
    File json_in
    String out_name

    command {
        cp "${json_in}" "${out_name}"
    }

    output {
        File json_out = "${out_name}"
    }
}

task optional_fhir_json_task {
    File? json_in
    String file_name

    command <<<
        if [[ -f "${json_in}" ]]; then
          mv "${json_in}" "${file_name}";
        else
          echo '{"resourceType": "bundle", "entry": []}' > "${file_name}";
        fi
    >>>
    output {
        File json_out = "${file_name}"
    }
}
