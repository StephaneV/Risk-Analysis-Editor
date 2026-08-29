"""Rendu Word (moteur de gabarit) du Markdown inline : couleur ([texte]{.nom}),
surlignage (==texte==), gras/italique et sauts de ligne.

Exerce le vrai chemin de substitution (tmplRenderTokens -> tmplRichParts ->
tmplSubstituteRun -> tmplRunFromDesc), sans dépendre d'un gabarit fixture : on
insère un run porteur d'une balise, on règle une valeur Markdown, on substitue,
puis on inspecte le XML produit. Couvre les deux chemins de valeur Markdown :
- champ « enrichi » (kind:md) : description d'un risque ;
- valeur de champ texte multi-lignes (kind:cf textarea) : attribut d'objet.
"""
import io
import re
import zipfile

import pytest

from harness import exports, ooxml

pytestmark = pytest.mark.export

# Rend un run {{ <path> }} après avoir posé `md` sur `<target>`, via le chemin réel du
# moteur, et renvoie le XML du paragraphe produit. `setup` règle la valeur et le contexte.
SUBST = r"""
([path, md, mode]) => {
  const W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main';
  let obj, ctx;
  if (mode === 'risk') {
    obj = analyse.risks[0]; obj.description = md;
    ctx = [{ name:'risk', type:'risk', obj, index:0 }];
  } else {                                   // attribut d'objet (textarea)
    obj = (analyse.objects || []).find(o => o.type === 'evenement_redoute');
    obj.values = obj.values || {}; obj.values.impacts = md;
    ctx = [{ name:'object', type:'object', obj, index:0 }];
  }
  const xml = '<w:document xmlns:w="'+W+'"><w:body><w:p><w:r><w:rPr><w:sz w:val="22"/></w:rPr>'
    + '<w:t>{{ ' + path + ' }}</w:t></w:r></w:p></w:body></w:document>';
  const doc = new DOMParser().parseFromString(xml, 'application/xml');
  const run = doc.getElementsByTagNameNS(W, 'r')[0];
  tmplWarnings.length = 0;
  tmplReport = { date_format:null, filter:null, badge:'flat' };
  tmplImgReqs = []; tmplBlocksAllowed = true;
  tmplSubstituteRun(run, ctx, false);
  return new XMLSerializer().serializeToString(doc.getElementsByTagNameNS(W, 'p')[0]);
}
"""

RED = '<w:color w:val="d64545"/>'   # rouge de la palette
HL = 'w:fill="FFF2A8"'              # surlignage (ombrage jaune clair)

MD_SAMPLE = "Risque [élevé]{.red}, à traiter en ==priorité==. Voir **PCA/PRA**."


def _texts(xml):
    return "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", xml))


def test_risk_description_markdown_renders_as_runs(app):
    app.load("ebios-objets.rae.json")
    xml = app.js(SUBST, ["risk.description", MD_SAMPLE, "risk"])
    assert RED in xml            # couleur rouge
    assert HL in xml             # surlignage
    assert "<w:b/>" in xml       # gras (**PCA/PRA**)
    # aucune fuite littérale des syntaxes
    assert "]{.red}" not in xml
    assert "==priorit" not in xml
    assert not app.console_errors()


def test_object_textarea_attribute_markdown_renders(app):
    app.load("ebios-objets.rae.json")
    xml = app.js(SUBST, ["object.attr.impacts", MD_SAMPLE, "object"])
    assert RED in xml
    assert HL in xml
    assert "<w:b/>" in xml
    assert "]{.red}" not in xml


def test_plain_text_has_no_colour_or_shading(app):
    """Régression : un texte sans Markdown ne produit ni couleur ni ombrage, et reste intact."""
    app.load("ebios-objets.rae.json")
    plain = "Une description en texte simple, sans mise en forme."
    xml = app.js(SUBST, ["risk.description", plain, "risk"])
    assert "<w:color" not in xml
    assert "<w:shd" not in xml
    assert _texts(xml) == plain


def test_multiline_markdown_uses_line_breaks(app):
    app.load("ebios-objets.rae.json")
    xml = app.js(SUBST, ["risk.description", "ligne un\nligne deux", "risk"])
    assert "<w:br/>" in xml
    assert "ligne un" in _texts(xml) and "ligne deux" in _texts(xml)


# --- Artefact vérifiable : un .docx vitrine du rendu Markdown (couleur, surlignage, emphase) ---

# Construit le corps document.xml à partir d'échantillons Markdown, via le vrai rendu
# de runs (mdInlineToDescs -> tmplRunFromDesc). Un paragraphe de titre précède chaque
# échantillon pour rendre l'artefact lisible à l'ouverture.
BUILD_BODY = r"""
() => {
  const W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main';
  const base = '<w:sz w:val="22"/>';
  const samples = [
    ["Couleurs (palette de l'app)",
     "[red]{.red} · [orange]{.orange} · [yellow]{.yellow} · [green]{.green} · [teal]{.teal} · [blue]{.blue} · [purple]{.purple} · [cyan]{.cyan} · [pink]{.pink} · [gray]{.gray}"],
    ["Surlignage", "Mesure ==prioritaire== à traiter en ==priorité haute==."],
    ["Emphase", "**gras**, *italique*, ~~barré~~, `code`."],
    ["Combiné", "[**alerte**]{.red} ==critique==, action *urgente* — voir [PCA/PRA]{.blue}."],
    ["Multi-lignes", "Impacts :\n- fuite de données [confidentielles]{.red}\n- indisponibilité ==prolongée=="]
  ];
  const heading = t => '<w:p><w:r><w:rPr><w:b/><w:sz w:val="24"/><w:color w:val="0F766E"/></w:rPr>'
    + '<w:t xml:space="preserve">' + t + '</w:t></w:r></w:p>';
  const para = md => '<w:p>' + mdInlineToDescs(md).map(d => tmplRunFromDesc(base, d)).join('') + '</w:p>';
  const body = samples.map(([h, md]) => heading(h) + para(md)).join('<w:p/>');
  return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    + '<w:document xmlns:w="' + W + '"><w:body>' + body
    + '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"/></w:sectPr>'
    + '</w:body></w:document>';
}
"""

_CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    "</Types>"
)
_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    "</Relationships>"
)


def _pack_docx(document_xml: str) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", _CONTENT_TYPES)
        z.writestr("_rels/.rels", _RELS)
        z.writestr("word/document.xml", document_xml)
    return buf.getvalue()


def test_markdown_export_artifact_docx(app):
    """Produit `tests/_artifacts/exports/rapport-word-markdown.docx` — ouvrable dans Word /
    LibreOffice — montrant le rendu Markdown (couleur, surlignage, gras/italique, sauts de ligne)."""
    app.load("ebios-objets.rae.json")
    document_xml = app.js(BUILD_BODY)
    data = _pack_docx(document_xml)
    path = exports.save("rapport-word-markdown.docx", data)          # artefact à examiner
    # le paquet est un .docx valide et porte bien la mise en forme attendue
    xml = ooxml.document_xml(data)
    assert '<w:color w:val="d64545"/>' in xml     # couleur (red)
    assert 'w:fill="FFF2A8"' in xml               # surlignage
    assert "<w:b/>" in xml                         # gras
    assert "<w:br/>" in xml                        # saut de ligne
    assert path.exists() and path.stat().st_size > 0
