CPP = g++
CPPFLAGS = -g -Wall -ansi -pedantic
SFLAGS = -fPIC -lboost_python -lpython2.7 -lmpfr -lgmp -I /usr/include/python2.7

all: shared

shared: mpoint.so

%.so: %.cpp %.hpp
	$(CPP) $(CPPFLAGS) $^ $(SFLAGS) -o $@ -shared
