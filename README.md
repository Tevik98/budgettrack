# BudgetTrack

[![Django checks](https://github.com/Tevik98/budgettrack/actions/workflows/tests.yml/badge.svg)](https://github.com/Tevik98/budgettrack/actions/workflows/tests.yml)

BudgetTrack is a small personal expense tracker built with Django. It runs locally and keeps its data in a SQLite database on your computer.

## Features

- Private accounts with sign-up, login, and logout
- Expense tracking with month and category filters
- Built-in categories and support for custom ones
- Monthly budgets with optional limits for each category
- A dashboard showing spending totals, category breakdowns, and recent activity
- A responsive interface that works on desktop and mobile screens

## Getting started

BudgetTrack supports Python 3.12, 3.13, and 3.14. Use a separate virtual environment on each computer rather than copying one between Windows and macOS.

### macOS

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Once the server starts, open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) and create an account. New accounts start with eight common expense categories, and you can add your own from the Categories page.

## Budgets and dashboard

The Budgets page lets you set one overall budget for a month and optional limits for individual categories. Leaving a category blank means it has no limit; entering zero means no spending is planned for it. If a month does not have a budget yet, the previous month's amounts are shown as a starting point until you save.

The Dashboard brings together the selected month's spending, budget balance, category breakdown, six-month history, and latest expenses. The charts are plain HTML and CSS, so they do not need an internet connection or an external chart service.

## Demo data

To create a sample account, run:

```sh
.venv/bin/python manage.py seed_demo
```

On Windows, use `.\.venv\Scripts\python.exe` instead. The command asks you to choose a password and creates a `demo` account with fictional expenses. Use `--username another_name` if that username is already taken. It will not overwrite an existing account.

## Running the tests

macOS:

```sh
.venv/bin/python manage.py check
.venv/bin/python manage.py test
```

Windows:

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py test
```

The GitHub Actions workflow runs the same checks on Windows and macOS with every supported Python version.

## Project notes

This project is set up for local development, not production hosting. The SQLite database, virtual environment, and local environment files are ignored by Git, so each installation keeps its own data.

More project documentation:

- [Requirements](docs/requirements.md)
- [Design notes](docs/design.md)
- [Verification notes](docs/verification.md)
- [Scrum board](docs/scrum-board.md)
