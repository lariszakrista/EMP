**Circle detection parameter grid search**

The `detect_circles.py` performs a run on one set of parameters. We then
generate many parameter combinations and run them in parallel. *This program
assumes that you will have an `images.txt` file in the directory in which it is
run with a list of image files, and that these image files will be located in
a directory called `images` contained in the directory in which the script is
run.*

To run the grid search:

```bash
$ # Create the parameter configurations
$ python3 generate_runs.py > runs.txt
$
$ # Randomize
$ python -c "import random; lines = open('runs.txt').readlines(); random.shuffle(lines); open('runs-shuffled.txt', 'w').writelines(lines)"
$
$ # Create scripts files for xargs
$ python3 generate_script_files.py
$
$ # Run the grid search - this will generate stdout/stderr files from each run
$ # called script_xxxxxx.output and will create files containing the actual
$ # circle detection output called output_run-{params}. These
$ # output_run-{params} files are what should be run through the
$ # compute_loss/compute_imgproc_loss.py file against a ground
$ # truth file, like gs://eclipse_image_ground_truth_dataset in the
$ # northamericaneclipseimages Google Cloud project
$ ./run_xargs_cmd
```

This is intended to be run on a GCE instance (preferable multiple). The
`setup` script can be used to install Opencv 3 for python3 on that machine.
To run it:

```bash
$ sudo ./setup
```

Using the `compute_loss/compute_imgproc_loss.py` file to compute the loss
between an output file from `detect_circles.py` to a ground truth file like that
mentioned above:

```bash
$ cd compute_loss
$ python3 compute_imgproc_loss.py <ground_truth_file> <file_to_score>
```
