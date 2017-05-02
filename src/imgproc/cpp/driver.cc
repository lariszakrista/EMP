#include "imgproc_pipeline_base.h"
#include "dilation_pipeline.h"


int main(int argc, char **argv){
    
    // Create pipeline object, passing in input image file to constructor    
    ImgProcPipelineBase *pipeline;
    
    pipeline = new DilationPipeline(argc, argv);
    pipeline->run_all();
    
    return 0;
}
