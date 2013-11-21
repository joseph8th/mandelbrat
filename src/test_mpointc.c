#include <stdio.h>
#include <stdlib.h>
#include "mpointc.h"

int main(void) {

  int i=0, res=0, prec, iter;
  MPt mpt;
  TraceBuf tracebuf;

  /* define parameters to be passed */
  prec = 53;
  iter = 100;

  printf("Tests C version of 'mpoint' ...\n");

  /* malloc a tracebuffer */
  tracebuf = (char**)malloc(iter * sizeof(char*));
  if (tracebuf == NULL) {
    printf("ERROR: out of memory.\n");
    return 1;
  }

  /* malloc each string into the array */
  for (i=0; i < iter; i++) {
    tracebuf[iter] = (char*)malloc((prec+1) * sizeof(char));

    if (tracebuf == NULL) {
      printf("ERROR: out of memory.\n");
      return 1;
    }

    tracebuf[iter][0] = '\0';
  }

  /* make an MPoint */
  mpt.real = "0.012";
  mpt.imag = "-0.123";
  mpt.trace = &tracebuf;

  /* test the functions */
  inMset(prec, iter, &mpt);
  printf("'inMset' test: %d\n", res);

  /* free stuff up */
  for (i=0; i < iter; i++) {
    free(tracebuf[iter]);
  }
  free(tracebuf);

  return 0;
}
