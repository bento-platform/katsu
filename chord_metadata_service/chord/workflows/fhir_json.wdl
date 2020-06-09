workflow fhir_json {
    File patients
    File? observations
    File? conditions
    File? specimens
    String? created_by

    call identity_task {
        input:
            patients_in = patients,
            observations_in = observations,
            conditions_in = conditions,
            specimens_in = specimens,
            created_by_in = created_by
    }
}

task identity_task {
    File patients_in
    File? observations_in
    File? conditions_in
    File? specimens_in
    String? created_by_in

    command {
        true
    }
    output {
        File patients = "${patients_in}"
        File? observations = "${observations_in}"
        File? conditions = "${conditions_in}"
        File? specimens = "${specimens_in}"
        String? created_by = "${created_by_in}"
    }
}