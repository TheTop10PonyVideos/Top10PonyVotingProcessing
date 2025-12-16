# Top 10 Pony Voting Processing
Python GUI application to process the monthly voting for the Top 10 Pony Videos showcase.

## Prerequisites
* Python 3.13 or higher
* [Poetry](https://python-poetry.org/docs/#installation) for dependency management

## Setting up your development environment
1. Create a [fork](https://github.com/TheTop10PonyVideos/Top10PonyVotingProcessing/fork) of the live [Top10PonyVotingProcessing](https://github.com/TheTop10PonyVideos/Top10PonyVotingProcessing) repository on GitHub. This is so you have somewhere to push your code after you've made changes, as you won't have access to the live repository.

2. Clone the forked repository to your machine with `git clone`.

3. Add the live repository as an upstream remote. This will allow you to keep your fork in sync with live.

       git remote add upstream https://github.com/TheTop10PonyVideos/Top10PonyVotingProcessing

   Use `git fetch upstream` whenever you need to fetch new changes from the live repo. You can bring your local `master` branch up-to-date with live by using `git merge upstream/master`. 

4. In the project root directory, run `poetry install` to install all dependencies for the project. Poetry automatically creates a virtual environment for your project.

## Running the application
The main application is called `main.py`. To run it, use

    poetry run python main.py

Using `poetry run` will run the command in the context of the Poetry virtual environment, where the project dependencies are defined. If it worked, you should see a GUI window appear.

## Useful development commands
* Add a project dependency (e.g. a third-party Python package):

      poetry add PACKAGE

* Add a dev dependency (something needed for development but not for the end user, e.g. testing software):

      poetry add --group dev PACKAGE

* Update all project dependencies to latest versions:

      poetry update

* Run (old, to be deprecated) unit tests:

      poetry run python test.py

* Run unit tests:

      poetry run pytest

* Format Python files to PEP8 style (save your code changes first!):

      poetry run black .

## Making code changes
* Make sure your local `master` branch is up-to-date with the live repository. (See "Setting up your development environment" if you're not sure how to synchronize a forked repo with live).
* Before starting on a new feature, check out a new local branch:

      git checkout -b feature/your-new-feature

* Make your code changes and commit them.
* Use `git push` to push your new branch to your forked repository.
* Open a pull request (PR) for your changes. If using command-line Git, it should automatically give you a URL for this - if not, go to GitHub in your browser and open the pull request there. The merge target should be the live repository.
* Ask someone in the #tech-team channel to review your pull request. If they are satisfied, they will merge your changes to live!

## Project structure
* `classes`: Various custom classes used by the project.
* `config`: Configuration files for the application.
* `processes`: The individual main processes (sub-applications) that can be accessed via the main application.
* `data`: Data used by the application to make decisions, e.g. allowed domains, uploader whitelists.
* `functions`: Various Python functions used in the project, organized by purpose.
* `images`: Images used in the application's GUI.
* `outputs`: Directory to which the application typically writes out data after processing.
* `tests`: Unit tests for the project.
* `test.py`: Test runner script for the project. Use `poetry run python test.py` to run.
* `main.py`: Entry point to the application. Use `poetry run python main.py` to run.

## Guidelines
* We use the [PEP8 style guide](https://pep8.org/) for formatting Python code, but you don't have to remember the rules or write perfectly-formatted code - just use the [Black formatter](https://pypi.org/project/black/) (`poetry run black .`) to apply PEP8 formatting to all Python source files. (Save your code changes first!)
* Don't push updates directly to the master branch - always check out a new branch when working on a new feature. See "Making code changes" for more details.
* Please comment your code to help future developers (or future you!). Use Python [docstrings](https://peps.python.org/pep-0257/) (triple-quotes underneath the function definition) to describe what a particular function does, and feel free to add inline comments to ease understanding, particularly if the reason for the code isn't obvious.
* Writing unit tests isn't mandatory, but is encouraged! Check the [tests](/tests) directory for examples of tests and use `poetry run pytest` to run the test suite. If you're not sure how to write a test, feel free to ask in the #tech-team channel.

## Links
* [TheTop10PonyVideos Github](https://github.com/TheTop10PonyVideos)
* [Overhaul Meeting](https://docs.google.com/drawings/d/1p4D8QmpdhN-f_IkulZAoQoT7WqaGD-Hd2b8RkN1IWOA/edit?usp=sharing)


***

May Derpy light our way.

<img src="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fimages.wikia.com%2Fmlp%2Fimages%2F1%2F1e%2FDerpy_Castle_Creator.png&f=1&nofb=1&ipt=d7813515f2cf2d088e0c0903c9f49d9490f4e53249f47c9907843f19e2453fb1&ipo=images" width="350" />
