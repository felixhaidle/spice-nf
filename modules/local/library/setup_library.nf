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


    sequences.py \
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
        path "spice_lib_*/transcript_data/genes.txt", emit: genes_txt_ch


    script:
    """


    create_library.py \
    --outdir "./" \
    --gtf_path ${gtf_file} \
    --fasta_path ${fasta_file} \
    --species ${species} \
    --release ${release}

    filter_library.py \
    --library_dir spice_lib_*

    finish_setup.py \
    --library_dir spice_lib_*


    """
}

