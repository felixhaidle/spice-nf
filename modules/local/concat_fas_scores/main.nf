process CONCAT_FAS_SCORES {
    executor 'local'
    publishDir "${outdir}", mode: 'copy'


    cpus '1'
    memory '6G'

    input:
        path fas_scores_dir
        path spice_library // Directory containing all necessary files
        val outdir // Output directory path

    output:
        path "${spice_library}", emit: finished_library


    script:
    """

    # Convert fas_scores_dir input (which could be multiple paths) into a bash array
    fas_dirs=(${fas_scores_dir})


    # Find the first valid .phyloprofile file
    echo "Looking for a .phyloprofile file in gene directories..."

    found_header=0  # Flag to track if the header was found

    for subdir in "\${fas_dirs[@]}"; do
        # Extract gene directory name (basename)
        gene_id=\$(basename "\${subdir}")

        # Construct the expected .phyloprofile file path
        phyloprofile_file="\${subdir}/\${gene_id}.phyloprofile"

        if [[ -f "\${phyloprofile_file}" ]]; then
            echo "Found .phyloprofile file: \${phyloprofile_file}"

            # Extract the first line (header)
            header=\$(head -n 1 "\${phyloprofile_file}")

            # Ensure the output directory exists
            mkdir -p "${spice_library}/fas_data/"

            # Write the header to fas.phyloprofile
            echo "\${header}" > "${spice_library}/fas_data/fas.phyloprofile"

            echo "Extracted header and saved to ${spice_library}/fas_data/fas.phyloprofile"
            found_header=1
            break  # Stop searching after the first valid file is found
        fi
    done

    # Check if we successfully found a .phyloprofile file
    if [[ \$found_header -eq 0 ]]; then
        echo "Warning: No .phyloprofile file found in any gene directory!"
    fi

    # Count how many directories we have
    total=\${#fas_dirs[@]}
    count=0

    for subdir in "\${fas_dirs[@]}"; do
        # Increment the counter
        count=\$((count + 1))

        # Extract the name of the subdirectory
        gene_id=\${subdir}

        echo "[\$count/\$total] Starting: Concatenation for gene \${gene_id}"


        FASResultHandler.py \
            --mode concat \
            --gene_id "\${gene_id}" \
            --out_dir "\${gene_id}" \
            --anno_dir "${spice_library}/fas_data/"

        echo "[\$count/\$total] Finished: Concatenation for gene \${gene_id}"
    done

    echo "Starting FAS score integration"

        FASResultHandler.py \
            --mode integrate \
            --out_dir "${spice_library}/fas_data/" \
            --anno_dir "${spice_library}/fas_data"

        echo "FAS score integration completed."

    echo "Processing complete. All \$total genes processed."
    parse_domain_out.py \
    -f "${spice_library}/fas_data/forward.domains" \
    -r "${spice_library}/fas_data/reverse.domains" \
    -m "${spice_library}/fas_data/architectures" \
    -o "${spice_library}/fas_data/architectures/"

    """
}
