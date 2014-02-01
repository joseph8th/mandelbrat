#ifndef MPOINTC_H
#define MPOINTC_H

#include <inttypes.h>

#include <gmp.h>
#include <mpfr.h>

typedef void (*Mpfr2Str)(mpfr_t number, char ** strbuf) ;
typedef void (*Str2Mpfr)(char * string, mpfr_t * numbuf) ;

typedef struct parsefun_t {
  Mpfr2Str mpfr2str;
  Str2Mpfr str2mpfr;
} ParseFun; 

typedef struct mpt_mpc_t {
  mpfr_t real;
  mpfr_t imag;
} MCPt;

typedef char ** TraceBuf ;

typedef struct mpt_t {
  char * real;
  char * imag;
  int inmset;
  unsigned int index[2];
  TraceBuf * trace;
} MPt; 

extern int inMset(size_t prec, size_t iter, MPt * mpt) ;

#endif /* MPOINTC_H */
