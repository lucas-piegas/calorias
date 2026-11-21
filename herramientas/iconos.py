"""Genera los íconos PNG (sin dependencias): fondo verde y un anillo blanco con una porción."""
import math, struct, zlib, sys
def png(tam, ruta):
    filas = []
    c = tam / 2
    for y in range(tam):
        fila = bytearray([0])
        for x in range(tam):
            dx, dy = x + .5 - c, y + .5 - c
            r = math.hypot(dx, dy) / tam
            ang = (math.degrees(math.atan2(dx, -dy)) + 360) % 360
            col = (15, 118, 110)
            if 0.24 < r < 0.34 and ang < 290: col = (255, 255, 255)
            elif 0.24 < r < 0.34: col = (122, 196, 186)
            fila += bytes(col)
        filas.append(bytes(fila))
    raw = zlib.compress(b"".join(filas), 9)
    ch = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xffffffff)
    open(ruta, "wb").write(b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", tam, tam, 8, 2, 0, 0, 0)) + ch(b"IDAT", raw) + ch(b"IEND", b""))
png(180, sys.argv[1] + "/icono-180.png"); png(512, sys.argv[1] + "/icono-512.png")
