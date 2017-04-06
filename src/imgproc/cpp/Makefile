
LIBS = -lopencv_core -lopencv_imgproc -lopencv_imgcodecs -lopencv_highgui

all: pipeline

imgproc: imgproc.cc imgproc_util.o
	g++ imgproc.cc imgproc_util.o -o imgproc $(LIBS)

imgproc_util.o: imgproc_util.cc
	g++ -c imgproc_util.cc -o imgproc_util.o $(LIBS)

pipeline: imgproc_pipeline.o image.o
	g++ pipeline_runner.cc imgproc_pipeline.o image.o $(LIBS)

imgproc_pipeline.o: imgproc_pipeline.cc
	g++ -c imgproc_pipeline.cc -o imgproc_pipeline.o $(LIBS)

image.o: image.cc
	g++ -c image.cc -o image.o $(LIBS)

clean:
	rm -f imgproc *.o
