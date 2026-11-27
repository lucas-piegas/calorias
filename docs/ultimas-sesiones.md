# Últimas sesiones

> Una entrada por día de trabajo, la más nueva arriba, para retomar sin leer el historial.
> Se guardan las últimas 10. El detalle está en los commits y en `LEEME.md`.
> Las entradas anteriores al 2026-11-27 se reconstruyeron desde `git log`.

## 2026-11-27 — Rediseño móvil de la PWA

- **Hecho:** cada comida es una tarjeta con ícono y color. El Diario tiene una tira de la semana, un botón Agregar flotante y una barra con íconos. Agregar usa pastillas y tiene tres accesos (escanear, foto, crear). Cantidad usa pasos ±. Historial tiene un gráfico de 7 o 30 días. Ajustes es una lista agrupada y cada fila abre su hoja.
- **Dónde quedó:** en `main` (213c14c), con push y publicado en GitHub Pages. Caché `calorias-v7`.
- **Abierto:** probarlo en el iPhone real. Solo se probó en el navegador, a 375 px, en modo claro y oscuro.
- **No rehacer:** la propuesta visual está en el lienzo «Calorías — rediseño móvil» (claude.ai/artifact/AmeyaE7Btzodoqp2zPeQjn). Se usa la fuente del sistema, no Inter ni Space Grotesk, para que funcione sin conexión. Ya está arreglado: el modelo de la foto cambiaba el filtro de búsqueda.
- **Detalle:** commit 213c14c.

## 2026-11-24 — Foto del plato con Claude

- **Hecho:** Claude identifica los alimentos de la foto y reparte el peso. Las calorías salen de la base local. Se puede sacar la foto o elegirla de la galería. La dirección y la clave del intermediario se guardan al escribir.
- **Dónde quedó:** en `main` (491c6e6). El intermediario está en `foto-worker/`.
- **Abierto:** nada de esta sesión.
- **No rehacer:** —
- **Detalle:** commits 039d4d9, 8c24347 y 491c6e6.

## 2026-11-22 — Separar la app Entreno

- **Hecho:** la carpeta `entreno/` quedó ignorada, porque tiene su propio repositorio.
- **Dónde quedó:** en `main` (e95a179).
- **Abierto:** nada de esta sesión.
- **No rehacer:** —
- **Detalle:** commit e95a179.

## 2026-11-21 — Primera versión de la PWA

- **Hecho:** contador de calorías instalable, con bases locales de Uruguay, USDA y Open Food Facts. Se pueden agregar varios alimentos seguidos a la misma comida.
- **Dónde quedó:** en `main` (11477ad), publicado por GitHub Pages.
- **Abierto:** nada de esta sesión.
- **No rehacer:** —
- **Detalle:** `LEEME.md`.
