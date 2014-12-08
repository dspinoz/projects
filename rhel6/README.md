A series of utilities for performing admin on RHEL

* setup_chroot.sh 

  Easily create a chroot environment

* list_packages 

  Helper for listing packages from various repos
	```bash
list_packages glibc
```

* fetch_packages

  Helper for downloading packages from various repos
  
	```bash
fetch_packages glibc
#download source
fetch_packages -s glibc 
#download from centos7
fetch_packages -c centos7.repo -s glibc 
```

* .repo files

  Various yum repo configuration files

