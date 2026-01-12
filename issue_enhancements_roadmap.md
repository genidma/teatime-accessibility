# Project Enhancements and Roadmap

Start Date: 2026-01-11
Start Time: 04:12 UTC

This issue summarizes recommended enhancements for the repository and a proposed phased approach. Related open issues are referenced (no duplication): #94, #95.

## Recommended Enhancements

- Modularize: Split `bin/teatime.py` into a `teatime/` package and migrate incrementally.
- Stabilize tests: Complete Issue #94 tests for `_load_config` and legacy stats; make tests authoritative before refactors.
- CI & lint: Add GitHub Actions to run tests, linting (black/flake8), and packaging checks on PRs.
- Incremental refactor strategy: Break Issue #95 into phases (package skeleton → core extraction → UI/stats migration) with tests per phase.
- Docs & dev guide: Add/update README, CONTRIBUTING, and a short developer guide describing package layout and migration steps.
- Import compatibility: Add compatibility shims and migration notes so old scripts keep working during transition.
- Assets & UI helpers: Consolidate sprites/sounds and extract `teatime/ui_utils.py` for reusable UI logic and automated smoke tests.
- Triage & labels: Clean/standardize labels, close stale issues, and group related low-priority enhancements for batching.

## Constraints / Notes
- Do not duplicate Issues #94 and #95; reference them where appropriate.
- Work should be done on `main-dev` unless instructed otherwise.

## Next Steps (Suggested)
1. Complete Issue #94 (tests/stabilization).  
2. Create package skeleton and update imports (small PR).  
3. Incrementally migrate core, then UI, updating tests as you go.  
4. Add CI to protect refactors and enforce style.

---

_Assisting status:_ queued for work when approved.
