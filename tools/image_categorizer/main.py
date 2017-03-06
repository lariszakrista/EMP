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

from PyQt5.QtWidgets import QApplication

from image_categorizer import get_images, ImageCategorizer

if __name__ == '__main__':
    try:
        given_dir = sys.argv[1] if os.path.isdir(sys.argv[1]) else None
    except IndexError:
        given_dir = None

    app = QApplication([''])
    images = get_images(given_dir)
    categorizor = ImageCategorizer(images, app)
    sys.exit(app.exec_())
