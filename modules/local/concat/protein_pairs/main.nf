// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

process CONCAT_PROTEIN_PAIRS {
    label 'process_single'


    input:
    path genes_txt
    path fas_scores_dir


    output:
    path "merged_genes/*"         , emit: genes_directorys
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """

    mkdir -p merged_tmp
    mkdir -p merged_genes

    # Merge forward.domains safely
    head -n 1 \$(ls *_forward.domains | head -n 1) > merged_tmp/merged_forward.domains
    tail -n +2 -q *_forward.domains >> merged_tmp/merged_forward.domains

    # Merge reverse.domains safely
    head -n 1 \$(ls *_reverse.domains | head -n 1) > merged_tmp/merged_reverse.domains
    tail -n +2 -q *_reverse.domains >> merged_tmp/merged_reverse.domains

    # Merge phyloprofile safely
    head -n 1 \$(ls *.phyloprofile | head -n 1) > merged_tmp/merged.phyloprofile
    tail -n +2 -q *.phyloprofile >> merged_tmp/merged.phyloprofile

    # Now run the Python script
    split_batches.py --batch_dir merged_tmp --output_base merged_genes


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
        python: \$(python --version | awk '{print \$2}')
    END_VERSIONS
    """
}
