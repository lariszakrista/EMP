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

#include <iostream>

#include "imgproc_util.h"


#define RADIUS_CROP_FACTOR                  4


using std::cerr;
using std::cout;
using std::endl;


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

    return avg;
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

    if (success) {
        dest = src(border);
    }

    return success;
}
