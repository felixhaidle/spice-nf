process SEQUENCE_FILES {

    input:
        val species
        val release
        val test_mode
        val annotation_gtf
        val peptide_fasta

    output:
        path '*.gtf', emit: gtf_file
        path '*.fa*', emit: fasta_file


    script:
    """


    python ${projectDir}/tools/spice_library_scripts/sequences.py \
    --outdir "./" \
    --species ${species} \
    --release ${release} \
    ${test_mode ? '--test' : ''} \
    ${annotation_gtf ? "--custom_gtf ${annotation_gtf}" : ''} \
    ${peptide_fasta ? "--custom_pep ${peptide_fasta}" : ''} \
    > sequence_file_paths.txt
    """
}

process CREATE_LIBRARY {

    input:
        path gtf_file
        path fasta_file
        val species
        val release

    output:
        path 'spice_lib_*', emit: library_dir


    script:
    """


    python ${projectDir}/tools/spice_library_scripts/create_library.py \
    --outdir "./" \
    --gtf_path ${gtf_file} \
    --fasta_path ${fasta_file} \
    --species ${species} \
    --release ${release}


    """
}

process FILTER_LIBRARY {

    input:
        path library_dir

    output:
        path "${library_dir}", emit: filtered_library_dir

    script:
    """
    python ${projectDir}/tools/spice_library_scripts/filter_library.py \
    --library_dir ${library_dir}
    """
}

process FINISH_LIBRARY_INITIALIZATION {

    input:
        path library_dir

    output:
        path "${library_dir}", emit: finished_library_dir

    script:
    """
    python ${projectDir}/tools/spice_library_scripts/finish_setup.py \
    --library_dir ${library_dir}
    """
}
