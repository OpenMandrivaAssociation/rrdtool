%define major 2
%define libname %mklibname rrdtool %{major}
%define develname %mklibname -d rrdtool
%define oldlibname %mklibname rrdtool 0

Summary:	RRDTool - round robin database
Name:		rrdtool
Version:	1.2.23
Release:	%mkrel 1
License:	GPL
Group:		Networking/Other
URL:		http://ee-staff.ethz.ch/~oetiker/webtools/rrdtool/
Source:		http://ee-staff.ethz.ch/~oetiker/webtools/rrdtool/pub/%{name}-%{version}.tar.bz2
Patch0:		rrdtool-1.2.12-pic.diff
BuildRequires:	png-devel >= 1.0.3
BuildRequires:	perl-devel
BuildRequires:	libgd-devel
BuildRequires:	zlib-devel
BuildRequires:	cgilib-devel
BuildRequires:	freetype-devel
BuildRequires:	libart_lgpl-devel
BuildRequires:	python-devel
BuildRequires:	chrpath
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	tcl tcl-devel
Buildroot:	%{_tmppath}/%{name}-%{version}-root

%description
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average). It stores the data in a very compact way that will not
expand over time, and it presents useful graphs by processing the data to
enforce a certain data density. It can be used either via simple wrapper
scripts (from shell or Perl) or via frontends that poll network devices and
put a friendly user interface on it.

%package -n	%{libname}
Summary:	RRDTool - round robin database shared libraries
Version:	%{version}
Group:		System/Libraries
Obsoletes:	%{oldlibname}

%description -n	%{libname}
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average). This package allow you to use this library directly.

%package -n	%{develname}
Summary:	Development libraries and headers for %{libname}
Group:		Development/Other
Requires:	%{libname} = %{version}
Requires:	libpng-devel >= 1.0.3
Requires:	perl-devel
Requires:	libgd-devel
Requires:	zlib-devel
Requires:	cgilib-devel
Requires:	freetype-devel
Requires:	libart_lgpl-devel
Provides:	librrdtool-devel
Obsoletes:	rrdtool-devel
Obsoletes:	%{oldlibname}-devel
Obsoletes:	%{libname}-devel
Provides:	rrdtool-devel = %{version}-%{release}

%description -n	%{develname}
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average).

This package provides development libraries and headers for %{libname}.

%package -n	perl-%{name}
Summary:	RRD Tool Perl interface
Group:		Development/Perl
Requires:	%{name} = %{version}

%description -n	perl-%{name}
The RRD Tools Perl modules.

%package -n	python-%{name}
Summary:	RRD Tool Python interface
Group:		Development/Python
Requires:	%{name} = %{version}  python >= 2.3

%description -n	python-%{name}
The RRD Tools Python modules.

%package -n	tcl-%{name}
Summary:	RRD Tool TCL interface
Group:		Development/Other
Requires:	%{name} = %{version}
Requires:	tcl

%description -n	tcl-%{name}
The RRD Tools TCL modules.

%prep

%setup -q
%patch0 -p1 -b .pic

# annoyance be gone
perl -pi -e "s|^sleep .*|usleep 10000|g" configure.*

# lib64 fix
perl -pi -e 's|/lib\b|/%{_lib}|g' configure* Makefile.*

%build
libtoolize --copy --force && aclocal-1.7 && autoconf && automake-1.7 --add-missing

#CFLAGS="$RPM_OPT_FLAGS" LIBS="-lm -lz -lpng"
OPT_FLAGS=`echo $RPM_OPT_FLAGS | sed -e "s/-ffast-math//"`
export CFLAGS="$OPT_FLAGS"

%configure2_5x \
    --with-rrd-default-font=%{_datadir}/rrdtool/fonts/DejaVuSansMono-Roman.ttf \
    --with-perl-options="INSTALLDIRS=vendor" \
    --enable-tcl-site

make

# @perl@ and @PERL@ correction
%{__find} -type f | xargs %{__perl} -pi -e 's|^#! @perl@|#!/usr/bin/perl|gi'
%{__find} -name "*.pl" | xargs %{__perl} -pi -e 's;\015;;gi'

%install
%{__rm} -rf %{buildroot}

%makeinstall_std

# equivalent of "make site-perl-install" except for the PREFIX
# "make site-perl-install" is not done by "make install"
%makeinstall_std -C bindings/perl-piped install_vendor
%makeinstall_std -C bindings/perl-shared install_vendor

%{__install} -d %{buildroot}%{_sbindir}

# now create include and files
%{__install} -d %{buildroot}%{_includedir}
%{__install} -m644 src/rrd*.h %{buildroot}%{_includedir}/

# moving the docs in the right place (another approach)
rm -rf installed_docs
mkdir -p installed_docs/{html,pod,txt}
cp doc/*.txt installed_docs/txt/
cp doc/*.pod installed_docs/pod/
cp doc/*.html installed_docs/html/

#removing things installed in the wrong place
%{__rm} -rf %{buildroot}%{_prefix}/lib/perl/*.pm
%{__rm} -rf %{buildroot}%{_prefix}/lib/perl/auto/RRDs/RRDs*
%{__rm} -rf %{buildroot}%{_prefix}/lib/perl5/site_perl
%{__rm} -rf %{buildroot}%{_prefix}/examples
%{__rm} -rf %{buildroot}%{_prefix}/shared
#%{__rm} -rf %{buildroot}%{_datadir}/rrdtool
#%{__rm} -rf %{buildroot}%{_prefix}/shared/doc

# icky ntmake.pl
%{__rm} -f %{buildroot}%{perl_vendorarch}/ntmake.pl

# I've tried and tried and tried to get rid of the rpath.
# It only appears after you do a make install, so I have
# no idea what is doing it but this gets rid of it...
#chrpath -d %{buildroot}%{_bindir}/*

# the problem has now moved to the perl stuff...
find %{buildroot}%{_prefix}/lib/perl* -name "*.so" | xargs chrpath -d 

# and the tcl stuff
chrpath -d %{buildroot}%{_libdir}/tclrrd%{version}.so

# remove .in/.am files
find %{buildroot} -name "*.in" | xargs %{__rm} -f
find %{buildroot} -name "*.am" | xargs %{__rm} -f

%clean
%{__rm} -rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%files
%defattr(-,root,root)
%doc CONTRIBUTORS COPYING COPYRIGHT NEWS README THREADS TODO
%doc installed_docs/txt installed_docs/html
%{_bindir}/rrdcgi
%{_bindir}/rrdtool
%{_bindir}/rrdupdate
%{_datadir}/rrdtool
%{_mandir}/man1/*

%files -n %{libname}
%defattr(-,root,root)
%doc COPYING
%{_libdir}/librrd.so.%{major}*
%{_libdir}/librrd_th.so.*

%files -n %{develname}
%defattr(-,root,root)
%doc COPYING
%exclude %{_libdir}/tclrrd%{version}.so
%{_libdir}/*.so
%{_libdir}/*.a
%{_libdir}/*.la
%{_includedir}/*.h

%files -n perl-%{name}
%defattr (-,root,root)
%doc installed_docs/pod examples/*.pl
%{perl_vendorarch}/*.pm
%{perl_vendorlib}/*.pm
%dir %{perl_vendorarch}/auto/RRDs
%{perl_vendorarch}/auto/RRDs/RRDs.so
%{_mandir}/man3*/RRDp.3*
%{_mandir}/man3*/RRDs.3*

%files -n python-%{name}
%defattr (-,root,root)
%doc bindings/python/AUTHORS bindings/python/COPYING bindings/python/README
%py_platsitedir/*.so

%files -n tcl-%{name}
%defattr (-,root,root)
%doc bindings/tcl/README
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_libdir}/tclrrd%{version}.so
