
LIBS = -lopencv_core -lopencv_imgproc -lopencv_imgcodecs -lopencv_highgui

all: imgproc_batch imgproc

imgproc_batch: imgproc_batch.cc
	g++ imgproc_batch.cc -o imgproc_batch $(LIBS)

imgproc: imgproc.cc
	g++ imgproc.cc -o imgproc $(LIBS)

clean:
	rm -f imgproc imgproc_batch
