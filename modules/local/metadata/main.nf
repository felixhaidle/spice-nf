// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

process METADATA {
    label 'process_single'

    input:
    val species
    val is_ensembl
    val taxonomy_id

    output:
    env('SPECIES_NAME')           , emit: species_name
    env('TAXON_ID')               , emit: taxon_id
    env('RELEASE')                , emit: release

    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''
    def flag = is_ensembl ? "" : "--use_placeholder"
    //def set_taxon = taxonomy_id ? "TAXON_ID=${taxonomy_id}" : ""
    def set_taxon = taxonomy_id != '' ? "export TAXON_ID=${taxonomy_id}" : ""



    """
    IFS=\$'\\t' read SPECIES_NAME TAXON_ID RELEASE < <(fetch_metadata.py --species ${species} ${flag} | tail -n1)
    export SPECIES_NAME
    export TAXON_ID
    export RELEASE

    ${set_taxon}

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
