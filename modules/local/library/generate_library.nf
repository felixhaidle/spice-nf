process GENERATE_LIBRARY {
    memory '2 GB'  // Set a default memory value
    cpus '1'
    conda './environment.yml'
    input:
        val species          // String: Species name
        val release         // Integer: Ensembl release version
        path anno_tools         // Path: Path to annotation tools file
        val outdir             // Path: Output directory
        val test_mode       // Boolean: Whether to run in test mode


    output:
        path "test.txt", emit: ch_library // Capture the generated library

    publishDir "${outdir}/test.txt", mode: 'copy'

    script:
    """
    
    #python tools/SPICE/spice_library.py  --outdir ${outdir} --species '${species}' --release '${release}' --modefas '${anno_tools}' ${test_mode ? '--test' : ''}
    python ${projectDir}/tools/SPICE/spice_library.py --help > test.txt
    """
}
