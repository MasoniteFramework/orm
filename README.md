
<p align="center">
<img src="https://i.imgur.com/rEXcoMn.png" width="160px"> 
</p>

## Learning Masonite

Masonite strives to have extremely comprehensive documentation. All documentation can be [Found Here](https://masoniteframework.gitbooks.io/docs/content/) and would be wise to go through the tutorials there. If you find any discrepencies or anything that doesn't make sense, be sure to comment directly on the documentation to start a discussion!

Also be sure to join the [Slack channel](https://masoniteframework.gitbooks.io/docs/content/)!

## Setting up

To setup the package to get your package up and running, you should first take a look at `setup.py` and make any packages specific changes there. These include the classifiers and package name.

Then you should create a virtual environment and activate it

```
$ python3 -m venv venv
$ source venv/bin/activate
```

Then install from the requirements file

```
$ pip install -r requirements.txt
```

This will install Masonite and a few development related packages like pytest.

Finally you can run the tests and start building your application.

```
$ python -m pytest
```

# Short Term Tasks

- [ ] Finish basic grammar for:
    - [x] MySQL
    - [ ] MSSQL
    - [ ] Postgres
    - [ ] SQLite
- [x] Get the query builder to use the grammar
- [x] Refactor to use `%s` symbols so we can use avoid sql injection attacks

TODO

- [x] MySQL
    - [x] Grammar
    - [x] Connection
    - [x] Schema
        - [x] SQL Injection
    - [x] Tests

- [ ] MSSQL
    - [ ] Grammar
    - [ ] Connection
    - [ ] Schema
        - [ ] SQL Injection
    - [ ] Tests

- [ ] Postgres
    - [ ] Grammar
    - [ ] Connection
    - [ ] Schema
        - [ ] SQL Injection
    - [ ] Tests

- [ ] SQLite
    - [x] Grammar
    - [x] Connection
    - [ ] Schema
        - [ ] Needs type mappings and aggregates
        - [ ] SQL Injection
    - [ ] Tests

- [ ] Relationships
- [ ] Eager Loading
    - [ ] N + 1 Problem
- [ ] Make new collection class