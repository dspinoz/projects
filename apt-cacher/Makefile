
all: 

build: Dockerfile
	docker build --tag=apt-cacher:latest .

ps:
	docker ps

run: 
	docker run --tty=true --interactive=true --publish=3142:3142 apt-cacher:latest

bash: 
	docker run --tty=true --interactive=true --publish=3142:3142 apt-cacher:latest /bin/bash
