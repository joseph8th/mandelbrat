#include <complex>
#include <boost/python.hpp>
#include "mpoint.hpp"

/*************************************************************************
 * MandelBrat Library - Experiments in MandelBrot/Julia Set based crypto *
 * Author: Joseph Edwards VIII <joseph8th@urcomics.com>                  *
 *************************************************************************/

/* constructors */
MPoint :: MPoint(ldcomplex c_in) { 
  c = c_in; iter = 0; inmset = false; index[0] = index[1] = 0;
}
MPoint :: MPoint(long double x, long double y) { 
  c = ldcomplex(x, y); iter = 0; inmset = false; index[0] = index[1] = 0;
}

/* accessors */
void MPoint :: Set_c(ldcomplex c_in) { c = c_in; }
void MPoint :: Set_c(long double x, long double y) { c = std::complex<long double>(x, y); }
ldcomplex MPoint :: Get_c() { return c; }
void MPoint :: Set_x(long double x) { c = std::complex<long double>(x, c.imag()); }
long double MPoint :: Get_x() { return c.real(); }
void MPoint :: Set_y(long double y) { c = std::complex<long double>(c.real(), y); }
long double MPoint :: Get_y() { return c.imag(); }
void MPoint :: Set_Iter(unsigned long iter_in) { iter = iter_in; }
unsigned long MPoint :: Get_Iter() { return iter; }
void MPoint :: Set_Index(unsigned int ix, unsigned int iy) { 
  index[0] = ix; 
  index[1] = iy; 
} 
unsigned int MPoint :: Get_ix() { return index[0]; }
unsigned int MPoint :: Get_iy() { return index[1]; }
void MPoint :: Set_InMSet(bool inmset_in) { inmset = inmset_in; }
bool MPoint :: Get_InMSet() { return inmset; }

/*
** run the mandelbrot algorithm using this point as c
*/
void MPoint :: Run_MFun(unsigned long itermax, ldcomplex z0) {
  long double zz;
  ldcomplex z = z0;
  long unsigned i = 0;

  while(i<itermax) {
    z = z*z + c;
    zz = (z.real()*z.real()) + (z.imag()*z.imag());
    if (zz>4.0) break;
    ++i;
  }
  iter = i;
  if (iter == itermax) inmset = true;
}

/*
** extend with boost.python
*/

void (MPoint::*set_c1)(ldcomplex) = &MPoint::Set_c;
void (MPoint::*set_c2)(long double, long double) = &MPoint::Set_c;

using namespace boost::python;

BOOST_PYTHON_MODULE(mpoint) {
  class_<MPoint>("MPoint", init<ldcomplex>())
    .def(init<long double, long double>())
    .def("Run_MFun", &MPoint::Run_MFun)
    .def("Set_c", set_c1)
    .def("Set_c", set_c2)
    .def("Set_Index", &MPoint::Set_Index)
    .def("Get_ix", &MPoint::Get_ix)
    .def("Get_iy", &MPoint::Get_iy)
    .add_property("c", &MPoint::Get_c, set_c1)
    .add_property("real", &MPoint::Get_x, &MPoint::Set_x)
    .add_property("imag", &MPoint::Get_y, &MPoint::Set_y)
    .add_property("iter", &MPoint::Get_Iter, &MPoint::Set_Iter)
    .add_property("inmset", &MPoint::Get_InMSet, &MPoint::Set_InMSet)
    ;
}