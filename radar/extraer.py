"""Extracción con requests + BeautifulSoup: precio actual, tachado, cupón, disponibilidad e ID de Mercado Libre.

Sin navegador headless (regla de hardware: la laptop del radar tiene 4 GB).
"""
import hashlib
import json
import re

import requests
from bs4 import BeautifulSoup

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
     "Accept-Language": "es-MX,es;q=0.9"}
ID_RE = re.compile(r"\b(MLM)-?(\d{6,})", re.I)
CUPONES = [
    (re.compile(r"(\d{1,2})\s*%\s*OFF\s+(?:con|usando|aplicando)\s+cup[oó]n", re.I), "pct"),
    (re.compile(r"cup[oó]n\s+(?:de\s+)?(\d{1,2})\s*%", re.I), "pct"),
    (re.compile(r"cup[oó]n\s+(?:de\s+)?\$\s*([\d.,]+)", re.I), "monto"),
    (re.compile(r"\$\s*([\d.,]+)\s+(?:OFF\s+)?con\s+cup[oó]n", re.I), "monto"),
]


def nueva_sesion():
    s = requests.Session()
    s.headers.update(H)
    return s


def digitos(txt):
    d = re.sub(r"\D", "", str(txt or ""))
    return float(d) if d else 0.0


def flt(x):
    try:
        return float(str(x).replace(",", "").strip())
    except Exception:
        return 0.0


def producto_jsonld(sopa):
    for s in sopa.find_all("script", type="application/ld+json"):
        try:
            d = json.loads(s.string or "")
        except Exception:
            continue
        cola = d if isinstance(d, list) else [d]
        for o in cola:
            if isinstance(o, dict) and "@graph" in o:
                cola += o["@graph"]
            if isinstance(o, dict) and o.get("@type") == "Product":
                return o
    return None


def oferta_ld(ld):
    of = (ld or {}).get("offers")
    of = of[0] if isinstance(of, list) and of else of
    return of if isinstance(of, dict) else {}


def precio_dom(sopa):
    """Precio grande visible en pantalla (no el tachado ni las mensualidades)."""
    cand = sopa.select(".ui-pdp-price__second-line .andes-money-amount") or sopa.select(".andes-money-amount")
    for el in cand:
        if el.name == "s" or el.find_parent("s") or "andes-money-amount--previous" in (el.get("class") or []):
            continue
        fr = el.select_one(".andes-money-amount__fraction")
        if not fr:
            continue
        v = digitos(fr.get_text())
        c = el.select_one(".andes-money-amount__cents")
        if c:
            v += digitos(c.get_text()) / 100
        if v > 0:
            return v
    return 0.0


def precio_actual(sopa, html, ld):
    """Devuelve (precio, fuente). Nunca se calcula con porcentajes."""
    v = flt(oferta_ld(ld).get("price") or oferta_ld(ld).get("lowPrice"))
    if v > 0:
        return v, "json-ld"
    for attrs in ({"itemprop": "price"}, {"property": "product:price:amount"}, {"property": "og:price:amount"}):
        m = sopa.find("meta", attrs=attrs)
        if m and flt(m.get("content")) > 0:
            return flt(m["content"]), "meta"
    v = precio_dom(sopa)
    if v > 0:
        return v, "pantalla"
    m = re.search(r'"price"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)', html)
    if m and flt(m.group(1)) > 0:
        return flt(m.group(1)), "texto-json"
    return 0.0, "ninguna"


def precio_tachado(sopa):
    previo = sopa.select_one("s.andes-money-amount--previous .andes-money-amount__fraction") \
        or sopa.select_one("s .andes-money-amount__fraction")
    return digitos(previo.get_text()) if previo else 0.0


def ml_id(url_final, ld, html):
    for fuente in (url_final, str((ld or {}).get("productID") or ""), str((ld or {}).get("sku") or "")):
        m = ID_RE.search(fuente)
        if m:
            return (m.group(1) + m.group(2)).upper()
    m = re.search(r'"(?:item_id|itemId|product_id)"\s*:\s*"(MLM-?\d{6,})"', html)
    return m.group(1).replace("-", "").upper() if m else None


AJENOS = ("poly-card", "recommendations", "carousel", "nav-")  # tarjetas de otros productos y el menú


def ajeno(nodo):
    for p in nodo.parents:
        if p.name in ("script", "style", "noscript"):
            return True
        if any(a in c for c in (p.get("class") or []) for a in AJENOS):
            return True
    return False


def cupon(sopa, precio):
    """Cupón del producto principal, si viene en el HTML (sin sesión no siempre aparece).

    Se ignoran los cupones de las tarjetas de productos recomendados que Mercado Libre pone en la misma página.
    """
    for nodo in sopa.find_all(string=re.compile(r"cup[oó]n", re.I)):
        if ajeno(nodo):
            continue
        texto = " ".join(nodo.parent.parent.stripped_strings) if nodo.parent.parent else str(nodo)
        for regex, tipo in CUPONES:
            m = regex.search(texto)
            if not m:
                continue
            valor = flt(m.group(1)) if tipo == "pct" else digitos(m.group(1))
            if tipo == "pct" and 0 < valor < 90:
                return {"texto": f"{valor:g}% OFF con cupón", "pct": valor, "monto": None}
            if tipo == "monto" and 0 < valor < precio:
                # "$3,819 con cupón" es el precio final con cupón: el ahorro es la diferencia
                ahorro = round(precio - valor, 2) if valor > precio * 0.5 else valor
                return {"texto": f"${ahorro:,.0f} menos con cupón", "pct": None, "monto": ahorro}
    return None


def extraer(sesion, link):
    r = sesion.get(link, timeout=25)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    sopa = BeautifulSoup(r.text, "html.parser")
    t = sopa.find("meta", property="og:title")
    i = sopa.find("meta", property="og:image")
    if not t or not i:
        raise RuntimeError(f"sin título/imagen (página: {r.url[:70]})")
    ld = producto_jsonld(sopa)
    precio, fuente = precio_actual(sopa, r.text, ld)
    if precio <= 0:
        raise RuntimeError(f"no se encontró el precio actual (página: {r.url[:70]}). Corre con --debug")
    tachado = precio_tachado(sopa)
    disp = str(oferta_ld(ld).get("availability") or "")
    lectura = {
        "link": link,
        "url_final": r.url,
        "ml_id": ml_id(r.url, ld, r.text) or "X" + hashlib.md5(link.encode()).hexdigest()[:10],
        "titulo": re.sub(r"\s*[|\-–]\s*Mercado Libre.*$", "", t["content"]).strip(),
        "imagen": i["content"],
        "precio": precio,
        "tachado": tachado if tachado > precio else None,
        "cupon": cupon(sopa, precio),
        "disponible": "OutOfStock" not in disp and "SoldOut" not in disp,
        "fuente": fuente,
    }
    sopa.decompose()  # libera memoria del árbol HTML de inmediato
    return lectura


def diagnostico(sesion, url):
    r = sesion.get(url, timeout=25)
    sopa = BeautifulSoup(r.text, "html.parser")
    print("URL final:", r.url, "| HTTP", r.status_code, "| bytes", len(r.text))
    print("title:", sopa.title.get_text(strip=True)[:90] if sopa.title else None)
    ld = producto_jsonld(sopa)
    print("JSON-LD Product:", bool(ld), "| ID:", ml_id(r.url, ld, r.text), "| cupón:", cupon(sopa, precio_actual(sopa, r.text, ld)[0]))
    for m in sopa.find_all("meta"):
        if "price" in str(m.attrs).lower():
            print("meta:", dict(m.attrs))
    for el in sopa.select(".andes-money-amount")[:8]:
        print("monto:", el.name, el.get("class"), "|", el.get_text(" ", strip=True)[:40])
    print("OFF:", re.findall(r".{0,25}\d+%\s*OFF", r.text)[:3])
