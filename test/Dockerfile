FROM ubuntu:14.10
RUN  echo "Acquire::http { Proxy \"http://apt-cache:3142\"; };" >> /etc/apt/apt.conf.d/01proxy
CMD tail -f /var/log/dmesg
