# Totality Image Classification


## Dependencies:

- Python3
- Keras


## `logistic_reg.py`

### Required files

- Labeled data JSON file
  - Output file from `tools/label_images`
- Labels JSON file
  - JSON file containing one dictionary that maps each
    label that appears in the labeled data file to an integer
    id (0-(num_labels - 1)). This file can be created by running
    `create_labels_file.py` (see below).

### Arguments

- `--pred-type`
  - Optional. The prediction type to use. If `onehot` is used, a 1-hot vector prediction
    will be used. Default value is `onehot`. If any value other than `onehot` is
    specified, a single digit binary prediction will be used where 1 corresponds to
    totality, and 0 corresponds to non-totality. Basic tests have shown that 1-hot
    vector predictions tend to perform about 1% better than single digit ones. Maybe
    this is because they have twice as many weights...
- `--pred-thresh`
  - Optional. If specified, only predictions with confidence greater than this threshold
    will be accepted. Others will be thrown out.
- `labeled-data`
  - Optional. Path to labeled data json file, as produced by `run_vgg.py` or
    `tools/label_images/label_images.py`. Default `labeled_data.json`.
- `labels`
  - Optional. Path to file that associates a text label with a numeric >= 0.
    Default `labels.json`.


### To Run

```bash
$ # Assumes that labeled_data.json file has already been created and is in pwd
$
$ # Create labels file. labeled-data is input file, labels is output file
$ python3 create_labels_file.py --labeled-data=labeled_data.json --labels=labels.json
$
$ # Train/evaluate classifier
$ python3 logistic_reg.py [args]
```

### Current Model Description

The currently best performing model is a single layer logistic regression model
that outputs a one-hot vector reprisenting `[totality_confidence, non_totality_confidence]`.
The input for this model is a feature vector with an index corresponding to every label
in the set of all labels (this is the set of every label that appears in the labeled data JSON file).
Each value in this feature vector corresponds to Google Cloud Vision's confidence for that
particular label.

This model is trained/tested on 10 k-fold cross validation sets. For each fold, a new model
is instanciated and trained on the given training set for 10 epochs. The weights and
biases for this model are then saved along with its performance metrics on the given test set. 
After running through all folds, the model reports "Average k-fold test case performance," an 
average of the test metrics reported from each of the k test sets. 

After running through the k training/testing iterations, we average the weights and biases
from each of these iterations. These averaged weights are used to report the 10 most significant 
weights. These are obtained by comparing the weights by sum of absolute values (as each weight is 
actually a vector of two numbers). Finally, we instantiate a new model and set its weights/biases
to these averaged values. We then test this model on all the images we have. These results are
reported as "Results for averaged model on all images."

**Latest Metrics:**

Average k-fold test case performance:
- Accuracy: 0.818659
- False positive ratio: 0.104582
- Acceptance ratio: 1.0

Results for averaged model on all images:
- Accuracy: 0.8322010869565217
- False positive ratio: 0.09782608695652174
- Acceptance ratio: 1.0

10 most significant weights (these generally vary a bit run to run, but the top 3 or 4 are pretty consistant):
- corona [ 0.27336371 -0.24147423]
- crescent [-0.2130824   0.27699929]
- eye [ 0.23350556 -0.17512074]
- sunlight [-0.13484731  0.2705484 ]
- monochrome photography [ 0.17697689 -0.15571758]
- geological phenomenon [-0.08167853  0.24848738]
- lighting [-0.06975647  0.2528134 ]
- shape [ 0.23209687 -0.08375302]
- sunrise [-0.12619147  0.18861598]
- font [-0.06696153  0.24628183]


## `run_vgg.py`

### Required Files

- Labeled data JSON file
  - A JSON file with a top level dictionary where the keys are Google Cloud Storage
    URLs. Each key in this dictionary must have another dictionary associated with
    it. These dictionaries must have a `'classification'` key that points to the
    image classification, either `'TOTALITY'` or some other string, which will be treated
    as non-totality. Note: the labeled data json file described above will work here.
- Images
  - All images referenced the labeled data JSON file
    must be saved in the same directory with their filenames
    being the same as the basename of the files referenced in
    the labeled data JSON file.

### Arguments

- `--download`
  - Optional flag. If specified, images will be downloaded from Google Cloud Storage
    using gsutil.
- `--img-dir`
  - Optional. Directory where images live / are to be downloaded to. Default `./img/`.
- `--label-file`
  - Optional. Labeled data JSON file described above. Default `labled_data.json`
- `--output-file`
  - Optional. File to write predicted labels / confidences to. Default `vgg_output_labels.json`.

### To Run

```bash
$ mkdir img
$
$ python3 run_vgg.py --img-dir=img --download --label-file=labeled_data.json --output-file=vgg16-squash.json
```

### Current Model Description

The current best results are obtained by running our images through VGG16 pre-trained on imagenet.
The input image shape is (224, 224, 3). This is obtained by resizing images to this size, squashing
non-square images, i.e. circles can become ellipses.

**Latest metrics, obtained by running the output of `run_vgg.py` through `logistic_reg.py`**

Results for averaged model on all images:
- Accuracy: 0.818497 -- ***nearly as good as the results obtained using Google Cloud Vision!***
- False positive rate: 0.132127
- Acceptance ratio: 1.0

10 most significant weights:
- birdhouse [ 0.3512364  -0.27704924]
- torch [-0.24949209  0.30951935]
- candle [-0.20805046  0.34352452]
- volcano [-0.17042127  0.3416324 ]
- iPod [ 0.332791   -0.17752783]
- spotlight [ 0.29485711  0.20454247]
- matchstick [-0.19356573  0.28479972]
- ashcan [ 0.26150069 -0.1923448 ]
- hook [-0.11934551  0.32199374]
- space\_shuttle [-0.19966826  0.23903966]

