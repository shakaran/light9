LIB=/usr/local/lib

go: parportmodule.so
	sudo python pypar

parportmodule.so: parport_wrap.c
	gcc -shared -I/usr/local/include/python2.2 parport_wrap.c parport.c -o parportmodule.so 

parport_wrap.c: parport.c parport.i
	swig -python parport.i

clean:
	rm -f parport_wrap.c *.o *.so