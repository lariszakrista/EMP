
LIBS = -lopencv_core -lopencv_imgproc -lopencv_imgcodecs -lopencv_highgui

all: pipeline

pipeline: driver.cc imgproc_pipeline_base.o imgproc_image.o
	g++ driver.cc imgproc_pipeline_base.o imgproc_image.o -o pipeline $(LIBS)

imgproc_pipeline_base.o: imgproc_pipeline_base.cc
	g++ -c imgproc_pipeline_base.cc -o imgproc_pipeline_base.o $(LIBS)

imgproc_image.o: imgproc_image.cc
	g++ -c imgproc_image.cc -o imgproc_image.o $(LIBS)

imgproc_util.o: imgproc_util.cc
	g++ -c imgproc_util.cc -o imgproc_util.o $(LIBS)

clean:
	rm -f pipeline *.o
