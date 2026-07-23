# <img src="docs/images/RAE-logo-mini.svg" alt="" height="38" align="top"> Risk Analysis Editor (RAE)

**English** · [Français](README.fr.md)

Standalone tool for **building and visualizing risk matrices** — inherent (gross) risk and residual (net) risk — with an open, documented file format, `.rae.json`.

### ▶️ [Open the app](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html) · 📖 [**User guide**](docs/guide-utilisateur.md) · 📊 [EBIOS RM demo](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html?file=../examples/demo-ebios-rm-information-system.rae.json) · 🛡️ [DPIA demo](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html?file=../examples/demo-dpia-ohs.rae.json) · ⬇️ [Download](https://github.com/StephaneV/Risk-Analysis-Editor/releases/latest/download/risk-analysis-editor.html)

*No installation: the tool runs entirely in your browser. Two ready-to-open demos: an **EBIOS RM–inspired** risk analysis (12 risks, 11 measures) and a **DPIA following the CNIL PIA method** for an occupational health service (12 risks, 12 measures) — both showcasing descriptions, notes, colored **tags**, **progress bars**, owners and per-link rationale. The download provides **the single HTML file** of the [latest release](https://github.com/StephaneV/Risk-Analysis-Editor/releases/latest): double-click it to work **offline**.*

![Matrices › Trajectory view of the "Information system" analysis (light theme)](docs/images/capture-trajectoire.png)

> ***Matrices › Trajectory** view: each arrow links a risk's initial position (dashed outline) to its residual position (solid outline).*

---

## Overview

**Risk Analysis Editor** is a **standalone** web app: a single HTML file, with no external dependency, that works **offline** (a simple double-click is enough — no installation, no server).

It lets you carry out a complete risk analysis: define a scoring grid, enter risks and controls, link them, then **visualize** the shift from **inherent** to **residual** risk as matrices or arrowed trajectories.

The tool is **methodology-agnostic** (ISO 27005, EBIOS RM, DPIA/PIA, internal framework…): the grid (size, labels, thresholds, colors, scoring method) is fully configurable and saved inside the file.

The whole analysis fits in a self-contained **`.rae.json`** file: grid, risks, measures, links and initial/residual assessments. The format is **specified** ([technical documentation](specs/SPEC-format-analyse-risque.md), in French) and validated by a **JSON schema** ([schema-analyse-risque.json](specs/schema-analyse-risque.json)). Property names are in English; values (labels, descriptions) stay in the analysis's own language.

**Official website:** [www.risk-analysis-editor.com](https://www.risk-analysis-editor.com/) — presentation, screenshots and links.

**Getting started:** the illustrated **[user guide](docs/guide-utilisateur.md)** (in French) walks through every screen and feature.

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
- **Risk ↔ measure links**, in two sub-tabs: *Associations* (checkbox cross-table, many-to-many) and *Details* (editable register where each link carries a **note** and its own **custom fields**); enriched links are flagged in the cross-table.
- **Action plan**: measure tracking across three views (timeline, kanban by status, grouped by owner), **overdue** measures highlighted (past due date and not finalized), and **overall progress** (bar + per-status counters). Each measure is **editable on click** (due date, status, owner, notes, custom fields) and, in the kanban, can be **dragged and dropped** between status columns.
- **Custom fields**: define, in *Settings*, extra fields attached to the analysis, risks, measures or links — 10 types (yes/no, integer, decimal, date, text, dropdown, checklist, **colored tags** with single/multiple choice, **progress bar** in %), multilingual labels (label and help are entered in the active interface language; when a translation is missing, the code is shown), a required flag and bounds (min/max, length, item count); values are entered in the records (risks, measures) and in the *Overview* tab (analysis fields), with validation, and are included in the **report** and in the **CSV import/export**.
- **CSV import** of risks, measures and links: columns named after the format's **English** keys, auto-detected separator; merge by identifier (risks/measures); integrity check and deduplication (links).
- **CSV export of risks, measures and links**: headers = **English** key names (identical whatever the interface language), `;` delimiter and UTF-8 BOM (Excel), with read-only derived columns (score/criticality for risks; covered risks for measures; labels for links); re-importable.
- **Sorting and filtering** of the Risks, Measures and Action plan lists: text search, sort by clicking columns (ascending → descending → original order), and dropdown filters (category, type, status, owner, "overdue only"). When no sort is active, rows can be **reordered by drag-and-drop** (⠿ handle on row hover, Ctrl+↑/↓ with the keyboard): the new order is saved in the file and drives the default display, the report and the exports.
- **Entry aids & safety nets**: one-click **duplicate** (⧉) of a risk or measure, **“Save and new”** for batch entry, an **“Undo”** toast after every deletion, clickable R*x*/M*x* pills that open the referenced record, an optional *“don't ask again”* for link confirmations, a warning when editing an already-assessed grid, and a **Help & shortcuts** panel (File menu, or the `?` key).
- **Customizable columns** in the Risks, Measures and Link details registers: show/hide columns and reorder them (drag the headers, or the ▲/▼ arrows in the ⚙ column menu), surface fields otherwise hidden (owner, due date, cost…) and add **custom-field columns**. The ID and Actions columns stay pinned; the layout is **saved in the file** (`extensions.display.columns`).

### File & export
- **New / Load / Save** in `.rae.json` format.
- **Load by URL**: opening the tool with `?file=<url>` (alias `?url=`) automatically loads the pointed analysis at startup — e.g. `risk-analysis-editor.html?file=../examples/risk-analysis-information-system.rae.json`. Requires the tool to be served over HTTP(S) (the `file://` protocol blocks this read).
- **Startup URL parameters** (combinable): `?lang=fr|en|it` forces the interface language (overrides the file's saved language and the browser language); `?tab=<tab>[.<sub-tab>]` opens a given tab, and optionally its sub-tab — e.g. `?tab=matrices.traj` (Matrices › Trajectory), `?tab=settings.grid`, `?tab=plan`; `?filter=code:value;code:value` applies custom-field filters — e.g. `?filter=feared_event:access`. Unknown tokens are ignored.
- **Filtering by custom field**: a field with closed values (dropdown, checklist, tags, yes/no) can be flagged *usable as a filter*. Every filter bar then lists **all** filterable fields — risk, measure and link alike — in every view, since a filter of any family affects every view. All active criteria apply together (AND) and **propagate along the links**: filtering on a risk keeps its links and the measures that treat it, and symmetrically for a measure or link filter. The current filtering is reflected in the URL, so a filtered view can be shared by copying the address.
- **Image export** of the matrices: **PNG** (×1 / ×2 / ×3 resolution) and **SVG**, copy to clipboard, with title, subtitle, axis labels and legend.
- **Word export (.docx)** of the report and **Excel export (.xlsx)** of the analysis: *File* menu (and a button in the *Report* tab for Word). The Word file mirrors the printable report — metadata, presentation, summary, grid, **matrices as embedded images**, registers and detailed sheets — ready to merge into a corporate template; the Excel workbook has four styled sheets (Summary / Risks / Measures / Links) with typed cells (real dates and numbers), criticality and status colors, frozen header rows and autofilters. Both are generated **locally, offline**: hand-written OOXML plus the embedded MIT-licensed [fflate](https://github.com/101arrowz/fflate) library for the ZIP container — still a single HTML file, no external dependency.
- **Printable report**: the *Report* tab generates a complete document (metadata, an **Overview block** with the analysis description and custom fields, summary, grid and criticality levels with descriptions, Initial/Residual and Trajectory matrices as vectors, risk register, detailed risk and measure lists with their descriptions **and custom field values**, links), rendered in a light, printable style (→ PDF via the browser).

### Customization
- **Themes**: dark, light.
- **Language selector**: French / English / Italian (interface and default data for a new analysis), architecture extensible to other languages.

---

## Project structure

| Folder | Contents |
|---|---|
| [`app/`](app/) | The application (`risk-analysis-editor.html`). |
| [`docs/`](docs/) | **User documentation** (in French): the illustrated [user guide](docs/guide-utilisateur.md), and shared images. |
| [`specs/`](specs/) | **Specifications** (in French): file-format specification, JSON schema and layout strategies. |
| [`examples/`](examples/) | Sample analyses in `.rae.json` format (French and English), including two **complete demos**: an **EBIOS RM–inspired** risk analysis (`demo-ebios-rm-*.rae.json`) and a **DPIA following the CNIL PIA method** for an occupational health service (`demo-aipd-sst.rae.json` / `demo-dpia-ohs.rae.json`) — with colored tags, progress bars, owners and justified links. |
| [`templates/`](templates/) | **Methodology templates** (`xxx.template.<lang>.rae.json`, one file per language): blank skeletons — grid, criticality levels and custom fields preconfigured, no risks or measures. **EBIOS RM**, **CNIL PIA / DPIA**, **ISO/IEC 27005** and a **generic** 5×5, each in **French, English and Italian**. Listed under *Start from a template* in the onboarding block (the file matching the current interface language is loaded); opening one (from there, or via *Load…*) starts a new, **unlinked** analysis. You can also turn the current analysis into a template with **File › Save as template…**, and return to the onboarding block with **File › Home screen**. |

---

## Getting started

1. [Open the app online](https://stephanev.github.io/Risk-Analysis-Editor/app/risk-analysis-editor.html) — or open [`app/risk-analysis-editor.html`](app/risk-analysis-editor.html) from a local copy, in a recent browser.
2. The tool starts on a **blank analysis**, opened on the **Overview** tab.
3. Use **Load…** to open a `.rae.json` file (e.g. from [`examples/`](examples/)), **Save** to export yours.

---

## Browser support

**Prerequisites**: a recent desktop browser (evergreen version) with JavaScript enabled — nothing else. No server, no network access and no installation are required; the app runs from a simple `file://` double-click. Only **Load by URL** (`?file=…`) needs the tool to be served over HTTP(S).

Development and testing are done primarily with **Microsoft Edge (Chromium)**; any Chromium-based browser (Chrome, Edge, Opera, Brave…) offers the full experience. Known differences with other engines:

- **Firefox / Safari** — the File System Access API (`showSaveFilePicker`) is not available: *Save* falls back to a standard **download** of the `.rae.json` file (and *Load* to a classic file picker) instead of writing directly into the opened file. Everything else works identically.
- **Older Firefox (< 127)** — copying a matrix to the clipboard **as an image** (`ClipboardItem`) is not supported; the PNG and SVG download buttons remain available.
- **Touch devices** — drag-and-drop interactions (chips, kanban, column headers) target mouse usage; keyboard and menu alternatives exist (Ctrl+arrows in the kanban and matrices, ▲/▼ arrows in the column menu), but the tool is designed for desktop use.

---

## Credits

RAE embeds exactly **one third-party library**: [**fflate** v0.8.2](https://github.com/101arrowz/fflate) (MIT license, © Arjun Barrett), a tiny, fast ZIP/deflate implementation. It provides the ZIP container required by the Word (`.docx`) and Excel (`.xlsx`) exports — OOXML files being ZIP archives of XML parts. The library is **vendored inline** in the HTML file, with its license notice, so the app keeps working fully offline with no external dependency. Everything else (Markdown engine, SVG/PNG export, OOXML generation, UI components) is written from scratch for this project.

---

## License

Distributed under the **MIT** license — see [`LICENSE`](LICENSE).

© 2026 Stéphane Vinter
