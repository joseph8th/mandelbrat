#include "mpointc.h"

static void defMpfr2Str(mpfr_t number, char ** strbuf) { }
static void defStr2Mpfr(char * string, mpfr_t * numbuf) { }
static ParseFun defParseFun = { defMpfr2Str, defStr2Mpfr };


/* 'Public' functions */

void inMset(size_t prec, size_t iter, MPt * mpt) { 
  printf("==> 'inMset()' stub here ...\n");
  return 0;
}
