# -*- coding: utf-8 -*-
# Embarque les modèles méthodologiques (templates/*.template.<lang>.rae.json) dans
# l'application, entre les marqueurs __TEMPLATES_DATA_START__ / __TEMPLATES_DATA_END__.
# À relancer après toute modification des fichiers de templates/.
#
#   python tools/embed-templates.py
#
# Produit : const TEMPLATE_DATA={"<base>":{"fr":{...},"en":{...},"it":{...}}, ...};
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL_DIR = os.path.join(ROOT, "templates")
APP = os.path.join(ROOT, "app", "risk-analysis-editor.html")
LANGS = ("fr", "en", "it")
START = "/*__TEMPLATES_DATA_START__*/"
END = "/*__TEMPLATES_DATA_END__*/"

def main():
    # Regroupe par base (ex. "ebios-rm.template") puis par langue.
    data = {}
    pat = re.compile(r"^(?P<base>.+)\.(?P<lang>fr|en|it)\.rae\.json$")
    for fn in sorted(os.listdir(TPL_DIR)):
        m = pat.match(fn)
        if not m:
            continue
        base, lang = m.group("base"), m.group("lang")
        with open(os.path.join(TPL_DIR, fn), encoding="utf-8") as f:
            data.setdefault(base, {})[lang] = json.load(f)

    if not data:
        print("Aucun modèle trouvé dans", TPL_DIR); sys.exit(1)

    for base, langs in sorted(data.items()):
        missing = [l for l in LANGS if l not in langs]
        if missing:
            print("Attention : %s — langues manquantes : %s" % (base, ",".join(missing)))

    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    block = "const TEMPLATE_DATA=" + payload + ";"

    with open(APP, encoding="utf-8") as f:
        html = f.read()
    i, j = html.find(START), html.find(END)
    if i < 0 or j < 0 or j < i:
        print("Marqueurs introuvables dans", APP); sys.exit(1)
    new = html[: i + len(START)] + "\n" + block + "\n" + html[j:]
    with open(APP, "w", encoding="utf-8", newline="") as f:
        f.write(new)

    n_tpl = len(data)
    n_lang = sum(len(v) for v in data.values())
    print("Embarqué : %d modèles (%d fichiers), %d octets de données." % (n_tpl, n_lang, len(payload)))

if __name__ == "__main__":
    main()
