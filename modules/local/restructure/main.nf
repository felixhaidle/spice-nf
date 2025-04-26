// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

process LIBRARY_RESTRUCTURE {
    label 'process_single'


    input:
    path annotated_library

    output:
    path "${annotated_library}"   , emit: domain_importance_library_ch
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """
    get_domain_importance.py \
    -i "${annotated_library}/fas_data/annotations.json" \
    -o "${annotated_library}/fas_data/"

    restructure_anno.py \
    -i "${annotated_library}/fas_data/annotations.json" \
    -o "${annotated_library}/fas_data/architectures"

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
