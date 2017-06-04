**Under development image processing code**

*Requires OpenCV 3 and [GFlags](https://github.com/gflags/gflags)*

**Parameters:** 
- images_file: text file of image filenames with no path prefix, one per line 
- mode: batch or window (see below).
- output_dir: directory to save image processed image and metadata files 
- hough transform parameters
  - hough_dp (double)
  - hough_param1 (double)
  - hough_param2 (double)
  - hough_min_dist (double)
  - hough_min_radius (int)
  - hough_max_radius (int)

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
$ # Example usage
$ ./pipeline --images_file=/path/to.file --mode=$MODE --output_dir=/path/to/dir --hough_dp=2.0
```
