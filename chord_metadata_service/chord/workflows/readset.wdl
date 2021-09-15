workflow readset {
    File readset_files

    call identity_task {
        input: readset_files_in = readset_files
    }
}

task identity_task {
    File readset_files_in
    command {
        true
    }
    output {
        File readset_files = "${readset_files_in}"
    }
}
