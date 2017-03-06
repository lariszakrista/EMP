**Image processing ground truth data collection app**

This is an application to aid in development of the image processing pipeline.
It allows users to iterate through the images in a directory, and mark images
as being of either a unobscured sun, a fully eclipsed sun, a partially eclipsed
sun, or sun in the "diamond ring" eclipse phase. Additionally, the solar and
[lunar] disks can be marked. This data is then exported to an output file.

Dependencies:
- python3
- PyQt5
- OpenCV 3 with python3 bindings


**To run:**

```bash
$ ./record_ground_truth [src_dir] [dest_file]
```

**Visualizing data that has been output**

You can use the `visualize.py` script to visualize the data you have recorded.

```bash
$ ./visualize output_file
```
