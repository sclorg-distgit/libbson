%{?scl:%scl_package libbson}
%{!?scl:%global pkg_name %{name}}

%global pythonscl rh-python36
%global buildscls %{?scl} %{pythonscl}

Name:       %{?scl_prefix}libbson
Version:    1.6.3
Release:    3%{?dist}
Summary:    Building, parsing, and iterating BSON documents
## Installed:
# COPYING:                              ASL 2.0
# THIRD_PARTY_NOTICES:                  other license texts
# src/bson/b64_ntop.h:                  ISC and MIT
# src/bson/b64_pton.h:                  ISC and MIT
# src/bson/bson-md5.h:                  zlib
# src/jsonsl:                           MIT (LICENSE file exists in git)
## Not installed:
# configure:                            FSFUL and GPLv2+ with exceptions
# aclocal.m4:                           FSFULLR
# Makefile.in:                          FSFULLR
# build/autotools/compile:              GPLv2+ with exceptions
# build/autotools/config.guess:         GPLv3+ with exceptions
# build/autotools/config.sub:           GPLv3+ with exceptions
# build/autotools/depcomp:              GPLv2+ with exceptions
# build/autotools/ltmain.sh:            GPLv2+ with exceptions
# build/autotools/m4/ax_pthread.m4:     GPLv3+ with exceptions
# build/autotools/m4/ax_check_compile_flag.m4:  GPLv3+ with exceptions
# build/autotools/m4/ax_check_link_flag.m4:     GPLv3+ with exceptions
# build/autotools/m4/libtool.m4:        FSFUL and FSFULLR and GPLv2+ with exceptions
# build/autotools/m4/lt~obsolete.m4:    FSFULLR
# build/autotools/m4/ltoptions.m4:      FSFULLR
# build/autotools/m4/ltsugar.m4:        FSFULLR
# build/autotools/m4/ltversion.m4:      FSFULLR
# build/autotools/missing:              GPLv2+ with exceptions
# build/autotools/install-sh:           MIT and Public Domain
# doc/html/_static/basic.css:           BSD
# doc/html/_static/doctools.js:         BSD
# doc/html/_static/jquery.js:           MIT
# doc/html/_static/jquery-3.1.0.js:     MIT
# doc/html/_static/mongoc.css:          MIT
# doc/html/_static/searchtools.js:      BSD
# doc/html/_static/underscore.js:       MIT
# doc/html/_static/underscore-1.3.1.js: MIT
# doc/html/_static/websupport.js:       BSD
# doc/mongoc-theme/static/mongoc.css_t: MIT
# doc/taglist.py:                       MIT
# src/bson/bson-stdint-win32.h:         BSD
License:    ASL 2.0 and ISC and MIT and zlib
URL:        https://github.com/mongodb/%{pkg_name}
Source0:    %{url}/releases/download/%{version}/%{pkg_name}-%{version}.tar.gz
# Do not install COPYING, install ChangeLog, distribution specific
Patch0:     %{pkg_name}-1.5.0-rc3-Install-documentation-according-to-guidelines.patch
# Fix undefined behavior exhibiting with GCC 7, bug #1420440,
# <https://jira.mongodb.org/browse/CDRIVER-2010>
Patch1:     %{pkg_name}-1.6.0-Fix-signed-integer-wrap-in-time2sub.patch
%{?scl:Requires: %{scl}-runtime}

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  coreutils
BuildRequires:  findutils
BuildRequires:  gcc
BuildRequires:  libtool
BuildRequires:  make
# sphinx-build is executed from a build script. Depend on the executable name
# instead of a package name not to be disturbed by transition to a different
# Python version.
BuildRequires:  /opt/rh/%{pythonscl}/root/usr/bin/sphinx-build
# Modified (with bson allocator and some warning fixes and huge indentation
# refactoring) jsonsl is bundled <https://github.com/mnunberg/jsonsl>.
# jsonsl upstream likes copylib approach and does not plan a release
# <https://github.com/mnunberg/jsonsl/issues/14>.
Provides:       bundled(jsonsl)

# we don't want to require or provide any pkgconfig(xxx) symbols
%global __pkgconfig_requires ""
%global __pkgconfig_provides ""

%description
This is a library providing useful routines related to building, parsing,
and iterating BSON documents <http://bsonspec.org/>.


%package devel
Summary:    Development files for %{name}
Group:      Development/Libraries
License:    ASL 2.0
Requires:   %{?scl_prefix}%{pkg_name}%{?_isa} = %{version}-%{release}
Requires:   pkgconfig


%description devel
This package contains libraries and header files needed for developing
applications that use %{pkg_name}.


%prep
%{?scl:scl enable %{buildscls} - << \EOF}
set -e
%setup -q -n %{pkg_name}-%{version}
%patch0 -p1
%patch1 -p1
# Remove pregenerated documentation
rm -r doc/html/_static doc/html/*.{html,inv,js} doc/man/*.3
# Generate build scripts from sources
autoreconf --force --install
sed -e 's|major=.$func_arith_result|major=.$verstring_prefix$func_arith_result|g' \
    -i build/autotools/ltmain.sh
%{?scl:EOF}


%build
%{?scl_prefix:export verstring_prefix="%{scl_prefix}"}
%{?scl:scl enable %{buildscls} - << \EOF}
set -e
# Switching experimental-features support changes ABI (bson_visitor_t type)
%configure \
    --disable-coverage \
    --disable-debug \
    --disable-debug-symbols \
    --enable-examples \
    --enable-extra-align \
    --disable-html-docs \
    --enable-libtool-lock \
    --disable-lto \
    --disable-maintainer-flags \
    --enable-man-pages \
    --disable-optimizations \
    --enable-shared \
    --disable-silent-rules \
    --disable-static \
    --enable-tests
# Explicit man target is needed for generating manual pages
make %{?_smp_mflags} all doc/man
%{?scl:EOF}


%install
%{?scl_prefix:export verstring_prefix="%{scl_prefix}"}
%{?scl:scl enable %{buildscls} - << \EOF}
set -e
make install DESTDIR=%{buildroot}
find %{buildroot} -name '*.la' -delete
# Install examples here because it's forbidden to use relative %%doc with
# installing into %%_pkgdocdir
install -d -m 0755 %{buildroot}%{_docdir}/%{pkg_name}-devel/examples
install -m 0644 -t %{buildroot}%{_docdir}/%{pkg_name}-devel/examples examples/*.c
%{?scl:EOF}


%check
%{?scl:scl enable %{scl} - << \EOF}
set -e
make %{?_smp_mflags} check
%{?scl:EOF}

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%{!?_licensedir:%global license %%doc}
%files
%license COPYING THIRD_PARTY_NOTICES
# AUTHORS is empty, README etc. are installed by "make install"
%{_docdir}/%{pkg_name}
%{_libdir}/*.so.*


%files devel
%{_docdir}/%{pkg_name}-devel
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_mandir}/man3/*


%changelog
* Wed Jun 21 2017 Marek Skalický <mskalick@redhat.com> - 1.6.3-3
- Remove pkgconfig() provides

* Wed Jun 21 2017 Marek Skalický <mskalick@redhat.com> - 1.6.3-2
- Rebase to libbson from Fedora 27 and convert it to SCL
- use newer shinx from rh-python36

* Wed May 24 2017 Petr Pisar <ppisar@redhat.com> - 1.6.3-1
- 1.6.3 bump

* Tue Mar 28 2017 Petr Pisar <ppisar@redhat.com> - 1.6.2-1
- 1.6.2 bump

* Tue Mar 07 2017 Petr Pisar <ppisar@redhat.com> - 1.6.1-1
- 1.6.1 bump

* Thu Feb 09 2017 Petr Pisar <ppisar@redhat.com> - 1.6.0-1
- 1.6.0 bump

* Wed Feb 08 2017 Petr Pisar <ppisar@redhat.com> - 1.5.3-2
- Fix undefined behavior exhibiting with GCC 7 (bug #1420440)

* Thu Jan 12 2017 Petr Pisar <ppisar@redhat.com> - 1.5.3-1
- 1.5.3 bump

* Wed Jan 11 2017 Remi Collet <remi@fedoraproject.org> - 1.5.2-1
- 1.5.2 bump

* Mon Dec 19 2016 Petr Pisar <ppisar@redhat.com> - 1.5.1-1
- 1.5.1 bump

* Thu Dec 01 2016 Petr Pisar <ppisar@redhat.com> - 1.5.0-1
- 1.5.0 bump

* Fri Nov 18 2016 Petr Pisar <ppisar@redhat.com> - 1.5.0-0.4.rc6
- 1.5.0-rc6 bump

* Fri Nov 04 2016 Petr Pisar <ppisar@redhat.com> - 1.5.0-0.3.rc4
- 1.5.0-rc4 bump

* Thu Oct 20 2016 Petr Pisar <ppisar@redhat.com> - 1.5.0-0.2.rc3
- 1.5.0-rc3 bump

* Thu Oct 13 2016 Petr Pisar <ppisar@redhat.com> - 1.5.0-0.1.rc2
- 1.5.0-rc2 bump

* Wed Sep 21 2016 Petr Pisar <ppisar@redhat.com> - 1.4.1-1
- 1.4.1 bump

* Mon Aug 29 2016 Petr Pisar <ppisar@redhat.com> - 1.4.0-1
- 1.4.0 bump

* Thu Mar 31 2016 Petr Pisar <ppisar@redhat.com> - 1.3.5-1
- 1.3.5 bump

* Tue Mar 15 2016 Petr Pisar <ppisar@redhat.com> - 1.3.4-1
- 1.3.4 bump

* Mon Feb 15 2016 Petr Pisar <ppisar@redhat.com> - 1.3.3-1
- 1.3.3 bump

* Fri Jan 22 2016 Petr Pisar <ppisar@redhat.com> - 1.3.1-1
- Packaged
