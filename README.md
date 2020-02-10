
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
        - [x] SELECT
        - [x] UPDATE
        - [x] INSERT
        - [x] DELETE
        - [ ] ALTER
    - [x] Connection
    - [x] Schema
        - [x] SQL Injection
        - [x] Needs type mappings and aggregates
        - [ ] Alter query AFTER keyword (for adding column after another column)
        - [ ] Constraints
            - [x] Primary Keys
            - [x] Unique
    - [x] Tests

- [ ] MSSQL
    - [-] Grammar
        - [x] SELECT
        - [x] UPDATE
        - [x] INSERT
        - [x] DELETE
        - [ ] ALTER
    - [ ] Connection
    - [ ] Schema
        - [ ] SQL Injection
        - [ ] Needs type mappings and aggregates
        - [ ] Constraints
            - [ ] Primary Keys
            - [ ] Unique
    - [-] Tests

- [ ] Postgres
    - [ ] Grammar
        - [ ] SELECT
        - [ ] UPDATE
        - [ ] INSERT
        - [ ] DELETE
        - [ ] ALTER
    - [ ] Connection
    - [ ] Schema
        - [ ] SQL Injection
        - [ ] Needs type mappings and aggregates
        - [ ] Constraints
            - [ ] Primary Keys
            - [ ] Unique
    - [ ] Full Tests

- [ ] SQLite
    - [x] Grammar
        - [ ] SELECT
        - [ ] UPDATE
        - [ ] INSERT
        - [ ] DELETE
        - [ ] ALTER
    - [x] Connection
    - [ ] Schema
        - [x] Needs type mappings and aggregates
        - [ ] Constraints
            - [ ] Primary Keys
            - [ ] Unique
    - [x] SQL Injection
    - [ ] Full Tests

- [x] Create Schema Builder class (just a wrapper around create and alter queries)
- [ ] Relationships
- [in progress] Add indexes to schema 
- [ ] Eager Loading
    - [ ] N + 1 Problem
- [ ] Make new collection class
- [x] Make `Column` classes to better interact with building data
- [ ] Fully document every part of the project. Will need to first get a basic working project and then start documenting everything. Then start opening pull requests and documenting as we add new features. Similiar to the way Masonite has good documentation.