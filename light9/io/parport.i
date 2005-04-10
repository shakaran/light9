%module parport


extern void getparport();
extern void outdata( unsigned char val);
extern void outcontrol( unsigned char val );
extern void outbyte( unsigned char val );
extern void outstart();



