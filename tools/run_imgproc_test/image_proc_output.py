import subprocess
from jinja2 import Environment, Template
import time
import os
import sys

METADATA_FILE = "metadata.txt"
OUTPUT_FILE = "output.html"

HTML = """
<script defer src="https://code.getmdl.io/1.2.1/material.min.js"></script>

<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:regular,bold,italic,thin,light,bolditalic,black,medium&amp;lang=en">
<link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
<link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.indigo-pink.min.css">

<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
	<meta charset="utf-8">

    <title>{{ title }}</title>

    <style>
		.content-list {
			width: calc(100% - 50px);
		}
		.mdl-layout__drawer-button .material-icons {
			margin-top: 12px;
		}
		.mdl-data-table {
			margin-left: 10px;
			width: calc(100% - 200px);
		}
		img {
			max-width: 300px;
			max-height: 300px;
		}
	</style>
</head>
<body>

    <div class="mdl-layout mdl-js-layout mdl-layout--fixed-header">
		<header class="mdl-layout__header">
			<div class="mdl-layout__header-row">
				<!-- Title -->
				<span class="mdl-layout-title">{{ title }}</span>
				<!-- Spacer to align links on the right -->
				<div class="mdl-layout-spacer"></div>

			</div>
		</header>
		
		<main class="drawer-tab mdl-layout__content">
			<div class="page-content">

                <h3 id="revision">Git Revision</h3>
                    <p>{{ gitrev }}</p>

		<h3> Test Timestamp:</h3>
			<p>{{ date }}</p>

                <h3>Output Table</h3>

                <table class="mdl-data-table mdl-js-data-table">
				    <thead>
					    <tr>
						    <th class="mdl-data-table__cell--non-numeric">
							    Original
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Processed
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Sun Diff
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Moon Diff
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Pre-process time
						    </th>
                    				<th class="mdl-data-table__cell--non-numeric">
							    Hough time
						    </th>
                    				<th class="mdl-data-table__cell--non-numeric">
							    Discarded Reasons
						    </th>
					    </tr>
					</thead>
				    <tbody>
                    {% for item in items %}
					    <tr>
						    <td class="mdl-data-table__cell--non-numeric img-cell">
							    <img src={{item.original}}> <br>
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
							    <img src={{item.processed}}>
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
							    {{item.sun_diff}}
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
							    {{item.moon_diff}}
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
							    {{item.pre_proc_time}}
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
							    {{item.hough_time}}
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
							    {{item.discard_reasons}}
						    </td>
					    </tr>
                    {% endfor %}
				    </tbody>
			    </table>

			</div>
		</main>
	</div>

</body>
</html>
"""

def read_metadata(original_path, processed_path):
    
    f = open(os.path.join(processed_path, METADATA_FILE), 'r')

    metadata_items = []

    for line in f.readlines():
        tokens = line.split('|')

        item = dict(image_name = tokens[0], 
                    original = os.path.join(original_path, tokens[0]), 
                    processed = os.path.join(processed_path, tokens[0]), 
                    sun_diff = tokens[1],
                    moon_diff = tokens[2], 
                    pre_proc_time = tokens[3], 
                    hough_time = tokens[4])

        if tokens[5] == "1":
            item['discard_reasons'] = '<br>'.join(item.strip() for item in tokens[6].split(';'))

        metadata_items.append(item)

    return metadata_items
    
def build_html_doc(original_path, processed_path, output_file_dir):

    #get all 40 characters of the commit hash
    commit_hash = str(subprocess.check_output("git rev-parse HEAD", shell=True))[2:42]

    #set date/time for title
    date_time = time.strftime("%c", time.localtime())

    page_title = "Eclipse Image Processor Output"

    metadata = read_metadata(original_path, processed_path)

    f = open(os.path.join(output_file_dir, OUTPUT_FILE), 'w')
    f.write( Environment().from_string(HTML).render(title=page_title, 
                                                    gitrev=commit_hash, date=date_time, items=metadata) )

def main():

    if len(sys.argv) != 4:
        print ("Please run this script in the form:")
        print ("$python image_proc_output.py [/path/to/original/images] [/path/to/processed/images] [/output/html/dir]")
        return 

    build_html_doc(sys.argv[1], sys.argv[2], sys.argv[3])

if __name__ == '__main__':

    main()

