"""Comparaison d'images tolérante (régression visuelle), via Pillow.

diff_ratio renvoie l'écart absolu moyen normalisé (0 = identique, 1 = opposé). Une faible tolérance
absorbe les micro-différences d'anticrénelage entre exécutions.

Les captures de chaque exécution sont conservées sous tests/_artifacts/visual/ pour examen :
- <nom>.png                       : capture courante (toujours écrite) ;
- _diff/<nom>.current.png         : capture courante (en cas d'échec) ;
- _diff/<nom>.baseline.png        : baseline de référence (en cas d'échec) ;
- _diff/<nom>.diff.png            : différence amplifiée, zones changées en clair (en cas d'échec).
Ce dossier est entièrement gitignoré (tests/_artifacts/), jamais versionné.
"""
import io
import shutil

from PIL import Image, ImageChops

from .browser import ARTIFACTS

VISUAL_DIR = ARTIFACTS / "visual"
DIFF_DIR = VISUAL_DIR / "_diff"


def diff_ratio(current_png: bytes, baseline_path) -> float:
    a = Image.open(io.BytesIO(current_png)).convert("RGB")
    b = Image.open(baseline_path).convert("RGB")
    if a.size != b.size:
        return 1.0  # dimensions différentes -> écart maximal
    hist = ImageChops.difference(a, b).histogram()  # 3 bandes × 256
    total = sum((i % 256) * c for i, c in enumerate(hist))
    pixels = a.size[0] * a.size[1] * 3
    return total / (pixels * 255) if pixels else 0.0


def save_current(current_png: bytes, name: str):
    """Écrit la capture courante sous _artifacts/visual/<name>.png (toujours). Renvoie le chemin."""
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    p = VISUAL_DIR / f"{name}.png"
    p.write_bytes(current_png)
    return p


def save_failure(current_png: bytes, baseline_path, name: str):
    """En cas d'écart : écrit courante + baseline + différence amplifiée sous _diff/. Renvoie le dossier."""
    DIFF_DIR.mkdir(parents=True, exist_ok=True)
    (DIFF_DIR / f"{name}.current.png").write_bytes(current_png)
    try:
        shutil.copyfile(baseline_path, DIFF_DIR / f"{name}.baseline.png")
    except OSError:
        pass
    a = Image.open(io.BytesIO(current_png)).convert("RGB")
    try:
        b = Image.open(baseline_path).convert("RGB")
    except (OSError, ValueError):
        return DIFF_DIR
    if a.size == b.size:
        # différence amplifiée (×8, saturée) : les zones changées ressortent en clair sur fond noir
        diff = ImageChops.difference(a, b).point(lambda v: min(255, v * 8))
        diff.save(DIFF_DIR / f"{name}.diff.png")
    return DIFF_DIR
