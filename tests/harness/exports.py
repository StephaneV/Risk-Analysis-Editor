"""Sauvegarde des livrables produits par les tests d'export (Word/Excel/CSV/PDF).

Écrits sous tests/_artifacts/exports/ pour examen humain. Ce dossier est entièrement
gitignoré (voir tests/_artifacts/.gitignore) : jamais versionné, jamais effacé entre
deux exécutions (aucun nettoyage automatique). Réexécuter un test écrase simplement
son propre fichier.
"""
from pathlib import Path

from .browser import ARTIFACTS

EXPORTS = ARTIFACTS / "exports"


def save(name, data):
    """Écrit `data` (bytes ou str) dans _artifacts/exports/<name> et renvoie le chemin."""
    p = EXPORTS / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        p.write_text(data, encoding="utf-8")
    else:
        p.write_bytes(data)
    return p
