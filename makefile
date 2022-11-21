init:
	cp .env-example .env
	pip install -r requirements.txt -r requirements.dev
# 	Create MySQL Database
# 	Create Postgres Database
test: init
	python -m pytest tests
ci:
	make test
lint: format
	python -m flake8 src/masoniteorm/ --ignore=E501,F401,E203,E128,E402,E731,F821,E712,W503,F811
format: init
	black src/masoniteorm
	black tests/
	make lint
sort: init
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