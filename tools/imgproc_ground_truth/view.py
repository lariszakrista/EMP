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

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import constants


class ControlLayout(QtWidgets.QBoxLayout):
    """
    Layout class containing user controls.
    """

    WIDTH = 200

    def __init__(self):
        super().__init__(self.TopToBottom)

        label = QtWidgets.QLabel()
        label.setText('Select picture type')

        self.type_dropdown = QtWidgets.QComboBox()
        self.type_dropdown.addItem(None)
        self.type_dropdown.addItems(constants.IMAGE_TYPES)

        self.solar_button = QtWidgets.QPushButton('Set solar perimeter')
        self.lunar_button = QtWidgets.QPushButton('Set lunar perimeter')

        self.save_button = QtWidgets.QPushButton('Save')
        self.save_button.setEnabled(False)

        self.reset_button = QtWidgets.QPushButton('Reset')

        self.skip_button = QtWidgets.QPushButton('Skip this image')


        widgets = [label, self.type_dropdown, self.solar_button,
                   self.lunar_button, self.save_button, self.reset_button,
                   self.skip_button]

        fixed = QtWidgets.QSizePolicy.Fixed
        for w in widgets:
            w.setSizePolicy(QtWidgets.QSizePolicy(fixed, fixed))
            w.setMinimumWidth(self.WIDTH)
            self.addWidget(w)

    def reset(self):
        """
        Reset controls to their original state.
        """
        self.type_dropdown.setCurrentIndex(0)
        self.solar_button.setEnabled(True)
        self.lunar_button.setEnabled(True)
        self.save_button.setEnabled(False)

    def width(self):
        return self.WIDTH


class ImageLabel(QtWidgets.QLabel):
    """
    QLabel subclass that will display images. Adds event handling for mouse
    clicks.
    """

    def __init__(self, parent_layout, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_layout = parent_layout

    def mousePressEvent(self, event):
        pos = event.pos().x(), event.pos().y()
        self.parent_layout.mouse_pressed.emit(pos)


class ImageLayout(QtWidgets.QBoxLayout):
    """
    Layout class responsible for displaying images.
    """

    # We make this signal part of ImageLayout, instead of part of the
    # ImageLabel instance, because the ImageLayout instace lives for the
    # life of the application, where the ImageLabel instances do not
    # Signal should be emitted with a tuple of two ints
    mouse_pressed = QtCore.pyqtSignal(tuple, name='mouse_pressed')

    def __init__(self):
        super().__init__(self.TopToBottom)
        self.widget = None

    def show_image(self, image):
        """
        Sets current image to image, where image is a numpy array - OpenCV's
        image format.
        """
        if self.widget is not None:
            # Effectively removes the widget from the layout
            self.widget.setParent(None)

        height, width, channel = image.shape
        bytes_per_line = width * channel

        if channel == 1:
            fmt = QtGui.QImage.Format_Mono
        elif channel == 3:
            # Unfortunatly, this results in blues and reds being swapped
            # as OpenCV uses BGR, not RGB and this is not supported by Qt.
            # We could do a conversion, but this would be slow and it is not
            # worth it
            fmt = QtGui.QImage.Format_RGB888
        else:
            raise ValueError('Invalid number of channels')

        qimage = QtGui.QImage(image.data, width, height, bytes_per_line, fmt)

        self.widget = QtWidgets.QWidget()
        pixmap = QtGui.QPixmap(qimage)
        label = ImageLabel(self, self.widget)
        label.setPixmap(pixmap)

        self.addWidget(self.widget)
        self.widget.setFixedSize(qimage.width(), qimage.height())
        self.widget.show()

    def height(self):
        return self.spacing() + self._get_widget_dim(width=False)

    def width(self):
        return self.spacing() + self._get_widget_dim(width=True)

    def _get_widget_dim(self, width):
        """
        Returns dimension of layout's main widget. Simply calling
        self.widget.[width|height]() is not effective here.
        """
        item = self.itemAt(0)
        if item is None:
            return 0
        if width:
            return item.widget().width()
        return item.widget().height()


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window.
    """

    def __init__(self):
        super().__init__()
        self.ctrl_layout = None
        self.image_layout = None
        self._create_main_layout()

    def _create_main_layout(self):
        """
        Constructs main window layout.
        """
        self.ctrl_layout = ControlLayout()
        self.image_layout = ImageLayout()

        layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
        layout.addLayout(self.ctrl_layout)
        layout.addLayout(self.image_layout)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
        self._resize()

    def _resize(self):
        """
        Resizes main window to fit image and control layouts.
        """
        self.resize(self.ctrl_layout.width() + self.image_layout.width(),
                    self.image_layout.height())
