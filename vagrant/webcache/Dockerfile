FROM ubuntu:14.10
RUN apt-get update
RUN apt-get install -y polipo
EXPOSE 8123
VOLUME ["/var/cache/polipo"]
CMD polipo logSyslog=false logFile= logLevel=0xFF proxyAddress=0.0.0.0

