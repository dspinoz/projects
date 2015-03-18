
all: 

build: Dockerfile
	docker build --tag=test .

ps:
	docker ps

run: 
	docker run --tty=true --interactive=true --link=test-apt-cacher:apt-cache test

