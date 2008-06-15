%define major 4
%define libname %mklibname rrdtool %{major}
%define develname %mklibname -d rrdtool

Summary:	RRDTool - round robin database
Name:		rrdtool
Version:	1.3.0
Release:	%mkrel 2
License:	GPL+
Group:		Networking/Other
URL:		http://oss.oetiker.ch/rrdtool/
Source:		http://oss.oetiker.ch/rrdtool/pub/%{name}-%{version}.tar.gz
Patch0:		rrdtool-1.2.12-pic.diff
Patch1:		rrdtool-1.2.23-fix-examples.patch
Patch2:		rrdtool-bts428778-floating-point-exception.diff
Patch3:		rrdtool-autoconf262.diff
Patch4:		rrdtool-setup.py-module-name.diff
Patch6:		rrdtool-no-rpath.diff
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cairo-devel
BuildRequires:	cgilib-devel
BuildRequires:	chrpath
BuildRequires:	freetype-devel
BuildRequires:	gettext
BuildRequires:	gettext-devel
BuildRequires:	groff
BuildRequires:	intltool >= 0.35.0
BuildRequires:	libart_lgpl-devel
BuildRequires:	libgd-devel
BuildRequires:	perl-devel
BuildRequires:	png-devel >= 1.0.3
BuildRequires:	python-devel
BuildRequires:	tcl tcl-devel
BuildRequires:	zlib-devel
Buildroot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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
Provides:	rrdtool-devel = %{version}-%{release}
Provides:	librrdtool-devel = %{version}-%{release}
Obsoletes:	rrdtool-devel
Conflicts:	%{mklibname rrdtool 0 -d}
Conflicts:	%{mklibname rrdtool 2 -d}

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
%patch1 -p1
%patch2 -p0
%patch3 -p0
%patch4 -p0
%patch6 -p1

# annoyance be gone
perl -pi -e "s|^sleep .*|usleep 10000|g" configure.*

%build
autoreconf

%configure2_5x \
    --with-perl-options="INSTALLDIRS=vendor" \
    --enable-tcl-site --disable-ruby

make

%install
rm -rf %{buildroot}

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
mkdir -p installed_docs/{html,pod,txt,examples}
cp doc/*.txt installed_docs/txt/
cp doc/*.pod installed_docs/pod/
cp doc/*.html installed_docs/html/
cp examples/*.{cgi,pl} installed_docs/examples/

#removing things installed in the wrong place
%{__rm} -rf %{buildroot}%{_prefix}/lib/perl/*.pm
%{__rm} -rf %{buildroot}%{_prefix}/lib/perl/auto/RRDs/RRDs*
%{__rm} -rf %{buildroot}%{_prefix}/lib/perl5/site_perl
%{__rm} -rf %{buildroot}%{_prefix}/shared
%{__rm} -rf %{buildroot}%{_datadir}/doc/%{name}*

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

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CONTRIBUTORS COPYING COPYRIGHT NEWS README THREADS TODO
%doc installed_docs/txt installed_docs/html
%{_bindir}/rrdcgi
%{_bindir}/rrdtool
%{_bindir}/rrdupdate
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
%doc installed_docs/pod installed_docs/examples
%{perl_vendorarch}/*.pm
%{perl_vendorlib}/*.pm
%dir %{perl_vendorarch}/auto/RRDs
%{perl_vendorarch}/auto/RRDs/RRDs.so
%{_mandir}/man3*/RRDp.3*
%{_mandir}/man3*/RRDs.3*

%files -n python-%{name}
%defattr (-,root,root)
%doc bindings/python/AUTHORS bindings/python/COPYING bindings/python/README
%py_platsitedir/*

%files -n tcl-%{name}
%defattr (-,root,root)
%doc bindings/tcl/README
%dir %{_libdir}/%{name}
%{_libdir}/%{name}/*
%{_libdir}/tclrrd%{version}.so
