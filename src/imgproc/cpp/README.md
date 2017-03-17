**Under development image processing code**

*Requires OpenCV 3*

**Parameters:** 
- images_file: text file of image filenames with no path prefix, one per line 
- input_dir: location of images listed in images_file. 

**Modes:**
- `batch` mode: this will loop through all the images without stopping, 
  and will save images with detected circles overlayed into output_dir,
  along with a file called metadata.txt containing metadata collected during
  processing.
- `window` mode: this will loop through all the images, stopping after each one.
  After each image, numerous windows will be displayed including one of the original 
  image with overlayed circle, and other intermediate images that were created during 
  processing. Press any key to proceed to the next image. If you wish
  to terminate the program before you've gotten to the end of the program,
  press the ESC key.

To build/run:

```bash
$ # Build
$ make
$
$ # Run
$ ./imgproc
Usage:
	$ ./imgproc images_file input_dir mode [output_dir]

Modes:	[batch, window]
	output_dir required when run in batch mode
```
