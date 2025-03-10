process GET_GENE_SIZE {
    executor 'slurm'
    queue 'all'
    maxForks 10
    cpus '1'
    tag "$gene"

    input:
    val gene
    path annotation_file

    output:
        tuple(val(gene), env("requirements"))

    script:
    """
    # Run Python script to get gene classification
    result=\$(extract_gene_info.py ${annotation_file} ${gene})

    # Debugging: Print the result before parsing
    echo "Raw output: \$result"

    # Use awk to split tab-separated values
    gene=\$(echo "\$result" | awk -F'\\t' '{print \$1}')
    size=\$(echo "\$result" | awk -F'\\t' '{print \$2}')
    transcript_count=\$(echo "\$result" | awk -F'\\t' '{print \$3}')
    requirements=\$(echo "\$result" | awk -F'\\t' '{print \$4}')

    # Output results
    echo "\$gene \$size \$transcript_count \$requirements"
    """
}
