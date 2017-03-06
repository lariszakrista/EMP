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

import math
import os
import sys

from eclipse_image import EclipseImage


IMAGE_PATH_IDX      = 0
IMAGE_TYPE_IDX      = 1
SOLAR_CIRCLE_IDX    = 2
LUNAR_CIRCLE_IDX    = 3

EXTRA_OR_MISSING_CIRCLE_COST = 1000


def compute_imgproc_loss(exp_data, act_data):
    output_template = 'solar_circle: <exp: {0} act: {1}> lunar_circle: ' + \
                      '<exp: {2} act: {3}> => loss {4}'

    min_loss     = float('inf')
    max_loss     = 0
    total_loss   = 0
    samples      = 0
    loss_by_type = dict()

    for key in exp_data:

        if key not in act_data or key not in exp_data:
            print('key not found: {0}'.format(key))
            continue

        single_loss = _compute_single_loss(exp_data[key], act_data[key])
        total_loss += single_loss
        min_loss    = min(min_loss, single_loss)
        max_loss    = max(max_loss, single_loss)
        samples    += 1

        # If this is the first instance of a particular type
        if exp_data[key].type not in loss_by_type:
            loss_by_type[exp_data[key].type] = [0, 0]

        # Accumulated loss by type
        loss_by_type[exp_data[key].type][0] += single_loss

        # Number of instances by type
        loss_by_type[exp_data[key].type][1] += 1

        print(output_template.format(exp_data[key].solar_circle,
                                     act_data[key].solar_circle,
                                     exp_data[key].lunar_circle,
                                     act_data[key].lunar_circle,
                                     single_loss))

    avg_loss = float(total_loss) / float(samples)

    print('Min loss:   {0}'.format(min_loss))
    print('Max loss:   {0}'.format(max_loss))
    print('Avg loss:   {0}'.format(avg_loss))
    print('Total loss: {0}'.format(total_loss))

    for key in loss_by_type:
        avg_loss_for_type = float(loss_by_type[key][0]) / loss_by_type[key][1]
        print('Avg loss for {0} images: {1}'.format(key, avg_loss_for_type))


def read_eclipse_data_file(fpath):
    data = dict()

    with open(fpath) as f:
        lines = f.readlines()

    for line in lines:
        fields              = line.strip().split('|')
        img                 = EclipseImage()
        img.type            = fields[IMAGE_TYPE_IDX]
        img.solar_circle    = _parse_circle_str(fields[SOLAR_CIRCLE_IDX])
        img.lunar_circle    = _parse_circle_str(fields[LUNAR_CIRCLE_IDX])

        data[fields[IMAGE_PATH_IDX]] = img

    return data


def _compute_single_loss(exp_img, act_img):

    s_loss  = _compute_circle_loss(exp_img.solar_circle, act_img.solar_circle)
    l_loss  = _compute_circle_loss(exp_img.lunar_circle, act_img.lunar_circle)

    return s_loss + l_loss


def _compute_circle_loss(circle1, circle2):

    if (circle1 is None and circle2 is not None) or \
       (circle1 is not None and circle2 is None):
       return EXTRA_OR_MISSING_CIRCLE_COST

    if circle1 is None and circle2 is None:
        return 0

    # Distance between circles
    distance = _euclidian_distance(circle1, circle2)

    # Difference in diameters
    size_diff = 2 * abs(circle1[2] - circle2[2])

    return (distance ** 2) + (size_diff ** 2)


def _euclidian_distance(circle1, circle2):
    dx = circle1[0] - circle2[0]
    dy = circle1[1] - circle2[1]
    return math.sqrt((dx ** 2) + (dy ** 2))


def _parse_circle_str(data):
    if data == 'None':
        return None
    return tuple([int(i) for i in data.strip('()').split(', ')])


def main():
    try:
        ground_truth_file   = sys.argv[1]
        file_to_score       = sys.argv[2]
    except IndexError:
        print('Must pass in ground_truth_file file_to_score image_dir as ' +\
              'command line args')
        return

    ground_truth    = read_eclipse_data_file(ground_truth_file)
    computed_data   = read_eclipse_data_file(file_to_score)

    compute_imgproc_loss(ground_truth, computed_data)


if __name__ == '__main__':
    main()
