# First increment design

## Data

Django's built-in User owns Category and Expense records. Categories have a name and a premade/custom flag, with case-insensitive uniqueness per user. Registration creates eight premade categories in the same transaction as the account.

Expenses store an owner, category, integer amount in cents, date, optional description, and creation timestamp. Positive amounts are required by a database constraint. Currency input accepts at most two decimal places and converts using Decimal, never floating point. An owner/date index supports the history view. Category deletion is protected while referenced by an expense.

## Access

Every expense query is scoped to the signed-in user. Edit/delete routes return 404 for another user's records. Category choices and filters are scoped to the current user, and expense ownership comes from the session rather than submitted data. Django handles password hashing, session authentication, CSRF, and template escaping. Logout and deletion require POST; GET deletion only renders confirmation.

## Interface

Shared navigation links Expenses and Categories. The expense page shows totals for the filtered records, expense count, category count, month/category controls, and a paginated history. Separate pages handle entry/editing and deletion confirmation. Sign-in and sign-up use the same light/green visual style. System fonts and local CSS avoid external frontend dependencies.

Layouts include responsive breakpoints, labeled controls, visible keyboard focus, a skip link, and horizontal table scrolling on narrow screens. These responsive styles are implemented but visual browser and device verification remains pending because preview tooling failed.

## Remaining increments

Category archival and full platform/browser review remain pending. No hosted deployment is configured.

## Budget increment

MonthlyBudget stores an owner, the first day of the month, and an integer-cent limit. Database constraints enforce one budget per user/month and first-day normalization. CategoryLimit stores an integer-cent limit per budget/category. Both accept zero; absent category rows mean no limit.

The budget page scopes all queries and dynamically generated category fields to the signed-in user. Updates are atomic. The immediately preceding calendar month's saved limits prefill unsaved months, with explicit Save required; GET requests never modify budgets. Copying duplicates values rather than sharing records. Category limits are independent caps, not allocations that must sum to the overall budget.

Spending totals group user-owned expenses by category and calendar month. Remaining balances are computed on each request using Decimal/integer cents; negative balances show overspending without restricting expense entry. Seven additional tests cover persistence, independent copying across years, totals after expense edits/deletion, zero versus unset, invalid input, ownership/CSRF, and new categories.

## Dashboard increment

The dashboard at `/dashboard/` reuses budget_summary for the selected month. Category bars show each category's share of that month's spending, ordered by amount. A separate chart compares up to six calendar months ending with the selected month, including zero-spend months. Dollar labels accompany every bar. History bars are scaled to the largest amount in the window; category bars are scaled to total monthly spending. The most recent five records are ordered by expense date and ID within the selected month.

All queries require the current user's ownership. Month selection is validated before querying. Existing expense routes remain unchanged; the brand and default login destination now lead to the dashboard. Charts use local CSS, require no scripts or external dependencies, and expose visible text values while decorative bars are hidden from screen readers.

Seven dashboard tests cover exact totals, consistency with budgets, year boundaries, account privacy, empty/zero-budget states, the recent-record limit, updates/deletion, invalid months, escaping, and authentication. All 27 project tests passed. Live HTTP returned 200 and browser navigation confirmed login protection; authenticated visual and macOS verification remain pending.
