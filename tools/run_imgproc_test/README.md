This tool will run the image processor and summarize the results in an HTML file. This script 
will take care of downloading the images from Google Cloud Storage (if the `download` flag is set), 
and building the image processor. This tool assumes access to the `northamericaneclipseimages` 
Google Cloud Project.

Requirements:

- Python3
- jinja2 for Python3 (`pip3 install Jinja2`)
- gsutil
- Google Chrome

To run the tool:

```bash
$ ./test $DIR $GCS_BUCKET [download] [$PIPELINE_FLAGS]
$
$ # $PIPELINE_FLAGS should be of the form "--flag1=value --flag2=othervalue"
```

- `$DIR` is the directory to use for image/data storage. The following will be saved into `DIR`:
   - ***If `download` flag set***: A clone of the `$GCS_BUCKET`
     - A directory called `output` that will contain:
       - All the processed images `$GCS_BUCKET`
       - A metadata file that will contain the processed image names along with output information from the image processor
       - An HTML file that includes summarizes the image processor output info.
- `$GCS_BUCKET` is the Google Cloud Storage bucket holding the images to process. All the images in this bucket will
be processed
- `$PIPELINE_FLAGS` is a single argument containing the flags that should be passed to the image processor pipeline

The output HTML file will be automatically uploaded to Google Cloud Storage. The URL to access this page 
will be printed to the console.
