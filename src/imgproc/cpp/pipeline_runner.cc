#include "imgproc_pipeline.h"
#include "imgproc_defs.h"

int main(int argc, char **argv){
	

	// Create pipeline object, passing in input image file to constructor	
	ImgProcPipeline pipeline(argc, argv); 
	pipeline.run_all();
	
	return 0;

}
