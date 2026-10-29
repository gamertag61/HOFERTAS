"""Arma datos.json (catálogo) y alertas.json (súper ofertas) a partir de precios.db."""
import datetime
import json

from . import ia, reglas

DIA = 86400


def iso(ts):
    return datetime.datetime.fromtimestamp(ts).astimezone().isoformat(timespec="seconds")


def enriquecido(db, prod):
    fila = db.ia(prod["id"])
    if fila and fila["estado"] == "ok":
        return {"nombre": fila["nombre"], "categoria": fila["categoria"],
                "specs": json.loads(fila["specs_json"] or "[]"), "fuente": "ia"}
    return ia.respaldo(prod["titulo"] or "")


def slug(cat):
    return (cat.lower().replace("ó", "o").replace("í", "i").replace("á", "a").replace("é", "e").replace("ú", "u")
            .replace(" ", "-"))


def construir(db, R, ahora):
    productos, categorias = [], {}
    for prod in db.activos():
        hist = db.historial(prod["id"], ahora - (R["dias_referencia"] + 1) * DIA)
        if not hist:
            continue
        ult = hist[-1]
        ev = reglas.evaluar(ult["precio"], ult["precio_tachado"], [(o["ts"], o["precio"]) for o in hist[:-1]], ult["ts"], R)
        if not ev["publicable"] or not ult["disponible"]:
            continue
        e = enriquecido(db, prod)
        sup = db.ultima_super(prod["id"], ahora - DIA)
        es_super = bool(sup and ult["precio"] <= sup["precio_ahora"] * 1.01)
        cupon = None
        if ult["cupon_texto"]:
            cupon = {"texto": ult["cupon_texto"], "pct": ult["cupon_pct"], "monto": ult["cupon_monto"]}
        productos.append({
            "id": prod["ml_id"],
            "link": prod["link"],
            "nombre": e["nombre"],
            "titulo": prod["titulo"],
            "categoria": slug(e["categoria"]),
            "imagen": prod["imagen"],
            "precio": {"actual": ult["precio"], "antes": ev["antes"], "tachado": ult["precio_tachado"],
                       "referencia_30d": ev["referencia_30d"], "minimo_30d": ev["minimo_30d"]},
            "descuento": {"pct": ev["descuento_pct"], "real_pct": ev["descuento_real_pct"],
                          "tachado_pct": ev["tachado_pct"], "ahorro": round(ev["antes"] - ult["precio"], 2)},
            "cupon": cupon,
            "specs": e["specs"],
            "senales": {"tachado_inflado": ev["tachado_inflado"], "historial_dias": ev["historial_dias"],
                        "historial_suficiente": ev["suficiente"], "nombre_ia": e["fuente"] == "ia",
                        "verificado": iso(ult["ts"])},
            "super_deal": es_super,
            "historial": reglas.serie_diaria([(o["ts"], o["precio"]) for o in hist], R["dias_referencia"], ahora),
        })
        c = categorias.setdefault(slug(e["categoria"]), {"id": slug(e["categoria"]), "nombre": e["categoria"], "total": 0})
        c["total"] += 1
    productos.sort(key=lambda p: (not p["super_deal"], -p["descuento"]["pct"]))

    def alerta(a):
        e = enriquecido(db, {"id": a["producto_id"], "titulo": a["titulo"]})
        return {"id": a["ml_id"], "link": a["link"], "nombre": e["nombre"], "imagen": a["imagen"],
                "precio_antes": a["precio_antes"], "precio_ahora": a["precio_ahora"], "caida_pct": a["caida_pct"],
                "descuento_real_pct": a["descuento_real_pct"], "ts": iso(a["ts"]), "motivo": a["motivo"]}

    bajas = [alerta(a) for a in db.alertas("baja", ahora - 7 * DIA, 30)]
    supers = [alerta(a) for a in db.alertas("super", ahora - 7 * DIA, 30)]
    datos = {"version": 2, "actualizado": iso(ahora),
             "categorias": sorted(categorias.values(), key=lambda c: -c["total"]),
             "productos": productos, "bajas": bajas}
    return datos, {"version": 2, "actualizado": iso(ahora), "alertas": supers}


def a_texto(obj):
    return json.dumps(obj, ensure_ascii=False, indent=1) + "\n"
