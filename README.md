[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-c66648af7eb3fe8bc4f294546bfd86ef473780cde1dea487d3c4ff354943c9ae.svg)](https://classroom.github.com/online_ide?assignment_repo_id=8874460&assignment_repo_type=AssignmentRepo)
# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.


## Team Members of Team 15

Victoria Zhang [Github](https://github.com/Ruixi-Zhang)
Leah Durrett [Github](https://github.com/howtofly-lab)
Brandon Chao [Github](https://github.com/Sciao)
Lucy Kocharian [Github](https://github.com/Lkochar19)

## Product vision statement

To help users keep track of deadlines and the tasks they wish to complete.

## User stories

Link to User Stories on Project Repository Issue Page:
[Issues](https://github.com/software-students-fall2022/web-app-exercise-team-15-1/issues?q=)

## Task boards

Link to Task Boards for Sprints 1 and 2
[Projects](https://github.com/software-students-fall2022/web-app-exercise-team-15-1/projects?query=is%3Aopen)

## Running our app locally - Commands for mac
- note: before you run the command, supply the <password> in .env with user password

- python3 -m venv .venv
- source .venv/bin/activate
- pip3 install -r requirements.txt
- export FLASK_APP=app.py
- export FLASK_ENV=development
- python3 -m flask run --host=0.0.0.0 --port=10000
- Go to [http://0.0.0.0:10000/deadline] MAY CHANGE IF HOMEPAGE AVALIABLE

### .env file 

MONGO_DBNAME=todo_list
MONGO_URI= FILL IN LATER
FLASK_APP=app.py
FLASK_ENV=development
GITHUB_SECRET=your_github_secret
GITHUB_REPO=https://github.com/your-repository-url