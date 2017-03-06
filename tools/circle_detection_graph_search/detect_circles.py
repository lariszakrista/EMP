#
# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import time

import cv2


def compute_circles(image, dp, minDist, param1, param2, minRadius, maxRadius):
    circle1 = None
    circle2 = None

    # Compute the circles
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, dp, minDist,
                               param1=param1, param2=param2,
                               minRadius=minRadius, maxRadius=maxRadius)

    # Extract the circles
    try:
        circle1 = circles[0][0]
    except (IndexError, TypeError):
        pass

    try:
        circle2 = circles[0][1]
    except (IndexError, TypeError):
        pass

    return circle1, circle2


def compute_resized_dims(image, max_w, max_h):
        """
        Returns (width, height) for the given image such that it fits in the max
        resolution bounds passed in but maintains its original
        aspect ratio.
        """
        # Width / height
        ratio = float(image.shape[1]) / image.shape[0]

        if ratio > (float(max_w) / max_h):
            return max_w, round(max_w / ratio)

        return round(ratio * max_h), max_h


def preprocess_image(image, size_bound, enable_unsharp, unsharp_blur_type,
                     unsharp_blur_ksize, unsharp_blur_sigmaXY,
                     unsharp_add_weight, unsharp_gamma,
                     blur_type, blur_ksize, blur_sigmaXY):

    # Resize the image
    processed = cv2.resize(image,
                           compute_resized_dims(image, size_bound, size_bound))

    # Add unsharp mask
    if enable_unsharp:

        # Blur image to subtract from original
        blurred = _apply_blur(processed, unsharp_blur_type, unsharp_blur_ksize,
                              unsharp_blur_sigmaXY)

        # Apply the unsharp mask
        processed = cv2.addWeighted(processed, 1 + unsharp_add_weight,
                                    blurred, unsharp_add_weight - 1,
                                    unsharp_gamma)

    # Apply final blur
    processed = _apply_blur(processed, blur_type, blur_ksize, blur_sigmaXY)

    return processed


def scale_circles(circle1, circle2, original, resized):

    ratio = float(original.shape[0]) / float(resized.shape[0])

    if circle1 is not None:
        circle1 = tuple([int(round(ratio * i)) for i in circle1])

    if circle2 is not None:
        circle2 = tuple([int(round(ratio * i)) for i in circle2])

    return circle1, circle2


def _apply_blur(image, blur_type, ksize, sigmaXY):
    # Use gaussian blur
    if blur_type == 'g':
        ksize = (ksize, ksize)
        # Only have to pass in sigmaX param, as sigmaY will be set to
        # the same value if it is not provided
        blurred = cv2.GaussianBlur(image, ksize, sigmaXY)

    # Use median blur
    elif blur_type == 'm':
        blurred = cv2.medianBlur(image, ksize)

    else:
        print('Unknown blur type: {}'.format(blur_type),
              file=sys.stderr)
        sys.exit(-1)

    return blurred


def main():
    """
    params:
        image_list.txt          str
        image_dir               str
        size_bound              int
        enable_unsharp          1/0
        unsharp_blur_type       g/m   (gaussian/median)
        unsharp_blur_ksize      int   (same used for x/y)
        unsharp_blur_sigmaXY    int   (only for gaussian blur)
        unsharp_add_weight      float (alpha = 1 + unsharp_add_weight
                                       beta  = unsharp_add_weight - 1)
        unsharp_gamma           int
        blur_type               g/m   (gaussian/median)
        blur_ksize              int   (same used for x/y)
        blur_sigmaXY            int   (only for gaussian blur)
        dp                      int
        minDist                 int
        param1                  int
        param2                  int
        minRadius               int
        maxRadius               int
    """
    t = time.time()

    try:
        image_list                  = sys.argv[1]
        image_dir                   = sys.argv[2]
        size_bound                  = int(sys.argv[3])
        enable_unsharp              = sys.argv[4] == '1'
        unsharp_blur_type           = sys.argv[5]
        unsharp_blur_ksize          = int(sys.argv[6])
        unsharp_blur_sigmaXY        = int(sys.argv[7])
        unsharp_add_weight          = float(sys.argv[8])
        unsharp_gamma               = int(sys.argv[9])
        blur_type                   = sys.argv[10]
        blur_ksize                  = int(sys.argv[11])
        blur_sigmaXY                = int(sys.argv[12])
        dp                          = int(sys.argv[13])
        minDist                     = int(sys.argv[14])
        param1                      = int(sys.argv[15])
        param2                      = int(sys.argv[16])
        minRadius                   = int(sys.argv[17])
        maxRadius                   = int(sys.argv[18])

    except IndexError:
        print('Error: missing arguments', file=sys.stderr)
        return

    output_file = '_'.join(
        [str(i) for i in [
            size_bound,
            enable_unsharp,
            unsharp_blur_type,
            unsharp_blur_ksize,
            unsharp_blur_sigmaXY,
            unsharp_add_weight,
            unsharp_gamma,
            blur_type,
            blur_ksize,
            blur_sigmaXY,
            dp,
            minDist,
            param1,
            param2,
            minRadius,
            maxRadius
        ]
    ])
    output_file = 'output_run-' + output_file

    images = list()
    with open(image_list) as f:
        images = [l.strip() for l in f.readlines()]

    if len(images) == 0:
        print('Error: no images found', file=sys.stderr)
        return

    with open(output_file, 'w') as f:

        i = 0

        for imname in images:

            impath = os.path.join(image_dir, imname)
            image  = cv2.imread(impath, cv2.IMREAD_GRAYSCALE)
            if image is None:
                print('Error: {} could not be read'.format(impath),
                      file=sys.stderr)

            processed = preprocess_image(
                image,
                size_bound,
                enable_unsharp,
                unsharp_blur_type,
                unsharp_blur_ksize,
                unsharp_blur_sigmaXY,
                unsharp_add_weight,
                unsharp_gamma,
                blur_type,
                blur_ksize,
                blur_sigmaXY,
            )

            circle1, circle2 = compute_circles(
                processed,
                dp,
                minDist,
                param1,
                param2,
                minRadius,
                maxRadius
            )

            # DEBUG
            # cv2.circle(processed, tuple(circle1[:2]), circle1[2],
            #            (255, 255, 255), thickness=1, lineType=8)
            # cv2.circle(processed, tuple(circle2[:2]), circle2[2],
            #            (255, 255, 255), thickness=1, lineType=8)

            # Scale circles to fit on original image dimensions
            circle1, circle2 = scale_circles(circle1, circle2, image, processed)

            # DEBUG
            # print(tuple(circle1), tuple(circle2))
            # cv2.circle(image, tuple(circle1[:2]), circle1[2],
            #            (0, 255, 0), thickness=1, lineType=8)
            # cv2.circle(image, tuple(circle2[:2]), circle2[2],
            #            (0, 255, 0), thickness=1, lineType=8)

            # NC for 'Not classified'
            output = '|'.join([str(i) for i in [imname, 'NC', circle1, circle2]])
            f.write(output + '\n')

    print('Elapsed: ' + str(time.time() - t))

if __name__ == '__main__':
    main()
