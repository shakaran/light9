cdef extern from "fcntl.h":
    int open(char *pathname, int flags)
    int O_WRONLY

cdef extern from "unistd.h":
    int write(int fd, void *buf, int count)

cdef extern from "string.h":
    char *strncpy(char *dest, char *src, int n)

cdef extern from "Python.h":
    char* PyString_AsString(object string)

cdef class Dmx:
    cdef int fd
    def __cinit__(self, port="/dev/dmx0"):
        self.fd = open(port, O_WRONLY)
        if self.fd < 0:
            raise OSError("open failed")

    def write(self, buf):
        cdef char *cbuf
        cbuf = PyString_AsString(buf)
        if cbuf == NULL:
            raise ValueError("string buffer conversion failed")
        res = write(self.fd, cbuf, 513)
        if res < 0:
            raise OSError("write failed")
