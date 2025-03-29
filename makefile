SHELL := /bin/bash

init: .env .bootstrapped-pip .git/hooks/pre-commit
init-ci:
	touch .ignore-pre-commit
	make init

.bootstrapped-pip: requirements.txt requirements.dev
	pip install -r requirements.txt -r requirements.dev
	touch .bootstrapped-pip

.git/hooks/pre-commit:
	@if ! test -e ".ignore-pre-commit"; then \
  		pip install pre-commit; \
  		pre-commit install --install-hooks; \
	fi

.env:
	cp .env-example .env

# 	Create MySQL Database
# 	Create Postgres Database
test: init
	python -m pytest tests
ci:
	make test
check: format sort lint
lint:
	flake8 src/masoniteorm/
format: init
	black src/masoniteorm tests/
sort: init
	isort src/masoniteorm tests/
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
