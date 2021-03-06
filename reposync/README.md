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

2. Perform yum commands

   Upgrade the system to the latest packages available, but cache the downloaded packages (like reposync) and build "incremental" files.

   ```bash
yum --reposync2-enable upgrade
```

   Allow yum to use packages (where available) that have been downloaded via reposync. This will help speed-up downloads and also produce a "incremental" files for new packages.

   ```bash
yum --reposync2-enable install git
```

   Download packages using yum, and build "incremental" files

   ```bash
yum --reposync2-enable --downloadonly install gcc-c++
```

   Run commands inside the directory where reposync is performed, or ensure that --download_path is consistent between reposync and yum.

   See ```yum --help``` for more information

   Incrementals may need to be unpacked, refer below.

3. Transfer incremental files

   ```bash
scp reposync-*.tar.gz* user@anotherhost:~/
```

4. Unpack incrementals

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

## Changelog

* Version 0.5 - rewrite with OO. Much better for maintenance :)

* Version 0.4 - when using yum, download files from reposync into the yum cache in order to speed up downloads

* Version 0.3 - allow yum to build incrementals too! yum requires the --reposync2-enable option

* Version 0.2 - when extracting incrementals, make the directory structure look like it does when it comes from reposync

* Version 0.1 - first version
