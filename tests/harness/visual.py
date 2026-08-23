"""Comparaison d'images tolérante (régression visuelle), via Pillow.

diff_ratio renvoie l'écart absolu moyen normalisé (0 = identique, 1 = opposé). Une faible tolérance
absorbe les micro-différences d'anticrénelage entre exécutions.
"""
import io

from PIL import Image, ImageChops


def diff_ratio(current_png: bytes, baseline_path) -> float:
    a = Image.open(io.BytesIO(current_png)).convert("RGB")
    b = Image.open(baseline_path).convert("RGB")
    if a.size != b.size:
        return 1.0  # dimensions différentes -> écart maximal
    hist = ImageChops.difference(a, b).histogram()  # 3 bandes × 256
    total = sum((i % 256) * c for i, c in enumerate(hist))
    pixels = a.size[0] * a.size[1] * 3
    return total / (pixels * 255) if pixels else 0.0
