FROM centos:7

# Make changes to yum config in order to use local cache/proxy
RUN sed -i --expression='s/enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf
ADD yum-disable-mirrorlist yum-install-epel usr/bin/
#RUN  echo "Acquire::http { Proxy \"http://10.0.2.15:8123\"; };" >> /etc/apt/apt.conf.d/01proxy
#RUN apt-get update
EXPOSE 8080
CMD tail -f /var/log/messages
