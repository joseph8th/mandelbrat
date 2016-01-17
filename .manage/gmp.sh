# EXPERIMENTAL: attempt to install gmp>=5.0.x in custom location

function run_install_gmp {
    
    pkg_basename=gmp-6.0.0a
    gmp_dir=gmp-6.0.0
    prefix=/usr/local/lib

    # attempts to install gmp v6.0.0a
    pkg_sha256=8890803a2715d592eac37dca630e36b470f047eb5ab1efe38d323b02a99ac232
    pkg_url="https://ftp.gnu.org/gnu/gmp/${pkg_basename}.tar.bz2"

    # download and decompress the tarball
    wget $pkg_url
    bzip2 -d "${pkg_basename}.tar.bz2"

    # sha256 checksum the tarball
    sha_ary=( $(sha256sum "${pkg_basename}.tar") )
    if [[ "$pkg_sha256" != "${sha_ary[0]}" ]]; then
        echo "==> Error: SHA256 checksum does not match!"
        _err; return
    fi

    # extract the files quietly, then attempt install
    tar -xf "${pkg_basename}.tar"
    cd "${gmp_dir}"

    ./configure
    [[ ! "$?" ]] && _err && return

    make
    [[ ! "$?" ]] && _err && return

    make install --prefix "$prefix"
    [[ ! "$?" ]] && _err && return || return
}
