FROM ubuntu:14.10
RUN apt-get update
RUN apt-get install -y apt-cacher-ng

EXPOSE 3142
VOLUME ["/var/cache/apt-cacher-ng"]
CMD chmod 777 /var/cache/apt-cacher-ng && /etc/init.d/apt-cacher-ng start && tail -f /var/log/apt-cacher-ng/*


