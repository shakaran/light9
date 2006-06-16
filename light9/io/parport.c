#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <asm/io.h>
#include <fcntl.h>
#include <Python.h>

int getparport() {
  printf("parport - ver 4\n");
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
  int i;
  // set data, raise clock, lower clock
  outdata(val);

  /* this was originally 26 outcontrol calls, but on new dash that
     leads to screwed up dmx about once a minute. I tried doing 26*4
     outcontrol calls, but it still screwed up. I suspect the athlon64
     or my new kernel version is sending the parport really fast,
     sometimes faster than the pic sees the bits. Then I put a 1ms
     sleep after the outcontrol(2)'s and that didn't help either, so
     I'm not sure what's going on. Putting the parallel cable on miles
     seems to work. 

     todo:
     try a little pause after outcontrol(3) to make sure pic sees that
  */

  for (i=0; i<26*4; i++) {
    outcontrol(2);
  }
  outcontrol(3);
}
void outstart() {
  // send start code: pin 14 high, 5ms to let a dmx cycle finish,
  // then pin14 low (pin1 stays low)
  outcontrol(1);
  usleep(5000);
  outcontrol(3);
}
