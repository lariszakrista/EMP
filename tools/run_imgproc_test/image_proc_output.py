import subprocess
from jinja2 import Environment, Template
import time
import os
import sys
from ast import literal_eval
import math

METADATA_FILE = "metadata.txt"
OUTPUT_FILE = "output.html"
TRUTH_FILE = "image_data.txt"

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
							    Sun Diff (px)
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Moon Diff (px)
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Pre-process time (secs)
						    </th>
                    				<th class="mdl-data-table__cell--non-numeric">
							    Hough time (secs)
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
							    Center offset: <br>{{item.sun_center_diff}}<br>
                                <br>
                                Radius difference: <br>{{item.sun_rad_diff}}<br>
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
                                {{ item.no_moon }}
							    Center offset: <br>{{item.moon_center_diff}}<br>
                                <br>
                                Radius difference: <br>{{item.moon_rad_diff}}<br>
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

def calc_position_diff(result, truth):

    result_pos = (result[0], result[1])
    truth_pos = (truth[0], truth[1])

    radius_diff = result[2] - truth[2]

    center_offset = euclidean_distance(result_pos, truth_pos)

    return center_offset, radius_diff

def euclidean_distance(circle1, circle2):

	dx = circle1[0] - circle2[0]
	dy = circle1[1] - circle2[1]

	return math.sqrt((dx ** 2) + (dy ** 2))

def read_metadata(original_path, processed_path):

    truth_file = open(os.path.join(original_path, TRUTH_FILE), 'r')

    truth_positions = {}
    for line in truth_file:
        tokens = line.split('|')

        position = dict(sun = literal_eval(tokens[2]), moon = literal_eval(tokens[3]))

        truth_positions[tokens[0]] = position
    
    f = open(os.path.join(processed_path, METADATA_FILE), 'r')

    metadata_items = []

    for line in f.readlines():
        tokens = line.split('|')

        item = dict(image_name = tokens[0], 
                    original = os.path.join(original_path, tokens[0]), 
                    processed = os.path.join(processed_path, tokens[0]), 
                    pre_proc_time = tokens[3], 
                    hough_time = tokens[4])

        
        if truth_positions[tokens[0]]['moon'] is not None:
            moon_center_offset, moon_radius_diff = calc_position_diff(literal_eval(tokens[2]), truth_positions[tokens[0]]['moon'])
            item['moon_center_diff'] = moon_center_offset
            item['moon_rad_diff'] = moon_radius_diff
        else:
            item['moon_center_diff'] = "No Moon in ground truth"
            item['moon_rad_diff'] = "No Moon in ground truth"

        sun_center_offset, sun_radius_diff = calc_position_diff(literal_eval(tokens[1]), truth_positions[tokens[0]]['sun'])

        item['sun_center_diff'] = sun_center_offset
        item['sun_rad_diff'] = sun_radius_diff

         

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

