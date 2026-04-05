# Release Notes - teatime kcresonance

High-level summary of notable changes on the `kcresonance` line of work. For exact file-level history, use `git log` and `git diff`.

## 1.0.4

Session date: 2026-04-04

### Highlights

- changes tracked under issue [#127](https://github.com/genidma/teatime-accessibility/issues/127)
- Rhythm long-range plotting was tightened up so `30d`, `90d`, `180d`, and `All` preserve more complete history by combining event detail with stats-based fallback data.
- Rhythm time-range switching from `4h` through `All` now uses more stable redraw and sizing behavior.
- Rhythm opens as a normal resizable window with improved maximize behavior.
- Rhythm includes `Fit data in window` by default; turning it off allows the chart to expand and scroll for dense long-range views.
- Flow no longer uses a fixed last-21-days slice.
- Flow now supports range presets (`7d`, `30d`, `90d`, `All`) plus auto-populated `Year`, `Month`, and `Week` filters based on the dates found in saved data.
- Flow includes `Fit data in window` by default, with scrollable expansion when it is unchecked.
- Flow label placement was adjusted so the last date/value no longer clips at the edge of the window.
- Flow now marks deep-work full days at `240m+` with an orange vertical marker plus `dw` / `dw-fd` visual treatment.

### Statistics - Rhythm

- Added helper-driven coverage for range resolution, long-range fallback assembly, popup sizing, and fit-versus-scroll layout behavior.
- Preserved existing category filtering while improving how missing long-range days are surfaced.

### Statistics - Flow

- Added helper-driven coverage for range filtering, year/month/week availability, fit-versus-scroll sizing, label placement, and deep-work threshold logic.
- Calendar filters now narrow the currently selected range instead of replacing it outright.

### Authorship

- Cursor AI
- Codex by OpenAI

### Facilitator

- @genidma

### Tool Use

- Cursor
- VS Code
- GNOME
- ImageMagick
- Peek
- Firefox
- teatime-accessibility

### Validation

- Updated unit coverage in `tests/test_flow_logic.py` and `tests/test_rhythm_logic.py`.
- Repeated verification using `python -m unittest` for Flow, Rhythm, and compatibility logic.
- Syntax validation using `python -m py_compile bin/teatime/stats.py`.

---

If you are shipping from another branch, compare against this branch and adjust version numbers and bullets accordingly.
