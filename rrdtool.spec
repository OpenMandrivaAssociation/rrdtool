%define major 8
%define libname %mklibname rrd
%define oldlibname %mklibname rrd 8
%define devname %mklibname -d rrdtool
%define _disable_rebuild_configure 1
# Allow undefined references to python in the python module,
# those are not an error
%define _disable_ld_no_undefined 1

Summary:	Round Robin Database Tool to store and display time-series data
Name:		rrdtool
Version:	1.9.0
Release:	1
License:	GPLv2+
Group:		Networking/Other
Url:		http://oss.oetiker.ch/rrdtool/
Source0:	https://github.com/oetiker/rrdtool-1.x/releases/download/v%{version}/rrdtool-%{version}.tar.gz
Source1:	rrdcached.service
Source2:	rrdcached.sysconfig
Source3:	rrdcached.tmpfiles
Source100:	rrdtool.rpmlintrc
Patch1:         rrdtool-1.2.23-fix-examples.patch
Patch2:         rrdtool-1.4.1-avoid-version.diff
# Install tcl bindings to correct location as per policy (the upstream
# conditional that should nearly do this doesn't work) - AdamW 2008/12
Patch5:         rrdtool-1.4.8-tcl_location.diff
Patch6:         rrdtool-1.6.0-ruby-2-fix.patch
Patch9:         rrdtool-1.5.5-socket_dir.diff
BuildRequires:	chrpath
BuildRequires:	dbi-devel
BuildRequires:	gettext
BuildRequires:	groff
BuildRequires:	intltool >= 0.35.0
BuildRequires:	libtool
BuildRequires:	gd-devel
BuildRequires:	gettext-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig(cairo)
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	pkgconfig(freetype2) >= 2.4.6
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(libart-2.0)
BuildRequires:	pkgconfig(libpng)
BuildRequires:	pkgconfig(lua)
BuildRequires:	pkgconfig(pango) >= 1.28.4
BuildRequires:	pkgconfig(pangocairo)  >= 1.28.4
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(tcl)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	systemd-macros
Requires:	fonts-ttf-dejavu

%description
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average). It stores the data in a very compact way that will not
expand over time, and it presents useful graphs by processing the data to
enforce a certain data density. It can be used either via simple wrapper
scripts (from shell or Perl) or via frontends that poll network devices and
put a friendly user interface on it.

%package -n rrdcached
Summary:	Data caching daemon for RRDtool
Group:		System/Servers
BuildRequires:	rpm-helper
Requires(post,preun,pre,postun):	rpm-helper
Requires:	%{name} >= %{version}-%{release}

%description -n	rrdcached
rrdcached is a daemon that receives updates to existing RRD files, accumulates
them and, if enough have been received or a defined time has passed, writes the
updates to the RRD file. The daemon was written with big setups in mind which
usually runs into I/O related problems. This daemon was written to alleviate
these problems.

%package -n %{libname}
Summary:	RRDTool - round robin database shared libraries
Group:		System/Libraries
Obsoletes:	%{_lib}rrdtool4 < 1.4.8-7
Obsoletes:	%{mklibname rrd_th 8} < 1.7.0-2
%rename %{oldlibname}

%description -n %{libname}
This package contains a shared library for %{name}.

%package -n %{devname}
Summary:	Development libraries and headers for %{libname}
Group:		Development/Other
Requires:	%{libname} >= %{EVRD}
Provides:	%{name}-devel = %{EVRD}
Obsoletes:	%{_lib}rrdtool-devel < 1.4.8-7
Conflicts:	%{_lib}rrdtool4 < 1.4.8-7

%description -n %{devname}
RRD is the Acronym for Round Robin Database. RRD is a system to store and
display time-series data (i.e. network bandwidth, machine-room temperature,
server load average).

This package provides development libraries and headers for %{libname}.

%package -n perl-%{name}
Summary:	RRD Tool Perl interface
Group:		Development/Perl
Requires:	%{name} >= %{version}-%{release}

%description -n perl-%{name}
The RRD Tools Perl modules.

%package -n python-%{name}
Summary:	RRD Tool Python interface
Group:		Development/Python
Requires:	%{name} >= %{EVRD}

%description -n python-%{name}
The RRD Tools Python modules.

%package -n tcl-%{name}
Summary:	RRD Tool TCL interface
Group:		Development/Other
Requires:	%{name} >= %{EVRD}
Requires:	tcl

%description -n tcl-%{name}
The RRD Tools TCL modules.

%package -n lua-%{name}
Summary:	RRD Tool LUA interface
Group:		Development/Other
Requires:	%{name} >= %{EVRD}
Requires:	lua

%description -n lua-%{name}
The RRD Tools LUA module.

%prep
%autosetup -p1

cp %{SOURCE1} .
cp %{SOURCE2} .

%build
autoreconf -fi

# FIXME cross-compiling various bindings uses system headers causing
# incorrect intrinsics to be emitted... So for now we just exclude
# these bindings while crosscompiling
%configure \
	--disable-static \
	--with-systemdsystemunitdir="%{_unitdir}" \
%if %{cross_compiling}
	--disable-tcl \
	--disable-perl \
	--disable-python \
	--disable-lua \
%else
	--with-perl-options="INSTALLDIRS=vendor" \
	--enable-tcl-site \
%endif
	--disable-ruby \
	--disable-docs

%make_build -j1

%install
%make_install

%if ! %{cross_compiling}
# equivalent of "make site-perl-install" except for the PREFIX
# "make site-perl-install" is not done by "make install"
%make_install -C bindings/perl-piped install_vendor
%make_install -C bindings/perl-shared install_vendor
%endif

install -d %{buildroot}%{_sbindir}

# now create include and files
install -d %{buildroot}%{_includedir}
install -m644 src/rrd*.h %{buildroot}%{_includedir}/

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
rm -rf %{buildroot}%{_prefix}/lib/perl/*.pm
rm -rf %{buildroot}%{_prefix}/lib/perl/auto/RRDs/RRDs*
rm -rf %{buildroot}%{_prefix}/lib/perl5/site_perl
rm -rf %{buildroot}%{_prefix}/shared
rm -rf %{buildroot}%{_datadir}/doc/%{name}*

# icky ntmake.pl
rm -f %{buildroot}%{perl_vendorarch}/ntmake.pl

# I've tried and tried and tried to get rid of the rpath.
# It only appears after you do a make install, so I have
# no idea what is doing it but this gets rid of it...
chrpath -d %{buildroot}%{_bindir}/*

%if ! %{cross_compiling}
# the problem has now moved to the perl stuff...
find %{buildroot}/%{_libdir}/perl* -name "*.so" | xargs chmod u+w
find %{buildroot}/%{_libdir}/perl* -name "*.so" | xargs chrpath -d

# and the tcl stuff
chrpath -d %{buildroot}%{_libdir}/tclrrd%{version}.so
%endif

# remove .in/.am files
find %{buildroot} -name "*.in" | xargs rm -f
find %{buildroot} -name "*.am" | xargs rm -f

# install rrdcached files
install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}/var/lib/rrdcached
install -d %{buildroot}/var/run/rrdcached

install -D -m 755 %{SOURCE1} %{buildroot}%{_unitdir}/rrdcached.service
install -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/rrdcached
install -D -m 644 %{SOURCE3} %{buildroot}%{_prefix}/lib/tmpfiles.d/rrdcached.conf

# cleanup
rm -rf %{buildroot}%{_datadir}/rrdtool
rm -rf %{buildroot}%{_docdir}/python-rrdtool

# (tpg) systemd preset
install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-rrdcached.preset << EOF
enable rrdcached.socket
enable rrdcached.service
EOF

install -d %{buildroot}%{_sysusersdir}
cat > %{buildroot}%{_sysusersdir}/rrdcached.conf <<EOF
u rrdcached - %{_localstatedir}/lib/rrdcached /sbin/nologin
EOF

%find_lang %{name}

%files -f %{name}.lang
%doc CONTRIBUTORS COPYRIGHT NEWS THREADS TODO
%doc installed_docs/txt installed_docs/html
%{_bindir}/rrdcgi
%{_bindir}/rrdtool
%{_bindir}/rrdcreate
%{_bindir}/rrdinfo
%{_bindir}/rrdupdate

%files -n rrdcached
%config(noreplace) %{_sysconfdir}/sysconfig/rrdcached
%{_prefix}/lib/tmpfiles.d/rrdcached.conf
%{_sysusersdir}/rrdcached.conf
%{_presetdir}/86-rrdcached.preset
%{_unitdir}/rrdcached.service
%{_unitdir}/rrdcached.socket
%{_bindir}/rrdcached
%attr(0755,rrdcached,rrdcached) %dir /var/lib/rrdcached

%files -n %{libname}
%{_libdir}/librrd.so.%{major}*

%files -n %{devname}
%if ! %{cross_compiling}
%exclude %{_libdir}/tclrrd%{version}.so
%endif
%{_libdir}/*.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/librrd.pc

%if ! %{cross_compiling}
%files -n python-%{name}
%py_platsitedir/*

%files -n perl-%{name}
%doc installed_docs/pod installed_docs/examples
%{perl_vendorarch}/*.pm
%{perl_vendorlib}/*.pm
%dir %{perl_vendorarch}/auto/RRDs
%{perl_vendorarch}/auto/RRDs/RRDs.so
%{_mandir}/man3*/RRDp.3*
%{_mandir}/man3*/RRDs.3*

%files -n tcl-%{name}
%doc bindings/tcl/README
%{tcl_sitearch}/tclrrd
%{_libdir}/tclrrd%{version}.so

%files -n lua-%{name}
%doc bindings/lua/README
%{_libdir}/lua/*/rrd.so
%endif
