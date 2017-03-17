
LIBS = -lopencv_core -lopencv_imgproc -lopencv_imgcodecs -lopencv_highgui

all: imgproc

imgproc: imgproc.cc imgproc_util.o
	g++ imgproc.cc imgproc_util.o -o imgproc $(LIBS)

imgproc_util.o: imgproc_util.cc
	g++ -c imgproc_util.cc -o imgproc_util.o $(LIBS)

clean:
	rm -f imgproc *.o
