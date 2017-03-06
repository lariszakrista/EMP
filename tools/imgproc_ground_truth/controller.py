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

from collections import deque
import os
import sys

from PyQt5 import QtCore
from PyQt5 import QtWidgets

import constants
from image import Image
from view import MainWindow

class Controller(QtCore.QObject):
    """
    Application controller. Coordinates between view objects and Image
    state/model object.
    """

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.src_dir = None
        self.dest_file = None
        self.images = None
        self.current_image = None
        self.main_window = None

        # These methods will launch their corresponding state. These states
        # Determine the high level application flow.
        self._state_launchers = deque([
            self._choose_src_dir_and_dest_file,
            self._create_main_window,
            self.app.quit,
        ])

    def run(self):
        """
        Starts the application.
        """
        self._next_state()

    def show_next_image(self, write=False):
        """
        Displays the next image in images. If there is an image open and write
        is True, that image's data will be written to dest_file.
        """
        if write and self.current_image is not None:
            self._write_data(str(self.current_image))

        try:
            impath = self.images.pop()
        except IndexError:
            self._next_state()
            return

        self.current_image = Image(impath)
        self.main_window.image_layout.show_image(self.current_image.resized_cv_img)
        self.main_window.ctrl_layout.reset()
        self.main_window._resize()

    def _choose_src_dir_and_dest_file(self):
        """
        Application setup. Gets src dir and dest file, if not specified from
        command line or command line args were invalid.
        """
        if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
            self.src_dir = sys.argv[1]
        else:
            self.src_dir = QtWidgets.QFileDialog.getExistingDirectory(
                caption='Select source directory')

        if len(sys.argv) > 2 and \
           (os.path.dirname(sys.argv[2]) == '' or
            os.path.isdir(os.path.dirname(sys.argv[2]))):
            self.dest_file = sys.argv[2]
        else:
            self.dest_file = QtWidgets.QFileDialog.getSaveFileName(
                caption='Select save file')[0]

        try:
            # Create output file
            open(self.dest_file, 'w').close()
            self.images = self._get_image_files(self.src_dir)
        except (IOError, OSError):
            self.app.quit()
            return

        self._next_state()

    def _connect_signals_and_slots(self):
        """
        Connects view and model with signals and slots.
        """
        # Save line length
        ctrl = self.main_window.ctrl_layout
        img = self.main_window.image_layout

        # Wire up skip image button
        ctrl.skip_button.clicked.connect(self.show_next_image)

        # Wire up image type dropdown
        ctrl.type_dropdown.currentIndexChanged[str].connect(
            self._set_image_type)

        # Wire up solar perimeter button
        ctrl.solar_button.clicked.connect(
            lambda _: self._set_image_circle(Image.SOLAR))

        # Wire up lunar perimeter button
        ctrl.lunar_button.clicked.connect(
            lambda _: self._set_image_circle(Image.LUNAR))

        # Wire up reset button
        ctrl.reset_button.clicked.connect(self._reset)

        # Wire up save button
        ctrl.save_button.clicked.connect(
            lambda _: self.show_next_image(write=True))

        # Handle click events on the displayed image
        img.mouse_pressed.connect(self._record_mouse_press)

    def _create_main_window(self):
        """
        Creates the main window initiating the main application state.
        """
        self.main_window = MainWindow()
        self._connect_signals_and_slots()
        self.show_next_image()
        self.main_window.show()

    def _disable_circle_buttons(self):
        """
        Disables [solar|lunar]_circle buttons if their corresponding circles
        have been defined.
        """
        if self.current_image.solar_circle is not None:
            self.main_window.ctrl_layout.solar_button.setEnabled(False)
        if self.current_image.lunar_circle is not None:
            self.main_window.ctrl_layout.lunar_button.setEnabled(False)

    def _enable_disable_save(self):
        """
        Enables/disables the save button depending on whether or not the
        current_image's complete flag is set.
        """
        self.main_window.ctrl_layout.save_button.setEnabled(
            self.current_image.complete)

    def _next_state(self):
        """
        Launches the next application state.
        """
        state = self._state_launchers.popleft()
        timer = QtCore.QTimer(self.app)
        timer.setSingleShot(True)
        timer.timeout.connect(state)
        timer.start(0)

    def _record_mouse_press(self, point):
        """
        Adds a point clicked by the user to current_image. Updates view
        accordingly.
        """
        self.current_image.add_point(point)

        # If the active circle is fully defined
        if self.current_image.active_circle_complete():

            # Compute circle center/radius, visualize it on
            # current_image.resized_cv_img
            self.current_image.process_active_circle()

            # Update the displayed image to have the newly added circle overlay
            self.main_window.image_layout.show_image(
                self.current_image.resized_cv_img)

        # Disable circle buttons, enable/disable save button as necessary
        self._disable_circle_buttons()
        self._enable_disable_save()

    def _reset(self):
        """
        Reset state for current image. Resets the Image object and UI.
        """
        self.main_window.ctrl_layout.reset()
        self.current_image.reset()
        self.main_window.image_layout.show_image(self.current_image.resized_cv_img)

    def _set_image_circle(self, circle):
        """
        Activates the circle chosen by the user.
        """
        self.current_image.activate_circle(circle)
        self._enable_disable_save()

    def _set_image_type(self, img_type):
        """
        Updates the Image.type flag based on user dropdown input.
        """
        self.current_image.type = img_type
        self.current_image.set_complete()
        self._enable_disable_save()

    def _write_data(self, data):
        """
        Write data + '\n' to dest_file
        """
        with open(self.dest_file, 'a') as f:
            f.write(data + '\n')

    @staticmethod
    def _get_image_files(directory):
        """
        Returns a list of image files (defined as files ending with extensions in
        constants.ALLOWED_IMAGE_FORMATS) in directory.
        """
        images = list()
        for f in os.listdir(directory):
            fname = f.lower()
            for ext in constants.ALLOWED_IMAGE_FORMATS:
                if fname.endswith('.' + ext):
                    images.append(os.path.join(directory, f))
        return images
