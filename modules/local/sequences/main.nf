

process SEQUENCES {
    label 'process_low'

    input:
    val species
    val release
    val annotation_gtf
    val peptide_fasta

    output:
    path '*.gtf'                  , emit: gtf_file
    path '*.fa*'                  , emit: fasta_file


    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """
    sequences.py \
    --outdir "./" \
    --species ${species} \
    --release ${release} \
    ${annotation_gtf ? "--custom_gtf ${annotation_gtf}" : ''} \
    ${peptide_fasta ? "--custom_pep ${peptide_fasta}" : ''} \
    > sequence_file_paths.txt

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | awk '{print \$2}'))
    END_VERSIONS
    """

    stub:
    def args = task.ext.args ?: ''


    """


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | awk '{print \$2}'))
    END_VERSIONS
    """
}
