// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

process COMPLEXITY{
    label 'process_single'



    input:
    path spice_library
    path genes_txt
    path anno_tools_file

    output:
    path "sorted_genes.txt"           , emit: ordered_genes
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """

    fas.calcComplexity \
    -i "${spice_library}/fas_data/annotations.json" \
    -d "${anno_tools_file}" \
    > complexity.txt

    sort_genes_by_complexity.py \
    --genes_txt ${genes_txt} \
    --complexity_txt complexity.txt \
    --output_txt sorted_genes.txt

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        greedyFas: \$(pip show greedyFAS | awk '/^Version:/ {print \$2}')
        python: \$(python --version | awk '{print \$2}'))
    END_VERSIONS
    """

    stub:
    def args = task.ext.args ?: ''


    """


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        greedyFas: \$(pip show greedyFAS | awk '/^Version:/ {print \$2}')
        python: \$(python --version | awk '{print \$2}'))
    END_VERSIONS
    """
}
