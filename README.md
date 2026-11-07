# BudgetTrack

A local personal expense tracking demo for Group 6.

## Project status

Implemented: sign-up/login/logout, private expense records, premade and custom categories, month/category filters, exact spending totals, pagination, editing, confirmed deletion, monthly budgets, optional category limits, and the dashboard with category and monthly spending charts.

All 27 automated tests passed on Windows. Authenticated screens were reviewed in the in-app browser, including dashboard phone-width layout and overflow checks at 390px/1280px. Full desktop, Safari, and physical-device review remain pending. See [verification details](docs/verification.md).

## Confirmed requirements

- Python and Django, running locally on Windows and macOS.
- SQLite database; Django templates, CSS, and minimal JavaScript.
- Clean, lightweight, responsive interface with a light theme and green accents.
- User registration, login, logout, and private user-owned records.
- Expense-only tracking: add, view, edit, and delete expenses.
- Premade categories plus user-created categories.
- Monthly budgets, optional category limits, and spending summaries/charts.
- Public GitHub repository named `budgettrack`.

See [requirements](docs/requirements.md) for behavior and acceptance criteria.

## Development environment

Use Python 3.12, 3.13, or 3.14 on either platform. Create a separate virtual environment on each computer; do not copy or commit it. Dependencies target Django 5.2 LTS.

### Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

### macOS (Terminal)

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000/ and select **Create an account**. Each new account receives eight premade categories. Add expenses and custom categories, then use the month/category filters to review spending. An empty month filter shows all months. Settings are for local development only.

SQLite data stays local to each computer and is excluded from Git. Use fictional sample expenses for demonstrations.

## Dashboard

Select **Dashboard** in the navigation or open http://127.0.0.1:8000/dashboard/. Choose a month to see total spending, the saved monthly budget, remaining balance, category spending shares, up to six months of spending history, and the five latest expenses in that month. Click a chart month to explore it or a recent expense to edit it. The dashboard uses the same calculations as Budgets, including negative remaining balances when over budget.

Charts are local HTML/CSS with visible numeric values; no chart service, JavaScript library, or internet connection is needed after installation. Months without records show zero spending, and months without saved budgets explicitly show **Not set**. Unsaved budget prefills are not treated as saved limits.

## Monthly budgets

Open **Budgets**, select a month, and enter the overall USD budget and any category limits. Blank category limits mean no limit; zero means no spending is planned. Category limits are independent of the overall budget, so their sum is not required to match it.

For an unsaved month, the previous calendar month's saved limits prefill the form. Select **Save monthly budget** to apply them. Visiting a month never creates records. Once saved, each month's budget is independent; unused money does not roll over. Remaining balances use all expenses dated in that month and update when expenses change. Overspending displays a warning but never blocks expense entry.

## Optional sample account

Run `manage.py seed_demo` using your platform's virtual-environment Python. It prompts for a password and creates a `demo` account with eight fictional expenses. Use `--username another_name` if `demo` already exists. Existing accounts and data are never overwritten. Sample dates span the last eight days; select **View all** to see them all if they cross a month boundary.

## Verification

Windows:

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
```

macOS:

```sh
.venv/bin/python manage.py test
.venv/bin/python manage.py check
```

Tests cover account creation and authentication, cross-user access, tampered form inputs, exact monetary calculations, month/category filtering, pagination, invalid input, CSRF, HTML escaping, and safe demo seeding. Run the same checks on your Mac after installation.

## Design and progress

- [Requirements](docs/requirements.md)
- [Scrum board](docs/scrum-board.md)
- [First increment design](docs/design.md)

Public repository: https://github.com/Tevik98/budgettrack

The GitHub Actions workflow checks Windows and macOS with Python 3.12–3.14 after each push and pull request. [All six compatibility jobs passed](https://github.com/Tevik98/budgettrack/actions/runs/42415592784) for the initial implementation. Local data, virtual environments, and environment files are excluded from Git.
