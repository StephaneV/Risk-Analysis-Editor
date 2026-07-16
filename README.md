# Risk Analysis Editor (RAE)

**English** · [Français](README.fr.md)

Standalone tool for **building and visualizing risk matrices** — inherent (gross) risk and residual (net) risk — with an open, documented file format, `.rae.json`.

### ▶️ [Open the app](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html) · 📊 [Open a sample analysis](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html?file=../examples/risk-analysis-information-system.rae.json) · ⬇️ [Download](https://github.com/StephaneV/Risk-Analysis-Editor/releases/latest/download/risk-analysis-editor.html)

*No installation: the tool runs entirely in your browser. The sample analysis is the one shown in the screenshot below (8 risks, 7 measures). The download provides **the single HTML file** of the [latest release](https://github.com/StephaneV/Risk-Analysis-Editor/releases/latest): double-click it to work **offline**.*

![Matrices › Trajectory view of the "Information system" analysis (light theme)](docs/images/capture-trajectoire.png)

> ***Matrices › Trajectory** view: each arrow links a risk's initial position (dashed outline) to its residual position (solid outline).*

---

## Overview

**Risk Analysis Editor** is a **standalone** web app: a single HTML file, with no external dependency, that works **offline** (a simple double-click is enough — no installation, no server).

It lets you carry out a complete risk analysis: define a scoring grid, enter risks and controls, link them, then **visualize** the shift from **inherent** to **residual** risk as matrices or arrowed trajectories.

The tool is **methodology-agnostic** (ISO 27005, EBIOS RM, DPIA/PIA, internal framework…): the grid (size, labels, thresholds, colors, scoring method) is fully configurable and saved inside the file.

The whole analysis fits in a self-contained **`.rae.json`** file: grid, risks, measures, links and initial/residual assessments. The format is **specified** ([technical documentation](docs/SPEC-format-analyse-risque.md), in French) and validated by a **JSON schema** ([schema-analyse-risque.json](docs/schema-analyse-risque.json)). Property names are in English; values (labels, descriptions) stay in the analysis's own language.

**Entry point:** [open the app online](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html) — or, for **offline** use, download the repository and open [`app/risk-analysis-editor.html`](app/risk-analysis-editor.html) with a simple double-click.

---

## Features

### Visualization
- **Two side-by-side matrices**: *inherent (gross)* and *residual (net)* risk.
- **Trajectory view**: an arrow links each risk's initial position to its residual position; unreduced risks are highlighted.
- **Optimized trajectory layouts**: straight arrows, minimized crossings and overlaps, centered square grid.
- **Chip layout strategies** when a cell holds several risks: grid, row, column, cluster/spiral, "+N" overflow…
- **Manual placement** of chips by drag-and-drop, with a configurable N×N snap grid and positions saved in the file.
- **Statistics**: distribution by criticality level (initial → residual), number of reduced risks.

### Scoring grid
- **Configurable axes** (vertical / horizontal): free number of levels, labels and tooltip descriptions.
- **Score computation methods**: product (P × S), sum (P + S) or **matrix** (level defined cell by cell, with a dedicated editor).
- **Criticality levels**: colored zones, thresholds, color, acceptance decision and description, with a **coverage check** of reachable scores.
- **Axis transposition** (vertical ↔ horizontal) in one click, assessments and placements included.

### Data entry
- **Overview**: dedicated tab for the analysis's document metadata (title, status, author, organization, scope, methodology reference, description) and analysis-level custom field values.
- **Risk register**: category, owner, description, initial and residual assessment, change indicator.
- **Controls / measures**: type (technical / organizational…), status (color-coded), responsible, due date, cost.
- **Risk ↔ measure links** via a checkbox cross-table (many-to-many relationship).
- **Action plan**: measure tracking across three views (timeline, kanban by status, grouped by owner), **overdue** measures highlighted (past due date and not finalized), and **overall progress** (bar + per-status counters).
- **Custom fields**: define, in *Settings*, extra fields attached to the analysis, risks or measures — 8 types (yes/no, integer, decimal, date, text, dropdown, checklist), multilingual labels (label and help are entered in the active interface language; when a translation is missing, the code is shown), a required flag and bounds (min/max, length, item count); values are entered in the records (risks, measures) and in the *Overview* tab (analysis fields), with validation, and are included in the **report** and in the **CSV import/export**.
- **CSV import** of risks, measures and links: columns named after the format's **English** keys, auto-detected separator; merge by identifier (risks/measures); integrity check and deduplication (links).
- **CSV export of risks, measures and links**: headers = **English** key names (identical whatever the interface language), `;` delimiter and UTF-8 BOM (Excel), with read-only derived columns (score/criticality for risks; covered risks for measures; labels for links); re-importable.
- **Sorting and filtering** of the Risks, Measures and Action plan lists: text search, sort by clicking columns, and dropdown filters (category, type, status, owner, "overdue only").

### File & export
- **New / Load / Save** in `.rae.json` format.
- **Load by URL**: opening the tool with `?file=<url>` (alias `?url=`) automatically loads the pointed analysis at startup — e.g. `risk-analysis-editor.html?file=../examples/risk-analysis-information-system.rae.json`. Requires the tool to be served over HTTP(S) (the `file://` protocol blocks this read).
- **Startup URL parameters** (combinable): `?lang=fr|en|it` forces the interface language (overrides the file's saved language and the browser language); `?tab=<tab>[.<sub-tab>]` opens a given tab, and optionally its sub-tab — e.g. `?tab=matrices.traj` (Matrices › Trajectory), `?tab=settings.grid`, `?tab=plan`. Unknown tokens are ignored.
- **Image export** of the matrices: **PNG** (×1 / ×2 / ×3 resolution) and **SVG**, copy to clipboard, with title, subtitle, axis labels and legend.
- **Printable report**: the *Report* tab generates a complete document (metadata, an **Overview block** with the analysis description and custom fields, summary, grid and criticality levels with descriptions, Initial/Residual and Trajectory matrices as vectors, risk register, detailed risk and measure lists with their descriptions **and custom field values**, links), rendered in a light, printable style (→ PDF via the browser).

### Customization
- **Themes**: dark, light.
- **Language selector**: French / English / Italian (interface and default data for a new analysis), architecture extensible to other languages.

---

## Project structure

| Folder | Contents |
|---|---|
| [`app/`](app/) | The application (`risk-analysis-editor.html`). |
| [`docs/`](docs/) | Technical documentation (in French): format specification, JSON schema and layout strategies. |
| [`examples/`](examples/) | Sample analyses in `.rae.json` format (French and English). |

---

## Getting started

1. [Open the app online](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html) — or open [`app/risk-analysis-editor.html`](app/risk-analysis-editor.html) from a local copy, in a recent browser.
2. The tool starts on a **blank analysis**, opened on the **Overview** tab.
3. Use **Load…** to open a `.rae.json` file (e.g. from [`examples/`](examples/)), **Save** to export yours.

---

## License

Distributed under the **MIT** license — see [`LICENSE`](LICENSE).

© 2026 Stéphane Vinter
