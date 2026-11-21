"""Filtra el volcado CSV de Open Food Facts y guarda solo los productos vendidos en los
países elegidos, con nombre, marca, código de barras y valores por 100 g.

1) Bajar el volcado (1,5 GB, se actualiza todos los días):
   curl -L -o datos/off/off_productos.csv.gz https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz
2) Filtrar:
   python herramientas/bajar_off.py datos/off/off_productos.csv.gz datos/off/off.json uruguay argentina
(necesita duckdb: python -m pip install --user duckdb)
"""
import json
import sys
import time

import duckdb


def main(csv, destino, *paises):
    inicio = time.time()
    con = duckdb.connect()
    filtro = " OR ".join(f"countries_tags LIKE '%en:{p}%'" for p in paises)
    filas = con.execute(f"""
        SELECT code, product_name, brands, countries_tags,
               TRY_CAST("energy-kcal_100g" AS DOUBLE) AS kcal, TRY_CAST(energy_100g AS DOUBLE) AS kj,
               TRY_CAST(proteins_100g AS DOUBLE), TRY_CAST(carbohydrates_100g AS DOUBLE),
               TRY_CAST(fat_100g AS DOUBLE), TRY_CAST(fiber_100g AS DOUBLE),
               TRY_CAST(sugars_100g AS DOUBLE), TRY_CAST(sodium_100g AS DOUBLE),
               TRY_CAST(serving_quantity AS DOUBLE), serving_size, quantity,
               coalesce(TRY_CAST(unique_scans_n AS INTEGER), 0)
        FROM read_csv('{csv}', delim='\t', header=true, quote='', escape='', all_varchar=true,
                      ignore_errors=true, max_line_size=10000000)
        WHERE ({filtro})
    """).fetchall()

    productos = []
    for (code, nombre, marca, tags, kcal, kj, p, c, g, fi, az, na, porcion_g, porcion_txt, cantidad,
         escaneos) in filas:
        if kcal is None and kj is not None:
            kcal = kj / 4.184
        if not kcal or kcal > 950 or not (nombre or "").strip():
            continue
        productos.append({
            "code": code, "n": nombre.strip(), "marca": (marca or "").split(",")[0].strip(),
            "k": round(kcal, 1), "p": r1(p), "c": r1(c), "g": r1(g), "fi": r1(fi), "az": r1(az),
            "na": r1((na or 0) * 1000), "porcion_g": porcion_g, "porcion": porcion_txt, "cantidad": cantidad,
            "paises": [x for x in paises if f"en:{x}" in (tags or "")], "escaneos": escaneos,
        })
    json.dump(productos, open(destino, "w", encoding="utf-8"), ensure_ascii=False)
    print(f"{len(filas)} filas, {len(productos)} productos útiles -> {destino} ({time.time() - inicio:.0f} s)")


def r1(x):
    return round(x, 1) if x is not None else 0.0


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *sys.argv[3:])
