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

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class InvalidKeyError(Exception):
    pass


def get_images(given_dir):
    w = QtWidgets.QWidget()
    msg = 'Select a directory'
    img_dir = QtWidgets.QFileDialog.getExistingDirectory(w, msg, given_dir)
    w.hide()

    files = list()
    for f in os.listdir(img_dir):
        fpath = os.path.join(img_dir, f)
        if os.path.isfile(fpath):
            files.append(fpath)

    return files


class ImageCategorizer(QtWidgets.QMainWindow):

    IMG_W = 600

    def __init__(self, images, app):
        super().__init__()

        self.app = app
        self.displayed_image = None
        self.images = images
        self.previous = None

        timer = QtCore.QTimer(self.app)
        timer.setSingleShot(True)
        timer.timeout.connect(self._display_first_image)
        timer.start(0)

    def keyPressEvent(self, event):
        if event.key() == ord('U'):
            self._undo_previous()
            return

        try:
            self._move_image(self.displayed_image, event.key())
        except InvalidKeyError:
            print('Invalid key: {}. [a-z] accepted.'.format(event.text()))
            return

        try:
            image = self.images.pop()
        except IndexError:
            self.app.quit()
            return

        try:
            self._display_image(image)
        except ZeroDivisionError:
            pass

    def _display_first_image(self):
        print("Called")
        while True:
            try:
                image = self.images.pop()
                self._display_image(image)
                self.show()
                break
            except IndexError:
                self.app.quit()
                return
            except ZeroDivisionError:
                pass

    def _display_image(self, image_path):
        image = QtGui.QImage(image_path)
        try:
            image = image.scaled(self.IMG_W,
                                 self.IMG_W * image.height() / image.width())
        except ZeroDivisionError as e:
            os.remove(image_path)
            self.displayed_image = None
            raise e

        widget = QtWidgets.QWidget()
        pixmap = QtGui.QPixmap(image)
        label = QtWidgets.QLabel(widget)
        label.setPixmap(pixmap)

        widget.resize(image.width(), image.height())
        self.resize(image.width(), image.height())
        self.setWindowTitle(image_path)
        self.setCentralWidget(widget)

        self.displayed_image = image_path
        print('Displaying {}'.format(self.displayed_image))

        widget.show()

    def _undo_previous(self):
        if self.previous is None:
            print('Could not undo previous move. No move found')
            return
        dest, src = self.previous
        os.rename(src, dest)
        self.previous = None

    def _move_image(self, image_path, key_pressed):
        if image_path is None:
            return

        if key_pressed == QtCore.Qt.Key_Space:
            print('Image skipped and not moved.')
            return

        if key_pressed < ord('A') or key_pressed > ord('Z'):
            raise InvalidKeyError

        fdir, fname = os.path.split(image_path)
        target_dir = os.path.join(fdir, chr(key_pressed))

        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        dest = os.path.join(target_dir, fname)
        os.rename(image_path, dest)

        self.previous = (image_path, dest)
