LIB=/usr/local/lib
INC=-I/usr/local/include/python2.2

go: parportmodule.so FlyingFader.py serportmodule.so
	result="your modules and links are now up to date"

FlyingFader.py:
	ln -s ../Widgets/FlyingFader.py

parportmodule.so: parport_wrap.c
	gcc -shared ${INC} parport_wrap.c parport.c -o parportmodule.so 

parport_wrap.c: parport.c parport.i
	swig -python parport.i

serportmodule.so: serport_wrap.c
	gcc -shared -O ${INC} serport_wrap.c -o serportmodule.so 

serport_wrap.c: serport.i
	swig -python serport.i

clean:
	rm -f parport_wrap.c serport_wrap.c *.o *.so
