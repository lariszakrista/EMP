#include "imgproc_pipeline.h"

using namespace cv;
using std::string;
using std::ofstream;
using std::fstream;
using std::cout;
using std::endl;
using std::cerr;
using std::vector;
using cv::Mat;

#define HD_MAX_W                            1920
#define HD_MAX_H                            1080
#define METADATA_FILE_NAME                  "metadata.txt"

ImgProcPipeline::ImgProcPipeline(string file, string dest_dir, ImgprocMode mode, string metadata_name){

	this->mode = mode;
	this->dest_dir = dest_dir;

    this->metadata_file.open(metadata_name.c_str(), std::ofstream::out);

    if (!metadata_file.is_open()) {
        cerr << "Could not open metadata file " << metadata_file << endl;
        exit(0);
    }

    // open the image file
    this->image_file.open(file.c_str(), std::ifstream::in);	

    if(!this->image_file.is_open()){
		cerr << "Could not open images file " << file << endl;
		exit(0);
    }
}

void ImgProcPipeline::preprocess(const Mat &image){
     
    Mat blurred;
    Mat gray;
    std::pair<int, int> dimensions;

    time_t t = std::clock();

    // Convert image to black and white
    cvtColor(image, gray, CV_BGR2GRAY);
    this->current_image.add_intermediate_image("gray", gray);

    // Resize image to normalized size
    dimensions = getRescaledDimensions(gray, HD_MAX_W, HD_MAX_H);
    resize(gray, gray, Size(dimensions.first, dimensions.second));

    // Apply an unsharp mask to increase local contrast
    GaussianBlur(gray, blurred, Size(15, 15), 20, 20);
    addWeighted(gray, 1.5, blurred, -0.5, 0, gray);
    this->current_image.add_intermediate_image("unsharp", gray); 

    // Blur final image to reduce noise
    // GaussianBlur(gray, gray, Size(9, 9), 30, 30);
    medianBlur(gray, gray, 11);
    this->current_image.add_intermediate_image("blur", gray);

    t = std::clock() - t;
    
    // add execution time
    this->current_image.add_execution_time("preprocess", (double) t / (double) CLOCKS_PER_SEC);

}

std::pair<int, int> ImgProcPipeline::getRescaledDimensions(const Mat &image, int max_w, int max_h) {

    double given_ratio, ratio;
    std::pair<int, int> dimensions;

    given_ratio         = (double) max_w / (double) max_h;
    ratio               = (double) image.cols / (double) image.rows;
    // width
    dimensions.first    = ratio >  given_ratio ? max_w : cvRound(ratio * (double) max_h);
    // height
    dimensions.second   = ratio <= given_ratio ? max_h : cvRound(ratio * (double) max_w);

    return dimensions;
}

void ImgProcPipeline::find_circles(const Mat &image){
    
    Mat canny;
    vector<Vec3f> circles;
    double c1 = 30, c2 = 15;

    time_t t = std::clock();
    HoughCircles(image, circles, CV_HOUGH_GRADIENT, 2,
                 image.rows / 8, c1, c2, 0, 0);
    t = std::clock() - t;
    
    // Add performance time for computing circles to image object
    this->current_image.add_execution_time("circles", (double) t / (double) CLOCKS_PER_SEC);
    
    // Add circles to image object
    this->current_image.add_circles(circles);
    
    Canny(image, canny, MAX(c1 / 2, 1), c1, 3, false);
    this->current_image.add_intermediate_image("Canny edges", canny);
}


void ImgProcPipeline::run_single_image(const Mat &image){
	
    // Preprocess the image
    this->preprocess(image);
	
    // compute the circles	
    //this->find_circles(image);

    this->current_image.record();


}

void ImgProcPipeline::run_all(){

   Mat image = this->get_next_image();

   this->current_image = Image(image, this->mode, &this->metadata_file, "");

   // continually grab an image
   while (image.data) {
       
       this->run_single_image(image);
       
       image = this->get_next_image();
   }

}

// Will grab the next image name from the image file
Mat ImgProcPipeline::get_next_image(){
	
    string filename; 
    Mat src;	
	
    std::getline(this->image_file, filename);
	
    src = imread(filename, 1);
	
    if (!src.data) {
	cerr << "Failed to open image" << filename << endl;
    }

    return src;				
}
