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

import cv2

from compute_circle_from_three_points import compute_circle_from_three_points
import constants

class Image(object):
    """
    Class reprisenting an open image.
    """

    SOLAR = 0
    LUNAR = 1

    def __init__(self, path):

        self.path = path
        self.type = None
        self.solar_circle = None
        self.lunar_circle = None

        self.complete = False
        self.active_circle = None
        self.active_circle_coords = list()

        self.full_cv_img = cv2.imread(self.path)
        # OpenCV reverses width, height order we are used to
        height, width, _ = self.full_cv_img.shape
        self.full_dims = (width, height)

        self.resized_dims = self._compute_resized_dims()
        self.resized_cv_img = cv2.resize(self.full_cv_img, self.resized_dims)

    def __str__(self):
        """
        Used to generate string reprisentation that will be saved to output
        file.
        """
        return '|'.join([str(i) for i in (self.path, self.type,
                                          self.solar_circle,
                                          self.lunar_circle)])

    def activate_circle(self, circle):
        """
        Activates a particular circle. If a circle was in the process of being
        entered it will be overwritten.
        """
        if circle == self.SOLAR:
            self.solar_circle = None
        elif circle == self.LUNAR:
            self.lunar_circle = None
        else:
            msg = 'Invalid active_circle value: '.format(self.active_circle)
            raise ValueError(msg)

        self.active_circle = circle
        self.active_circle_coords = list()
        self.set_complete()

    def add_point(self, point):
        """
        Add point to active circle.
        """
        if self.active_circle is None or len(self.active_circle_coords) >= 3:
            print('Active circle not set. Click has no effect.')
            return
        self.active_circle_coords.append(point)

    def active_circle_complete(self):
        """
        Checks whether the active circle is fully defined.
        """
        return len(self.active_circle_coords) == 3

    def process_active_circle(self):
        """
        Takes the active_circle_coords and translates these points to
        a circle defined by its center and radius. Overlays this circle on
        resized_cv_img and scales them up and saves them in [solar|lunar]_circle
        depending on which is the current active circle.
        """
        if len(self.active_circle_coords) != 3:
            raise ValueError('active_circle not complete')

        # Circle scaled to the dimensions of the image shown with Qt
        scaled_circle = compute_circle_from_three_points(
            self.active_circle_coords)

        # Same scaled circle, but with interger values, as we are dealing with
        # pixel coordinates, which must be ints
        draw_circle = [round(i) for i in scaled_circle]

        # Scale up the circle for saving - this scaled version will line up
        # with the full resolution image
        ratio = float(self.full_dims[0]) / self.resized_dims[0]
        full_circle = tuple([round(ratio * i) for i in scaled_circle])

        if self.active_circle == self.SOLAR:
            self.solar_circle = full_circle
        elif self.active_circle == self.LUNAR:
            self.lunar_circle = full_circle
        else:
            msg = 'Invalid active_circle value: '.format(self.active_circle)
            raise ValueError(msg)

        # Draw the circle on our image
        cv2.circle(self.resized_cv_img, tuple(draw_circle[:2]), draw_circle[2],
                   (0, 255, 0), thickness=1, lineType=8)

        print('Scaled circle: {}'.format(scaled_circle))
        print('Full circle:   {}'.format(full_circle))

        self.active_circle = None
        self.active_circle_coords = list()
        self.set_complete()

    def reset(self):
        """
        Reset image state. Clears circles from resized_cv_img,
        [solar|lunar]_circle, type, deactivates active_circle and clears
        active_circle_coords.
        """
        self.active_circle = None
        self.active_circle_coords = list()
        self.type = None
        self.solar_circle = None
        self.lunar_circle = None
        self.resized_cv_img = cv2.resize(self.full_cv_img, self.resized_dims)

    def set_complete(self):
        """
        Sets the complete flag.
        """
        self.complete = self.type is not None and \
                        self.type != '' and \
                        self.solar_circle is not None and \
                        self.active_circle is None

    def _compute_resized_dims(self):
        """
        Returns (width, height) for the given image such that it fits in the max
        resolution bounds defined in constants.py but maintains its original
        aspect ratio.
        """
        max_w = constants.IMAGE_DISPLAY_W_MAX
        max_h = constants.IMAGE_DISPLAY_H_MAX
        ratio = float(self.full_dims[0]) / self.full_dims[1]

        if ratio > (max_w / max_h):
            return max_w, int(max_w / ratio)

        return int(ratio * max_h), max_h
