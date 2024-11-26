include { GENERATE_LIBRARY } from '../../modules/local/library/generate_library'

workflow LIBRARY_GENERATION {

    take:
        species
        release
        anno_tools
        outdir
        test_mode

    main:

        test = GENERATE_LIBRARY(
            species,
            release,
            anno_tools,
            outdir,
            test_mode
        )

    emit:
        library = test.ch_library
}
