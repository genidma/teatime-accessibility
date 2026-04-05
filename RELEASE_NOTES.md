# Release notes — teatime kcresonance

High-level summary of notable changes on the **kcresonance** line of work. For exact file-level history, use `git log` and `git diff`.

## 1.0.4

### Version and branding

- **About** dialog reports version **1.0.4** for this build (`APP_VERSION` in application metadata).

### Statistics — Rhythm

- **Long ranges (e.g. 90 days and “All”):** Y-axis date labels are thinned and shortened so dense ranges stay readable; plotting of sessions is unchanged.
- **Time-range switching:** Fixes for GTK + Matplotlib so changing presets (4h through All) no longer skews or stacks the chart; canvas sizing, redraw timing, and resize handling were aligned.
- **Window and layout:** Rhythm opens as a normal resizable window with improved maximize behavior.
- **“Fit data in window”:** New option (on by default) to fit the chart to the viewport; when off, a scrollable layout supports tall plots for long date spans.

### Statistics — Flow

- **Date range / timeline:** Corrects cases where the last day or segment was clipped or omitted at the end of the visible range.
- **Deep work — full days:** Visual cue (e.g. orange day marker) when a day’s total deep-work minutes reach **240** or more, with an updated **dw** / full-day label treatment.

### Packaging and tooling

- Desktop entry and launcher script updates for this variant where applicable.

### Tests and quality

- Added or expanded automated coverage around **Rhythm** and **Flow** logic, plus GUI testing helpers and documentation for Dogtail-oriented runs (see `tests/`).

---

*If you are shipping from another branch, compare against this branch and adjust version numbers and bullets accordingly.*
