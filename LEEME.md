# Calorías — contador personal para iPhone

App web instalable (PWA). No tiene suscripción ni cuentas. El diario vive solo en el iPhone.
Todas las búsquedas son locales: la app no consulta internet para buscar.

## Qué hay

| Carpeta | Contenido |
|---|---|
| `app/` | La app completa. `alimentos.json` (comidas y alimentos) y `productos.json` (envasados) son las bases. |
| `app/vendor/` | El lector de códigos de barras (html5-qrcode 2.3.8), guardado local. |
| `herramientas/construir_base.py` | Arma `alimentos.json` y `productos.json` desde las fuentes de `datos/`. |
| `herramientas/curados.py` | Comidas típicas de Uruguay y Argentina con nombre propio. |
| `herramientas/leer_tabla_uruguay.py` | Lee la tabla uruguaya 2002 desde su PDF. |
| `herramientas/bajar_off.py` | Filtra el volcado de Open Food Facts por país. |
| `herramientas/glosario.py` | Glosario inglés → español para los nombres de USDA. |
| `datos/` | Las descargas originales (no hacen falta para usar la app). |

## Fuentes de datos

| Fuente | Qué aporta | Licencia |
|---|---|---|
| Tabla de composición de alimentos de Uruguay 2002 (MTSS-INDA, UdelaR – Facultad de Química, LATINFOODS/FAO) | 373 alimentos uruguayos: cortes vacunos, milanesas, chorizo, quesos, galletas, panes, platos preparados. | Publicación oficial; el PDF original ya no está en línea y se recuperó de Internet Archive. |
| USDA FoodData Central (FNDDS 2021-2023 y Foundation 2025-12) | 5.600 alimentos y platos con porciones. Nombres traducidos con un glosario. | Dominio público (CC0) |
| Open Food Facts (volcado CSV) | Productos envasados vendidos en Uruguay y Argentina, con código de barras. | ODbL |
| Comidas típicas (`curados.py`) | Chivito, pascualina, tortas fritas, refuerzo, martín fierro, milanesa, choripán, mate… | Salen de las tablas de arriba o son estimaciones marcadas «aprox.» |

## Actualizar las bases

```
python herramientas/leer_tabla_uruguay.py "datos/uruguay/zip/Tabla de Alimentos.pdf" datos/uruguay/uruguay.json
curl -L -o datos/off/off_productos.csv.gz https://static.openfoodfacts.org/data/en.openfoodfacts.org.products.csv.gz
python herramientas/bajar_off.py datos/off/off_productos.csv.gz datos/off/off.json uruguay argentina
python -I herramientas/construir_base.py datos/usda app/alimentos.json
```

Después subir `VERSION` en `app/sw.js` para que el iPhone baje las bases nuevas.
Los scripts que usan `pypdf` o `duckdb` corren sin `-I` (están instalados con `pip --user`).

## Probar en la PC

```
python -m http.server 8765 --directory app
```

y abrir http://localhost:8765.

## Instalar en el iPhone

El iPhone necesita **HTTPS** para la cámara (código de barras) y para el modo sin conexión.
1. Publicar la carpeta `app/` en un sitio HTTPS (ver opciones abajo).
2. Abrir la dirección en **Safari**.
3. Tocar Compartir → **Agregar a inicio**.
4. Abrir la app desde el ícono. Desde ahí funciona sin conexión.

Opciones de alojamiento:
- **GitHub Pages o Cloudflare Pages** (gratis): la PC puede estar apagada.
  Solo se publica la app y las bases; el diario nunca sale del teléfono.
- **La PC con Tailscale** (`tailscale serve`): privado, con HTTPS. La PC solo tiene que estar prendida
  para instalar o actualizar; después la app queda guardada en el iPhone.

## Única consulta externa

Si escaneás un código de barras que no está en `productos.json`, la app pregunta a Open Food Facts
en línea. Sin conexión, avisa y ofrece cargarlo a mano.

## Copia de seguridad

Ajustes → Exportar genera un `.json` con todo el diario. Importar lo restaura.
