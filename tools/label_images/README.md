# Label Images

This tool uses the Google Cloud Vision API to label images and save the results to a json file.
The input for this tool is a file of images to label, formatted as follows:

```
source_uri_1 classification_1
...
source_uri_n classification_n
```

- `source_uri` can be either a Google Cloud Storage path (`gs://bucket/file`) or a web URL.
  *Note: if a GCS path is used, the file must have the public-read acl set*

- `classification` is any string, e.g. TOTALITY, PARTIAL\_ECLIPSE, etc.

The tool will output a json file called `labeled_data.json` structured as follows:

```
{
    "<source_uri_1>": {
        "labels": [
            ["<label_1>", <label_1_score>],
            // ...
            ["<label_n>", <label_n_score>],
        ],
        "classification": "<classification_1>",
    },
    // ...
}
```

### Dependencies

- Python3
- Google Cloud Vision Python Client Library (`$ pip3 install --upgrade google-cloud-vision`)

### Setup

In order to use this tool, you will need to create a file in this directory called `keys.py`
with a module level variable called `service_account_file` which the path to a json Google Cloud 
service account key file.

### Run the tool

```bash
$ python3 label_images.py --uri_file=<path/to/uri/file>
```

