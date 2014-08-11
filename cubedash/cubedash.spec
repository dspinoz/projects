%{?nodejs_find_provides_and_requires}

Name:           nodejs-cubedash
Version:        0.0.1
Release:        1%{?dist}
Summary:        Dashboard for cube

Group:          Monitoring Dashboard
License:        Free

# tarball created with `npm pack .`
Source0:        cubedash-%{version}.tgz

BuildArch:      noarch
ExclusiveArch:  %{ix86} x86_64 %{arm} noarch

BuildRequires:  nodejs-devel

Requires:       nodejs-express

%description
Dashboard for cube

%prep
%setup -q -n package


%build
#nothing to do


%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{nodejs_sitelib}/cubedash
cp -pr server.js package.json public %{buildroot}%{nodejs_sitelib}/cubedash

mkdir -p %{buildroot}%{_bindir}
ln -sf ../lib/node_modules/cubedash/server.js %{buildroot}%{_bindir}/cubedash

%nodejs_symlink_deps

%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%{nodejs_sitelib}/cubedash
%{_bindir}/cubedash


%changelog
* Mon Aug 11 2014 Daniel Spinozzi <dspinoz@gmail.com> - 0.0.1-1
- packaged for installation on redhat using epel nodejs
