"""Configuration pytest partagée : serveur, navigateur, fixture `app`, options,
skip des lanes à prérequis, écriture de TEST-REPORT.md / results.json.
"""
import json
from datetime import datetime, timedelta
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
    # horodatage de début (heure locale, avec décalage) pour le rapport de synthèse
    config._rae_start = datetime.now().astimezone()


def _fmt_duration(delta):
    """Durée « H:MM:SS » (+ secondes décimales sous la minute)."""
    s = delta.total_seconds()
    h, r = divmod(int(s), 3600)
    m, sec = divmod(r, 60)
    return f"{h}:{m:02d}:{sec:02d}" + (f" ({s:.1f}s)" if s < 60 else "")


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
    context = browser.new_context(reduced_motion="reduce", color_scheme=theme,
                                   viewport={"width": 1280, "height": 900}, device_scale_factor=1)
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
    end = datetime.now().astimezone()
    start = getattr(config, "_rae_start", end)
    elapsed = end - start
    tests_time = sum(r["duration"] for r in rows)   # cumul des durées de test (call)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "results.json").write_text(
        json.dumps({"generated": end.isoformat(),
                    "started": start.isoformat(), "ended": end.isoformat(),
                    "duration_seconds": round(elapsed.total_seconds(), 3),
                    "tests_time_seconds": round(tests_time, 3),
                    "counts": counts, "tests": rows},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(counts.values())
    md = ["# TEST-REPORT — Risk Analysis Editor", "",
          f"_{total} cas · statut de sortie pytest : {exitstatus}._", "",
          "| Exécution | |", "|---|---|",
          f"| Début | {start.isoformat(timespec='seconds')} |",
          f"| Fin | {end.isoformat(timespec='seconds')} |",
          f"| Durée (horloge) | {_fmt_duration(elapsed)} |",
          f"| Temps cumulé des tests | {_fmt_duration(timedelta(seconds=tests_time))} |",
          "",
          "| Résultat | Nombre |", "|---|---:|"]
    for k in ("passed", "failed", "error", "skipped", "xfailed", "xpassed"):
        if counts.get(k):
            md.append(f"| {k} | {counts[k]} |")
    fails = [r for r in rows if r["outcome"] in ("failed", "error")]
    if fails:
        md += ["", "## Échecs", "", "| Test | Durée (s) |", "|---|---:|"]
        md += [f"| `{r['id']}` | {r['duration']} |" for r in fails]
    (ARTIFACTS / "TEST-REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
