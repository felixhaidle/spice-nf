process FAS_SCORING {
    label 'fas_scoring'

    input:
    each path (protein_pair)
    path spice_library
    path anno_tools

    output:
    path "fas_scores/*"           , emit: fas_scored_directories
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''

    """
    mkdir -p "fas_scores"

    if [ -d "${protein_pair}" ]; then
        # If protein_pair is a directory, loop over each file
        echo "is folder"
        find -L "${protein_pair}" -type f | while IFS= read -r file; do
            echo "Running fas.run on: \${file}"
            fas.run \
                --seed "${spice_library}/transcript_data/annotations.fasta" \
                --query "${spice_library}/transcript_data/annotations.fasta" \
                --annotation_dir "${spice_library}/fas_data" \
                --out_dir "fas_scores" \
                --bidirectional \
                --pairwise "\${file}" \
                --out_name "\$(basename "\${file}")" \
                --tsv \
                --phyloprofile "${spice_library}/transcript_data/phyloprofile_ids.tsv" \
                --empty_as_1 \
                --featuretypes "${spice_library}/fas_data/annoTools.txt" \
                --toolPath "${anno_tools}" \
                ${args}
        done
    else
        # If it's a single file use the file
        fas.run \
            --seed "${spice_library}/transcript_data/annotations.fasta" \
            --query "${spice_library}/transcript_data/annotations.fasta" \
            --annotation_dir "${spice_library}/fas_data" \
            --out_dir "fas_scores" \
            --bidirectional \
            --pairwise "${protein_pair}" \
            --out_name "${protein_pair.baseName}" \
            --tsv \
            --phyloprofile "${spice_library}/transcript_data/phyloprofile_ids.tsv" \
            --empty_as_1 \
            --featuretypes "${spice_library}/fas_data/annoTools.txt" \
            --toolPath "${anno_tools}" \
            ${args}
    fi

    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        greedyFas: \$(pip show greedyFAS | awk '/^Version:/ {print \$2}')
        python: \$(python --version | awk '{print \$2}')
    END_VERSIONS
    """

    stub:
    def args = task.ext.args ?: ''

    """
    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        greedyFas: \$(pip show greedyFAS | awk '/^Version:/ {print \$2}')
        python: \$(python --version | awk '{print \$2}')
    END_VERSIONS
    """
}
