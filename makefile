export POSTGRES_DATABASE_PORT:=$(shell docker port masonite-test-postgres 5432/tcp | head -n 1 | cut -d: -f2-)
export MYSQL_DATABASE_PORT:=$(shell docker port masonite-test-mysql 3306 | head -n 1 | cut -d: -f2-)
export DB_CONFIG_PATH:=...tests.integrations.config.database

init:
	cp .env-example .env
	pip install -r requirements.txt
	pip install .
	docker-compose pull 
bootstrap:
	docker-compose up -d
	python orm migrate --connection postgres
	python orm migrate --connection mysql
test:
	make bootstrap
	python -m pytest tests
ci:
	make test
lint:
	python -m flake8 src/masoniteorm/ --ignore=E501,F401,E203,E128,E402,E731,F821,E712,W503,F811
format:
	black src/masoniteorm
	black tests/
	make lint
sort:
	isort tests
	isort src/masoniteorm
coverage:
	python -m pytest --cov-report term --cov-report xml --cov=src/masoniteorm tests/
	python -m coveralls
show:
	python -m pytest --cov-report term --cov-report html --cov=src/masoniteorm tests/
cov:
	python -m pytest --cov-report term --cov-report xml --cov=src/masoniteorm tests/
publish:
	pip install twine
	make test
	python setup.py sdist
	twine upload dist/*
	rm -fr build dist .egg masonite.egg-info
	rm -rf dist/*
pub:
	python setup.py sdist
	twine upload dist/*
	rm -fr build dist .egg masonite.egg-info
	rm -rf dist/*
pypirc:
	cp .pypirc ~/.pypirc