#include <ctime>

#include <opencv2/imgproc/imgproc.hpp>

#include "imgproc_pipeline_base.h"


using namespace cv;


class BilateralPipeline : public ImgProcPipelineBase {

public:

    BilateralPipeline(int argc, char **argv) : ImgProcPipelineBase(argc, argv) {};

    virtual void preprocess(const cv::Mat &image, cv::Mat &processed)
    {
        Mat blurred, blurred2;
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

        // Resize image to normalized size
        dimensions = getRescaledDimensions(processed, HD_MAX_W, HD_MAX_H);
        resize(processed, processed, Size(dimensions.first, dimensions.second));

        // Record BW/resized image
        this->current_image.add_intermediate_image("gray", processed);

        // Apply an unsharp mask to increase local contrast
        bilateralFilter(processed, blurred, 9, 75, 75);
        addWeighted(processed, 1.5, blurred, -0.5, 0, processed);
        this->current_image.add_intermediate_image("unsharp", processed);

        // Blur final image to reduce noise
        bilateralFilter(processed, blurred2, 9, 75, 75);
        processed = blurred2.clone();
        this->current_image.add_intermediate_image("blur", blurred2);

        t = std::clock() - t;

        // add execution time
        this->current_image.add_execution_time("preprocess", (double) t / (double) CLOCKS_PER_SEC);
    }

};
