## lwworkflow.py

Helper script for managing a lightworks project (video editing)

Workflow ensures:

* Proxy files used during editing
* Intermediate files used during render
* Automatic management of intermediates and proxy files from raw files

Getting started:

* Create a working directory to house all files

mkdir /library && cd /library

* Initialise a new lightworks repository

lwworkflow init

** Creates nosql database file, .lwf/lwf.db, with library settings (amongst other things)
rawdir = raw
intermediatedir = intermediate
proxydir = proxy
mode = raw

* Import all raw files from camera 

lwworkflow import --mode=raw --path=/media/camera 

** Files from /media/camera will be put into /library/.lwf/raw/media/camera
** Intermediate files (full resolution, transcoded for editing) will be created and stored at /library/.lwf/intermediate/media/camera
** Generating intermediates helps ensure valid proxy files are as equivalent as possible - suitable for high-res drop-in replacements. eg rotate video files from phones
** Proxy files (scaled resolution, transcoded from raw/intermediates files) will be created and stored at /library/.lwf/proxy/media/camera

** Once imported files are tracked and entries added to database file with associated metadata


* Show status of project

lwworkflow status 

** See the current mode of the workflow
** See transcoding status

* Show listing of imported files

lwworkflow ls

* Various other options available, refer to help

lwworkflow help
