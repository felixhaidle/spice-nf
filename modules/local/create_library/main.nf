process CREATE_LIBRARY {

    input:
        path gtf_file
        path fasta_file
        val species
        val release
        path prefixes

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
    --library_dir spice_lib_* \
    --taxon_prefixes "${prefixes}"

    finish_setup.py \
    --library_dir spice_lib_*


    """
}
