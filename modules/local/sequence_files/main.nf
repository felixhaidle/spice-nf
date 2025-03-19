process SEQUENCE_FILES {

    input:
        val species
        val release
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
    ${annotation_gtf ? "--custom_gtf ${annotation_gtf}" : ''} \
    ${peptide_fasta ? "--custom_pep ${peptide_fasta}" : ''} \
    > sequence_file_paths.txt
    """
}
