
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

# Phase 1

**Versions 0.1-0.5**

**Project Deadline: November 1 2020**. This should give enough time to incorporate the new ORM into Masonite's major release at the time.

Phase 1 will involve getting the foundation setup for this project. Making sure we can include all the basic use cases and relationships as well as a 100% full documentation. By the end of Phase 1, this ORM should be able to handle the 90% of use cases of a project. Phase 2 will complete the more uncommon or edge cases. Finally,. Phase 3 will be quality of life features.

## Short Term Tasks

- [ ] Finish basic grammar for:
    - [-] MySQL
    - [ ] MSSQL
    - [ ] Postgres
    - [ ] SQLite
- [x] Get the query builder to use the grammar
- [x] Refactor to use `%s` (or `?`) symbols so we can use avoid sql injection attacks

## TODO

- [x] MySQL
    - [x] Grammar
        - [x] SELECT
            - [x] Where
            - [x] Or Where
        - [x] UPDATE
        - [x] INSERT
        - [x] DELETE
        - [x] ALTER
        - [x] Subselects
            - [x] on wheres `where age > (SELECT ..)`
            - [x] Exists
        - [x] Joining
    - [x] Connection
    - [x] Schema
        - [x] SQL Injection
        - [x] Needs type mappings and aggregates
        - [x] Alter query AFTER keyword (for adding column after another column)
        - [x] Constraints
            - [x] Primary Keys
            - [x] Unique
    - [x] Tests

- [x] Create Schema Builder class (just a wrapper around create and alter queries)
- [x] Relationships
[in progress] Add indexes to schema 
- [x] Eager Loading
    - [x] N + 1 Problem
- [x] Make new collection class
- [x] Make `Column` classes to better interact with building data
- [ ] Fully document every part of the project. Will need to first get a basic working project and then start documenting everything. Then start opening pull requests and documenting as we add new features. Similiar to the way Masonite has good documentation.

# Phase 2

**Versions 0.5 - 0.9**

Phase 2 will involve further refactoring. By this phase, all the documentation should be done for the above phase.

- [ ] Where Has queries
- [ ] Chunking
- [ ] Migrations
    - [ ] Migration Schema
    - [ ] Migration Classes
    - [ ] Migration Command
- [ ] MSSQL
    - [-] Grammar
        - [x] SELECT
        - [x] UPDATE
        - [x] INSERT
        - [x] DELETE
        - [ ] ALTER
        - [ ] Joining
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
        - [ ] Joining
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
        - [ ] Joining
    - [x] Connection
    - [ ] Schema
        - [x] Needs type mappings and aggregates
        - [ ] Constraints
            - [ ] Primary Keys
            - [ ] Unique
    - [x] SQL Injection
    - [ ] Full Tests


# Phase 3

**Versions 1.0+**

This phase will be responsible for adding additional quality of life features and overall improvements to the ORM. These include additional options and additional wrapper methods

- [ ] Quality of Life Features
- [ ] Oracle
- [ ] MongoDB (?)
