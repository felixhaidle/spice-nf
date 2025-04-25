// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

process SEED_PARALLELIZATION {
    label 'process_single'

    input:
    path genes_txt
    path complexity_txt
    path spice_library
    val available_cpus

    output:
    path 'partition_*'          , emit: partition_ch
    path 'partition_*/*'        , emit: protein_pairings_ch

    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """

    mkdir protein_pairings



    partition_pairs.py \
        --pairings_json ${spice_library}/transcript_data/transcript_pairings.json\
        --paths_file ${complexity_txt}\
        --tmp_dir protein_pairings \
        --partitions ${available_cpus}


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
