# BudgetTrack Scrum board

Based on BudgetTrack_Scrum_Board_Group_6.pptx supplied by the user. Follow its work-package sequence and basic To Do / In Progress / Done workflow. Slide owners and statuses are proposed, not verified team assignments or evidence of completed implementation.

## Working rules

- Pull a small task from To Do into In Progress before implementing it.
- Move a task to Done only after its acceptance criteria and relevant checks pass.
- Track blockers alongside the task and demonstrate the completed increment at review.
- Keep team ownership provisional until the team confirms it.
- Treat the deck's W1-W10 labels as relative planning stages; they do not fit the September 30-November 17 charter window as ten calendar weeks.
- Local demo overrides hosted deployment: delivery means reproducible Windows/macOS setup, sample data, documentation, and handoff. Domain registration is not required.

## Implementation backlog

| Order | WBS | Work package | Status in this checkout | Proposed team owner from deck |
| --- | --- | --- | --- | --- |
| 1 | 2.1 | Requirements documentation | In Progress: confirmed scope recorded; defaults documented | Tire Kehinde |
| 2 | 2.2 | Interface and database design | In Progress: account, expense, budget, and dashboard designs documented; visual review pending | Yevgeniy Dymov |
| 3 | 3.1 | User accounts and access controls | In Progress: implemented and automated checks passed; visual review pending | Caleb Tevik |
| 4 | 3.2 | Expense tracking and categories | In Progress: implemented and automated checks passed; visual review pending | Bilal Nadeem |
| 5 | 3.3 | Monthly budget and category limits | In Progress: implemented, 7 budget tests passed; visual review pending | Bilal Nadeem |
| 6 | 3.4 | Dashboard and spending summaries | In Progress: implemented, 7 dashboard tests passed; authenticated visual review pending | Caleb Tevik |
| 7 | 4.1 | Functional and calculation tests | In Progress: all 27 tests passed | Yevgeniy Dymov |
| 8 | 4.2 | Access control and browser compatibility | In Progress: ownership/CSRF tests passed; browser/macOS review pending | Yevgeniy Dymov |
| 9 | 6.1 / 6.2 | Local configuration, documentation, and handoff | To Do: initial setup guide exists | Tire Kehinde (6.1); 6.2 unspecified |
| Ongoing | 1.1 | Planning and progress tracking | In Progress | Tire Kehinde |

## Setup completed

- Created Django scaffold and SQLite database.
- Passed Django system checks and initial migrations on Windows.
- Added setup instructions for Windows and macOS; macOS execution remains unverified.
- Created public GitHub repository: https://github.com/Tevik98/budgettrack. Local SQLite data and virtual environments are excluded.

## First increment

Goal: a user can register, sign in, and manage only their own expenses.

- [x] Define user-owned category and expense models, including exact monetary storage.
- [x] Implement shared navigation and expense/account forms; document design.
- [x] Implement registration, login, and logout.
- [x] Add premade categories and private custom categories.
- [x] Implement expense creation, list/filtering, editing, and confirmed deletion.
- [x] Verify input validation and cross-user access restrictions with automated tests.
- [ ] Review the working increment and update this board.

Verification: all 13 automated tests passed, Django system checks passed, migration consistency checked, and the tracking migration applied on Windows. Browser preview failed because the tool process exited; visual review remains pending. macOS has not been tested. The board is updated without marking the entire increment Done before that review.

## Definition of Done

Budget increment: monthly and category limits, previous-month prefill with explicit saving, independent edits, spending progress, and overspending indicators are implemented. All 20 tests passed; the budget migration is applied and migration consistency checks passed. In-app browser connection failed, so visual and macOS verification remain pending. Next work package: WBS 3.4 dashboard and spending summaries.

A feature works through the UI, enforces record ownership and validation, passes relevant checks, has no known blocking defects, and has updated documentation where needed. Cross-platform or browser compatibility is only marked verified after testing on the named platform/browser.

## Dashboard increment

- [x] Monthly spending, saved budget, and remaining balance.
- [x] Category breakdown with percentage and dollar labels.
- [x] Six-month spending history, including zero-spend months and year boundaries.
- [x] Recent expenses limited to the selected month.
- [x] Navigation, month selector, and links to expenses/budgets.
- [x] Seven dashboard tests; all 27 project tests pass.
- [x] Live HTTP and browser login protection verified.
- [ ] Authenticated desktop/mobile visual review and macOS checks.

November 7 review: authenticated navigation and sample values checked for all main screens; dashboard phone-width screenshot and 390px/1280px overflow checks completed. Full desktop/Safari/physical-device review remains pending. Temporary review data was removed. Added a Windows/macOS Python 3.12–3.14 CI matrix; hosted results pending repository push. See verification.md.

No database changes were needed for this increment. Next work: end-to-end review, compatibility checks, and GitHub repository setup.
