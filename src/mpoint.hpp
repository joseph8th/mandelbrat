#ifndef MPOINT_HPP
#define MPOINT_HPP

#include <vector>
#include <string>
#include <complex>
#include <sstream>

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <inttypes.h>

#include <mpfr.h>
#include <boost/python.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/multiprecision/mpfr.hpp>
#include <boost/python/converter/registry.hpp>
#include <boost/python/detail/wrap_python.hpp>


/****************************************************************************\
 **  MandelBrat MPoint - Experiments in MandelBrot/Julia Set based crypto   **
 **  Author: Joseph Edwards VIII <joseph8th@urcomics.com>                   **
 **  ---------------------------------------------------------------------  **
 **  MPoint v0.2 encapsulates 'point' data and methods for Mandelbrot set   ** 
 **  generation. Implements GNU MPFR via Boost's Multiprecision and Python  **
 **  libraries for arbitrary precision floating point and complex numbers.  **
 \*_________________________________________________________________________*/


// some custom types for shorthand ...
typedef std::vector< std::string > mpvector_t;

typedef std::complex<long double> ldcomplex;
typedef boost::multiprecision::mpfr_float mpfloat;

typedef struct mpcomplex_t {
  mpfloat real;
  mpfloat imag;
} mpcomplex;

/* to_python converter for mpfloat type */
struct mpfloat_to_pystr {
  static PyObject* convert(mpfloat const& num) {
    std::stringstream oss;
    oss << std::fixed << std::setprecision( mpfloat::default_precision() ) << num;
    return boost::python::incref( boost::python::object(oss.str()).ptr() );
  }
};

/* to_python converter for mpcomplex type */
struct mpcomplex_to_pytuple {
  static PyObject* convert(mpcomplex const& cnum) {
    return boost::python::incref( boost::python::make_tuple(cnum.real, cnum.imag).ptr() );
  }
};

void initializeConverters() {
  using namespace boost::python;

  type_info mpf_info = type_id<mpfloat>();
  const converter::registration* mpf_reg = converter::registry::query(mpf_info);
  if (mpf_reg == NULL) {
    to_python_converter<mpfloat, mpfloat_to_pystr>();
  } else if ((*mpf_reg).m_to_python == NULL) {
    to_python_converter<mpfloat, mpfloat_to_pystr>();
  }

  type_info mpc_info = type_id<mpcomplex>();
  const converter::registration* mpc_reg = converter::registry::query(mpc_info);
  if (mpc_reg == NULL) {
    to_python_converter<mpcomplex, mpcomplex_to_pytuple>();
  } else if ((*mpc_reg).m_to_python == NULL) {
    to_python_converter<mpcomplex, mpcomplex_to_pytuple>();
  }
}

/*
** The big kahuna itself. The MPoint extension class prototype ...
*/
class MPoint {

private:

  ldcomplex c;
  mpcomplex C;
  unsigned int prec;
  unsigned long iter;
  bool inmset;
  unsigned int index[2];

  /* initializer */
  void _initMPoint(unsigned int prec_in) {
    prec = prec_in;
    iter = 0;
    inmset = false;
    index[0] = index[1] = 0;
    // register converters if not already registered
    initializeConverters();
  }

  /* a private method to parse a string into 'complex' form */
  mpcomplex _get_mpcomplex_from_str_repr(std::string repr);

public:

  //  MPoint(mpcomplex c_in, unsigned int prec_in=15);
  MPoint(std::string c_in, unsigned int prec_in=15);
  MPoint(ldcomplex c_in, unsigned int prec_in=15);
  MPoint(std::string x, std::string y, unsigned int prec_in=15);
  MPoint(long double x, long double y, unsigned int prec_in=15);

  //  void Set_c(mpcomplex c_in);
  void Set_c(std::string c_in);
  void Set_c(ldcomplex c_in);
  void Set_c(std::string x, std::string y);
  void Set_c(long double x, long double y);

  mpcomplex Get_C();
  ldcomplex Get_c();

  void Set_x(std::string x);
  void Set_x(long double x);

  mpfloat Get_x();

  void Set_y(std::string y);
  void Set_y(long double y);

  mpfloat Get_y();

  void Set_Prec(unsigned long prec_in);
  unsigned long Get_Prec();

  void Set_Iter(unsigned long iter_in);
  unsigned long Get_Iter();

  void Set_Index(unsigned int ix, unsigned int iy);
  unsigned int Get_ix();
  unsigned int Get_iy();

  void Set_InMSet(bool inmset_in);
  bool Get_InMSet();

  //  void Run_MFun(unsigned long itermax, mpfloat x, mpfloat y);
  void Run_MFun(unsigned long itermax, std::string x, std::string y);
  void Run_MFun(unsigned long itermax, long double x, long double y);
  void Run_MFun(unsigned long itermax, std::string z0);
  void Run_MFun(unsigned long itermax, ldcomplex z0);
};

#endif /* MPOINT_HPP */
