
all: 

build: Dockerfile
	docker build -t apt-cacher-ng .

ps:
	docker ps

create: build
	docker create --name test-apt-cacher apt-cacher-ng

clean:
	docker rm test-apt-cacher

run: 
	docker start test-apt-cacher

stop:
	docker stop test-apt-cacher

logs:
	docker logs -f test-apt-cacher

backup:
	docker run -it --link=test-apt-cacher:apt-cache --volumes-from test-apt-cacher --volume `pwd`/cache:/backups apt-cacher-ng:latest sh -c 'echo "Acquire::http { Proxy \"http://apt-cache:3142\"; };" >> /etc/apt/apt.conf.d/01proxy && apt-get install rsync && rsync -arvb /var/cache/apt-cacher-ng /backups'


