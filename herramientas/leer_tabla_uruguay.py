"""Lee la Tabla de composición de alimentos de Uruguay (MTSS-INDA / UdelaR, 2002)
desde el PDF y escribe un JSON con los macronutrientes por 100 g.

Uso:  python herramientas/leer_tabla_uruguay.py "datos/uruguay/zip/Tabla de Alimentos.pdf" datos/uruguay/uruguay.json
(necesita pypdf: python -m pip install --user pypdf)
"""
import json
import re
import sys

import pypdf

# Columnas de la tabla, en orden, con la palabra del encabezado que las ubica.
COLUMNAS = [("medida", "Medida"), ("hum", "Humedad"), ("k", "Energía"), ("p", "Proteínas"),
            ("g", "Grasa total"), ("cen", "Cenizas"), ("fi", "Fibra"), ("c", "CHO total")]
FILA = re.compile(r"^([A-Z]{1,2}\d+\*?)\s+(.+?)\s{2,}(\d+\s.*)$")
GRUPO = re.compile(r"^([A-Z]{1,2})\s{3,}([A-ZÁÉÍÓÚ][^\d]+?)\s*$")


def valor(x):
    """'T' (trazas) cuenta como 0; '-', '•' o vacío es 'sin dato' (None)."""
    if x is None:
        return None
    if x == "T":
        return 0.0
    try:
        return float(x)
    except ValueError:
        return None


def centros(encabezado):
    out = []
    for clave, palabra in COLUMNAS:
        i = encabezado.find(palabra)
        out.append((clave, i + len(palabra) / 2))
    return out


def main(pdf, destino):
    lector = pypdf.PdfReader(pdf)
    alimentos, grupo, dudosas = [], "", []
    for pagina in lector.pages:
        texto = pagina.extract_text(extraction_mode="layout")
        if "Macronutrientes" not in texto:
            continue
        lineas = texto.splitlines()
        enc = next((l for l in lineas if "Humedad" in l and "Energía" in l), None)
        if not enc:
            continue
        cols = centros(enc)
        for linea in lineas:
            g = GRUPO.match(linea.strip())
            if g:
                nombre_grupo = g.group(2).strip()
                mitad = len(nombre_grupo) // 2
                grupo = nombre_grupo[:mitad] if nombre_grupo[:mitad] == nombre_grupo[mitad:] else nombre_grupo
                continue
            m = FILA.match(linea.strip())
            if not m:
                if re.match(r"^[A-Z]{1,2}\d+", linea.strip()):
                    dudosas.append(linea.strip())
                continue
            # Cada valor va a la columna cuyo encabezado le queda más cerca.
            fila = {}
            for t in re.finditer(r"\S+", linea):
                if t.start() < linea.find(m.group(3)):
                    continue
                centro = (t.start() + t.end()) / 2
                clave_col = min(cols, key=lambda c: abs(c[1] - centro))[0]
                fila[clave_col] = t.group()
            nu = {k: valor(fila.get(k)) for k in ("k", "p", "g", "c", "fi")}
            p, gr, c = nu["p"] or 0.0, nu["g"] or 0.0, nu["c"]
            k = nu["k"]
            if c is None and k is not None:        # carbohidratos por diferencia
                c = max(0.0, round((k - 4 * p - 9 * gr) / 4, 1))
            if k is None and c is not None:        # energía por factores (4-4-9)
                k = round(4 * p + 4 * c + 9 * gr)
            if k is None:
                dudosas.append("sin energía ni carbohidratos: " + linea.strip())
                continue
            alimentos.append({"clave": m.group(1), "n": re.sub(r"\s+", " ", m.group(2)).strip(), "grupo": grupo,
                              "k": k, "p": p, "g": gr, "c": c, "fi": nu["fi"] or 0.0})
    json.dump(alimentos, open(destino, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"{len(alimentos)} alimentos -> {destino}")
    if dudosas:
        print(f"{len(dudosas)} filas sin leer:", *dudosas[:20], sep="\n  ")


if __name__ == "__main__":
    main(*sys.argv[1:3])
