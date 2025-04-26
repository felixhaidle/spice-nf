// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

process SEQUENCES {
    label 'process_single'

    input:
    val species
    val release

    output:
    path '*.gtf'                  , emit: gtf_file
    path '*.fa*'                  , emit: fasta_file
    env('SPECIES_NAME')           , emit: species_name
    env('TAXON_ID')               , emit: taxon_id
    env('RELEASE')                , emit: release

    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """
    IFS=\$'\\t' read SPECIES_NAME TAXON_ID RELEASE < <(
        sequences.py \
        --outdir "./" \
        --species ${species} \
        --release ${release} \
        | tail -n1
    )

    export SPECIES_NAME
    export TAXON_ID
    export RELEASE

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | awk '{print \$2}')
    END_VERSIONS
    """

    stub:
    def args = task.ext.args ?: ''


    """


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        python: \$(python --version | awk '{print \$2}')
    END_VERSIONS
    """
}
