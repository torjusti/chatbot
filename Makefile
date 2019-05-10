install:
	pip install .

test: install
	TEST_FLAG=TRUE pytest
	flake8 --exclude=venv,build,website .

test-docker:
	docker exec --env TEST_FLAG=TRUE -it agent25 pytest 
	docker exec -it agent25 flake8 --exclude=venv,build,website .

build:
	docker-compose build

build-clean:
	docker-compose build --no-cache

start:
	docker-compose up -d

build-and-run:
	docker-compose build && docker-compose up -d

docker-logs:
	docker-compose logs

stop:
	docker-compose stop

make open-bash-agent25:
	docker exec -it agent25 bash

make open-bash-web:
	docker exec -it web bash

