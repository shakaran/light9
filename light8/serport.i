%module serport

%{
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/ioctl.h>
#include <fcntl.h>
#include <linux/i2c.h>
#include <linux/i2c-dev.h>
#include <unistd.h>
%}


%typemap(python,in) __u8 {
  if( !PyInt_Check($input)) {
    PyErr_SetString(PyExc_TypeError,"not an integer");
    return NULL;
  }
  $1 = ($type) PyInt_AsLong($input);
}

%typemap(python,out) __s32 {
  $result = Py_BuildValue("i", ($type) $1);
}

%inline %{

  __s32 i2c_smbus_write_byte(int file, __u8 value);
  __s32 i2c_smbus_read_byte(int file);

  PyObject *read_all_adc(int file) {
    PyObject *t=PyTuple_New(4);
    
    #define CHAN_TO_TUPLE_POS(chan,idx) i2c_smbus_write_byte(file, chan);\
    PyTuple_SetItem(t,idx,PyInt_FromLong(i2c_smbus_read_byte(file)));

    /*
      these are shuffled here to match the way the pots read in. in
      the returned tuple, 0=left pot..3=right pot.
    */
    CHAN_TO_TUPLE_POS(1,0)
    CHAN_TO_TUPLE_POS(2,1)
    CHAN_TO_TUPLE_POS(3,2)
    CHAN_TO_TUPLE_POS(0,3)
      
    return t;

  }

%}
