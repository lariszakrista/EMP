#include "imgproc_pipeline_base.h"

// #include "derived_pipeline_ex.h"

int main(int argc, char **argv){
    
    // Create pipeline object, passing in input image file to constructor    
    ImgProcPipelineBase *pipeline;
    
    pipeline = new ImgProcPipelineBase(argc, argv);
    // pipeline = new DerivedPipelineEx(argc, argv); 

    pipeline->run_all();
    
    return 0;
}
