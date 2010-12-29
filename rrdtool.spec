%define major 4
%define libname %mklibname rrdtool %{major}
%define develname %mklibname -d rrdtool

Summary:	Round Robin Database Tool to store and display time-series data
Name:		rrdtool
Version:	1.4.5
Release:	%mkrel 1
License:	GPLv2+
Group:		Networking/Other
URL:		http://oss.oetiker.ch/rrdtool/
Source0:	http://oss.oetiker.ch/rrdtool/pub/%{name}-%{version}.tar.gz
Source1:	rrdcached.init
Source2:	rrdcached.sysconfig
Patch0:		rrdtool-1.3.4-pic.diff
Patch1:		rrdtool-1.2.23-fix-examples.patch
Patch2:		rrdtool-1.4.1-avoid-version.diff
Patch3:		rrdtool-setup.py-module-name.diff
Patch4:		rrdtool-1.3.6-no-rpath.patch
# Install tcl bindings to correct location as per policy (the upstream
# conditional that should nearly do this doesn't work) - AdamW 2008/12
Patch5:		rrdtool-1.3.4-tcl_location.patch
# Relax version requirement for Tcl, it breaks if you're using a
# pre-release - AdamW 2008/12
Patch6:		rrdtool-1.3.4-tcl_require.patch
Patch7:		rrdtool-1.4.1-tcl_soname.diff
Patch8:		rrdtool-1.4.4-gettext-0.17_hack.diff
Requires:	fonts-ttf-dejavu
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	cairo-devel
BuildRequires:	chrpath
BuildRequires:	dbi-devel
BuildRequires:	freetype-devel
BuildRequires:	gettext
BuildRequires:	gettext-devel
BuildRequires:	glib2-devel
BuildRequires:	groff
BuildRequires:	intltool >= 0.35.0
BuildRequires:	libart_lgpl-devel
BuildRequires:	libgd-devel
BuildRequires:	libtool
BuildRequires:	lua-devel
BuildRequires:	pango-devel
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

%package -n	rrdcached
Summary:	Data caching daemon for RRDtool
Group:		System/Servers
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	%{name} >= %{version}-%{release}

%description -n	rrdcached
rrdcached is a daemon that receives updates to existing RRD files, accumulates
them and, if enough have been received or a defined time has passed, writes the
updates to the RRD file. The daemon was written with big setups in mind which
usually runs into I/O related problems. This daemon was written to alleviate
these problems.

%package -n	%{libname}
Summary:	RRDTool - round robin database shared libraries
Group:		System/Libraries

%description -n	%{libname}
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average). This package allow you to use this library directly.

%package -n	%{develname}
Summary:	Development libraries and headers for %{libname}
Group:		Development/Other
Requires:	%{libname} >= %{version}-%{release}
Requires:	perl-devel
Requires:	libgd-devel
Requires:	zlib-devel
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
Requires:	%{name} >= %{version}-%{release}

%description -n	perl-%{name}
The RRD Tools Perl modules.

%package -n	python-%{name}
Summary:	RRD Tool Python interface
Group:		Development/Python
Requires:	%{name} >= %{version}-%{release}
Requires:	python >= 2.3

%description -n	python-%{name}
The RRD Tools Python modules.

%package -n	tcl-%{name}
Summary:	RRD Tool TCL interface
Group:		Development/Other
Requires:	%{name} >= %{version}-%{release}
Requires:	tcl

%description -n	tcl-%{name}
The RRD Tools TCL modules.

%package -n	lua-%{name}
Summary:	RRD Tool LUA interface
Group:		Development/Other
Requires:	%{name} >= %{version}-%{release}
Requires:	lua

%description -n	lua-%{name}
The RRD Tools LUA module.

%prep

%setup -q
%patch0 -p1 -b .pic
%patch1 -p1
%patch2 -p0
%patch3 -p0
%patch4 -p1
%patch5 -p1 -b .tcl_location
%patch6 -p1 -b .tcl_require
%patch7 -p0 -b .tcl_soname

cp %{SOURCE1} .
cp %{SOURCE2} .

# annoyance be gone
perl -pi -e "s|^sleep .*|usleep 10000|g" configure.*

# friggin gettext bump
gettext_version=`gettext --version | head -1 | awk '{ print $4}'`
perl -pi -e "s|^AM_GNU_GETTEXT_VERSION.*|AM_GNU_GETTEXT_VERSION\($gettext_version\)|g" configure.ac

%build
mkdir -p m4
autoreconf -fi

%configure2_5x \
    --disable-rpath \
    --disable-static \
    --with-perl-options="INSTALLDIRS=vendor" \
    --enable-tcl-site \
    --disable-ruby

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
mkdir -p installed_docs/{html,pod,txt,examples/rrdcached}
cp doc/*.txt installed_docs/txt/
cp doc/*.pod installed_docs/pod/
cp doc/*.html installed_docs/html/
cp examples/*.{cgi,pl} installed_docs/examples/
cp examples/rrdcached/*.{pm,pl} installed_docs/examples/rrdcached/
# fix attribs
find installed_docs -type f | xargs chmod 644

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

# install rrdcached files
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/var/lib/rrdcached
install -d %{buildroot}/var/run/rrdcached

install -m0755 rrdcached.init %{buildroot}%{_initrddir}/rrdcached
install -m0644 rrdcached.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/rrdcached

# cleanup
rm -f %{buildroot}%{_prefix}/lib/lua/*/*.*a
rm -rf %{buildroot}%{_datadir}/rrdtool

%if %mdkversion < 200900
%post -n %{libname} -p /sbin/ldconfig
%endif

%if %mdkversion < 200900
%postun -n %{libname} -p /sbin/ldconfig
%endif

%pre -n rrdcached
%_pre_useradd rrdcached /var/lib/rrdcached /sbin/nologin

%post -n rrdcached
%_post_service rrdcached

%preun -n rrdcached
%_preun_service rrdcached

%postun -n rrdcached
%_postun_userdel rrdcached

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc CONTRIBUTORS COPYING COPYRIGHT NEWS README THREADS TODO
%doc installed_docs/txt installed_docs/html
%{_bindir}/rrdcgi
%{_bindir}/rrdtool
%{_bindir}/rrdupdate
%exclude %{_mandir}/man1/rrdcached.1*
%{_mandir}/man1/*

%files -n rrdcached
%defattr(-,root,root)
%{_initrddir}/rrdcached
%{_sysconfdir}/sysconfig/rrdcached
%{_bindir}/rrdcached
%attr(0755,rrdcached,rrdcached) %dir /var/lib/rrdcached
%attr(0755,rrdcached,rrdcached) %dir /var/run/rrdcached
%{_mandir}/man1/rrdcached*

%files -n %{libname}
%defattr(-,root,root)
%doc COPYING
%{_libdir}/librrd.so.%{major}*
%{_libdir}/librrd_th.so.*
%{_mandir}/man3/librrd.3*

%files -n %{develname}
%defattr(-,root,root)
%doc COPYING
%exclude %{_libdir}/tclrrd%{version}.so
%{_libdir}/*.so
%{_libdir}/*.*a
%{_includedir}/*.h
%{_libdir}/pkgconfig/librrd.pc

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
%{tcl_sitearch}/tclrrd
%{_libdir}/tclrrd%{version}.so

%files -n lua-%{name}
%defattr (-,root,root)
%doc bindings/lua/README
%{_prefix}/lib/lua/*/rrd.so
