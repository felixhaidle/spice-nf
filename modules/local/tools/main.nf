

process TOOLS {
    label 'process_single'

    input:
    path anno_file
    val  tools_to_remove

    output:
    path 'tmp/annoTools.txt'          , emit: anno_file

    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """

    # This is not great but I needed to hard copy the annoTools.txt, otherwise the original gets overwritten
    mkdir tmp
    cp "${anno_file}" "tmp/annoTools.txt"


    update_annoTools.py \
        --annoTools "tmp/annoTools.txt" \
        --tools_to_remove ${tools_to_remove}


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
