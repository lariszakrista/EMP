Given a directory of images, this application will cycle through the images,
displaying them. When an image is displayed, it can be left as-is by pressing
the space bar. Otherwise, letters a-z (excluding u, see below) can be pressed
to place the image in a subdirectory named according to the letter key pressed.

Reserved key u:
Pressing the u key undoes the previous file move. This can only be used to go
back one file move. If there is no previous file move, pressing u has no effect.


Requires python3 and PyQt5. To install PyQt5:

```bash
$ apt-get install pyqt5-dev
```

To run the application:

```bash
$ python3 main.py [directory]
```
