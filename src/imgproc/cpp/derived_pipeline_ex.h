#include <opencv2/imgproc/imgproc.hpp>

#include "imgproc_pipeline_base.h"

using namespace cv;

class DerivedPipelineEx : public ImgProcPipelineBase {

public:
    DerivedPipelineEx(int argc, char **argv) : ImgProcPipelineBase(argc, argv) {};

    virtual void preprocess(const cv::Mat &image, cv::Mat &processed)
    {
        Mat blurred;
        std::pair<int, int> dimensions;

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
        this->current_image.add_intermediate_image("gray", processed.clone());

        // Resize image to normalized size
        dimensions = getRescaledDimensions(processed, HD_MAX_W, HD_MAX_H);
        resize(processed, processed, Size(dimensions.first, dimensions.second));

        // Blur final image to reduce noise
        GaussianBlur(processed, processed, Size(91, 91), 30, 30);
        this->current_image.add_intermediate_image("blur", processed.clone());
    }
};
