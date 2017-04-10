#include <cstdlib>
#include <ctime>
#include <iostream>
#include <fstream>
#include <libgen.h>

#include "imgproc_pipeline.h"

using namespace cv;
using std::string;
using std::ofstream;
using std::ifstream;
using std::cout;
using std::endl;
using std::cerr;
using std::vector;
using cv::Mat;

ImgProcPipeline::ImgProcPipeline(int argc, char **argv){

    ifstream f;
    ofstream metadata_file;
    string valid_modes, input_file, dest_dir, mode_str, output_dir;

    if (argc < 3) {
        cerr << "Usage:\n\t$ ./imgproc images_file mode output_dir" << endl;
        cerr << endl << "Modes:\t" << valid_modes << "\n";
        cerr << "\toutput_dir required when run in batch mode\n" << endl;
		exit(1);
    } 

    input_file = argv[1];
    mode_str   = argv[2];
    
    if (mode_str == "batch")
    {
        this->mode       = BATCH;
        this->output_dir = argv[3];
    }
    else if (mode_str == "window")
    {
        this->mode = WINDOW;
		this->output_dir = "";
    }
    else
    {
        cerr << "Invalid mode: " << mode_str << ". Valid modes: " << valid_modes << endl;
     	exit(1);
    }

    if (this->mode == BATCH)
    {
        // Add trailing slash to dir path if necessary
	    this->output_dir += this->output_dir[this->output_dir.size() - 1] == '/' ? "" : "/";
    	
		this->metadata_file.open(string(this->output_dir + METADATA_FILE_NAME).c_str(), std::ofstream::out);
		
		if(!this->metadata_file.is_open()){
			cerr << "Could not open metadata file " << this->output_dir << METADATA_FILE_NAME << endl;
			exit(0);
    	}
	}	

    // open the image file
    this->image_file.open(input_file.c_str(), std::ifstream::in);	

    if(!this->image_file.is_open()){
		cerr << "Could not open images file " << input_file << endl;
		exit(0);
    }
}

void ImgProcPipeline::preprocess(const Mat &image, Mat &processed){
     
    Mat blurred;
    std::pair<int, int> dimensions;

    time_t t = std::clock();

    // Convert image to black and white
    cvtColor(image, processed, CV_BGR2GRAY);
    this->current_image.add_intermediate_image("gray", processed);

    // Resize image to normalized size
    dimensions = getRescaledDimensions(processed, HD_MAX_W, HD_MAX_H);
    resize(processed, processed, Size(dimensions.first, dimensions.second));

    // Apply an unsharp mask to increase local contrast
    GaussianBlur(processed, blurred, Size(15, 15), 20, 20);
    addWeighted(processed, 1.5, blurred, -0.5, 0, processed);
    this->current_image.add_intermediate_image("unsharp", processed); 

    // Blur final image to reduce noise
    GaussianBlur(processed, processed, Size(9, 9), 30, 30);
    // medianBlur(processed, processed, 11);
    this->current_image.add_intermediate_image("blur", processed);

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

Vec3f ImgProcPipeline::rescaleCircle(const Vec3f &circle, const Mat &image) {
    double  factor;
    int     old_w, new_w;
    Vec3f   rescaled;

    old_w   = image.cols;
    new_w   = getRescaledDimensions(image, HD_MAX_W, HD_MAX_H).first;
    factor  = (double) old_w / (double) new_w;

    for (int i = 0; i < 3; i++) {
        rescaled[i] = cvRound(factor * circle[i]);
    }

    return rescaled;
}

// NOTE: Image that is passed in needs to be gray for the HoughCircles() function to work
vector<Vec3f> ImgProcPipeline::find_circles(const Mat &image){
    
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
	
	// If no circles are found, record the observation
	if (circles.size() == 0) {
		this->current_image.add_observation("No sun found");
	}
	
	// Create a canny image of the image and it add it as an intermediate image
    Canny(image, canny, MAX(c1 / 2, 1), c1, 3, false);
    this->current_image.add_intermediate_image("Canny edges", canny);
	
	return circles;
}

void ImgProcPipeline::record_circles(vector<Vec3f> circles, const Mat &image) {

	Vec3f circle1, circle2;
	Mat circled_image;
	Point center;
	int radius;
	
	// Check if a gray scaled image exists. If so, convert it to color	
	if (image.channels() == 1) {
		cvtColor(image, circled_image, CV_GRAY2BGR);
	}
	else {
		circled_image = image.clone();
	}	

	circle1 = this->rescaleCircle(circles[0], circled_image);
		
	if(circles.size() > 1) {
		circle2 = rescaleCircle(circles[1], circled_image);
	}
	if (circle1[2] < MIN_SUN_RADIUS) {
		this->current_image.add_observation("Sun is too small");
	}	
	
	// Display circle1	
	center      = Point(cvRound(circle1[0]), cvRound(circle1[1]));
    radius      = cvRound(circle1[2]);
    circle(circled_image, center, 3, Scalar(255, 0, 0), -1, 8, 0);
    circle(circled_image, center, radius, Scalar(255, 0, 0), 4, 8, 0);

    // Display circle2
    center      = Point(cvRound(circle2[0]), cvRound(circle2[1]));
    radius      = cvRound(circle2[2]);
    circle(circled_image, center, 3, Scalar(255, 0, 0), -1, 8, 0);
    circle(circled_image, center, radius, Scalar(0, 255, 0), 4, 8, 0);
	
	// Add the final circled image to the current_image object	
	this->current_image.add_final_image(circled_image);
}

void ImgProcPipeline::run_single_image(const Mat &image){
	
	Mat processed;
	vector<Vec3f> circles;
	
    // Preprocess the image
    this->preprocess(image, processed);
	
    // Compute the circles with the preprocessed image
    circles = this->find_circles(processed);
	
	// Rescale the circles and add them to the final image
	this->record_circles(circles, image);			
}

void ImgProcPipeline::run_all(){

   // Continually grab an image
   while (this->get_next_image()) {
		
        this->run_single_image(this->current_image.get_original_image());
	
		if (this->current_image.record()){
			break;
		}

   }

}

// Will grab the next image name from the image file
bool ImgProcPipeline::get_next_image(){
	
    string filename;
	char *abs_path;
    Mat src;
	char c_filename[256];	
	
	// If image fails to open, it will go to the next image 
    while(!src.data) {
		
		// Stop grabbing images if we are at the end of a file
		if (this->image_file.eof()) {
			return false;
		}
		
		std::getline(this->image_file, filename);
		strcpy(c_filename, filename.c_str());
		
		// Read image 
		src = imread(filename, 1);
		
		// Only break out when a good image is found
		if(src.data)
			break;

		cerr << "Failed to open image: " << filename << endl;
    }
	
	// Construct absolute path filename string when in batch mode
	if (this->mode == BATCH) {
		abs_path = realpath(this->output_dir.c_str(), NULL);
		filename = string(abs_path) + "/" + basename(c_filename);	
	}
	else {
		filename = "";
	}
	
	// Initialize current_image object
	this->current_image = Image(src, this->mode, &this->metadata_file, filename);
	
	delete [] abs_path;	
	
   	return true;			
}

