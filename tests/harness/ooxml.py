"""Inspection d'un paquet OOXML (.docx/.xlsx) produit par l'application.

L'app construit ses exports en mémoire (buildDocx/buildXlsx) ; les tests récupèrent
les octets (base64) puis les analysent ici, sans écrire de fichier ni cliquer « Enregistrer ».
"""
import io
import re
import zipfile


def open_pkg(data: bytes):
    """Renvoie un dict {nom_de_partie: octets} du ZIP OOXML."""
    zf = zipfile.ZipFile(io.BytesIO(data))
    return {n: zf.read(n) for n in zf.namelist()}


def document_xml(data: bytes) -> str:
    return open_pkg(data)["word/document.xml"].decode("utf-8", "replace")


def texts(xml: str):
    """Liste des textes <w:t> d'un document Word."""
    return re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml)


def count(xml: str, needle: str) -> int:
    return xml.count(needle)


def media_names(data: bytes):
    return [n for n in open_pkg(data) if n.startswith("word/media/")]
