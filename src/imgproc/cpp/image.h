#include <fstream>
#include <map>
#include <string>
#include <vector>

#include <opencv2/imgproc/imgproc.hpp>

#include "imgproc_defs.h"

class Image
{
public:

    Image();

    Image(const cv::Mat &image, ImgprocMode mode, std::ofstream *metadata_file, const std::string &image_dest = "");

    // Adds intermediate image **if in window mode** because intermediate images
    // are not used in other modes. 
    void add_intermediate_image(const std::string &name, const cv::Mat &image);

    // Add final processed image
    void add_final_image(const cv::Mat &image);

    // "Records" image - behavior of this method depends on the mode. 
    // 
    // In WINDOW mode, this method displays the original, final, and all intermediate
    // images on screen and hangs until the user presses a key. Returns true
    // if the user pressed ESC key, otherwise returns false.
    // 
    // In BATCH mode, this method saves the final image and records the image's
    // metadata
    bool record();    

    // Add single circle - this will be exported to the metadata file
    void add_circle(const cv::Vec3f &circle);

    // Add multiple circles - these will all be exported to the metadata file
    void add_circles(const std::vector<cv::Vec3f> &circles);

    void add_observation(const std::string &observation);

    void add_execution_time(const std::string &name, double num_secs);

private:
    // Imgproc pipeline execution mode determines whether intermediate images 
    // are saved or not and the behavior of record
    ImgprocMode mode;

    // Original image
    cv::Mat original;
    
    // Processed image
    cv::Mat processed;
    
    // Images created between original and processed image
    // these are used in WINDOW mode and are all displayed
    std::map<std::string, cv::Mat> intermediate_images;
    
    // Circles that were detected
    std::vector<cv::Vec3f> circles;
    
    // Times it took for various parts of the pipeline to execute
    std::map<std::string, double> execution_times;
    
    // General observations - can be added at will by ImgprocPipeline
    // creator
    std::vector<std::string> observations;

    // Destination file for processed image to be saved to
    // Image will not actually be saved if run in BATCH mode
    std::string dest;
 
    // Open file stream that metadata will be written to
    std::ofstream *metadata_file;
};
