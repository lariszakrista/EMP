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

from itertools import product
import sys


IMAGE_LIST                       = 'images.txt'
IMAGE_DIR                        = 'images'
SIZE_VALS                        = (1200, 1800)
ENABLE_UNSHARP_VALS              = (1, 0)
UNSHARP_BLUR_TYPE_VALS           = ('g', 'm')
UNSHARP_BLUR_KSIZE_VALS          = (3, 9, 15, 21)
UNSHARP_BLUR_SIGMAXY_VALS        = (0, 5, 10, 20)
UNSHARP_ADD_WEIGHT_VALS          = (0.4, 0.8, 2)
UNSHARP_GAMMA_VALS               = (0, )
BLUR_TYPE_VALS                   = ('g', 'm')
BLUR_KSIZE_VALS                  = (3, 9, 15, 21)
BLUR_SIGMAXY_VALS                = (0, 5, 10, 20)
DP_VALS                          = (1, 2, 4, 8)
MINDIST_VALS                     = (1, )
PARAM1_VALS                      = (7, 15, 30, 60)
PARAM2_VALS                      = (7, 15, 30, 60)
MINRADIUS_VALS                   = (lambda s: 0, lambda s: s/32.0,
                                    lambda s: s/16.0, lambda s: s/8.0)
MAXRADIUS_VALS                   = (lambda s: 0, lambda s: s)


def print_program_invocation(size, blur_type, blur_ksize, dp, minDist, param1,
                             param2, minRadius, maxRadius, enable_unsharp,
                             unsharp_blur_type='g', unsharp_blur_ksize=0,
                             unsharp_add_weight=0, unsharp_gamma=0,
                             unsharp_blur_sigmaXY=0, blur_sigmaXY=0):
    ordered_params = (
        IMAGE_LIST,
        IMAGE_DIR,
        size,
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
        int(round(minRadius(size))),
        int(round(maxRadius(size))),
    )

    params = ' '.join([str(i) for i in ordered_params])
    print('python3 detect_circles.py {0}'.format(params))


def loop_through_unsharp_params_and_generate_calls(eip, blur_sigmaXY=0):
    i = 0

    (size, blur_type, blur_ksize, dp,
     minDist, param1, param2, minRadius, maxRadius) = eip

    for enable_unsharp in ENABLE_UNSHARP_VALS:

        if enable_unsharp == 1:
            # This is a generator so we have to recreate it every time its
            # used
            unsharp_common_params = product(UNSHARP_BLUR_TYPE_VALS,
                                            UNSHARP_BLUR_KSIZE_VALS,
                                            UNSHARP_ADD_WEIGHT_VALS,
                                            UNSHARP_GAMMA_VALS)

            for ucp in unsharp_common_params:

                (unsharp_blur_type, unsharp_blur_ksize,
                 unsharp_add_weight, unsharp_gamma) = ucp

                if unsharp_blur_type == 'g':
                    for unsharp_blur_sigmaXY in UNSHARP_BLUR_SIGMAXY_VALS:
                        i += 1
                        print_program_invocation(
                            size, blur_type, blur_ksize, dp, minDist, param1,
                            param2, minRadius, maxRadius,
                            enable_unsharp, unsharp_blur_type=unsharp_blur_type,
                            unsharp_blur_ksize=unsharp_blur_ksize,
                            unsharp_add_weight=unsharp_add_weight,
                            unsharp_gamma=unsharp_gamma,
                            unsharp_blur_sigmaXY=unsharp_blur_sigmaXY,
                            blur_sigmaXY=blur_sigmaXY)
                else:
                    i += 1
                    print_program_invocation(
                        size, blur_type, blur_ksize, dp, minDist, param1,
                        param2, minRadius, maxRadius,
                        enable_unsharp, unsharp_blur_type=unsharp_blur_type,
                        unsharp_blur_ksize=unsharp_blur_ksize,
                        unsharp_add_weight=unsharp_add_weight,
                        unsharp_gamma=unsharp_gamma,
                        blur_sigmaXY=blur_sigmaXY)
        else:
            i += 1
            print_program_invocation(
                size, blur_type, blur_ksize, dp, minDist, param1,
                param2, minRadius, maxRadius,
                enable_unsharp, blur_sigmaXY=blur_sigmaXY)

    return i


def main():
    i = 0

    every_iter_params = product(SIZE_VALS, BLUR_TYPE_VALS, BLUR_KSIZE_VALS,
                                DP_VALS, MINDIST_VALS, PARAM1_VALS,
                                PARAM2_VALS, MINRADIUS_VALS, MAXRADIUS_VALS)

    for eip in every_iter_params:

        blur_type = eip[1]

        if blur_type == 'g':
             for blur_sigmaXY in BLUR_SIGMAXY_VALS:
                 i += loop_through_unsharp_params_and_generate_calls(
                    eip, blur_sigmaXY)
        else:
            i += loop_through_unsharp_params_and_generate_calls(eip)

    print(str(i) + ' iterations', file=sys.stderr)


if __name__ == '__main__':
    main()
