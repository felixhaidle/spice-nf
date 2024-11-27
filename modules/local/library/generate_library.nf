process GENERATE_LIBRARY {
    memory '2 GB'  // Set a default memory value
    cpus '1'
    conda '/home/felix/miniconda3/envs/spice_env'
    input:
        val species          // String: Species name
        val release         // Integer: Ensembl release version
        val outdir             // Path: Output directory
        val test_mode       // Boolean: Whether to run in test mode


    output:
        
        path "library/spice_lib_*", emit: library_ch // Declare the generated directory as output


    publishDir "${outdir}", mode: 'copy'

    script:
    """
    mkdir -p library  

    conda list

    python ${projectDir}/tools/SPICE/spice_library.py \
        --outdir library \
        --species '${species}' \
        --release '${release}' \
        --test 
        
    """
}


process FAS_ANNOTATION {
    queue 'all'
    executor 'slurm'
    cpus '16'
    conda '/home/felix/miniconda3/envs/spice_env'
    input:
        path anno_tools         // Path: Path to annotation tools file
        path spice_library_dir   // Path: Library generated by spice_library.py
        val test_mode           // Boolean: Whether to run in test mode
        val outdir             // Path: Output directory


    output:
        path "${outdir}/annotated_library", emit: annotated_library_ch // Declare the generated directory as output


    publishDir "${outdir}/annotated_library", mode: 'copy'

    script:
    """
    mkdir -p ${outdir}/annotated_library  
    anno_path=\$(dirname ${anno_tools})

    echo '${anno_tools}' > anno_path.txt

    fas.doAnno \
        -i "${spice_library_dir}/transcript_data/transcript_set.fasta" \
        -o "${spice_library_dir}/fas_data/" \
        -t "\${anno_path}" \
        -n annotations \
        --cpus ${task.cpus} \
        
    """
}
