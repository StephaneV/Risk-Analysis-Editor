"""Configuration pytest partagée : serveur, navigateur, fixture `app`, options,
skip des lanes à prérequis, écriture de TEST-REPORT.md / results.json.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from harness.browser import start_server, ARTIFACTS
from harness.app import App
from harness.render import has_soffice


# ------------------------------------------------------------------ configuration
def pytest_configure(config):
    # junit toujours sous tests/_artifacts/ (chemin absolu, indépendant du dossier d'invocation)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    if not getattr(config.option, "xmlpath", None):
        config.option.xmlpath = str(ARTIFACTS / "junit.xml")


# ------------------------------------------------------------------ options
def pytest_addoption(parser):
    parser.addoption("--lang", default="fr", choices=["fr", "en", "it"], help="Langue par défaut de l'UI")
    parser.addoption("--theme", default="light", choices=["light", "dark"], help="Thème par défaut de l'UI")
    parser.addoption("--update-baselines", action="store_true", help="Régénère les baselines visuelles")


@pytest.fixture
def update_baselines(request):
    return request.config.getoption("--update-baselines")


# ------------------------------------------------------------------ skips de lane
def pytest_runtest_setup(item):
    if item.get_closest_marker("pdf") and not has_soffice():
        pytest.skip("LibreOffice (soffice) indisponible — lane PDF sautée")


# ------------------------------------------------------------------ serveur & navigateur (session)
@pytest.fixture(scope="session")
def base_url():
    httpd, url = start_server()
    yield url
    httpd.shutdown()


@pytest.fixture(scope="session")
def _pw():
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(_pw):
    b = _pw.chromium.launch()
    yield b
    b.close()


# ------------------------------------------------------------------ app (une par test, isolée)
@pytest.fixture
def app(browser, base_url, request):
    lang = request.config.getoption("--lang")
    theme = request.config.getoption("--theme")
    context = browser.new_context(reduced_motion="reduce", color_scheme=theme)
    page = context.new_page()
    a = App(page, base_url).open()
    a.set_lang(lang).set_theme(theme)
    yield a
    context.close()


# ------------------------------------------------------------------ rapport agrégé
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    stats = terminalreporter.stats
    rows, counts = [], {}
    for outcome in ("passed", "failed", "error", "skipped", "xfailed", "xpassed"):
        for rep in stats.get(outcome, []):
            if getattr(rep, "when", "call") != "call" and outcome == "passed":
                continue
            counts[outcome] = counts.get(outcome, 0) + 1
            rows.append({"id": getattr(rep, "nodeid", "?"), "outcome": outcome,
                         "duration": round(getattr(rep, "duration", 0.0), 3)})
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "results.json").write_text(
        json.dumps({"generated": datetime.now(timezone.utc).isoformat(), "counts": counts, "tests": rows},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(counts.values())
    md = ["# TEST-REPORT — Risk Analysis Editor", "",
          f"_Généré le {datetime.now(timezone.utc).isoformat(timespec='seconds')} · "
          f"{total} cas · statut de sortie pytest : {exitstatus}._", "",
          "| Résultat | Nombre |", "|---|---:|"]
    for k in ("passed", "failed", "error", "skipped", "xfailed", "xpassed"):
        if counts.get(k):
            md.append(f"| {k} | {counts[k]} |")
    fails = [r for r in rows if r["outcome"] in ("failed", "error")]
    if fails:
        md += ["", "## Échecs", "", "| Test | Durée (s) |", "|---|---:|"]
        md += [f"| `{r['id']}` | {r['duration']} |" for r in fails]
    (ARTIFACTS / "TEST-REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
