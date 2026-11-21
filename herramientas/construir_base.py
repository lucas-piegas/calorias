"""Arma app/alimentos.json a partir de USDA FoodData Central (FNDDS + Foundation)
y de la lista de comidas argentinas de curados.py.

Uso:  python -I herramientas/construir_base.py datos/usda app/alimentos.json
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from glosario import FRASES, PALABRAS, PORCIONES  # noqa: E402
from curados import CURADOS  # noqa: E402

ENERGIA = ("208", "957", "958")  # kcal; Foundation a veces solo trae Atwater (957/958)
NUT = {"p": "203", "g": "204", "c": "205", "fi": "291", "az": "269", "na": "307"}


def patron(dic):
    claves = sorted(dic, key=len, reverse=True)
    return re.compile(r"(?<![a-z])(" + "|".join(re.escape(k) for k in claves) + r")(?![a-z])")


P_NOMBRE = patron({**PALABRAS, **FRASES})
P_PORCION = patron(PORCIONES)
DIC_NOMBRE = {**PALABRAS, **FRASES}


def traducir(texto, pat, dic):
    t = pat.sub(lambda m: dic[m.group(1)], texto.lower())
    t = re.sub(r"\s+", " ", t).strip(" ,")
    t = re.sub(r"\s+,", ",", t)
    return t[:1].upper() + t[1:]


def nutrientes(f):
    v = {}
    for n in f.get("foodNutrients", []):
        num = n.get("nutrient", {}).get("number")
        if n.get("amount") is None:
            continue
        v.setdefault(num, n["amount"])
    kcal = next((v[k] for k in ENERGIA if k in v), None)
    if kcal is None:
        return None
    r = {"k": round(kcal, 1)}
    for clave, num in NUT.items():
        r[clave] = round(v.get(num, 0.0), 1)
    return r


def porciones(f):
    out = []
    for p in f.get("foodPortions", []):
        g = p.get("gramWeight") or 0
        if g <= 0:
            continue
        desc = p.get("portionDescription")
        if not desc:
            unidad = (p.get("measureUnit") or {}).get("name", "")
            if unidad in ("undetermined", "RACC"):
                unidad = ""
            desc = " ".join(str(x) for x in (fmt(p.get("amount")), unidad, p.get("modifier") or "") if x)
        if not desc or desc.isdigit():
            continue
        out.append([traducir(desc, P_PORCION, PORCIONES), round(g, 1)])
    return out[:8]


def fmt(x):
    if x is None:
        return ""
    return str(int(x)) if float(x).is_integer() else str(x)


def main(origen, destino):
    origen = Path(origen)
    fndds = json.loads((origen / "surveyDownload.json").read_text(encoding="utf-8"))["SurveyFoods"]
    found = json.loads(next(origen.glob("FoodData_Central_foundation_food_json_*.json")).read_text(encoding="utf-8"))["FoundationFoods"]

    por_desc = {}
    items = []
    for fuente, lista in (("FNDDS", fndds), ("Foundation", found)):
        for f in lista:
            nu = nutrientes(f)
            if not nu:
                continue
            en = f["description"].strip()
            if re.search(r"\b(baby|toddler|infant formula|enfamil|similac|gerber)\b", en, re.I):
                continue
            item = {"id": f"u{f['fdcId']}", "n": traducir(en, P_NOMBRE, DIC_NOMBRE), "en": en,
                    **nu, "por": porciones(f), "f": "USDA " + fuente}
            por_desc.setdefault(en.lower(), item)
            items.append(item)

    # Tabla de composición de alimentos de Uruguay (2002)
    uy_items, por_uy = [], {}
    ruta_uy = origen.parent / "uruguay" / "uruguay.json"
    if ruta_uy.exists():
        for a in json.loads(ruta_uy.read_text(encoding="utf-8")):
            item = {"id": "uy" + a["clave"].rstrip("*"), "n": a["n"], "en": "", "k": a["k"], "p": a["p"],
                    "c": a["c"], "g": a["g"], "fi": a["fi"], "az": 0, "na": 0, "por": [],
                    "f": "Tabla de composición de alimentos de Uruguay 2002 · " + a["grupo"], "pais": "uy"}
            por_uy.setdefault(a["n"].lower(), item)
            uy_items.append(item)

    def buscar(desc):
        if desc.startswith("UY:"):
            return por_uy.get(desc[3:].lower())
        return por_desc.get(desc.lower())

    claves = ("k", "p", "c", "g", "fi", "az", "na")
    faltan = []
    curados = []
    for i, c in enumerate(CURADOS):
        if "usda" in c or "uy" in c:
            desc = c["usda"] if "usda" in c else "UY:" + c["uy"]
            base = buscar(desc)
            if not base:
                faltan.append(desc)
                continue
            nu = {k: base[k] for k in claves}
            fuente = f"USDA: {base['en']}" if "usda" in c else f"Tabla Uruguay 2002: {base['n']}"
        elif "receta" in c:
            total = sum(g for _, g in c["receta"])
            nu = {k: 0.0 for k in claves}
            ok = True
            for desc, g in c["receta"]:
                b = buscar(desc)
                if not b:
                    faltan.append(desc)
                    ok = False
                    continue
                for k in nu:
                    nu[k] += b[k] * g / total
            if not ok:
                continue
            nu = {k: round(v, 1) for k, v in nu.items()}
            fuente = "Receta: " + " + ".join(f"{d.replace('UY:', '')} {g} g" for d, g in c["receta"])
        else:
            k, p, cc, g = c["aprox"]
            nu = {"k": k, "p": p, "c": cc, "g": g, "fi": 0, "az": 0, "na": 0}
            fuente = "Valor aproximado (" + c.get("fuente", "estimado") + ")"
        curados.append({"id": f"ar{i}", "n": c["n"], "en": "", **nu, "por": [list(x) for x in c["por"]],
                        "f": fuente, "tipico": 1, "pais": c.get("pais", "ar")})

    if faltan:
        print("NO ENCONTRADOS:", *sorted(set(faltan)), sep="\n  ")
        sys.exit(1)

    salida = {"version": 2,
              "fuentes": "USDA FoodData Central (CC0) — FNDDS 2021-2023 y Foundation 2025-12; "
                         "Tabla de composición de alimentos de Uruguay 2002 (MTSS-INDA, UdelaR, LATINFOODS/FAO)",
              "alimentos": curados + uy_items + items}
    Path(destino).write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(curados)} típicos + {len(uy_items)} Uruguay + {len(items)} USDA -> {destino} "
          f"({Path(destino).stat().st_size // 1024} KB)")

    # Productos envasados de Open Food Facts (archivo aparte: es el más grande)
    ruta_off = origen.parent / "off" / "off.json"
    if ruta_off.exists():
        productos = productos_off(json.loads(ruta_off.read_text(encoding="utf-8")))
        destino_off = Path(destino).with_name("productos.json")
        destino_off.write_text(json.dumps({"version": 2, "fuentes": "Open Food Facts (ODbL) — volcado Parquet",
                                           "productos": productos}, ensure_ascii=False, separators=(",", ":")),
                               encoding="utf-8")
        print(f"{len(productos)} productos -> {destino_off} ({destino_off.stat().st_size // 1024} KB)")


def gramos_envase(texto):
    """'500 g' -> 500, '1 kg' -> 1000, '250 ml' -> 250, '1,5 L' -> 1500."""
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*(kg|g|gr|grs|ml|cc|l|lt|cl)\b", (texto or "").lower())
    if not m:
        return None
    n = float(m.group(1).replace(",", "."))
    return n * {"kg": 1000, "l": 1000, "lt": 1000, "cl": 10}.get(m.group(2), 1)


def productos_off(lista):
    """Compacta cada producto en una lista: [código, nombre, marca, k, p, c, g, porciones, país, escaneos]."""
    vistos, out = set(), []
    for p in sorted(lista, key=lambda x: -x["escaneos"]):
        if p["code"] in vistos:
            continue
        vistos.add(p["code"])
        por = []
        if p.get("porcion_g") and 0 < p["porcion_g"] < 2000:
            por.append([f"1 porción ({p['porcion'] or str(p['porcion_g']) + ' g'})", round(p["porcion_g"], 1)])
        env = gramos_envase(p.get("cantidad"))
        if env and 0 < env <= 5000:
            por.append([f"1 envase ({p['cantidad']})", round(env, 1)])
        pais = "uy" if "uruguay" in p["paises"] else "ar"
        out.append([p["code"], p["n"], p["marca"], p["k"], p["p"], p["c"], p["g"], por, pais, p["escaneos"]])
    return out


if __name__ == "__main__":
    main(*sys.argv[1:3])
