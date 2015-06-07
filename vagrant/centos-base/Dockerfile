FROM centos:7

# Make changes to yum config in order to use local cache/proxy
RUN sed -i --expression='s/enabled=1/enabled=0/' /etc/yum/pluginconf.d/fastestmirror.conf
RUN rm  -rf /etc/yum.repos.d/*.repo
RUN echo "proxy=http://localhost:8123/" >> /etc/yum.conf
ADD use-local-proxy.repo /etc/yum.repos.d/




CMD tail -f /var/log/yum.log
