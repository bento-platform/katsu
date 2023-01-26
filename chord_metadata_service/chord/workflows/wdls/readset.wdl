workflow readset {
    Array[File] readset_files

    scatter(file in readset_files) {
        call copy_task {
            input: readset_file_in = file
        }
    }

    output {
        Array[File] readset_files_out = copy_task.readset_file
    }
}

task copy_task {
    File readset_file_in
    command {
        cp '${readset_file_in}' $(basename -- ${readset_file_in})
        echo $(basename -- ${readset_file_in})
    }
    output {
        File readset_file = read_string(stdout())
    }
}
