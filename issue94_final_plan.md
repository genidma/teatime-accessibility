# Issue 94 — Sanitized Estimate and Plan
Author: GitHub Copilot — Created: 03:57 UTC

Estimate: 8 hours (one developer day) — confident (~70%).

- Review: 1 hr — inspect `_load_config`, stats loader, and existing tests.
- Tests — config: 1.5 hr — add unit tests for missing/null fields.
- Fixes — config: 2 hr — implement robust handling in `_load_config`.
- Tests — stats/old-format: 1.5 hr — add tests for legacy stats & null/missing category.
- Test run & fixes: 1 hr — run full suite, resolve regressions.
- PR prep: 1 hr — branch, commits, PR description per `main-dev` constraint.

Assumptions:
- Tests currently fail only for issue-specific cases; no external approvals required.
- Changes will be made on `main-dev` and will not be synced to other branches.

Next step: review the referenced files and run the test suite to begin work.
