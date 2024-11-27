include { GENERATE_LIBRARY } from '../../modules/local/library/generate_library'
include { FAS_ANNOTATION } from '../../modules/local/library/generate_library'

workflow LIBRARY_GENERATION {

    take:
        species
        release
        anno_tools
        outdir
        test_mode

    main:

        spice_library = GENERATE_LIBRARY(
            species,
            release,
            outdir,
            test_mode
        )

        // Define the input for FAS_ANNOTATION based on test_mode
        fasAnno_library_input = test_mode ? file("${projectDir}/tools/SPICE/test_data/Spice_Library/spice_lib_test_homo_sapiens_94_1ee") : spice_library.library_ch

        annotated_library = FAS_ANNOTATION(
            anno_tools,
            fasAnno_library_input,
            test_mode,
            outdir
        )


        annotated_library.annotated_library_ch.view()

    emit:
        library = spice_library.library_ch
        
}
