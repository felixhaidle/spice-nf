// Copyright (C) 2025 Felix Haidle
// Licensed under GNU GPL v3. See LICENSE file or https://www.gnu.org/licenses/gpl-3.0.en.html

process FAS_ANNOTATION {
    label 'process_high'


    input:
    path anno_tools         // Path: Path to annotation tools folder
    path spice_library_dir  // Path: Library generated by spice_library.py
    path anno_tools_file    // Path: Path to annotation tools file


    output:
    path "${spice_library_dir}"   , emit: annotated_library_ch
    path "versions.yml"           , emit: versions

    when:
    task.ext.when == null || task.ext.when

    script:
    def args = task.ext.args ?: ''


    """

    # run the annotaion
    source "${anno_tools}/fas.profile"

    fas.doAnno \
        -i "${spice_library_dir}/transcript_data/transcript_set.fasta" \
        -o "${spice_library_dir}/fas_data/" \
        -t "${anno_tools}" \
        --annoToolFile "${anno_tools_file}" \
        -n annotations \
        --cpus ${task.cpus} \
        ${args}


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        greedyFas: \$(pip show greedyFAS | awk '/^Version:/ {print \$2}')
    END_VERSIONS

    # Append tool versions from annotations.json to versions.yml
    python3 - <<EOF >> versions.yml
    import json
    with open("${spice_library_dir}/fas_data/annotations.json") as f:
        data = json.load(f)
        versions = data.get("version", {})
        for tool, info in versions.items():
            version = info.get("version", "NA") if isinstance(info, dict) else "NA"
            print(f"    {tool}: {version}")
    EOF
    """


    stub:
    def args = task.ext.args ?: ''


    """


    cat <<-END_VERSIONS > versions.yml
    "${task.process}":
        greedyFas: \$(pip show greedyFAS | awk '/^Version:/ {print \$2}')
    END_VERSIONS

    # Append tool versions from annotations.json to versions.yml
    python3 - <<EOF >> versions.yml
    import json
    with open("${spice_library_dir}/fas_data/annotations.json") as f:
        data = json.load(f)
        versions = data.get("version", {})
        for tool, info in versions.items():
            version = info.get("version", "NA") if isinstance(info, dict) else "NA"
            print(f"    {tool}: {version}")
    EOF
    """
}
