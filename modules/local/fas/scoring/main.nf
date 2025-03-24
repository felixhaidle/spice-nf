

process FAS_SCORING {
    tag "$gene_id"
    label 'fas_scoring'



    input:
    each  gene_id
    path spice_library
    path anno_tools

    output:
    path "fas_scores/*"           , emit: fas_scored_directories, optional: true
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """
    # Ensure output directory exists
    mkdir -p "fas_scores"


    # Run FASResultHandler to unpack and process the gene
    echo "Starting: Unpacking gene ${gene_id}"
    FASResultHandler.py \
        --pairings_path ${spice_library}/transcript_data/transcript_pairings.json \
        --gene_id ${gene_id} \
        --mode unpack \
        --out_dir "./"
    echo "Finished: Unpacking gene ${gene_id}"

    # Check if the pairwise TSV file was created
    if [ -f "${gene_id}.tsv" ]; then

        mkdir -p "fas_scores/${gene_id}"

        # Run FAS analysis using fas.run
        echo "Starting: FAS analysis for gene ${gene_id}"
        fas.run \
            --seed "${spice_library}/transcript_data/annotations.fasta" \
            --query "${spice_library}/transcript_data/annotations.fasta" \
            --annotation_dir "${spice_library}/fas_data" \
            --out_dir "fas_scores/${gene_id}" \
            --bidirectional \
            --pairwise "${gene_id}.tsv" \
            --out_name "${gene_id}" \
            --tsv \
            --phyloprofile "${spice_library}/transcript_data/phyloprofile_ids.tsv" \
            --empty_as_1 \
            --featuretypes "${spice_library}/fas_data/annoTools.txt" \
            --toolPath "${anno_tools}" \
            --cpus ${task.cpus} \
            ${args}

        echo "Finished: FAS analysis for gene ${gene_id}"

    else
        echo "Pairwise TSV file not found for gene ${gene_id}. Skipping FAS analysis."
    fi


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
