#include "image.h"

using std::string;
using std::vector;

using cv::Mat;
using cv::Vec3f;

Image::Image(){}

Image::Image(const cv::Mat &image, ImgprocMode mode, std::ofstream *metadata_file, const string &image_dest)
: original(image), mode(mode), metadata_file(metadata_file), dest(image_dest)
{
}

void Image::add_intermediate_image(const string &name, const Mat &image)
{
    return;
}

bool Image::record()
{
    return true;
}

void Image::add_circle(const Vec3f &circle)
{
    this->circles.push_back(circle);
}

void Image::add_circles(const vector<Vec3f> &new_circles)
{
    this->circles.reserve(this->circles.size() + std::distance(new_circles.begin(), new_circles.end()));
    this->circles.insert(this->circles.end(), new_circles.begin(), new_circles.end());
}

void Image::add_observation(const std::string &observation)
{
    this->observations.push_back(observation);
}

void Image::add_execution_time(const std::string &name, double num_secs)
{
    this->execution_times[name] = num_secs;
}
