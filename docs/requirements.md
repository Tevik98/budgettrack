# BudgetTrack requirements

## Scope

Group 6 course project, September 30 to November 17, 2026. Deliver a local web demo using Python/Django, compatible with Windows and macOS and usable in desktop/mobile browsers. No hosted deployment is required.

## Confirmed features

1. Accounts: register, log in, log out; each user can access only their own records.
2. Expenses: create, list, edit, delete; filter by month and category; confirm deletion.
3. Categories: provide Food, Housing, Transportation, Utilities, Shopping, Entertainment, Health, and Other; allow custom categories belonging to the creating user.
4. Budgets: overall monthly budget and optional per-category spending limits.
5. Dashboard: monthly expense totals, remaining budget, spending by category, recent expenses, and charts.
6. Design: clean, light, lightweight, responsive interface.
7. Repository: public GitHub repository named budgettrack.

## Proposed defaults for review

- USD only; positive expense amounts with at most two decimal places.
- Expense fields: amount, date, category, optional description.
- Use integer cents for exact storage and total calculations.
- Assign an expense to the calendar month of its entered date.
- Copy the previous month's budget limits when initializing a new month; subsequent edits affect only the selected month.
- Show overspending warnings without blocking expense entry.
- Custom category names must be unique per user, ignoring case.
- Archive categories rather than removing historical expense references.
- No email verification or email-based password reset required for the local demo.

## Screens

Sign up / sign in; Dashboard; Expenses (list and forms); Budgets; Categories.

## Acceptance criteria

- A new user can create an account and complete the expense and budget workflows.
- Two users cannot view or modify each other's records, including by changing URLs or form values.
- Editing or deleting an expense updates the correct month's totals and remaining budgets.
- Invalid amounts and dates produce readable errors without losing entered form values.
- Default and custom categories are selectable when entering expenses.
- Empty months and months with no budget show useful, accurate states.
- All core controls work at phone and desktop widths and support keyboard use.
- A fresh clone can be installed using documented commands on Windows and macOS without hard-coded machine paths or separate database software.
- Tests cover ownership, monetary calculations, filters, and budget behavior.

## Outside scope

Income tracking, bank integrations, automatic imports, payments, native mobile apps, shared budgets, recurring transactions, and receipt uploads.

## Implementation sequence

Track work using [the Scrum board](scrum-board.md), following the supplied deck's work-package sequence and verifying actual progress in this checkout.

1. Repository, Django scaffold, settings, and environment documentation.
2. Accounts, data models, and default categories.
3. Expense and custom category workflows.
4. Monthly budgets and dashboard.
5. Responsive polish, representative demo data, and verification.
