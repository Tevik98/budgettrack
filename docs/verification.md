# Verification record

## Local review — November 7, 2026

- Windows, Python 3.14, Django 5.2.19: all 27 automated tests passed.
- Django system checks and migration consistency checks passed.
- Authenticated browser navigation verified Dashboard, Budgets, Expenses, Add Expense, and Categories using a temporary account with fictional records.
- Inspected dashboard, entry form, and category screenshots at the normal in-app browser width. Inspected dashboard at a 390px viewport and checked page widths at 390px and 1280px; neither reported horizontal document overflow. The embedded screenshot surface clipped the desktop-sized view, so this is not a complete desktop visual certification.
- The budget page displayed the expected $209.14 spending, $1,500.00 budget, $1,290.86 remaining, and Food overspending by $5.25 for the review fixture.
- Signed out and removed the temporary review account and its records after checking. Existing user data was not changed.

## Automated compatibility checks

The GitHub Actions workflow runs checks, migrations, and the full test suite on Windows and macOS with Python 3.12, 3.13, and 3.14. All six combinations passed for implementation commit `a89983a` on November 7, 2026: https://github.com/Tevik98/budgettrack/actions/runs/42415592784. Each job installed dependencies, checked Django and migration consistency, applied migrations, and ran all 27 tests.

## Remaining manual checks

- Run the app on the user's Mac and inspect Safari.
- Review a full desktop viewport and a physical mobile browser, including keyboard navigation and expense-table scrolling.
- Complete a team acceptance review using the Scrum board.
