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

class EclipseImage(object):

    def __init__(self):
        self.type           = None
        self.solar_circle   = None
        self.lunar_circle   = None

    def __str__(self):
        template = '<{0} type: {1} solar_circle: {2} lunar_circle: {3}>'
        return template.format(self.__class__.__name__, self.type,
                               self.solar_circle, self.lunar_circle)
