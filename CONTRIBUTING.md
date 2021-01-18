# Contributing Guide

This guide is intended to explain how to contribute to this project.

## Preface

Note that you do not need to write code in order to contribute to the project. You can contribute your voice, your ideas, past experiences or just join general discussions we are having in GitHub or the Slack channel. Whether its 1 hour per day or 1 minute per week. All input and ideas are important for the success of the project. That one sentence could lead to more discussion and ideas.

If you have any questions at all then be sure to join the [Slack Channel](https://slack.masoniteproject.com).

If you are interested in the project then it would be a great idea to read the "White Paper". This is a document about how the project works and how the classes all work together. The White Paper can be [Found Here](https://orm.masoniteproject.com/white-page)

## Issues

Everything really should start with opening an issue or finding an issue. If you feel you have an idea for how the project can be improved, no matter how small, you should open an issue so we can have an open dicussion with the maintainers of the project.

We can discuss in that issue the solution to the problem or feature you have. If we do not feel it fits within the project then we will close the issue. Feel free to open a new issue if new information comes up.

If there is already an issue open that you want to contribute ideas to, have information to add to the discussion, or want to contribute to the issue by writing code to complete the issue then please comment on the issue saying you would like to contribute to it.

## Labels

To improve the quality of issues, please add any related labels to the issue you think are most relevant. You may add as many as you think make sense. There are tag descriptions on the labels section of the repo so please read those descriptions to choose which labels best work for the issue.

**Please do not use any of the difficulty labels (easy, medium or hard). A maintainer will label the issue with the difficulty level after reviewing the issue**

## Difficulty Levels

Before contributing, it is assumed you have basic Python or programming skills and you are able to understand the issues enough to have a discussion about it without much information direction. All issues are marked with a difficulty level to determine how much effort will be involved in closing the issue. There are several difficulty level issues:

**good first issue** - Issues marked with this label are great issues to take if you have never contributed to open source before. These issues typically have a step by step solution in the issues are are intended for first time contributors to expand the pool of maintainers.

**easy** - Issues marked as easy are great issues to take if you have never contributed to this project before. Take this opportunity to take a simple issue to understand how some of the code works together and a simple test.

**medium** - Issues marked with this should not be worked on by someone who has not contributed to the project before. These issues assume you have basic knowledge of the codebase and can work on the issue with little direction. Discussions should be had on these issues on the best way to solve and close them.

**hard** - These issues should really not be worked on unless you are a maintainer of the Masonite organization. These issues are very involved and assume advanced knowledge of the codebase. You may contribute your voice to the issue but it is not advised you work on these issues unless you are a maintainer or have contributed to the past and have completed a medium difficulty task

## Pull Request Flow

If you choose to contribute to an issue via code contribution then please follow the steps below:

* First you will need to fork the repository. You can do this directly in GitHub by clicking the fork icon in the top right corner of the repository.
* You should then checkout the repository to your computer
* Make the code change and push up your changes to a local branch.
* **The branch should should follow a common naming convention. If the issue is #123 then your branch should be called `feature/123`. This helps me identify which issue the branch is supposed to fix.**
* You should then open a pull request to the repository.
* **All tests are required to be written before merging a pull request.** If you do not know how to write tests you can open the pull request without tests and we can discuss the best way to test the code you wrote. A maintainer or contributor could also step in and write tests for you

Once the pull request is open, the code will be reviewed and we will discuss how this particular solution to the problem solves the original issue. If there are code improvements or corrections to be made then they will be discussed with maintainers of the project.



## Running Tests

You should run all tests locally and make sure they pass before writing any code. This way you can be sure if your code is not breaking any tests that may be failing for other reasons.

You should set up a virtual environment and run tests via pytest:

```
$ python -m venv venv
$ source venv/bin/activate
$ python -m pytest
```

This should run all tests successfully. The code was written in a way where you do not need a database to test the code so all tests should run fine.
