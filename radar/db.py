"""Memoria del radar en SQLite (precios.db). Vive solo en la laptop del radar; no se sube a git."""
import sqlite3
import time

ESQUEMA = """
PRAGMA journal_mode = WAL;
CREATE TABLE IF NOT EXISTS productos (
    id          INTEGER PRIMARY KEY,
    link        TEXT    NOT NULL UNIQUE,      -- enlace de afiliado (https://meli.la/…)
    ml_id       TEXT,                         -- ID de Mercado Libre (MLM…)
    url_final   TEXT,
    titulo      TEXT,
    imagen      TEXT,
    activo      INTEGER NOT NULL DEFAULT 1,   -- 0 si salió de enlaces.txt
    creado      INTEGER NOT NULL,
    actualizado INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS observaciones (
    id             INTEGER PRIMARY KEY,
    producto_id    INTEGER NOT NULL REFERENCES productos(id),
    ts             INTEGER NOT NULL,          -- Unix UTC
    precio         REAL    NOT NULL,
    precio_tachado REAL,
    cupon_texto    TEXT,
    cupon_pct      REAL,
    cupon_monto    REAL,
    disponible     INTEGER NOT NULL DEFAULT 1,
    fuente         TEXT,
    sospechosa     INTEGER NOT NULL DEFAULT 0 -- lectura descartada por las reglas
);
CREATE INDEX IF NOT EXISTS obs_producto_ts ON observaciones (producto_id, ts);
CREATE TABLE IF NOT EXISTS enriquecimiento_ia (
    producto_id     INTEGER PRIMARY KEY REFERENCES productos(id),
    titulo_hash     TEXT    NOT NULL,         -- si cambia el título, se vuelve a procesar
    nombre          TEXT,
    categoria       TEXT,
    specs_json      TEXT,
    estado          TEXT    NOT NULL DEFAULT 'pendiente',  -- pendiente | reintentando | ok
    intentos        INTEGER NOT NULL DEFAULT 0,
    proximo_intento INTEGER NOT NULL DEFAULT 0,
    ultimo_error    TEXT,
    modelo          TEXT,
    ts              INTEGER
);
CREATE TABLE IF NOT EXISTS alertas (
    id                 INTEGER PRIMARY KEY,
    producto_id        INTEGER NOT NULL REFERENCES productos(id),
    ts                 INTEGER NOT NULL,
    tipo               TEXT    NOT NULL,      -- super (súper oferta) | baja (cualquier baja real)
    precio_antes       REAL    NOT NULL,      -- súper: precio de hace ~1 h; baja: lectura anterior
    precio_ahora       REAL    NOT NULL,
    referencia_30d     REAL,
    caida_pct          REAL,
    descuento_real_pct REAL,
    motivo             TEXT
);
CREATE INDEX IF NOT EXISTS alertas_tipo_ts ON alertas (tipo, ts);
CREATE TABLE IF NOT EXISTS meta (clave TEXT PRIMARY KEY, valor TEXT);
"""


class DB:
    def __init__(self, ruta="precios.db"):
        self.c = sqlite3.connect(ruta, timeout=30)
        self.c.row_factory = sqlite3.Row
        self.c.executescript(ESQUEMA)

    def cerrar(self):
        # Pasa todo el WAL al archivo principal: precios.db queda completo por sí solo (caché de GitHub Actions)
        self.c.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        self.c.close()

    # ---------- productos ----------
    def producto(self, link):
        return self.c.execute("SELECT * FROM productos WHERE link = ?", (link,)).fetchone()

    def guardar_producto(self, lectura, ahora=None):
        ahora = int(ahora or time.time())
        with self.c:
            self.c.execute("""
                INSERT INTO productos (link, ml_id, url_final, titulo, imagen, activo, creado, actualizado)
                VALUES (?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(link) DO UPDATE SET ml_id = excluded.ml_id, url_final = excluded.url_final,
                    titulo = excluded.titulo, imagen = excluded.imagen, activo = 1, actualizado = excluded.actualizado
            """, (lectura["link"], lectura["ml_id"], lectura["url_final"], lectura["titulo"], lectura["imagen"], ahora, ahora))
        return self.producto(lectura["link"])["id"]

    def asegurar_producto(self, link, ahora=None):
        """Producto sin leer todavía (p. ej. al importar el historial anterior)."""
        ahora = int(ahora or time.time())
        with self.c:
            self.c.execute("INSERT OR IGNORE INTO productos (link, creado, actualizado) VALUES (?, ?, ?)", (link, ahora, ahora))
        return self.producto(link)["id"]

    def sincronizar_activos(self, links):
        with self.c:
            self.c.execute("UPDATE productos SET activo = 0")
            self.c.executemany("UPDATE productos SET activo = 1 WHERE link = ?", [(u,) for u in links])

    def activos(self):
        return self.c.execute("SELECT * FROM productos WHERE activo = 1 AND titulo IS NOT NULL ORDER BY id").fetchall()

    # ---------- observaciones ----------
    def guardar_observacion(self, pid, lectura, sospechosa=False, ts=None):
        cup = lectura.get("cupon") or {}
        with self.c:
            self.c.execute("""
                INSERT INTO observaciones (producto_id, ts, precio, precio_tachado, cupon_texto, cupon_pct,
                    cupon_monto, disponible, fuente, sospechosa) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pid, int(ts or time.time()), lectura["precio"], lectura.get("tachado"), cup.get("texto"),
                  cup.get("pct"), cup.get("monto"), int(lectura.get("disponible", True)), lectura.get("fuente"),
                  int(bool(sospechosa))))

    def historial(self, pid, desde):
        """Lecturas válidas desde `desde` (Unix), de la más vieja a la más nueva."""
        return self.c.execute("""
            SELECT * FROM observaciones WHERE producto_id = ? AND ts >= ? AND sospechosa = 0 ORDER BY ts
        """, (pid, int(desde))).fetchall()

    def hay_observaciones(self):
        return self.c.execute("SELECT 1 FROM observaciones LIMIT 1").fetchone() is not None

    # ---------- alertas ----------
    def guardar_alerta(self, pid, tipo, antes, ahora_precio, referencia=None, caida=None, descuento=None, motivo=None, ts=None):
        with self.c:
            self.c.execute("""
                INSERT INTO alertas (producto_id, ts, tipo, precio_antes, precio_ahora, referencia_30d, caida_pct,
                    descuento_real_pct, motivo) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (pid, int(ts or time.time()), tipo, antes, ahora_precio, referencia, caida, descuento, motivo))

    def alertas(self, tipo, desde, limite=30):
        return self.c.execute("""
            SELECT a.*, p.link, p.titulo, p.imagen, p.ml_id FROM alertas a JOIN productos p ON p.id = a.producto_id
            WHERE a.tipo = ? AND a.ts >= ? AND p.activo = 1 ORDER BY a.ts DESC LIMIT ?
        """, (tipo, int(desde), limite)).fetchall()

    def ultima_super(self, pid, desde):
        return self.c.execute("""
            SELECT * FROM alertas WHERE producto_id = ? AND tipo = 'super' AND ts >= ? ORDER BY ts DESC LIMIT 1
        """, (pid, int(desde))).fetchone()

    # ---------- IA ----------
    def ia(self, pid):
        return self.c.execute("SELECT * FROM enriquecimiento_ia WHERE producto_id = ?", (pid,)).fetchone()

    def encolar_ia(self, pid, titulo_hash):
        """Encola si el producto nunca pasó por la IA o si su título cambió."""
        fila = self.ia(pid)
        if fila and fila["titulo_hash"] == titulo_hash:
            return False
        with self.c:
            self.c.execute("""
                INSERT INTO enriquecimiento_ia (producto_id, titulo_hash, estado, intentos, proximo_intento)
                VALUES (?, ?, 'pendiente', 0, 0)
                ON CONFLICT(producto_id) DO UPDATE SET titulo_hash = excluded.titulo_hash, estado = 'pendiente',
                    intentos = 0, proximo_intento = 0, ultimo_error = NULL
            """, (pid, titulo_hash))
        return True

    def pendientes_ia(self, ahora, limite):
        return self.c.execute("""
            SELECT e.*, p.titulo FROM enriquecimiento_ia e JOIN productos p ON p.id = e.producto_id
            WHERE e.estado != 'ok' AND e.proximo_intento <= ? AND p.activo = 1
            ORDER BY e.proximo_intento, e.producto_id LIMIT ?
        """, (int(ahora), limite)).fetchall()

    def cuenta_pendientes_ia(self):
        return self.c.execute("SELECT COUNT(*) FROM enriquecimiento_ia WHERE estado != 'ok'").fetchone()[0]

    def ia_ok(self, pid, datos, specs_json, modelo, ahora=None):
        with self.c:
            self.c.execute("""
                UPDATE enriquecimiento_ia SET nombre = ?, categoria = ?, specs_json = ?, estado = 'ok', modelo = ?,
                    ts = ?, ultimo_error = NULL, intentos = intentos + 1 WHERE producto_id = ?
            """, (datos["nombre"], datos["categoria"], specs_json, modelo, int(ahora or time.time()), pid))

    def ia_reprogramar(self, pid, cuando, error):
        with self.c:
            self.c.execute("""
                UPDATE enriquecimiento_ia SET estado = 'reintentando', intentos = intentos + 1, proximo_intento = ?,
                    ultimo_error = ? WHERE producto_id = ?
            """, (int(cuando), str(error)[:300], pid))

    def ia_pausar_todos(self, cuando, error):
        with self.c:
            self.c.execute("""
                UPDATE enriquecimiento_ia SET estado = 'reintentando', proximo_intento = MAX(proximo_intento, ?),
                    ultimo_error = ? WHERE estado != 'ok'
            """, (int(cuando), str(error)[:300]))

    # ---------- meta ----------
    def meta(self, clave, defecto=None):
        fila = self.c.execute("SELECT valor FROM meta WHERE clave = ?", (clave,)).fetchone()
        return fila["valor"] if fila else defecto

    def poner_meta(self, clave, valor):
        with self.c:
            self.c.execute("INSERT INTO meta (clave, valor) VALUES (?, ?) ON CONFLICT(clave) DO UPDATE SET valor = excluded.valor",
                           (clave, str(valor)))
