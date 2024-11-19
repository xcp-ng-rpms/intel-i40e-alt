%define vendor_name Intel
%define vendor_label intel
%define driver_name i40e

# XCP-ng: install to the override directory
%define module_dir override

## kernel_version will be set during build because then kernel-devel
## package installs an RPM macro which sets it. This check keeps
## rpmlint happy.
%if %undefined kernel_version
%define kernel_version dummy
%endif

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}-alt
Version: 2.26.8
Release: 1%{?dist}
License: GPL
Source0: intel-i40e-%{version}.tar.gz
Patch0: disable-fw-lldp-by-default.patch
Patch1: fix-memory-leak-and-other-bugs.patch

BuildRequires: gcc
BuildRequires: kernel-devel
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n %{vendor_label}-%{driver_name}-%{version}

%build
cd src
KSRC=/lib/modules/%{kernel_version}/build OUT=kcompat_generated_defs.h CONFFILE=/lib/modules/%{kernel_version}/build/.config bash kcompat-generator.sh
cd ..
%{make_build} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src KSRC=/lib/modules/%{kernel_version}/build modules

%install
%{__make} %{?_smp_mflags} -C /lib/modules/%{kernel_version}/build M=$(pwd)/src INSTALL_MOD_PATH=%{buildroot} INSTALL_MOD_DIR=%{module_dir} DEPMOD=/bin/true modules_install

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/*/*.ko

%changelog
* Fri Nov 15 2024 David Morel <david.morel@vates.tech> - 2.26.8-1
- Update from Intel's latest driver 2.26.8
- NEED_AUX_BUS=2 compiles auxiliary bus code within the driver, but our kernel
  already provides it. This leads to redefinition of AUXILIARY_MODULE_PREFIX,
  so remove it to make the driver compile.

* Mon Aug 21 2023 Gael Duperrey <gduperrey@vates.fr> - 2.22.20-3.1
- initial package, version 2.22.20-3.1
- Synced from XS driver SRPM intel-i40e-2.22.20-3.xs8~2_1.src.rpm
