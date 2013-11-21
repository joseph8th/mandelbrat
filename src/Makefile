CREG = gcc
CPP = g++
CFLAGS = -g -Wall -ansi -pedantic
SFLAGS_BOOST = -fPIC -lboost_python -lpython2.7 -lmpfr -lgmp -I /usr/include/python2.7
SFLAGS = -fPIC -lmpfr -lgmp

all: sharedcpp sharedc

testc: test_mpointc.o
	$(CREG) -g $^ -o $@

sharedcpp: mpoint.so

sharedc: mpointc.so

%.so: %.cpp %.hpp
	$(CPP) $(CFLAGS) $^ $(SFLAGS_BOOST) -o $@ -shared

%.so: %.c %.h
	$(CREG) $(CFLAGS) $^ $(SFLAGS) -o $@ -shared

%.o: %.c %.h
	$(CREG) -c $(CFLAGS) $<
