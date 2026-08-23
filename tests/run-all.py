#!/usr/bin/env python3
"""Point d'entrée unique : lance les suites et agrège le rapport (tests/_artifacts/).

  python tests/run-all.py                    # cœur (sans lanes lourdes)
  python tests/run-all.py --with-pdf         # + lane PDF (LibreOffice)
  python tests/run-all.py --with-visual      # + régression visuelle
  python tests/run-all.py --with-pdf --with-visual
Tout argument supplémentaire est transmis à pytest (ex. -k, -q, --lang en).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv):
    with_pdf = "--with-pdf" in argv
    with_visual = "--with-visual" in argv
    passthrough = [a for a in argv if a not in ("--with-pdf", "--with-visual")]

    excludes = []
    if not with_pdf:
        excludes.append("not pdf")
    if not with_visual:
        excludes.append("not visual")
    args = [str(HERE)]
    if excludes:
        args += ["-m", " and ".join(excludes)]
    args += passthrough

    import pytest
    return pytest.main(args)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
