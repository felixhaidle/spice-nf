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

        annotated_library = FAS_ANNOTATION(
            anno_tools,
            spice_library.library_ch,
            test_mode,
            outdir
        )

        annotated_library.annotated_library_ch.view()

    emit:
        library = spice_library.library_ch
        
}
