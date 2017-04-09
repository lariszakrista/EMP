#ifndef _IMGPROC_DEFS_H
#define _IMGPROC_DEFS_H

#define METADATA_SEP "|"
#define ESC_KEY      1048603
#define HD_MAX_W                            1920
#define HD_MAX_H                            1080
#define METADATA_FILE_NAME                  "metadata.txt"
#define MIN_SUN_RADIUS 50

enum ImgprocMode {
    BATCH = 0,
    WINDOW,
};

#endif
