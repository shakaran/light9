#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <asm/io.h>
#include <fcntl.h>
#include <Python.h>

int getparport() {
    if( ioperm(888,3,1) ) {
      printf("Couldn't get parallel port at 888-890\n");

      // the following doesn't have any effect!
      PyErr_SetString(PyExc_IOError,"Couldn't get parallel port at 888-890");
      return 0;
    } 
    return 1;
}

void outdata(unsigned char val) {
  outb(val,888);
}

void outcontrol( unsigned char val ) {
  outb(val,890);
}

void outbyte( unsigned char val ) {
  // set data, raise clock, lower clock
  outdata(val);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(2);
  outcontrol(3);
}
void outstart() {
  // send start code: pin 14 high, 5ms to let a dmx cycle finish,
  // then pin14 low (pin1 stays low)
  outcontrol(1);
  usleep(5000);
  outcontrol(3);
}
