#include "imgproc_pipeline.h"
#include "imgproc_defs.h"

#define METADATA_FILE_NAME                  "metadata.txt"

using std::ifstream;
using std::ofstream;
using std::string;
using std::cout;
using std::endl;
using std::cerr;

int main(int argc, char **argv){
	
    ImgprocMode mode;
    int key;
    ifstream f;
    ofstream metadata_file;
    string valid_modes, input_file, dest_dir, mode_str, output_dir;

    if (argc < 4) {
        cerr << "Usage:\n\t$ ./imgproc images_file input_dir mode [output_dir]" << endl;
        cerr << endl << "Modes:\t" << valid_modes << "\n";
        cerr << "\toutput_dir required when run in batch mode\n" << endl;
        return -1;
    } 

    input_file = argv[1];
    dest_dir  = argv[2];
    mode_str   = argv[3];
    
    if (mode_str == "batch")
    {
        mode       = BATCH;
        output_dir = argv[4];
    }
    else if (mode_str == "window")
    {
        mode = WINDOW;
		output_dir = "";
    }
    else
    {
        cerr << "Invalid mode: " << mode_str << ". Valid modes: " << valid_modes << endl;
        return -1;
    }

	dest_dir += dest_dir[dest_dir.size() - 1] == '/' ? "" : "/";

    if (mode == BATCH)
    {
        // Add trailing slash to dir path if necessary
	    output_dir += output_dir[output_dir.size() - 1] == '/' ? "" : "/";
    }

	// Create pipeline object, passing in input image file to constructor	
	ImgProcPipeline pipeline(input_file, dest_dir, mode, string(output_dir + METADATA_FILE_NAME)); 
	pipeline.run_all();

	
	return 0;

}
