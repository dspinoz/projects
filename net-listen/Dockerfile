FROM ubuntu:14.10
RUN apt-get update
RUN apt-get install -y net-tools netcat

EXPOSE 3142
CMD nc -lk 3142
