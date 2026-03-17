SHELL := /bin/bash

.PHONY: init
init: .env .bootstrapped-dev

.PHONY: init-ci
init-ci: .env .bootstrapped-tests

.bootstrapped-tests:
	pip install -r requirements.txt
	touch .bootstrapped-tests

.bootstrapped-dev: .bootstrapped-tests
	pip install pre-commit faker
	pre-commit install
	touch .bootstrapped-dev

.env:
	cp .env-example .env

# 	Create MySQL Database
# 	Create Postgres Database

.PHONY: test
test: .bootstrapped-tests
	python -m pytest tests

.PHONY: ci
ci:
	make test

.PHONY: check
check: format lint

.PHONY: lint
lint: .bootstrapped-tests
	ruff check --fix --exit-non-zero-on-fix src/masoniteorm tests

format: .bootstrapped-tests
	ruff format --check src/masoniteorm tests/

coverage:
	python -m pytest --cov-report term --cov-report xml --cov=src/masoniteorm tests/
	python -m coveralls

show:
	python -m pytest --cov-report term --cov-report html --cov=src/masoniteorm tests/

cov:
	python -m pytest --cov-report term --cov-report xml --cov=src/masoniteorm tests/

publish:
	pip install build twine
	make test
	python -m build
	twine upload dist/*
	rm -rf build dist *.egg-info

pub:
	python -m build
	twine upload dist/*
	rm -rf build dist *.egg-info

pypirc:
	cp .pypirc ~/.pypirc
