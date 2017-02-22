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


def compute_circle_from_three_points(points):
    '''
    Given a list of three points, each of which are 2-tuples, this
    function computes the circle that passes through all three points.
    If the three points do not lie on a circle, a ZeroDivisionError will
    be raised. Return value is a 3-tuple of the form
    (center_x, center_y, radius).

    The computation is based on the following:

        - Three unique points A, B, C on a circle define a triangle ABC
        - The perpendicular bisectors of the lines AB and BC intersect at the
          center of the circle

    In variable names below:
        m_[...] refers to the slope of [...]
        b_[...] refers to the y-intercept of [...]
    '''
    if len(points) != 3:
        raise ValueError('Must pass in 3 points')

    if _valid_b_point(points[1], points[0], points[2]):
        A_idx = 0
    elif _valid_b_point(points[2], points[1], points[0]):
        A_idx = 1
    else:
        A_idx = 2

    A = points[A_idx % 3]
    B = points[(A_idx + 1) % 3]
    C = points[(A_idx + 2) % 3]

    # AB
    dx, dy          = A[0] - B[0], A[1] - B[1];
    midpoint_AB     = A[0] - (dx / 2), A[1] - (dy / 2)
    m_AB            = dy / dx
    m_bisect_AB     = -1.0 / m_AB
    b_bisect_AB     = midpoint_AB[1] - (m_bisect_AB * midpoint_AB[0])

    # BC
    dx, dy          = B[0] - C[0], B[1] - C[1];
    midpoint_BC     = B[0] - (dx / 2), B[1] - (dy / 2)
    m_BC            = dy / dx
    m_bisect_BC     = -1.0 / m_BC
    b_bisect_BC     = midpoint_BC[1] - (m_bisect_BC * midpoint_BC[0])

    # Compute center_x, center_y, circle_radius
    cx              = (b_bisect_AB - b_bisect_BC) / (m_bisect_BC - m_bisect_AB)
    cy              = (m_bisect_AB * cx) + b_bisect_AB
    cr              = math.sqrt(math.pow(cx - A[0], 2) + math.pow(cy - A[1], 2))

    return cx, cy, cr


def _valid_b_point(B, A, C):

    return B[0] != A[0] and B[1] != A[1] and \
           B[0] != C[0] and B[1] != C[1]
