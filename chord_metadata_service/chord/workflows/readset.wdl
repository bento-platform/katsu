workflow readset {
    Array[File] readset_files

    scatter(file in readset_files) {
        call identity_task {
            input: readset_file_in = file
        }
    }
}

task identity_task {
    File readset_file_in
    command {
        true
    }
    output {
        File readset_file = "${readset_file_in}"
    }
}
