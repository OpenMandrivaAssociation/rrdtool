%define major 4
%define libname %mklibname rrdtool %{major}
%define develname %mklibname -d rrdtool

Summary:	Round Robin Database Tool to store and display time-series data
Name:		rrdtool
Version:	1.4.7
Release:	1
License:	GPLv2+
Group:		Networking/Other
URL:		http://oss.oetiker.ch/rrdtool/
Source0:	http://oss.oetiker.ch/rrdtool/pub/%{name}-%{version}.tar.gz
Source1:	rrdcached.init
Source2:	rrdcached.sysconfig
Patch0:		rrdtool-1.4.7-pic.diff
Patch1:		rrdtool-1.2.23-fix-examples.patch
Patch2:		rrdtool-1.4.1-avoid-version.diff
Patch3:		rrdtool-setup.py-module-name.diff
Patch4:		rrdtool-1.4.7-no-rpath.diff
# Install tcl bindings to correct location as per policy (the upstream
# conditional that should nearly do this doesn't work) - AdamW 2008/12
Patch5:		rrdtool-1.3.4-tcl_location.patch
# Relax version requirement for Tcl, it breaks if you're using a
# pre-release - AdamW 2008/12
Patch6:		rrdtool-1.3.4-tcl_require.patch
Patch7:		rrdtool-1.4.1-tcl_soname.diff
Patch8:		rrdtool-1.4.4-gettext-0.17_hack.diff
Requires:	fonts-ttf-dejavu
BuildRequires:	autoconf automake libtool
BuildRequires:	cairo-devel >= 1.10.2
BuildRequires:	chrpath
BuildRequires:	dbi-devel
BuildRequires:	fontconfig-devel >= 2.8.0
BuildRequires:	freetype2-devel >= 2.4.6
BuildRequires:	gd-devel
BuildRequires:	gettext
BuildRequires:	gettext-devel
BuildRequires:	glib2-devel
BuildRequires:	groff
BuildRequires:	intltool >= 0.35.0
BuildRequires:	libart_lgpl-devel
BuildRequires:	libpng-devel >= 1.5
BuildRequires:	lua-devel
BuildRequires:	perl-devel
BuildRequires:	pkgconfig
BuildRequires:	pkgconfig(pango) >= 1.28.4
BuildRequires:	pkgconfig(pangocairo)  >= 1.28.4
BuildRequires:	python-devel
BuildRequires:	tcl tcl-devel
BuildRequires:	zlib-devel

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
Requires:	gd-devel
Requires:	zlib-devel
Requires:	freetype2-devel
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

rm -f %{buildroot}%{_libdir}/*.*a

%pre -n rrdcached
%_pre_useradd rrdcached /var/lib/rrdcached /sbin/nologin

%post -n rrdcached
%_post_service rrdcached

%preun -n rrdcached
%_preun_service rrdcached

%postun -n rrdcached
%_postun_userdel rrdcached

%files
%doc CONTRIBUTORS COPYING COPYRIGHT NEWS README THREADS TODO
%doc installed_docs/txt installed_docs/html
%{_bindir}/rrdcgi
%{_bindir}/rrdtool
%{_bindir}/rrdupdate
%exclude %{_mandir}/man1/rrdcached.1*
%{_mandir}/man1/*

%files -n rrdcached
%{_initrddir}/rrdcached
%{_sysconfdir}/sysconfig/rrdcached
%{_bindir}/rrdcached
%attr(0755,rrdcached,rrdcached) %dir /var/lib/rrdcached
%attr(0755,rrdcached,rrdcached) %dir /var/run/rrdcached
%{_mandir}/man1/rrdcached*

%files -n %{libname}
%doc COPYING
%{_libdir}/librrd.so.%{major}*
%{_libdir}/librrd_th.so.*
%{_mandir}/man3/librrd.3*

%files -n %{develname}
%doc COPYING
%exclude %{_libdir}/tclrrd%{version}.so
%{_libdir}/*.so
%{_includedir}/*.h
%{_libdir}/pkgconfig/librrd.pc

%files -n perl-%{name}
%doc installed_docs/pod installed_docs/examples
%{perl_vendorarch}/*.pm
%{perl_vendorlib}/*.pm
%dir %{perl_vendorarch}/auto/RRDs
%{perl_vendorarch}/auto/RRDs/RRDs.so
%{_mandir}/man3*/RRDp.3*
%{_mandir}/man3*/RRDs.3*

%files -n python-%{name}
%doc bindings/python/AUTHORS bindings/python/COPYING bindings/python/README
%py_platsitedir/*

%files -n tcl-%{name}
%doc bindings/tcl/README
%{tcl_sitearch}/tclrrd
%{_libdir}/tclrrd%{version}.so

%files -n lua-%{name}
%doc bindings/lua/README
%{_prefix}/lib/lua/*/rrd.so


%changelog
* Sat Jan 28 2012 Oden Eriksson <oeriksson@mandriva.com> 1.4.7-1
+ Revision: 769516
- 1.4.7
- rediff some patches
- fix deps

* Sun Jan 22 2012 Oden Eriksson <oeriksson@mandriva.com> 1.4.5-7
+ Revision: 765962
- rebuilt for perl-5.14.2

* Sat Nov 26 2011 Oden Eriksson <oeriksson@mandriva.com> 1.4.5-6
+ Revision: 733655
- nuke the chngelog
- nuke static libs as well
- more deps
- attempt to fix the new build deps hell
- nuke the *.la files because it was removed in fontconfig

* Sun Nov 20 2011 Oden Eriksson <oeriksson@mandriva.com> 1.4.5-5
+ Revision: 731965
- rebuild
- slight cleanups
- remove some quite annoying /usr/usr

* Tue Sep 13 2011 Tomasz Pawel Gajc <tpg@mandriva.org> 1.4.5-4
+ Revision: 699591
- rebuild for new libpng15

* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 1.4.5-3
+ Revision: 669450
- mass rebuild

* Wed Dec 29 2010 Oden Eriksson <oeriksson@mandriva.com> 1.4.5-2mdv2011.0
+ Revision: 625977
- make rrdcached actually work...

* Wed Dec 29 2010 Oden Eriksson <oeriksson@mandriva.com> 1.4.5-1mdv2011.0
+ Revision: 625745
- 1.4.5

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 1.4.4-5mdv2011.0
+ Revision: 609661
- rebuilt against new libdbi

* Fri Nov 05 2010 Funda Wang <fwang@mandriva.org> 1.4.4-4mdv2011.0
+ Revision: 593649
- do not apply patch8 now

  + Michael Scherer <misc@mandriva.org>
    - rebuild for python 2.7

* Sun Aug 01 2010 Funda Wang <fwang@mandriva.org> 1.4.4-3mdv2011.0
+ Revision: 564329
- rebuild for perl 5.12.1

* Thu Jul 22 2010 Jérôme Quelin <jquelin@mandriva.org> 1.4.4-2mdv2011.0
+ Revision: 556775
- rebuild for perl 5.12

* Mon Jul 12 2010 Oden Eriksson <oeriksson@mandriva.com> 1.4.4-1mdv2011.0
+ Revision: 551262
- 1.4.4

* Thu Mar 25 2010 Oden Eriksson <oeriksson@mandriva.com> 1.4.3-1mdv2010.1
+ Revision: 527343
- 1.4.3
- rediffed one patch

* Sat Jan 02 2010 Frederik Himpe <fhimpe@mandriva.org> 1.4.2-1mdv2010.1
+ Revision: 484959
- update to new version 1.4.2

* Sat Nov 07 2009 Oden Eriksson <oeriksson@mandriva.com> 1.4.1-1mdv2010.1
+ Revision: 462388
- fix deps (lua-devel)
- 1.4.1
- rediffed some patches
- added some patches
- added the new rrdcached and lua-rrdtool packages
- fix deps

* Wed Sep 23 2009 Oden Eriksson <oeriksson@mandriva.com> 1.3.8-2mdv2010.0
+ Revision: 447849
- fix build
- fix #52619 (RRDTool needs at least a font installed)

* Tue May 19 2009 Oden Eriksson <oeriksson@mandriva.com> 1.3.8-1mdv2010.0
+ Revision: 377718
- 1.3.8

  + Christophe Fergeau <cfergeau@mandriva.com>
    - make sure autoreconf updates libtool files to avoid libtool 1.5/2.2 mismatches

* Mon Jan 19 2009 Guillaume Rousse <guillomovitch@mandriva.org> 1.3.6-1mdv2009.1
+ Revision: 331396
- new version

* Sat Dec 27 2008 Funda Wang <fwang@mandriva.org> 1.3.4-4mdv2009.1
+ Revision: 319793
- rediff pic patch
- rebuild for new python

* Sat Dec 06 2008 Adam Williamson <awilliamson@mandriva.org> 1.3.4-3mdv2009.1
+ Revision: 310981
- rebuild for new tcl
- add tcl_require.patch to relax a tcl requirement
- add tcl_location.patch to install to new location per policy

* Sun Nov 09 2008 Oden Eriksson <oeriksson@mandriva.com> 1.3.4-2mdv2009.1
+ Revision: 301463
- rebuilt against new libxcb

* Mon Oct 27 2008 Oden Eriksson <oeriksson@mandriva.com> 1.3.4-1mdv2009.1
+ Revision: 297570
- 1.3.4
- rediffed P6

* Mon Sep 15 2008 Oden Eriksson <oeriksson@mandriva.com> 1.3.3-1mdv2009.0
+ Revision: 285022
- 1.3.3
- drop the autoconf262 patch, it's in there

* Thu Jul 24 2008 Funda Wang <fwang@mandriva.org> 1.3.1-1mdv2009.0
+ Revision: 245284
- New version 1.3.1

* Sun Jun 15 2008 Oden Eriksson <oeriksson@mandriva.com> 1.3.0-2mdv2009.0
+ Revision: 219316
- fix deps (again)
- fix deps
- bump release
- fix deps
- fix autopoo borkiness with P3
- fix deps
- 1.3.0
- rediffed and removed some patches

  + Pixel <pixel@mandriva.com>
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Sun May 04 2008 Oden Eriksson <oeriksson@mandriva.com> 1.2.27-2mdv2009.0
+ Revision: 201008
- added P2-P6 from debian
- added P7 to fix autoconf-2.62 borkiness
- rebuild

* Sun Feb 17 2008 Guillaume Rousse <guillomovitch@mandriva.org> 1.2.27-1mdv2008.1
+ Revision: 169874
- update to new version 1.2.27

* Mon Jan 14 2008 Pixel <pixel@mandriva.com> 1.2.26-2mdv2008.1
+ Revision: 151324
- rebuild for perl-5.10.0

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Nov 21 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.2.26-1mdv2008.1
+ Revision: 110981
- new version
  drop useless CFLAGS mangling, no -ffast-math anymore

* Thu Sep 20 2007 Adam Williamson <awilliamson@mandriva.org> 1.2.23-4mdv2008.0
+ Revision: 91518
- rebuild to try and fix #33813
- new license policy

* Thu Sep 20 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.2.23-3mdv2008.0
+ Revision: 91232
- fix perl examples and ship them in documentation

* Wed Sep 19 2007 Guillaume Rousse <guillomovitch@mandriva.org> 1.2.23-2mdv2008.0
+ Revision: 90261
- rebuild

* Wed Aug 08 2007 Funda Wang <fwang@mandriva.org> 1.2.23-1mdv2008.0
+ Revision: 60125
- disable ruby binding
- fix file list
- add missing BR
- New version 1.2.23


* Fri Jan 26 2007 Oden Eriksson <oeriksson@mandriva.com> 1.2.18-1mdv2007.0
+ Revision: 113731
- 1.2.18

* Wed Dec 13 2006 Nicolas Lécureuil <neoclust@mandriva.org> 1.2.15-3mdv2007.1
+ Revision: 96486
- Rebuild against new python
- Import rrdtool

* Fri Aug 11 2006 Emmanuel Andry <eandry@mandriva.org> 1.2.15-2mdv2007.0
- fix python path for x86_64

* Mon Jul 24 2006 Emmanuel Andry <eandry@mandriva.org> 1.2.15-1mdv2007.0
- 1.2.15

* Sat Jul 01 2006 Stefan van der Eijk <stefan@eijk.nu> 1.2.13-2
- png rebuild

* Fri May 05 2006 Oden Eriksson <oeriksson@mandriva.com> 1.2.13-1mdk
- 1.2.13

* Wed Jan 04 2006 Oden Eriksson <oeriksson@mandriva.com> 1.2.12-2mdk
- rebuilt against soname aware deps (tcl/tk)
- fix deps

* Tue Dec 20 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.12-1mdk
- 1.2.12
- rediffed P0

* Wed Jul 27 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.11-1mdk
- 1.2.11 (Minor bugfixes)
- added the tcl bindings sub package
- added one lib64 fix

* Sun Jun 05 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.9-1mdk
- 1.2.9

* Thu May 19 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.8-1mdk
- 1.2.8
- added the python sub package

* Mon May 16 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.6-3mdk
- obsolete the old libname and devel packages

* Sun May 15 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.6-2mdk
- ship the provided ttf file

* Fri May 13 2005 Oden Eriksson <oeriksson@mandriva.com> 1.2.6-1mdk
- 1.2.6
- fix deps
- drop unneeded patches
- rediffed the pic patch (P0)
- don't ship the provided ttf file, it's in the fonts-ttf-dejavu
  package. instead use a more common font (a_d_mono.ttf) from the
  fonts-ttf-west_european package
- new major (2)
- merge ideas from the provided spec file, ie. obey perl package naming

* Fri May 13 2005 Oden Eriksson <oeriksson@mandriva.com> 1.0.50-1mdk
- 1.0.50
- rediffed the pic patch (P3)
- added one gcc4/amd64 fix (debian)

* Thu Nov 18 2004 Michael Scherer <misc@mandrake.org> 1.0.49-3mdk
- Rebuild for new perl

* Tue Oct 05 2004 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.0.49-2mdk
- merge lost fixes from 10.0-branch:
  * build DSO with -fPIC

* Mon Aug 09 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 1.0.49-1mdk
- 1.0.49
- fix P0

* Sat Jun 12 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 1.0.48-2mdk
- rebuild against new gd

* Fri May 21 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 1.0.48-1mdk
- 1.0.48
- use the %%configure2_5x macro
- removed the php stuff, broke it out into its own package

* Tue Apr 06 2004 Erwan Velu <erwan@mandrake.org> 1.0.47-1mdk
- 1.0.47

