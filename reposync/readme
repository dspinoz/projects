# reposync2

Yum plugin for downloading packages and keeping incremental changes so that they can be transferred to other machines

## Installation 

```bash
make install
```

## Usage

1. Perform reposync

--- Reposync will cache latest packages for all available yum repositories.
--- A series of "incremental" files will be dropped, containing the packages downloaded for this run.
--- Refer to /etc/yum/pluginconf.d/reposync2.conf for additional configuration options when running inside reposync
--- Refer to reposync(1) for more information


```bash
reposync --plugins --source --newest-only
```

2. Transfer incremental files

--- Useful for building a copy of the repository on other systems without having to perform reposync again

```bash
scp reposync-*.tar.gz* user@anotherhost:~/
```

3. Unpack incrementals

--- Using yum, unpack the incrementals and build a set of new repositories on the remote host
--- See additional options with --help

```bash
ssh user@anotherhost
yum --reposync2-merge
```


