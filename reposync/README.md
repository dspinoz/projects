# reposync2

Yum plugin for downloading packages and keeping incremental changes so that they can be transferred to other machines.

It's useful for building a copy of the repository on other systems without having to perform a full reposync again.

## Installation 

```bash
make install
```

## Usage

1. Perform reposync

   ```bash
reposync --plugins --source --newest-only
```

   Reposync will cache latest packages for all available yum repositories.
   
   A series of "incremental" files will be dropped, containing the packages downloaded for this run.
   
   Refer to /etc/yum/pluginconf.d/reposync2.conf for additional configuration options when running inside reposync
   
   Refer to reposync(1) for more information


2. Transfer incremental files

   ```bash
scp reposync-*.tar.gz* user@anotherhost:~/
```

3. Unpack incrementals

   ```bash
ssh user@anotherhost
yum --reposync2-merge --incremental-dir=<where copied to> --dest-dir=<all repos>
```

   Using yum, unpack the incrementals and build a set of new repositories on the remote host
   See additional options with --help

## TODOs

* catch exceptions
* handle disk filling up while creating incremental (ie. block, allow incrementals to be re-created from csv file)
* perform createrepo after processing incremental (make it look like a real repo)
* option to perform sync from yum interface (remove the need to explicitly rely on reposync)
* allow command line options to override config file
* specify options for all available in config
* show progress when creating incremental (large run of reposync will download LOTS of packages)
* allow incrementals to be built via yum (don't just limit the use to reposync)  

## Changelog

* Version 0.2 - when extracting incrementals, make the directory structure look like it does when it comes from reposync

* Version 0.1 - first version
