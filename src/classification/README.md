# Totality Image Classification

### Dependencies:

- Python3
- Keras

### Required files

- `labeled_data.json`
  - Output file from `tools/label_images`
- `labels.json`
  - JSON file containing one dictionary that maps each
    label in `labeled_data.json` to an integer id (0-(num_labels - 1)).
    This file can be created by running `create_labels_file.py`. This
    script assumes there is a `labeled_data.json` file in the directory
    from which it is run.

### Arguments

- `--pred-type`
  - The prediction type to use. If `onehot` is used, a 1-hot vector prediction
    will be used. Default value is `onehot`. If any value other than `onehot` is
    specified, a single digit binary prediction will be used where 1 corresponds to 
    totality, and 0 corresponds to non-totality. Basic tests have shown that 1-hot 
    vector predictions tend to perform about 1% better than single digit ones. Maybe
    this is because they have twice as many weights...

### To Run

```bash
$ # Assumes that labeled_data.json file has already been created and is in pwd
$
$ # Create labels.json
$ python3 create_labels_file.py
$
$ # Train/evaluate classifier
$ python3 logistic_reg.py
```

## Current Model

The currently best performing model is a single layer logistic regression model
that outputs a one-hot vector reprisenting `[totality_confidence, non_totality_confidence]`.
The input for this model is a feature vector with an index corresponding to every label
in the set of all labels (this is the set of every label that appears in `labeled_data.json`).
Each value in this feature vector corresponds to Google Cloud Vision's confidence for that
particular label.

This model is trained/tested on 10 k-fold cross validation sets. For each fold, a new model
is instanciated and trained on the given training set for 10 epochs. The weights and
biases for this model are then saved along with its performance metrics on the given test set. 
After running through all folds, the model reports "Overall Performance," an average of the 
test metrics reported from each of the k test sets. Additionally, the 10 most significant 
weights are reported. These are computed by averaging the weights from the k trained models 
and comparing them by sum of absolute values (as each weight is actually a vector of two numbers).

**Latest Metrics:**

Overall performance:
- Accuracy: 0.818659
- False positive ratio: 0.104582
- Acceptance ratio: 1.0

10 Most Significant Weights (these generally vary a bit run to run, but the top 3 or 4 are pretty consistant):
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

