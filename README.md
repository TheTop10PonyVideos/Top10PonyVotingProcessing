# Top 10 Pony Voting Processing
Python GUI application to process the monthly voting for the Top 10 Pony Videos showcase.

### Prerequisites
- Python 3.13 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management

### Development Setup
1. Clone the repository
2. Run the setup script: `python setup_dev.py`
3. Or manually install dependencies: `poetry install`

### Running the Application
- Main application: `poetry run python main.py`
- Run tests: `poetry run python test.py`
- Activate virtual environment: `poetry shell`

### Development Commands
- Add a dependency: `poetry add <package>`
- Add a dev dependency: `poetry add --group dev <package>`
- Update dependencies: `poetry update`
- Format code: `poetry run black .`

## Project structure
* `classes`: Directory containing various custom classes used by the project.
* `config`: Directory containing configuration files for the application.
* `core_utilities`: Directory containing the individual Python utilities that can be accessed via the application.
* `data`: Directory containing data used by the application to make decisions, eg. allowed domains, uploader whitelists.
* `functions`: Directory containing various Python functions used in the project, organized by purpose.
* `images`: Directory containing images used in the application's GUI.
* `modules`: Directory containing modules used in previous iterations of the project. Now largely obsolete.
* `outputs`: Directory to which the application typically writes out data after processing.
* `tests`: Contains unit tests for the project.
* `test.py`: Runs unit tests for the project. Use `poetry run python test.py` to run.
* `main.py`: Entry point to the application. Use `poetry run python main.py` to run.
* `setup_dev.py`: Development environment setup script.
* `build_exe.py`: Automated installer script that handles complete setup.
* `install_and_run.bat`: Windows batch file for one-click installation.
* `install_and_run.ps1`: PowerShell script for installation.
* `create_installer_exe.py`: Script to build standalone executable installer.

## Guidelines
- Python and VSC on Windows are the main tools we will be using. Feel free to use any other IDEs that suit you better but be aware that you will not get support from us if you do so.  

- Black is the most common Python code formatter and we will be using it throughout the project. If you are capable of producing PEP8 compliant code without using Black feel free to do so though we would appreciate if you did use it.  

- Code should be always commented to explain how it works and only to explain how it works. Explaining each function is the standard but if you feel like any lines are more complicated and thus worth further comment feel free to do so. Any questions in regards to the quality of the code ("How could I make this more efficient/why doesn't this work/why is Pi==3?") or the administrative part of it (pushing/branching/merging etc) should be discussed using Github's built in tools and their code commenting system in particular. This is so that in the future, whenever someone wants to read our code there are no confusing leftovers which are not related to the code itself.  

- Absolutely never, and I mean never push an update directly into master. The correct workflow is the usual; clone to your computer, create branch, work on that branch, ask for a PR. Most of us will have the right to push into master but even then we should never do so. PRs will always be reviewed by at least one other member before merging.   

- If any of this points aren't crystal clear or you don't understand what exactly I mean feel free to contact me via Discord ping (preferably on #tech-team) or DM (@Vari2508 on most MLP discord servers). I don't care if you think it is a dumb question or it will make you look stupid, chances are if you are not sure, we won't be sure either and the discussion will be beneficial for all of us. Nobody expects anyone to remember things they learnt years ago in college and the only way we can all freshen up a bit is by asking questions.   

 I will be making a Guide on the installation of everything I mentioned here over the next couple weeks. Meanwhile, have a few links you'll probably find useful:  

## Links

[Our Github](https://github.com/TheTop10PonyVideos)

[Visual Studio Install](https://code.visualstudio.com/)

[An introduction to PEP8 styling](https://pep8.org/)

[Black Formatter](https://pypi.org/project/black/)

[Github with VSC 101](https://www.youtube.com/watch?v=RGOj5yH7evk)

[Overhaul Meeting](https://docs.google.com/drawings/d/1p4D8QmpdhN-f_IkulZAoQoT7WqaGD-Hd2b8RkN1IWOA/edit?usp=sharing)


***

May Derpy light our way.

<img src="https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Fimages.wikia.com%2Fmlp%2Fimages%2F1%2F1e%2FDerpy_Castle_Creator.png&f=1&nofb=1&ipt=d7813515f2cf2d088e0c0903c9f49d9490f4e53249f47c9907843f19e2453fb1&ipo=images" width="350" />
