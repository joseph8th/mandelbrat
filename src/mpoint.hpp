#ifndef MPOINT_HPP
#define MPOINT_HPP

#include <complex>

/*************************************************************************
 * MandelBrat Library - Experiments in MandelBrot/Julia Set based crypto *
 * Author: Joseph Edwards VIII <joseph8th@urcomics.com>                  *
 *************************************************************************/

typedef std::complex<long double> ldcomplex;

class MPoint 
{
private:
  ldcomplex c;
  unsigned long iter;
  bool inmset;
  unsigned int index[2];
public:
  MPoint(ldcomplex c_in);
  MPoint(long double x, long double y);
  void Set_c(ldcomplex c_in);
  void Set_c(long double x, long double y);
  ldcomplex Get_c();
  void Set_x(long double x);
  long double Get_x();
  void Set_y(long double y);
  long double Get_y();
  void Set_Iter(unsigned long iter_in);
  unsigned long Get_Iter();
  void Set_Index(unsigned int ix, unsigned int iy);
  unsigned int Get_ix();
  unsigned int Get_iy();
  void Set_InMSet(bool inmset_in);
  bool Get_InMSet();
  void Run_MFun(unsigned long itermax, ldcomplex z0);
};

#endif /* MPOINT_HPP */
