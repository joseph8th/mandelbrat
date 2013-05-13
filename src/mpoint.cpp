#include "mpoint.hpp"

/****************************************************************************\
 **  MandelBrat MPoint - Experiments in MandelBrot/Julia Set based crypto   **
 **  Author: Joseph Edwards VIII <joseph8th@urcomics.com>                   **
 \*_________________________________________________________________________*/


using namespace boost::multiprecision;


// constructors

MPoint :: MPoint(std::string c_in, unsigned int prec_in) {
  mpfr_float::default_precision(prec_in);
  this->Set_c(c_in);
  this->_initMPoint(prec_in);
}
MPoint :: MPoint(ldcomplex c_in, unsigned int prec_in) { 
  mpfr_float::default_precision(prec_in);
  this->Set_c(c_in);
  this->_initMPoint(prec_in);
}
MPoint :: MPoint(std::string x, std::string y, unsigned int prec_in) {
  mpfr_float::default_precision(prec_in);
  this->Set_c(x, y);
  this->_initMPoint(prec_in);
}
MPoint :: MPoint(long double x, long double y, unsigned int prec_in) { 
  mpfr_float::default_precision(prec_in);
  this->Set_c(x, y);
  this->_initMPoint(prec_in);
}


// private methods

mpcomplex MPoint :: _get_mpcomplex_from_str_repr(std::string repr)  {
  std::string realstr, imagstr;
  mpcomplex retpt;

  // verify that we're dealing with something resembling a complex #
  unsigned ij_found = repr.find_last_of("ij");
  if ( (ij_found == std::string::npos) || (ij_found != repr.size()-1) ) {
    if (repr.size() != 0) {
      retpt.real = mpfloat(repr);
      retpt.imag = mpfloat(0.0);
    }
    return retpt;
  }
  else repr.resize(repr.size()-1);

  // split into real and imaginary parts assuming correct format
  unsigned op_found = repr.find_last_of("+-");

  realstr =  repr.substr(0, op_found);
  imagstr = repr.substr(op_found);

  if (imagstr[0] == '+')
    imagstr.erase(imagstr.begin());

  retpt.real = mpfloat(realstr);
  retpt.imag = mpfloat(imagstr);

  return retpt;
} 


// accessors for the Whole Complex Point

mpcomplex MPoint :: Get_C() { return C; }
ldcomplex MPoint :: Get_c() { return c; }

void MPoint :: Set_c(std::string c_in) {
  this->C = this->_get_mpcomplex_from_str_repr(c_in);
  this->c = ldcomplex( mpfr_get_ld(this->C.real.backend().data(), MPFR_RNDN), 
                       mpfr_get_ld(this->C.imag.backend().data(), MPFR_RNDN) );
}

void MPoint :: Set_c(ldcomplex c_in) { 
  this->Set_c( c_in.real(), c_in.imag() );
}
void MPoint :: Set_c(std::string x, std::string y) {
  this->Set_x(x);
  this->Set_y(y);
}
void MPoint :: Set_c(long double x, long double y) { 
  this->Set_x(x);
  this->Set_y(y);
}


// accessors for the Real Part of C

void MPoint :: Set_x(std::string x) { 
  C.real = mpfloat(x.c_str());
  c = ldcomplex( mpfr_get_ld(C.real.backend().data(), MPFR_RNDN),
                 c.imag() );
}
void MPoint :: Set_x(long double x) { 
  C.real = mpfloat(x);
  c = ldcomplex( x, c.imag() );
}

mpfloat MPoint :: Get_x() { return C.real; }


// accessors for the Imaginary Part of C

void MPoint :: Set_y(std::string y) { 
  C.imag = mpfloat(y.c_str());
  c = ldcomplex( c.real(), 
                 mpfr_get_ld(C.imag.backend().data(), MPFR_RNDN) );
}
void MPoint :: Set_y(long double y) { 
  C.imag = mpfloat(y);
  c = ldcomplex( c.real(), y );
}

mpfloat MPoint :: Get_y() { return C.imag; }


// accessors for other properties of this MPoint ...

void MPoint :: Set_Prec(unsigned long prec_in) { prec = prec_in; }
unsigned long MPoint :: Get_Prec() { return prec; }


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
** run the mandelbrot algorithm using this point as c... with overrides
*/

/*********************************************
 * attempt at multiprec version is unnec. slow for now ... 
 *********************************************
void MPoint :: Run_MFun(unsigned long itermax, mpfloat x, mpfloat y) {
  mpfloat tmp;
  long unsigned i = 0;
  
  while ( (x*x + y*y < 4.0) || (i < itermax) ) {
    tmp = x*x - y*y + c.real;
    y = 2*x*y + c.imag;
    x = tmp;
    ++i;
  }
  iter = i;
  if (iter == itermax) inmset = true;
}
\***********************************************/

// dummy override handlers for Run_MFun(unsig, ldcomplex) ...

void MPoint :: Run_MFun(unsigned long itermax, long double x, long double y) {
  this->Run_MFun( itermax, ldcomplex(x, y) );
}
void MPoint :: Run_MFun(unsigned long itermax, std::string x, std::string y) {
  this->Run_MFun( itermax, ldcomplex(strtold(x.c_str(), NULL), 
                                     strtold(y.c_str(), NULL)) );
} 
void MPoint :: Run_MFun(unsigned long itermax, std::string z0) {
  mpcomplex Z0 = this->_get_mpcomplex_from_str_repr(z0);
  this->Run_MFun( itermax, 
                  mpfr_get_ld(Z0.real.backend().data(), MPFR_RNDN),
                  mpfr_get_ld(Z0.imag.backend().data(), MPFR_RNDN) );
}

void MPoint :: Run_MFun(unsigned long itermax, ldcomplex z0) {
  //  this->Run_MFun( itermax, z0.real(), z0.imag() );
  long double zz;
  ldcomplex z = z0;
  long unsigned i = 0;
  ldcomplex c_ld = this->c;

  while(i<itermax) {
    z = z*z + c_ld;
    zz = (z.real()*z.real()) + (z.imag()*z.imag());
    if (zz>4.0) break;
    ++i;
  }
  iter = i;
  if (iter == itermax) inmset = true;
}


/*
** Wrapper for boost.python tying it all together ...
*/

void (MPoint::*set_c0)(std::string) = &MPoint::Set_c;
void (MPoint::*set_c1)(ldcomplex) = &MPoint::Set_c;
void (MPoint::*set_c2)(std::string, std::string) = &MPoint::Set_c;
void (MPoint::*set_c3)(long double, long double) = &MPoint::Set_c;
ldcomplex (MPoint::*get_c)() = &MPoint::Get_c;
mpcomplex (MPoint::*get_C)() = &MPoint::Get_C;

void (MPoint::*set_x0)(std::string) = &MPoint::Set_x;
void (MPoint::*set_x1)(long double) = &MPoint::Set_x;
mpfloat (MPoint::*get_x)() = &MPoint::Get_x;

void (MPoint::*set_y0)(std::string) = &MPoint::Set_y;
void (MPoint::*set_y1)(long double) = &MPoint::Set_y;
mpfloat (MPoint::*get_y)() = &MPoint::Get_y;

void (MPoint::*run_mfun0)(unsigned long, std::string, std::string) = &MPoint::Run_MFun;
void (MPoint::*run_mfun3)(unsigned long, long double, long double) = &MPoint::Run_MFun;
void (MPoint::*run_mfun1)(unsigned long, std::string) = &MPoint::Run_MFun;
void (MPoint::*run_mfun2)(unsigned long, ldcomplex) = &MPoint::Run_MFun;


using namespace boost::python;

BOOST_PYTHON_MODULE(_mpoint) 
{
  class_<MPoint>( "MPoint", init<std::string, unsigned int>() )
    .def( init<ldcomplex, unsigned int>() )
    .def( init<std::string, std::string, unsigned int>() )
    .def( init<long double, long double, unsigned int>() )
    .def( "Set_Index", &MPoint::Set_Index )
    .def( "Get_ix", &MPoint::Get_ix )
    .def( "Get_iy", &MPoint::Get_iy )
    .def( "Set_c", set_c0 )
    .def( "Set_c", set_c1 )
    .def( "Set_c", set_c2 )
    .def( "Set_c", set_c3 )
    .def( "Run_MFun", run_mfun0 )
    .def( "Run_MFun", run_mfun1 )
    .def( "Run_MFun", run_mfun2 )
    .def( "Run_MFun", run_mfun3 )
    .add_property( "C", get_C, set_c0 )     // 2 props here for __future__ ref ... 
    .add_property( "c", get_c, set_c1 )     // BigVar will be mpfr_t or the like.
    //    .add_property( "Real", get_x, set_x0 )
    .add_property( "real", get_x, set_x1 )
    //    .add_property( "Imag", get_y, set_y0 )
    .add_property( "imag", get_y, set_y1 )
    .add_property( "prec", &MPoint::Get_Prec, &MPoint::Set_Prec )
    .add_property( "iter", &MPoint::Get_Iter, &MPoint::Set_Iter )
    .add_property( "inmset", &MPoint::Get_InMSet, &MPoint::Set_InMSet )
    ;
}
