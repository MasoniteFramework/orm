## Contributing Guide

This guide is intended to explain how to contribute to this project.

### Preface

Note that you do not need to write code in order to contribute to the project. You can contribute your voice, your ideas, past experiences or just join general discussions we are having in GitHub or the Slack channel. Whether its 1 hour per day or 1 minute per week. All input and ideas are important for the success of the project. That one sentence could lead to more discussion and ideas.

If you have any questions at all then be sure to join the [Slack Channel](https://slack.masoniteproject.com).

### Issues

Everything really should start with opening an issue or finding an issue. If you feel you have an idea for how the project can be improved, no matter how small, you should open an issue so we can have an open dicussion with the maintainers of the project. 

We can discuss in that issue the solution to the problem or feature you have. If we do not feel it fits within the project then we will close the issue. Feel free to open a new issue if new information comes up. 

If there is already an issue open that you want to contribute ideas to, have information to add to the discussion, or want to contribute to the issue by writing code to complete the issue then please comment on the issue saying you would like to contribute to it.

### Pull Request Flow

If you choose to contribute to an issue via code contribution then please follow the steps below:

* First you will need to fork the repository. You can do this directly in GitHub by clicking the fork icon in the top right corner of the repository.
* You should then checkout the repository to your computer
* Make the code change and push up your changes to a local branch. 
* The branch should should follow a common naming convention. If the issue is #123 then your branch should be called `feature/123`. This helps me identify which issue the branch is supposed to fix.
* You should then open a pull request to the repository. 
* All tests are required to be written. If you do not know how to write tests you can open the pull request without tests and we can discuss the best way to test the code you wrote.

Once the pull request is open, the code will be reviewed and we will discuss how this particular solution to the problem solves the original issue. If there are code improvements or corrections to be made then they will be discussed with maintainers of the project.

### Running Tests

You should run all tests locally and make sure they pass before writing any code. This way you can be sure if your code is not breaking any tests that may be failing for other reasons. 

You should set up a virtual environment and run tests via pytest:

```
$ python -m venv venv
$ source venv/bin/activate
$ python -m pytest
```

This should run all tests successfully. The code was written in a way where you do not need a database to test the code so all tests should run fine. 