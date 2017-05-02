#include <ctime>

#include <opencv2/imgproc/imgproc.hpp>

#include "imgproc_pipeline_base.h"


using namespace cv;


class DilationPipeline : public ImgProcPipelineBase {

public:

    DilationPipeline(int argc, char **argv) : ImgProcPipelineBase(argc, argv) {};

    virtual void preprocess(const cv::Mat &image, cv::Mat &processed)
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
        // Resize image to normalized size
        dimensions = getRescaledDimensions(processed, HD_MAX_W, HD_MAX_H);
        resize(processed, processed, Size(dimensions.first, dimensions.second));

        this->current_image.add_intermediate_image("gray", processed);

        // Erosion/dilation kernel
        Mat kernel = getStructuringElement(MORPH_RECT, Size(5, 1));

        // Erosion
        // Mat k2 = getStructuringElement(MORPH_RECT, Size(50, 1));
        erode(processed, processed, kernel);
        this->current_image.add_intermediate_image("erode", processed); 

        // Dilation
        dilate(processed, processed, kernel);
        this->current_image.add_intermediate_image("dilate", processed);

        GaussianBlur(processed, processed, Size(9, 9), 30, 30);
        this->current_image.add_intermediate_image("blur", processed);

        t = std::clock() - t;

        // add execution time
        this->current_image.add_execution_time("preprocess", (double) t / (double) CLOCKS_PER_SEC);
        }
};
