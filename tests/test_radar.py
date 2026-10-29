"""Pruebas del radar sin red: reglas anti-fraude, cola de IA con saturación simulada y exportación.

Correr:  python -m unittest discover tests
"""
import json
import logging
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from radar import exportar, ia, reglas  # noqa: E402
from radar.db import DB  # noqa: E402

R = reglas.con_ajustes({})
H = 3600
DIA = 86400
AHORA = 1_800_000_000
log = logging.getLogger("prueba")
log.addHandler(logging.NullHandler())


def serie(precio, dias, cada_h=12, hasta=AHORA - 2 * H):
    """Lecturas cada `cada_h` horas durante `dias` días, terminando 2 h antes de AHORA."""
    n = int(dias * 24 / cada_h)
    return [(hasta - i * cada_h * H, precio) for i in range(n, -1, -1)]


class Reglas(unittest.TestCase):
    def test_producto_nuevo_usa_tachado_y_no_es_super(self):
        ev = reglas.evaluar(800, 1000, serie(1000, 2), AHORA, R)
        self.assertFalse(ev["suficiente"])
        self.assertEqual(ev["antes"], 1000)
        self.assertEqual(ev["descuento_pct"], 20)
        self.assertFalse(ev["super_deal"])
        self.assertEqual(ev["motivo"], "historial insuficiente")

    def test_descuento_falso_con_precio_inflado(self):
        # 30 días a $1000, luego el vendedor sube a $1500 tres días y "rebaja" a $1000 con tachado de $1500.
        hist = serie(1000, 30, hasta=AHORA - 4 * DIA) + serie(1500, 3)
        ev = reglas.evaluar(1000, 1500, hist, AHORA, R)
        self.assertTrue(ev["suficiente"])
        self.assertTrue(ev["tachado_inflado"])
        self.assertEqual(ev["descuento_real_pct"], 0)
        self.assertFalse(ev["publicable"])  # contra su historial no bajó nada: no se publica
        self.assertFalse(ev["super_deal"])

    def test_super_oferta_real(self):
        hist = serie(1000, 20) + [(AHORA - 60 * 60, 1000)]
        ev = reglas.evaluar(800, 1200, hist, AHORA, R)
        self.assertEqual(ev["caida_1h_pct"], 20)
        self.assertEqual(ev["descuento_real_pct"], 20)
        self.assertTrue(ev["es_minimo_30d"])
        self.assertTrue(ev["super_deal"], ev)
        self.assertTrue(ev["publicable"])

    def test_sin_lectura_de_hace_una_hora_no_hay_super(self):
        hist = serie(1000, 20, hasta=AHORA - 3 * H)  # la última lectura es de hace 3 h
        self.assertIsNone(reglas.precio_hace_1h(hist, AHORA, R))
        self.assertFalse(reglas.evaluar(800, None, hist, AHORA, R)["super_deal"])

    def test_caida_pequena_no_es_super(self):
        hist = serie(1000, 20) + [(AHORA - 55 * 60, 1000)]
        self.assertFalse(reglas.evaluar(950, None, hist, AHORA, R)["super_deal"])

    def test_lectura_sospechosa(self):
        self.assertTrue(reglas.es_sospechosa(99, [1000, 1010, 990, 1000], R))
        self.assertFalse(reglas.es_sospechosa(900, [1000, 1010, 990, 1000], R))
        self.assertFalse(reglas.es_sospechosa(99, [1000], R))  # con pocas lecturas no se juzga

    def test_ajustes_desde_config(self):
        r = reglas.con_ajustes({"min_caida_1h": 25, "inventada": 1})
        self.assertEqual(r["min_caida_1h"], 25)
        self.assertNotIn("inventada", r)


class Respaldo(unittest.TestCase):
    def test_nombre_categoria_specs(self):
        d = ia.respaldo("Teclado Inalámbrico Mecánico Attack Shark X85 Pro 82 Teclas Teclado RGB 4000mAh")
        self.assertEqual(d["nombre"], "Teclado Inalámbrico Mecánico Attack Shark X85")
        self.assertEqual(d["categoria"], "Teclados")
        self.assertEqual([s["texto"] for s in d["specs"]], ["Inalámbrico", "Mecánico", "4000 mAh"])
        self.assertEqual(d["specs"][0]["icono"], "wifi")

    def test_categorias_con_palabras_compartidas(self):
        self.assertEqual(ia.categoria_respaldo("Lámpara De Escritorio Giratoria"), "Iluminación")
        self.assertEqual(ia.categoria_respaldo("Silla De Escritorio Oficina Ergonomica"), "Sillas")
        self.assertEqual(ia.categoria_respaldo("Escritorio Gamer en L con Luces LED RGB"), "Escritorios")
        self.assertEqual(ia.categoria_respaldo("Soporte Tablet Base Giratoria"), "Accesorios")

    def test_validar_rechaza_formato_malo(self):
        with self.assertRaises(ValueError):
            ia.validar({"nombre": "X", "categoria": "Teclados", "specs": []})
        with self.assertRaises(ValueError):
            ia.validar({"nombre": "Teclado Aula", "categoria": "Cocina", "specs": [{"emoji": "a", "texto": "b"}] * 3})


class ClienteFalso:
    """Simula Gemini: falla con saturación `fallas` veces y luego responde."""
    modelo = "falso"

    def __init__(self, fallas, error=None):
        self.fallas, self.error, self.llamadas = fallas, error, 0

    def enriquecer(self, titulo):
        self.llamadas += 1
        if self.error:
            raise self.error
        if self.llamadas <= self.fallas:
            raise ia.Saturada("HTTP 429 RESOURCE_EXHAUSTED", 7)
        return ia.validar({"nombre": "Teclado Attack Shark X85", "categoria": "Teclados",
                           "specs": [{"emoji": "📶", "texto": "Inalámbrico"}, {"emoji": "⌨️", "texto": "Mecánico"},
                                     {"emoji": "🔋", "texto": "4000 mAh"}]})


class Reloj:
    def __init__(self):
        self.t = AHORA

    def __call__(self):
        return self.t

    def dormir(self, s):
        self.t += s


class ColaIA(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.db = DB(os.path.join(self.dir.name, "p.db"))
        lec = {"link": "https://meli.la/x", "ml_id": "MLM1", "url_final": "u", "imagen": "i",
               "titulo": "Teclado Inalámbrico Mecánico Attack Shark X85 Pro", "precio": 998, "tachado": 1968, "fuente": "t"}
        self.pid = self.db.guardar_producto(lec, AHORA)
        self.db.encolar_ia(self.pid, "h1")

    def tearDown(self):
        self.db.cerrar()
        self.dir.cleanup()

    def test_reintenta_hasta_lograrlo(self):
        reloj, cli = Reloj(), ClienteFalso(fallas=3)
        listos = ia.procesar_cola(self.db, cli, 5, 600, log, reloj=reloj, dormir=reloj.dormir)
        self.assertEqual(listos, 1)
        self.assertEqual(cli.llamadas, 4)
        fila = self.db.ia(self.pid)
        self.assertEqual(fila["estado"], "ok")
        self.assertEqual(fila["nombre"], "Teclado Attack Shark X85")

    def test_sin_tiempo_reprograma_sin_perder_el_producto(self):
        reloj, cli = Reloj(), ClienteFalso(fallas=99)
        listos = ia.procesar_cola(self.db, cli, 5, 60, log, reloj=reloj, dormir=reloj.dormir)
        self.assertEqual(listos, 0)
        fila = self.db.ia(self.pid)
        self.assertEqual(fila["estado"], "reintentando")
        self.assertGreater(fila["proximo_intento"], reloj.t)

    def test_cuota_diaria_pausa_hasta_manana(self):
        reloj = Reloj()
        ia.procesar_cola(self.db, ClienteFalso(0, ia.CuotaDiaria("PerDay")), 5, 600, log, reloj=reloj, dormir=reloj.dormir)
        self.assertGreaterEqual(self.db.ia(self.pid)["proximo_intento"], ia.manana(AHORA))

    def test_no_reencola_si_el_titulo_no_cambia(self):
        self.assertFalse(self.db.encolar_ia(self.pid, "h1"))
        self.assertTrue(self.db.encolar_ia(self.pid, "h2"))


class Exportar(unittest.TestCase):
    def test_datos_json_con_respaldo_y_super(self):
        with tempfile.TemporaryDirectory() as d:
            db = DB(os.path.join(d, "p.db"))
            lec = {"link": "https://meli.la/x", "ml_id": "MLM1", "url_final": "u", "imagen": "i",
                   "titulo": "Monitor Gamer 24 Pulgadas LG Ultragear 144 Hz", "precio": 1000, "tachado": None, "fuente": "t"}
            pid = db.guardar_producto(lec, AHORA)
            for ts, p in serie(1000, 20) + [(AHORA - 3600, 1000)]:
                db.guardar_observacion(pid, dict(lec, precio=p), ts=ts)
            db.guardar_observacion(pid, dict(lec, precio=800, tachado=1300), ts=AHORA)
            db.guardar_alerta(pid, "super", 1000, 800, 1000, 20, 20, "prueba", ts=AHORA)
            datos, alertas = exportar.construir(db, R, AHORA + 60)
            db.cerrar()
        p = datos["productos"][0]
        self.assertEqual(datos["version"], 2)
        self.assertEqual(p["precio"]["actual"], 800)
        self.assertEqual(p["precio"]["antes"], 1000)        # referencia de 30 días, no el tachado
        self.assertEqual(p["descuento"]["pct"], 20)
        self.assertTrue(p["super_deal"])
        self.assertEqual(p["categoria"], "monitores")
        self.assertEqual(p["nombre"], "Monitor Gamer 24 Pulgadas LG Ultragear")  # respaldo hasta que la IA lo procese
        self.assertFalse(p["senales"]["nombre_ia"])
        self.assertEqual(alertas["alertas"][0]["precio_ahora"], 800)
        json.dumps(datos, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()


class GeminiHTTP(unittest.TestCase):
    """Capa HTTP de Gemini contra un servidor local que imita sus respuestas (sin clave real)."""

    def servidor(self, respuestas):
        import http.server
        import threading
        cola = list(respuestas)
        recibidos = []

        class Manejador(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                recibidos.append(json.loads(self.rfile.read(int(self.headers["Content-Length"]))))
                codigo, cuerpo = cola.pop(0)
                datos = json.dumps(cuerpo).encode()
                self.send_response(codigo)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(datos)))
                self.end_headers()
                self.wfile.write(datos)

            def log_message(self, *a):
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), Manejador)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.shutdown)
        return f"http://127.0.0.1:{srv.server_port}/{{modelo}}", recibidos

    def error(self, codigo, status, detalles):
        return codigo, {"error": {"code": codigo, "status": status, "message": "x", "details": detalles}}

    def test_respuestas(self):
        ok = {"candidates": [{"content": {"parts": [{"text": json.dumps({
            "nombre": "Teclado Attack Shark X85", "categoria": "Teclados",
            "specs": [{"emoji": "📶", "texto": "Inalámbrico"}, {"emoji": "⌨️", "texto": "Mecánico"},
                      {"emoji": "🔋", "texto": "4000 mAh"}]})}]}}]}
        url, recibidos = self.servidor([
            self.error(429, "RESOURCE_EXHAUSTED", [{"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "37s"}]),
            self.error(429, "RESOURCE_EXHAUSTED", [{"@type": "type.googleapis.com/google.rpc.QuotaFailure",
                                                    "violations": [{"quotaId": "GenerateRequestsPerDayPerProjectPerModel-FreeTier"}]}]),
            self.error(503, "UNAVAILABLE", []),
            self.error(400, "INVALID_ARGUMENT", []),
            (200, ok),
        ])
        g = ia.Gemini("clave", "modelo-x", url=url)
        with self.assertRaises(ia.Saturada) as e:
            g.enriquecer("t")
        self.assertEqual(e.exception.espera, 37)
        with self.assertRaises(ia.CuotaDiaria):
            g.enriquecer("t")
        with self.assertRaises(ia.Saturada):
            g.enriquecer("t")
        with self.assertRaises(ia.ClaveInvalida):
            g.enriquecer("t")
        d = g.enriquecer("t")
        self.assertEqual(d["specs"][2]["icono"], "bateria")
        gen = recibidos[0]["generationConfig"]
        self.assertEqual(gen["responseMimeType"], "application/json")
        self.assertIn("responseJsonSchema", gen)
