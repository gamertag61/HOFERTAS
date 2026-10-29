"""Reglas anti-fraude y de súper oferta. Funciones puras: reciben precios, devuelven decisiones.

La referencia de "precio normal" es NUESTRO historial (mediana de 30 días), nunca el tachado del vendedor:
un vendedor puede inflar el precio base unos días y luego "rebajarlo" al precio de siempre.

Todos los umbrales se pueden cambiar en heleos_config.json → "reglas": {"min_caida_1h": 10, ...}.
"""
import datetime
import statistics

DIA = 86400

REGLAS = {
    "min_descuento_publicar": 5,      # % mínimo para que un producto aparezca en el catálogo
    "dias_referencia": 30,            # memoria usada para el precio de referencia
    "excluir_ultimas_horas": 24,      # la referencia no cuenta las últimas 24 h (no se contamina con la baja)
    "min_dias_historial": 7,          # días con lecturas necesarios para confiar en la referencia
    "max_desvio_sospechoso": 70,      # % de distancia a la mediana para descartar una lectura como error
    "ventana_1h_min": [45, 90],       # minutos atrás donde se busca "el precio de hace 1 hora"
    "min_caida_1h": 8,                # % de caída contra hace 1 h para súper oferta
    "min_descuento_real_super": 15,   # % de descuento real (contra la referencia) para súper oferta
    "tolerancia_minimo": 1,           # % de tolerancia para considerar el precio como mínimo de 30 días
    "dias_subida_previa": 7,          # ventana para detectar una subida justo antes de la "rebaja"
    "min_subida_previa": 15,          # % sobre la referencia que cuenta como subida sospechosa
    "tachado_sobre_maximo": 10,       # % por encima del máximo visto para marcar el tachado como inflado
    "min_baja": 1,                    # % para registrar una baja normal (gráfico del sitio)
    "confirmacion_seg": 300,          # espera antes de confirmar una súper oferta con una segunda lectura
}


def con_ajustes(ajustes):
    r = dict(REGLAS)
    r.update({k: v for k, v in (ajustes or {}).items() if k in REGLAS})
    return r


def pct(antes, ahora):
    """% que bajó `ahora` respecto de `antes` (0 si no bajó)."""
    return round(100 * (1 - ahora / antes)) if antes and antes > ahora else 0


def mediana(xs):
    return statistics.median(xs) if xs else None


def es_sospechosa(precio, precios_previos, R):
    """Lectura que se aleja demasiado de lo habitual: casi siempre es un error de lectura de la página."""
    if len(precios_previos) < 3:
        return False
    med = mediana(precios_previos)
    return abs(precio - med) / med * 100 > R["max_desvio_sospechoso"]


def precio_hace_1h(historial, ahora, R):
    """Precio de la lectura válida más cercana a 60 min atrás, dentro de la ventana [45, 90] min."""
    ini, fin = R["ventana_1h_min"]
    cand = [(abs((ahora - ts) / 60 - 60), p) for ts, p in historial if ini * 60 <= ahora - ts <= fin * 60]
    return min(cand)[1] if cand else None


def dias_con_lecturas(historial, desde):
    return len({datetime.datetime.fromtimestamp(ts).date() for ts, _ in historial if ts >= desde})


def evaluar(precio, tachado, historial, ahora, R):
    """Decide qué mostrar y si hay súper oferta.

    historial: [(ts, precio)] de lecturas válidas ANTERIORES a la actual (sin la actual).
    """
    desde = ahora - R["dias_referencia"] * DIA
    h30 = [(ts, p) for ts, p in historial if ts >= desde]
    precios30 = [p for _, p in h30]
    ventana_ref = [p for ts, p in h30 if ts <= ahora - R["excluir_ultimas_horas"] * 3600]
    referencia = mediana(ventana_ref)
    dias = dias_con_lecturas(h30, desde)
    suficiente = bool(referencia) and dias >= R["min_dias_historial"]

    minimo_30d = min(precios30 + [precio])
    maximo_30d = max(precios30 + [precio])
    recientes = [p for ts, p in h30 if ts >= ahora - R["dias_subida_previa"] * DIA]
    subida_previa = suficiente and bool(recientes) and max(recientes) > referencia * (1 + R["min_subida_previa"] / 100)
    tachado_inflado = bool(suficiente and tachado and
                           (tachado > maximo_30d * (1 + R["tachado_sobre_maximo"] / 100) or subida_previa))

    descuento_real = pct(referencia, precio) if suficiente else 0
    tachado_pct = pct(tachado, precio)
    # Con memoria suficiente manda nuestro historial; sin ella (producto nuevo) se usa el tachado.
    if suficiente:
        antes = referencia if referencia > precio else None
    else:
        antes = tachado if tachado and tachado > precio else None
    descuento = pct(antes, precio)

    p1h = precio_hace_1h(h30, ahora, R)
    caida_1h = pct(p1h, precio)
    es_minimo = bool(precios30) and precio <= min(precios30) * (1 + R["tolerancia_minimo"] / 100)
    super_deal = bool(suficiente and p1h and caida_1h >= R["min_caida_1h"]
                      and descuento_real >= R["min_descuento_real_super"] and es_minimo)

    if super_deal:
        motivo = f"bajó {caida_1h}% en 1 h y es el mínimo de {R['dias_referencia']} días"
    elif not suficiente:
        motivo = "historial insuficiente"
    elif tachado_inflado:
        motivo = "tachado inflado: se muestra el descuento contra el historial"
    else:
        motivo = ""
    return {
        "referencia_30d": round(referencia, 2) if referencia else None,
        "minimo_30d": minimo_30d,
        "historial_dias": dias,
        "suficiente": suficiente,
        "antes": antes,
        "descuento_pct": descuento,
        "descuento_real_pct": descuento_real,
        "tachado_pct": tachado_pct,
        "tachado_inflado": tachado_inflado,
        "subida_previa": subida_previa,
        "precio_1h": p1h,
        "caida_1h_pct": caida_1h,
        "es_minimo_30d": es_minimo,
        "publicable": descuento >= R["min_descuento_publicar"],
        "super_deal": super_deal,
        "motivo": motivo,
    }


def es_baja(precio, ultimo_precio, R):
    return bool(ultimo_precio) and precio < ultimo_precio * (1 - R["min_baja"] / 100)


def serie_diaria(historial, dias=30, ahora=None):
    """Precio mínimo de cada día (para el gráfico del sitio): [["2026-10-28", 998.0], ...]."""
    ahora = ahora or datetime.datetime.now().timestamp()
    por_dia = {}
    for ts, p in historial:
        if ts >= ahora - dias * DIA:
            d = datetime.datetime.fromtimestamp(ts).date().isoformat()
            por_dia[d] = min(p, por_dia.get(d, p))
    return [[d, por_dia[d]] for d in sorted(por_dia)]
