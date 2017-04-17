#include <cstdlib>
#include <ctime>
#include <iostream>
#include <fstream>
#include <libgen.h>

#include <gflags/gflags.h>

#include "imgproc_pipeline_base.h"


using namespace cv;
using std::string;
using std::ofstream;
using std::ifstream;
using std::cout;
using std::endl;
using std::cerr;
using std::vector;


/* ----- Command Line Flag Validators ----- */

static bool validate_mode_str(const char *flagname, const string &value)
{
    if (value == "window" || value == "batch")
    {     
        return true;
    }   

    cerr << "Invalid value for " << flagname << ": " << value << endl;
    cerr << "Valid values are \"batch\" and \"window\"" << endl;

    return false;
}

static bool validate_image_file(const char *flagname, const string &value)
{   
    if (value != "")
    {     
        return true;
    }
    
    cerr << flagname << " is required" << endl;
    
    return false;
}

/* ----- End Command Line Flag Validators ----- */


/* ----- Command Line Flag Definitions ----- */

DEFINE_string(
    mode, "window",
    "Optional. Mode in which to run the image processor pipeline. Valid modes: \"window\", \"batch\"."
);
DEFINE_validator(mode, &validate_mode_str);

DEFINE_string(
    output_dir, "",
    "Required in batch mode. Directory in which to save exported images and metadata when run in batch mode."
);

DEFINE_string(
    images_file, "",
    "Required. Path to file containing list of images to process. One line per image. Image files *must* be given as full paths."
);
DEFINE_validator(images_file, &validate_image_file);

DEFINE_double(
    hough_dp, 2.0,
    "Optional. dp parameter to cv::HoughCircles. From OpenCV documentation: Inverse ratio of the accumulator resolution to the "
    "image resolution. For example, if dp=1 , the accumulator has the same resolution as the input image. If dp=2 , the "
    "accumulator has half as big width and height."
);

DEFINE_double(
    hough_param1, 30.0,
    "Optional. param1 parameter to cv::HoughCircles. From OpenCV documentation: First method-specific parameter. In case of "
    "CV_HOUGH_GRADIENT , it is the higher threshold of the two passed to the Canny() edge detector (the lower one is twice smaller)."
);

DEFINE_double(
    hough_param2, 15.0,
    "Optional. param2 parameter to cv::HoughCircles. From OpenCV documentation: Second method-specific parameter. In case of CV_HOUGH_GRADIENT"
    ", it is the accumulator threshold for the circle centers at the detection stage. The smaller it is, the more false circles may be detected."
    " Circles, corresponding to the larger accumulator values, will be returned first."
);

DEFINE_double(
    hough_min_dist, -1,
    "Optional. If not provided, image_height / 8 will be used. min_dist parameter to cv::HoughCircles. From OpenCV documentation: "
    "Minimum distance between the centers of the detected circles. If the parameter is too small, multiple neighbor circles may be "
    "falsely detected in addition to a true one. If it is too large, some circles may be missed."
);

/* ----- End Command Line Flag Definitions ----- */


ImgProcPipelineBase::ImgProcPipelineBase(int argc, char **argv)
{
    ifstream f;
    ofstream metadata_file;
    string valid_modes, input_file, dest_dir, mode_str, output_dir;

    gflags::SetUsageMessage("Image processing pipeline for Eclipse Megamovie Project");
    gflags::ParseCommandLineFlags(&argc, &argv, true);
 
    if (FLAGS_mode == "batch" && FLAGS_output_dir == "")
    {
        cerr << "output_dir parameter is required in batch mode" << endl;
        exit(1);
    }

    // Mode has already been validated by gflags
    this->mode           = FLAGS_mode == "window" ? WINDOW : BATCH;
    this->output_dir     = FLAGS_output_dir;
    this->hough_dp       = FLAGS_hough_dp;
    this->hough_param1   = FLAGS_hough_param1;
    this->hough_param2   = FLAGS_hough_param2;
    this->hough_min_dist = FLAGS_hough_min_dist;

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
    this->image_file.open(FLAGS_images_file.c_str(), std::ifstream::in);    

    if (!this->image_file.is_open())
    {
        cerr << "Could not open images file " << input_file << endl;
        exit(0);
    }
}

void ImgProcPipelineBase::preprocess(const Mat &image, Mat &processed)
{     
    Mat blurred;
    std::pair<int, int> dimensions;

    time_t t = std::clock();

    // Convert image to black and white if it is not already
    if (image.channels() != 1)
    {
        cvtColor(image, processed, CV_BGR2GRAY);
    }    
    else
    {    
        processed = image.clone();
    }
    // When we add intermediate images (for debug purposes) we must add deep copies
    // so that they are not modified before being shown
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
    this->current_image.add_intermediate_image("blur", processed);

    t = std::clock() - t;
    
    // add execution time
    this->current_image.add_execution_time("preprocess", (double) t / (double) CLOCKS_PER_SEC);
}

std::pair<int, int> ImgProcPipelineBase::getRescaledDimensions(const Mat &image, int max_w, int max_h)
{
    double given_ratio, ratio;
    std::pair<int, int> dimensions;

    given_ratio         = (double) max_w / (double) max_h;
    ratio               = (double) image.cols / (double) image.rows;
    // width
    dimensions.first    = ratio > given_ratio ? max_w : cvRound(ratio * (double) max_h);
    // height
    dimensions.second   = ratio > given_ratio ? cvRound((double) max_w / ratio) : max_h;

    return dimensions;
}

Vec3f ImgProcPipelineBase::rescaleCircle(const Vec3f &circle, const Mat &image) 
{
    double  factor;
    int     old_w, new_w;
    Vec3f   rescaled;

    old_w   = image.cols;
    new_w   = getRescaledDimensions(image, HD_MAX_W, HD_MAX_H).first;
    factor  = (double) old_w / (double) new_w;

    for (int i = 0; i < 3; i++)
    {
        rescaled[i] = cvRound(factor * circle[i]);
    }

    return rescaled;
}

// NOTE: Image that is passed in needs to be gray for the HoughCircles() function to work
vector<Vec3f> ImgProcPipelineBase::find_circles(const Mat &image)
{    
    Mat canny;
    vector<Vec3f> circles;

    // Default hough_min_dist flag value is -1
    double min_dist = this->hough_min_dist == -1 ? image.rows / 8 : this->hough_min_dist;

    time_t t = std::clock();
    HoughCircles(image, circles, CV_HOUGH_GRADIENT, this->hough_dp,
                 min_dist, this->hough_param1, this->hough_param2, 0, 0);
    t = std::clock() - t;

    // Add performance time for computing circles to image object
    this->current_image.add_execution_time("circles", (double) t / (double) CLOCKS_PER_SEC);
    
    // Add circles to image object
    this->current_image.add_circles(circles);    
    
    // If no circles are found, record the observation
    if (circles.size() == 0) 
    {
        this->current_image.add_observation("No sun found");
    }
    
    if (this->mode == WINDOW)
    {
        // Create a canny image of the image and it add it as an intermediate image
        Canny(image, canny, MAX(this->hough_param1 / 2, 1), this->hough_param1, 3, false);
        this->current_image.add_intermediate_image("Canny edges", canny);
    }

    return circles;
}

void ImgProcPipelineBase::record_circles(vector<Vec3f> circles, const Mat &image) 
{
    Vec3f c;
    Mat circled_image;
    Point center;
    int radius;

    // Check if a gray scaled image exists. If so, convert it to color    
    if (image.channels() == 1) 
    {
        cvtColor(image, circled_image, CV_GRAY2BGR);
    }
    else 
    {
        circled_image = image.clone();
    }    

    // Display circle 1
    if (circles.size() > 0) 
    {
        c      = this->rescaleCircle(circles[0], circled_image);    
        center = Point(cvRound(c[0]), cvRound(c[1]));
        radius = cvRound(c[2]);
        circle(circled_image, center, 3, Scalar(255, 0, 0), -1, 8, 0);
        circle(circled_image, center, radius, Scalar(255, 0, 0), 4, 8, 0);

        if (radius < MIN_SUN_RADIUS) 
        {
            this->current_image.add_observation("Sun is too small");
        }    
    }
    
    // Display circle 2
    if (circles.size() > 1) 
    {
        c      = this->rescaleCircle(circles[1], circled_image);
        center = Point(cvRound(c[0]), cvRound(c[1]));
        radius = cvRound(c[2]);
        circle(circled_image, center, 3, Scalar(255, 0, 0), -1, 8, 0);
        circle(circled_image, center, radius, Scalar(0, 255, 0), 4, 8, 0);
    }
    
    // Add the final circled image to the current_image object    
    this->current_image.add_final_image(circled_image);
}

void ImgProcPipelineBase::run_single_image(const Mat &image)
{    
    Mat processed;
    vector<Vec3f> circles;

    // Preprocess the image
    this->preprocess(image, processed);
    
    // Compute the circles with the preprocessed image
    circles = this->find_circles(processed);

    // Rescale the circles and add them to the final image
    this->record_circles(circles, image);
}

void ImgProcPipelineBase::run_all()
{
   // Continually grab an image
   while (this->get_next_image()) 
    {        
        this->run_single_image(this->current_image.get_original_image());

        if (this->current_image.record())
        {
            break;
        }
   }
}

// Will grab the next image name from the image file
bool ImgProcPipelineBase::get_next_image()
{    
    string filename;
    Mat src;
    char c_filename[1024], abs_path[1024];    
    
    // If image fails to open, it will go to the next image 
    while (!src.data) 
    {        
        // Stop grabbing images if we are at the end of a file
        if (this->image_file.eof())
        {
            return false;
        }
        
        std::getline(this->image_file, filename);
        strcpy(c_filename, filename.c_str());
        
        cout << "Opening image: " << filename << endl;
        // Read image 
        src = imread(filename, CV_LOAD_IMAGE_UNCHANGED);
        
        // Only break out when a good image is found
        if (src.data)
        {
            break;
        }

        cerr << "Failed to open image: " << filename << endl;
    }
    
    // Construct absolute path of destination image when in batch mode
    if (this->mode == BATCH) 
    {
        realpath(this->output_dir.c_str(), abs_path);
        filename = string(abs_path) + "/" + basename(c_filename);    
    }
    else 
    {
        filename = "";
    }
    
    // Initialize current_image object
    this->current_image = ImgProcImage(src, this->mode, &this->metadata_file, filename);
    
       return true;            
}
