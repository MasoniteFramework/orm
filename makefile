init:
	cp .env-example .env
	pip install masonite_cli
	pip install -r requirements.txt
test:
	python -m pytest tests
ci:
	make test
coverage:
	python -m pytest --cov-report term --cov-report xml --cov=masonite tests/
	python -m coveralls
publish:
	pip install 'twine>=1.5.0'
	python setup.py sdist
	twine upload dist/*
	rm -fr build dist .egg masonite.egg-info
pypirc:
	cp .pypirc ~/.pypirc