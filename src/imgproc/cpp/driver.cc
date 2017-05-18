#include "imgproc_pipeline_base.h"
#include "bilateral_pipeline.h"


int main(int argc, char **argv){
    
    // Create pipeline object, passing in input image file to constructor    
    ImgProcPipelineBase *pipeline;
    
    pipeline = new BilateralPipeline(argc, argv);
    pipeline->run_all();
    
    return 0;
}
