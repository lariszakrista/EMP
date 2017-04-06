#include "imgproc_pipeline.h"

using namespace cv;
using std::string;
using std::ofstream;
using std::fstream;
using std::cout;
using std::endl;
using std::cerr;
using cv::Mat;

ImgProcPipeline::ImgProcPipeline(string file,string input_dir, ImgprocMode mode, ofstream &metadata_file){
	
	// open the image file
	this->image_file.open(file.c_str(), std::ifstream::in);	

	if(!this->image_file.is_open()){
		cerr << "Could not open images file " << file << endl;
		exit(0);
	}

	this->input_dir = input_dir;
}

void ImgProcPipeline::preprocess(const Mat &image){

	

}

void ImgProcPipeline::find_circles(const Mat &){


}


void ImgProcPipeline::run_single_image(){
	
	// Grab the next image
	this->get_next_image();
	
	// Preprocess the image
	//this->preprocess();
	
	// compute the circles

}

void ImgProcPipeline::run_all(){

}

// Will grab the next image name from the image file
void ImgProcPipeline::get_next_image(){
	
	string filename; 
	Mat src;	
	
	std::getline(this->image_file, filename);
	
	src = imread(this->input_dir + filename, 1);
	
	if (!src.data) {
		cerr << "Failed to open image" << filename << endl;
		// exit?
	}
	
	// Set the current image
	//this->current_image.set_original(src);				
}
