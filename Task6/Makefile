.PHONY: all build up down run-onehot

all: up

build:
	docker compose -f docker-compose.yml build

up:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

run-onehot:
	docker compose -f docker-compose.yml exec index-updater /app/update.sh
