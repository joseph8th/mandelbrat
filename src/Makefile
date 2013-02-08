CC=g++
CFLAGS=-g -Wall -ansi -pedantic
LIBPATH=/home/notroot/Dev/python/mbrat/src
SFLAGS=-fPIC -lboost_python -lpython2.7 -I /usr/include/python2.7/

all : shared

shared : mpoint.so

%.so : %.cpp %.hpp 
	${CC} ${CFLAGS} $^ ${SFLAGS} -o ${@} -shared
