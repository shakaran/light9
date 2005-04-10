LIB=/usr/local/lib
INC=-I/usr/local/include/python2.3

go: _parport.so _serport.so
	result="your modules and links are now up to date"

_parport.so: parport_wrap.c
	gcc -shared ${INC} parport_wrap.c parport.c -o _parport.so 

parport_wrap.c: parport.c parport.i
	swig -python parport.i

_serport.so: serport_wrap.c
	gcc -shared -O ${INC} serport_wrap.c -o _serport.so 

serport_wrap.c: serport.i
	swig -python serport.i

clean:
	rm -f parport_wrap.c serport_wrap.c *.o *.so
