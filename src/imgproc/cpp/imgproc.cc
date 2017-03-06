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
#include <vector>

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>


#define FULL_DISK_INTESITY_THRESH_FACTOR    10.0f
#define MAX_CIRCLE_DIFF_SCALAR              0.3
#define RADIUS_CROP_FACTOR                  4
#define HD_MAX_W                            1920
#define HD_MAX_H                            1080
#define WINDOW_WIDTH                        1000


enum EclipseView {
    FULL_DISK = 0,
    CRESCENT,
    TOTALITY,
    INVALID
};


using namespace cv;
using std::cerr;
using std::cout;
using std::endl;
using std::vector;


float avgBWImagePixelValue(const Mat &image);

float avgBWImagePixelValueInCircle(const Mat &image, const Vec3f &circle);

void computeCircles(Mat &image, vector<Vec3f> &circles, double c1, double c2);

void cropAroundSolarDisk(const Mat &src, Mat &dest, Vec3f disk);

void displayImageWithCircles(Mat &image, vector<Vec3f> &circles, String filepath);

void displayImageWith2Circles(Mat image, Vec3f circle1, Vec3f circle2,
                              String filepath);

EclipseView getImageType(const Mat &image, const Vec3f &circle1, const Vec3f &circle2);

void preprocessImage(const Mat &image, Mat &gray);

Vec3f rescaleCircle(const Vec3f &circle, const Mat &image);

std::pair<int, int> getRescaledDimensions(const Mat &image, int max_w, int max_h);

void runAlgorithm(std::string filepath);


int main(int argc, char **argv) {

    int key;
    std::ifstream f;

    if (argc < 2) {
        cerr << "Must pass in images file as command line arg" << endl;
        return -1;
    }

    f.open(argv[1]);
    if (!f.is_open()) {
        cerr << "Could not open images file " << argv[1] << endl;
    }

    for (std::string filepath; std::getline(f, filepath);) {

        runAlgorithm(filepath);
        key = waitKey(0);
        destroyAllWindows();

        // ESC key
        if (key == 1048603) {
            break;
        }
    }

    f.close();

    return 0;
}

float avgBWImagePixelValue(const Mat &image) {
    float                   avg;
    const unsigned char    *row;
    unsigned long           sum = 0;

    for (int i = 0; i < image.rows; i++) {

        row = image.ptr<uchar>(i);

        for (int j = 0; j < image.cols; j++) {
            sum += row[j];
        }
    }
    avg = (float) sum / (float) (image.rows * image.cols);

    // DEBUG
    cout << "OVERALL INTENSITY " << sum << " Avg: " << avg << endl;

    return avg;
}

float avgBWImagePixelValueInCircle(const Mat &image, const Vec3f &circle) {
    float                   avg;
    int                     center_x, center_y, r, r2, d, square_x, square_y,
                            dx, dy, dy2, count = 0;
    const unsigned char    *row;
    unsigned long           sum = 0;

    center_x    = (int) circle[0];
    center_y    = (int) circle[1];
    r           = (int) circle[2];
    r2          = r * r;
    d           = 2 * r;
    square_x    = center_x - r;
    square_y    = center_y - r;

    for (int i = square_y; i < square_y + d; i++) {

        dy  = abs(center_y - i);
        dy2 = dy * dy;
        row = image.ptr<uchar>(i);

        for (int j = square_x; j < square_x + d; j++) {

            dx = abs(center_x - j);

            // First check if the point is within a square diamond inscribed in
            // the circle and possibly short circuit. Otherwise check if it is
            // in the circle, i.e. sqrt(dy**2 + dx**2) <= r
            // <=>  (dy**2 + dx**2) <= r**2
            if ((dx + dy) <= r || (dy2 + (dx * dx)) <= r2) {
                sum += row[j];
                count++;
            }
        }
    }
    avg = (float) sum / (float) count;

    // DEBUG
    cout << "CIRCLE INTENSITY Sum: " << sum << " Avg: " << avg << endl;

    return avg;
}

void computeCircles(Mat &image, vector<Vec3f> &circles, double c1, double c2) {

    // Previously used 80, 52 however seems to be slightly more performant
    // double canny_param1 = 52;
    time_t t1;

    t1 = std::clock();
    HoughCircles(image, circles, CV_HOUGH_GRADIENT, 2,
                //  image.rows/8, canny_param1, 0.5 * canny_param1, 0, 0);
                image.rows/8, c1, c2, 0, 0);

    t1 = std::clock() - t1;

    double sec = (double) t1 / (double) CLOCKS_PER_SEC;
    cout << "Found " << circles.size() << " circles in "
         << sec << " seconds." << endl;
}

bool cropAroundSolarDisk(Mat &src, Mat &dest, Vec3f disk) {
    bool success;
    Rect border;

    border.width    = RADIUS_CROP_FACTOR * disk[2];
    border.height   = border.width;
    border.x        = disk[0] - (border.width  / 2);
    border.y        = disk[1] - (border.height / 2);

    success = (border.x + border.width)  <= src.cols &&
              (border.y + border.height) <= src.rows &&
              border.x >= 0 && border.y >= 0;

    cout << border.x << " " << border.y << " " << border.width << " " << border.height << endl;

    if (success) {
        dest = src(border);
    }

    return success;
}

void displayImageWith2Circles(Mat image, Vec3f circle1, Vec3f circle2,
                              String filepath) {
    int                 radius;
    Point               center;
    std::pair<int, int> dimensions;

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

    dimensions = getRescaledDimensions(image, HD_MAX_W, HD_MAX_H);
    resize(image, image, Size(dimensions.first, dimensions.second));

    namedWindow(filepath, CV_WINDOW_AUTOSIZE);
    imshow(filepath, image);
}

EclipseView getImageType(const Mat &image, const Vec3f &circle1, const Vec3f &circle2) {
    bool    same_center, crescent = true;
    float   distance, overall_intensity, disk_intensity;

    // Euclidian distance between circle centers
    distance        = sqrt(pow(circle1[0] - circle2[0], 2) +
                           pow(circle1[1] - circle2[1], 2));
    same_center     = (circle1[0] == circle2[0]) && (circle1[1] == circle2[1]);

    // If the image is of a crescent, the two circles' radii must be within
    // (100 * MAX_CIRCLE_DIFF_SCALAR)% of each other
    crescent &= (circle2[2] > (1 - MAX_CIRCLE_DIFF_SCALAR) * circle1[2] &&
                 circle2[2] <= circle1[2]) ||
                (circle1[2] > (1 - MAX_CIRCLE_DIFF_SCALAR) * circle2[2] &&
                 circle1[2] <= circle2[2]);

    // If the circles do not overlap then we cannot have a crescent
    crescent &= distance < (circle1[2] + circle2[2]);

    // If the image is og a crescent, the circles cannot share a center point
    crescent &= !same_center;

    if (crescent) {
        return CRESCENT;
    }

    overall_intensity   = avgBWImagePixelValue(image);
    disk_intensity      = avgBWImagePixelValueInCircle(image, circle1);

    if (disk_intensity > (FULL_DISK_INTESITY_THRESH_FACTOR * overall_intensity)) {
        return FULL_DISK;
    }

    // else
    return TOTALITY;
}

void preprocessImage(const Mat &image, Mat &gray) {

    Mat blurred;
    std::pair<int, int> dimensions;

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

void runAlgorithm(std::string filepath) {

    bool                        discard = false;
    EclipseView                 image_type;
    Mat                         src, gray, cropped;
    Vec3f                       circle1, circle2;
    vector<Vec3f>               circles;

    cout << "Opening " << filepath << endl;

    // Read the image
    src = imread(filepath, 1);

    if (!src.data) {
        cerr << "Failed to open image " << filepath << endl;
        return;
    }

    // Among other things, standardize image size - this allows us to
    // use the same hough/gauusian blur parameters for all images
    preprocessImage(src, gray);

    // DEBUG
    imshow("Processed", gray);

    computeCircles(gray, circles, 30, 15);

    // DEBUG
    Mat temp;
    Canny(gray, temp, 30 / 2, 30, 3, false);
    imshow("Edges", temp);

    // int key = 0, c1 = 52, c2 = 26;
    // while ((0x00FF & key) != ' ') {
    //     Mat temp;
    //     cout << "c1: " << c1 << endl;
    //     cout << "c2: " << c2 << endl;
    //     Canny(gray, temp, c1 / 2, c1, 3, false);
    //     computeCircles(gray, circles, c1, c2);
    //     imshow("Edges", temp);
    //     displayImageWith2Circles(gray, circles.size() > 0 ? circles[0] : Vec3f(), circles.size() > 1 ? circles[1] : Vec3f(), filepath);
    //     key = waitKey(0);
    //
    //     switch (key) {
    //         case 1113938:
    //             cout << "Up" << endl;
    //             c1++;
    //             break;
    //         case 1113940:
    //             cout << "Down" << endl;
    //             c1--;
    //             break;
    //         case 1113937:
    //             cout << "Left" << endl;
    //             c2++;
    //             break;
    //         case 1113939:
    //             cout << "Right" << endl;
    //             c2--;
    //             break;
    //         default:
    //             cout << "Invalid" << endl;
    //             break;
    //     }
    // }




    if (circles.size() == 0) {
        discard = true;
        cout << "No sun found. Discarding " << filepath << endl;
    }

    if (!discard) {
        circle1 = rescaleCircle(circles[0], src);
        if (circles.size() > 1) {
            circle2 = rescaleCircle(circles[1], src);
        }
        if (circle1[2] < 50) {
            discard = true;
            cout << "Sun is too small. Discarding " << filepath << endl;
        }
    }



    if (!discard) {
        // This computation can be done using our preprocessed image.
        // Since this image is smaller than most high quality images it will
        // improve performance.
        image_type = getImageType(gray, circles[0],
                                  circles.size() > 1 ? circles[1] : Vec3f());

        String type;
        switch (image_type) {
        case CRESCENT:
            type = "Crescent";
            break;
        case FULL_DISK:
            type = "Full Disk";
            break;
        case TOTALITY:
            type = "Totality";
            break;
        default:
            type = "Unknown";
            break;
        }

        cout << "Image type\t" << type << endl;

        // This is not really where this code will go - just here for now for debugging purposes.
        if (cropAroundSolarDisk(src, cropped, circle1)) {
            imshow("Cropped", cropped);
        }
        else {
            discard = true;
            cout << "Not enough padding around solar disk to crop. Discarding "
                 << filepath << endl;
        }
    }

    displayImageWith2Circles(src, circle1, circle2, filepath);
}
