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


	ImgprocMode mode;
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

    if (mode == BATCH)
    {
        // Add trailing slash to dir path if necessary
	    this->output_dir += this->output_dir[this->output_dir.size() - 1] == '/' ? "" : "/";
    }

	this->metadata_file.open(METADATA_FILE_NAME, std::ifstream::in);

	if(!this->metadata_file.is_open()){
		cerr << "Could not open images file " << METADATA_FILE_NAME << endl;
		exit(0);
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

// image needs to be gray
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

	if (circles.size() == 0) {
		this->current_image.add_observation("No sun found");
	}
    
    Canny(image, canny, MAX(c1 / 2, 1), c1, 3, false);
    this->current_image.add_intermediate_image("Canny edges", canny);
}


void ImgProcPipeline::run_single_image(const Mat &image){
	
	Mat processed;
	Vec3f circle1, circle2;
	
    // Preprocess the image
    this->preprocess(image, processed);
	
    // compute the circles with the preprocessed image
    this->find_circles(processed);

	this->current_image.add_final_image(image);
	
}

void ImgProcPipeline::run_all(){

   // continually grab an image
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
    Mat src;
	char c_filename[256];	
	
	// If image fails to open, it will go to the next image 
    while(!src.data) {
		
		// Stop grabbing images if we are at the end of a file
		if(this->image_file.eof()) return false;
		
		std::getline(this->image_file, filename);
		strcpy(c_filename, filename.c_str());
	
		src = imread(filename, 1);
		
		// Only break out a good image is taken
		if(src.data)
			break;

		cerr << "Failed to open image: " << filename << endl;
    }
	
	this->current_image = Image(src, this->mode, &this->metadata_file, this->output_dir + basename(c_filename));
	
   	return true;			
}

