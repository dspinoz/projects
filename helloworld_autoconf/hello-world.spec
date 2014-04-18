Name:           hello-world
Version:        1.0
Release:        1%{?dist}
Summary:        Hello World program made with autoconf

License:        GPL
URL:            http://dspinoz/hello-world
Source0:        http://dspinoz/hello-world-1.0.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Hello world program created with autoconf

%prep
%setup -q
echo %{_target}, %{_target_cpu}, and %{_target_os}

%build
%configure
make %{?_smp_mflags} 
make check

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc
/usr/bin/hello

%changelog
