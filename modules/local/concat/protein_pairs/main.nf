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

    mkdir merged_genes

    GENE_FILE=${genes_txt}

    # Loop over each line (gene ID) in the file
    while IFS= read -r GENE_ID || [ -n "\${GENE_ID}" ]; do
        # Skip empty lines
        if [ -z "\${GENE_ID}" ]; then
            continue
        fi

        echo "Processing gene: \${GENE_ID}"
        merge_protein_pairs.py \
            --gene_id "\${GENE_ID}" \
            --output_base "merged_genes"

    done < "\${GENE_FILE}"


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
