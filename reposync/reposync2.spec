Name:           reposync2
Version:        0.5
Release:        1%{?dist}
Summary:        Build incrementals from reposync

License:        Free
URL:            https://github.com/dspinoz/projects/reposync
Source0:        reposync2-%{version}.tgz

BuildRequires:  make tar python
Requires:       python yum-utils createrepo

%description
Yum plugin for building incremental downloads from reposync.

%prep
%setup -q

%build
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
%make_install


%files
%config /etc/yum/pluginconf.d/reposync2.conf
/usr/share/yum-plugins/reposync2.py
/usr/share/yum-plugins/reposync2.pyc
/usr/share/yum-plugins/reposync2.pyo


%changelog
