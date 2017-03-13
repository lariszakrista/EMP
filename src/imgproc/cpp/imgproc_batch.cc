/*
   Copyright 2016 Google Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/

#include <cmath>
#include <ctime>
#include <fstream>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>


#define METADATA_FILE_NAME                  "metadata.txt"
#define MIN_SUN_RADIUS                      50
#define HD_MAX_W                            1920
#define HD_MAX_H                            1080


using namespace cv;
using std::cerr;
using std::cout;
using std::endl;
using std::ifstream;
using std::ofstream;
using std::string;
using std::stringstream;
using std::vector;


struct ProcessedImageMetadata {

    string filename;
    Vec3f *circle1;
    Vec3f *circle2;
    double preprocess_secs;
    double hough_secs;
    bool   discard;
    string discard_reasons;
};


void computeCircles(Mat &image, vector<Vec3f> &circles, double c1, double c2, ProcessedImageMetadata &metadata);

string getCircleTuple(const Vec3f &c);

void saveImageWith2Circles(Mat image, const string &output_dir, ofstream &metadata_file, 
                           ProcessedImageMetadata &metadata);

void preprocessImage(const Mat &image, Mat &gray, ProcessedImageMetadata &metadata);

Vec3f rescaleCircle(const Vec3f &circle, const Mat &image);

std::pair<int, int> getRescaledDimensions(const Mat &image, int max_w, int max_h);

void runAlgorithm(const string &input_dir, const string &filename, 
                  const string &output_dir, ofstream &metadata_file);

void writeImageMetadata(ProcessedImageMetadata &metadata, ofstream &metadata_file);


int main(int argc, char **argv) {

    int key;
    ifstream f;
    ofstream metadata_file;
    string input_file, input_dir, output_dir;

    if (argc < 4) {
        cerr << "Must pass in images_file input_dir output_dir as command line args" << endl;
        return -1;
    }

    input_file     = argv[1];
    input_dir      = argv[2];
    output_dir     = argv[3];

    input_dir     += input_dir[input_dir.size() - 1] == '/' ? "" : "/";
	output_dir    += output_dir[output_dir.size() - 1] == '/' ? "" : "/";

    metadata_file.open(string(output_dir + METADATA_FILE_NAME).c_str(), std::ofstream::out);
    if (!metadata_file.is_open()) {
        cerr << "Could not open metadata file " << output_dir + METADATA_FILE_NAME << endl;
        return -1;
    }

    f.open(input_file.c_str(), std::ifstream::in);
    if (!f.is_open()) {
        cerr << "Could not open images file " << input_file << endl;
        return -1;
    }

    cout << output_dir << " " << metadata_file <<endl;

    for (string filename; std::getline(f, filename);) {

        runAlgorithm(input_dir, filename, output_dir, metadata_file);
    }

    f.close();
    metadata_file.close();

    return 0;
}


void computeCircles(Mat &image, vector<Vec3f> &circles, double c1, double c2, ProcessedImageMetadata &metadata) {

    // Previously used 80, 52 however seems to be slightly more performant
    // double canny_param1 = 52;
    
    time_t t = std::clock();
    HoughCircles(image, circles, CV_HOUGH_GRADIENT, 2,
                //  image.rows/8, canny_param1, 0.5 * canny_param1, 0, 0);
                image.rows/8, c1, c2, 0, 0);

    t = std::clock() - t;

    metadata.hough_secs = (double) t / (double) CLOCKS_PER_SEC;
    cout << "Found " << circles.size() << " circles in "
         << metadata.hough_secs << " seconds." << endl;
}


string getCircleTuple(const Vec3f &c) {
    stringstream ret;
    ret << "(" << c[0] << "," << c[1] << "," << c[2] << ")";
    return ret.str();
}


void saveImageWith2Circles(Mat image, const string &output_dir, ofstream &metadata_file, 
                           ProcessedImageMetadata &metadata) {
    
    int                 radius;
    Point               center;
    Vec3f               circle1, circle2;
    std::pair<int, int> dimensions;

    circle1 = *(metadata.circle1);
    circle2 = *(metadata.circle2);

    // Convert the BW image to color so that we can overlay colored circles on
    // it
    if (image.channels() == 1) {
        cvtColor(image, image, CV_GRAY2BGR);
    }

    // Display circle1
    center      = Point(cvRound(circle1[0]), cvRound(circle1[1]));
    radius      = cvRound(circle1[2]);
    circle(image, center, 3, Scalar(255, 0, 0), -1, 8, 0);
    circle(image, center, radius, Scalar(255, 0, 0), 4, 8, 0);

    // Display circle2
    center      = Point(cvRound(circle2[0]), cvRound(circle2[1]));
    radius      = cvRound(circle2[2]);
    circle(image, center, 3, Scalar(255, 0, 0), -1, 8, 0);
    circle(image, center, radius, Scalar(0, 255, 0), 4, 8, 0);


    try {
        imwrite(output_dir + metadata.filename, image);
    }
    catch (Exception &ex) {
        cerr << "Exception converting saving image " << (output_dir + metadata.filename) << " ";
        cerr << ex.what() << endl;
        return;
    }

    // else
    writeImageMetadata(metadata, metadata_file);
}


void preprocessImage(const Mat &image, Mat &gray, ProcessedImageMetadata &metadata) {

    Mat blurred;
    std::pair<int, int> dimensions;

    time_t t = std::clock();

    // Convert image to black and white
    cvtColor(image, gray, CV_BGR2GRAY);

    // Resize image to normalized size
    dimensions = getRescaledDimensions(gray, HD_MAX_W, HD_MAX_H);
    resize(gray, gray, Size(dimensions.first, dimensions.second));

    // Apply an unsharp mask to increase local contrast
    GaussianBlur(gray, blurred, Size(15, 15), 20, 20);
    addWeighted(gray, 1.5, blurred, -0.5, 0, gray);

    // Blur final image to reduce noise
    // GaussianBlur(gray, gray, Size(9, 9), 30, 30);
    medianBlur(gray, gray, 11);

    t = std::clock() - t;
    metadata.preprocess_secs = (double) t / (double) CLOCKS_PER_SEC;
}


Vec3f rescaleCircle(const Vec3f &circle, const Mat &image) {
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


std::pair<int, int> getRescaledDimensions(const Mat &image, int max_w, int max_h) {

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


void runAlgorithm(const string &input_dir, const string &filename, 
                  const string &output_dir, ofstream &metadata_file) {

    ProcessedImageMetadata      metadata;
    Mat                         src, gray, cropped;
    Vec3f                       circle1, circle2;
    vector<Vec3f>               circles;

    metadata.discard  = false;
    metadata.filename = filename;

    cout << "Opening " << filename << endl;

    // Read the image
    src = imread(input_dir + filename, 1);

    if (!src.data) {
        cerr << "Failed to open image " << filename << endl;
        return;
    }

    // Among other things, standardize image size - this allows us to
    // use the same hough/gauusian blur parameters for all images
    preprocessImage(src, gray, metadata);

    computeCircles(gray, circles, 30, 15, metadata);

    if (circles.size() == 0) {
        metadata.discard = true;
        metadata.discard_reasons += "No sun found;";
    }

    if (!metadata.discard) {
        circle1 = rescaleCircle(circles[0], src);
        if (circles.size() > 1) {
            circle2 = rescaleCircle(circles[1], src);
        }
        if (circle1[2] < MIN_SUN_RADIUS) {
            metadata.discard = true;
            metadata.discard_reasons += "Sun is too small;";
        }
    }
    
    metadata.circle1 = &circle1;
    metadata.circle2 = &circle2;

    saveImageWith2Circles(src, output_dir, metadata_file, metadata);
}


void writeImageMetadata(ProcessedImageMetadata &metadata, ofstream &metadata_file) {

    metadata_file << metadata.filename << "|";
    metadata_file << getCircleTuple(*(metadata.circle1)) << "|";
    metadata_file << getCircleTuple(*(metadata.circle2)) << "|";
    metadata_file << metadata.preprocess_secs << "|";
    metadata_file << metadata.hough_secs << "|";
    metadata_file << metadata.discard << "|";
    metadata_file << metadata.discard_reasons;
    metadata_file << endl;
}
