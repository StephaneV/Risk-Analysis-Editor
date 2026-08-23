"""Lane PDF (optionnelle) : conversion .docx -> .pdf via LibreOffice.

Absente sur une machine minimale : les fonctions renvoient None / lèvent RuntimeError,
et les tests marqués @pytest.mark.pdf sont SKIP (voir conftest) plutôt qu'en échec.
"""
import os
import shutil
import subprocess
from pathlib import Path

_SOFFICE_CANDIDATES = [
    "soffice",
    "libreoffice",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
]


def soffice_path():
    for c in _SOFFICE_CANDIDATES:
        if os.path.isabs(c):
            if Path(c).exists():
                return c
        elif shutil.which(c):
            return shutil.which(c)
    return None


def has_soffice() -> bool:
    return soffice_path() is not None


def docx_to_pdf(docx_path, out_dir) -> Path:
    exe = soffice_path()
    if not exe:
        raise RuntimeError("LibreOffice (soffice) introuvable")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [exe, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx_path)],
        check=True, capture_output=True, timeout=120,
    )
    pdf = out_dir / (Path(docx_path).stem + ".pdf")
    if not pdf.exists():
        raise RuntimeError(f"PDF non produit pour {docx_path}")
    return pdf
