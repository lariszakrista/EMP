import subprocess
from jinja2 import Environment, Template
import time
import os
import sys
from ast import literal_eval
import math

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

	<script>

        var prev_col_name = " ";
        var ascending = true;

        function hide_all_arrows() {

            document.getElementById("sun_diff_up").style.display = "none";
            document.getElementById("sun_diff_down").style.display = "none";

            document.getElementById("moon_diff_up").style.display = "none";
            document.getElementById("moon_diff_down").style.display = "none";

            document.getElementById("pre_proc_up").style.display = "none";
            document.getElementById("pre_proc_down").style.display = "none";

            document.getElementById("hough_up").style.display = "none";
            document.getElementById("hough_down").style.display = "none";

        }

        function sun_diff_comparator(row1, row2) {
            var col_val = 2;

            var row1_cell = row1.getElementsByTagName("td")[col_val];
            var row2_cell = row2.getElementsByTagName("td")[col_val];

            var row1_result = row1_cell.innerHTML.split("<br>");
            var row2_result = row2_cell.innerHTML.split("<br>");

            var row1_val = row1_result[1];
            row1_val = parseFloat(row1_val) + Math.abs(parseFloat(row1_result[4]));

            var row2_val = row2_result[1];
            row2_val = parseFloat(row2_val) + Math.abs(parseFloat(row2_result[4]));

            if (row1_val < row2_val) {
                return -1;
            }
            if (row1_val > row2_val) {
                return 1;
            }
            return 0;
        }

        function moon_diff_comparator(row1, row2) {
            var col_val = 3;

            var row1_cell = row1.getElementsByTagName("td")[col_val];
            var row2_cell = row2.getElementsByTagName("td")[col_val];

            var row1_result = row1_cell.innerHTML.split("<br>");
            var row2_result = row2_cell.innerHTML.split("<br>");

            var row1_val = row1_result[1];
            if (row1_val.toLowerCase().includes("no moon")) {
                row1_val = 10000;
            } else {
                row1_val = parseFloat(row1_val) + Math.abs(parseFloat(row1_result[4]));
            }

            var row2_val = row2_result[1];
            if (row2_val.toLowerCase().includes("no moon")) {
                row2_val = 10000;
            } else {
                row2_val = parseFloat(row2_val) + Math.abs(parseFloat(row2_result[4]));
            }

            if (row1_val < row2_val) {
                return -1;
            }
            if (row1_val > row2_val) {
                return 1;
            }
            return 0;
        }

        function pre_proc_comparator(row1, row2) {
            var col_val = 4;

            var row1_cell = row1.getElementsByTagName("td")[col_val];
            var row2_cell = row2.getElementsByTagName("td")[col_val];

            var row1_result = row1_cell.innerHTML.split(" ");
            var row2_result = row2_cell.innerHTML.split(" ");

            var row1_val = row1_result[4];
            var row2_val = row2_result[4];

            if (row1_val < row2_val) {
                return -1;
            }
            if (row1_val > row2_val) {
                return 1;
            }
            return 0;
        }

        function hough_comparator(row1, row2) {
            var col_val = 5;

            row1_cell = row1.getElementsByTagName("td")[col_val];
            row2_cell = row2.getElementsByTagName("td")[col_val];

            var row1_result = row1_cell.innerHTML.split(" ");
            var row2_result = row2_cell.innerHTML.split(" ");

            var row1_val = row1_result[4];
            var row2_val = row2_result[4];

            if (row1_val < row2_val) {
                return -1;
            }
            if (row1_val > row2_val) {
                return 1;
            }
            return 0;
        }

        function sort_table(n) {

            var table = document.getElementById("eclipse_data_table");
            var table_body = document.getElementById("eclipse_data_table_body");

            var row_array = Array.prototype.slice.call(table_body.children);

            var start = performance.now();

            switch(n) {
                case 2:
                    var col_name = "sun_diff";
                    row_array.sort(sun_diff_comparator);
                    break;
                case 3:
                    var col_name = "moon_diff";
                    row_array.sort(moon_diff_comparator);
                    break;
                case 4:
                    var col_name = "pre_proc";
                    row_array.sort(pre_proc_comparator);
                    break;
                case 5:
                    var col_name = "hough";
                    row_array.sort(hough_comparator);
                    break;
                defult:
                    console.log("error this isn't possible");
            }

            if(prev_col_name == col_name) {
                ascending = !ascending;
            } else {
                ascending = true;
            }

            if (ascending) {
                for (var i = 0; i < row_array.length; i++) {
                    table.children[1].appendChild(row_array[i]);
                }
                var arrow_direction = "up";
            } else {
                for (var i = row_array.length -1; i > -1; i--) {
                    table.children[1].appendChild(row_array[i]);
                }
                var arrow_direction = "down";
            }

            hide_all_arrows();
            document.getElementById(col_name + "_" + arrow_direction).style.display = "";

            var end = performance.now();
            var time = end - start;
            console.log('Execution time: ' + time);

            prev_col_name = col_name;
        }       

	</script>
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

                <table id="eclipse_data_table" class="mdl-data-table mdl-js-data-table">
				    <thead>
					    <tr>
						    <th class="mdl-data-table__cell--non-numeric">
							    Original
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Processed
						    </th>

						    <th class="mdl-data-table__cell--non-numeric" onclick="sort_table(2)" style="cursor: pointer;">
							    Sun Diff (px)
                                <i id="sun_diff_down" style="position: absolute; display: none;" class="material-icons">keyboard_arrow_down</i>
                                <i id="sun_diff_up" style="position: absolute; display: none;" class="material-icons">keyboard_arrow_up</i>
						    </th>
						    <th class="mdl-data-table__cell--non-numeric" onclick="sort_table(3)" style="cursor: pointer;">
							    Moon Diff (px)
                                <i id="moon_diff_down" style="position: absolute; display: none;" class="material-icons">keyboard_arrow_down</i>
                                <i id="moon_diff_up" style="position: absolute; display: none;" class="material-icons">keyboard_arrow_up</i>
						    </th>
						    <th class="mdl-data-table__cell--non-numeric">
							    Running times (secs)
						    </th>
                    		<th class="mdl-data-table__cell--non-numeric">
							    Comments
						    </th>
					    </tr>
					</thead>
				    <tbody id="eclipse_data_table_body">
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
						        <ul>
						        {% for time in item.times %}
						            <li> {{ time }} </li>
						        {% endfor %}
						        </ul>
						    </td>
						    <td class="mdl-data-table__cell--non-numeric">
							    <ul>
							    {% for comment in item.comments %}
							        <li> {{ comment }} </li>
							    {% endfor %}
							    </ul>
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

        truth_positions[os.path.join(processed_path, tokens[0])] = position
    
    f = open(os.path.join(processed_path, "metadata.txt"), 'r')

    metadata_items = []

    for line in f.readlines():
        tokens = line.split('|')
        
        path_tokens = tokens[0].split('/')
        img_name = path_tokens[len(path_tokens) - 1]

        item = dict(image_name = img_name, 
                    original = os.path.join(original_path, img_name), 
                    processed = os.path.join(processed_path, img_name))
                    
        times = []
        comments = []
        token_count = 0
        for token in tokens:
            if token.startswith('t'):
                tup = literal_eval(token[1:])
                times.append(tup[0] + ":\t" + str(tup[1]))
            elif token.startswith('c'):
                None
            elif token_count > 1 and token != "\n":
                comments.append(token)
            else:
                None
            token_count += 1
                
        item['times'] = times
        item['comments'] = comments

        if truth_positions[tokens[0]]['moon'] is not None:
            moon_center_offset, moon_radius_diff = calc_position_diff(literal_eval(tokens[2][1:]), truth_positions[tokens[0]]['moon'])
            item['moon_center_diff'] = moon_center_offset
            item['moon_rad_diff'] = moon_radius_diff
        else:
            item['moon_center_diff'] = "No Moon in ground truth"
            item['moon_rad_diff'] = "No Moon in ground truth"

        sun_center_offset, sun_radius_diff = calc_position_diff(literal_eval(tokens[1][1:]), truth_positions[tokens[0]]['sun'])

        item['sun_center_diff'] = sun_center_offset
        item['sun_rad_diff'] = sun_radius_diff

        #print (item) 

        if tokens[5] == "1":
            item['comments'] = '<br>'.join(item.strip() for item in tokens[6].split(';'))

        metadata_items.append(item)

    return metadata_items
    
def build_html_doc(original_path, processed_path):

    #get all 40 characters of the commit hash
    commit_hash = str(subprocess.check_output("git rev-parse HEAD", shell=True))[2:42]

    #set date/time for title
    date_time = time.strftime("%c", time.localtime())

    page_title = "Eclipse Image Processor Output"

    metadata = read_metadata(original_path, processed_path)

    f = open(os.path.join(processed_path, OUTPUT_FILE), 'w')
    f.write( Environment().from_string(HTML).render(title=page_title, 
                                                    gitrev=commit_hash, date=date_time, items=metadata) )

def main():

    if len(sys.argv) < 3:
        print ("Please run this script in the form:")
        print ("$python3 image_proc_output.py [/path/to/original/images] [/path/to/processed/images]")
        return 

    build_html_doc(sys.argv[1], sys.argv[2])

if __name__ == '__main__':

    main()

