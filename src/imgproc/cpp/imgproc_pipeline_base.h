#ifndef _IMGPROC_PIPELINE_BASE_H
#define _IMGPROC_PIPELINE_BASE_H

#include <vector>
#include <string>

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/core/core.hpp>

#include "imgproc_defs.h"
#include "imgproc_image.h"

class ImgProcPipelineBase
{
private:
    // Image object
    std::ofstream metadata_file;
    std::ifstream image_file;
    std::string output_dir;
    ImgprocMode mode;

protected:
    ImgProcImage current_image;

public:
    // Will open up the initialize image_file ifstream object given input_file string
    ImgProcPipelineBase(int, char **);        
        
    // Preprocesses the image before image processing
    virtual void preprocess(const cv::Mat &, cv::Mat &);
        
    std::pair<int, int> getRescaledDimensions(const cv::Mat &, int, int);
        
    // Rescales the circle found based on the Mat image passed in 
    cv::Vec3f rescaleCircle(const cv::Vec3f &, const cv::Mat &);            

    // Detect circles in the image
    virtual std::vector<cv::Vec3f> find_circles(const cv::Mat &);
        
    // Add the top two circles found to the original image
    virtual void record_circles(std::vector<cv::Vec3f> , const cv::Mat &);        

    // Invokes get_next_image and then initializes an image object
    void run_single_image(const cv::Mat &);
        
    // Will process all of the images in the input file
    // Utilizes grab_next_image() to grab the next image
    void run_all();

    // Will grab the next image from the input file
    bool get_next_image();     
};

#endif
