FROM ubuntu:14.10
RUN  echo "Acquire::http { Proxy \"http://10.0.2.15:8123\"; };" >> /etc/apt/apt.conf.d/01proxy
RUN apt-get update
CMD tail -f /var/log/dmesg
