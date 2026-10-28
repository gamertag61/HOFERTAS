"""Heleos Radar: lee enlaces.txt, extrae precio actual y original, y escribe ofertas.json.
Requiere: pip install requests beautifulsoup4
Uso:       python heleos_radar.py            (una vuelta)
           python heleos_radar.py --loop     (24/7: una vuelta cada INTERVALO minutos)
Diagnóstico (muestra qué hay en la primera página): python heleos_radar.py --debug

Con heleos_config.json (repo + token de GitHub) el radar lee enlaces.txt del repositorio
y publica ofertas.json + historial.json ahí mismo en un solo commit; GitHub Pages sirve
el catálogo y el Cockpit sin que la laptop principal esté encendida.
Sin heleos_config.json trabaja con los archivos locales.
"""
import base64, json, os, re, sys, time, hashlib, datetime
import requests
from bs4 import BeautifulSoup

ENLACES, SALIDA, HIST, CONFIG = "enlaces.txt", "ofertas.json", "historial.json", "heleos_config.json"
MIN_DESC = 5          # % mínimo para considerarlo oferta
PAUSA = 3             # segundos entre páginas
MAX_ALERTAS = 30      # bajas de precio que se conservan para el Cockpit
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
     "Accept-Language": "es-MX,es;q=0.9"}


def leer(nombre, defecto):
    try:
        with open(nombre, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return defecto


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
    if ld:
        of = ld.get("offers")
        of = of[0] if isinstance(of, list) and of else of
        if isinstance(of, dict):
            v = flt(of.get("price") or of.get("lowPrice"))
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
        return flt(m.group(1)), "texto-json (revisar)"
    return 0.0, "ninguna"


def precio_original(sopa):
    previo = sopa.select_one("s.andes-money-amount--previous .andes-money-amount__fraction") \
        or sopa.select_one("s .andes-money-amount__fraction")
    return digitos(previo.get_text()) if previo else 0.0


def extraer(url):
    r = requests.get(url, headers=H, timeout=20)
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    sopa = BeautifulSoup(r.text, "html.parser")
    t = sopa.find("meta", property="og:title")
    i = sopa.find("meta", property="og:image")
    if not t or not i:
        raise RuntimeError(f"sin título/imagen (página: {r.url[:70]})")
    n, fuente = precio_actual(sopa, r.text, producto_jsonld(sopa))
    if n <= 0:
        raise RuntimeError(f"no se encontró el precio actual (página: {r.url[:70]}). Corre con --debug")
    o = precio_original(sopa)
    titulo = re.sub(r"\s*[|\-–]\s*Mercado Libre.*$", "", t["content"]).strip()
    return {"id": hashlib.md5(url.encode()).hexdigest()[:10], "t": titulo, "o": max(o, n), "n": n,
            "i": i["content"], "link": url, "_fuente": fuente}


def diagnostico(url):
    r = requests.get(url, headers=H, timeout=20)
    sopa = BeautifulSoup(r.text, "html.parser")
    print("URL final:", r.url, "| HTTP", r.status_code, "| bytes", len(r.text))
    print("title:", sopa.title.get_text(strip=True)[:90] if sopa.title else None)
    print("JSON-LD:", len(sopa.find_all("script", type="application/ld+json")))
    for m in sopa.find_all("meta"):
        if "price" in str(m.attrs).lower():
            print("meta:", dict(m.attrs))
    for el in sopa.select(".andes-money-amount")[:8]:
        print("monto:", el.name, el.get("class"), "| padre:", (el.parent.get("class") if el.parent else None),
              "|", el.get_text(" ", strip=True)[:40])
    for m in list(re.finditer(r'.{0,40}"price".{0,60}', r.text))[:5]:
        print("price-json:", m.group(0))
    print("OFF:", re.findall(r'.{0,25}\d+%\s*OFF', r.text)[:3])


class GitHub:
    """Repositorio como bus de datos: solo requests contra la API REST de GitHub."""

    def __init__(self, repo, token, rama="main"):
        self.base, self.rama = f"https://api.github.com/repos/{repo}", rama
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                               "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "heleos-radar"})

    def _r(self, metodo, ruta, **kw):
        r = self.s.request(metodo, self.base + ruta, timeout=30, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"GitHub {metodo} {ruta}: HTTP {r.status_code} {r.text[:120]}")
        return r.json() if r.text else {}

    def leer(self, ruta, defecto=None):
        try:
            d = self._r("GET", f"/contents/{ruta}", params={"ref": self.rama})
        except RuntimeError as e:
            if "HTTP 404" in str(e):
                return defecto
            raise
        return base64.b64decode(d["content"]).decode("utf-8")

    def publicar(self, archivos, mensaje):
        """Sube varios archivos en un solo commit (un solo rebuild de Pages)."""
        ref = self._r("GET", f"/git/ref/heads/{self.rama}")
        padre = ref["object"]["sha"]
        arbol = self._r("GET", f"/git/commits/{padre}")["tree"]["sha"]
        nuevo = self._r("POST", "/git/trees", json={"base_tree": arbol, "tree": [
            {"path": p, "mode": "100644", "type": "blob", "content": c} for p, c in archivos.items()]})
        if nuevo["sha"] == arbol:
            return None
        c = self._r("POST", "/git/commits", json={"message": mensaje, "tree": nuevo["sha"], "parents": [padre]})
        self._r("PATCH", f"/git/refs/heads/{self.rama}", json={"sha": c["sha"]})
        return c["sha"]


def conectar():
    cfg = leer(CONFIG, {})
    repo = os.environ.get("HELEOS_REPO") or cfg.get("repo")
    token = os.environ.get("HELEOS_TOKEN") or cfg.get("token")
    if repo and token:
        return GitHub(repo, token, cfg.get("rama", "main")), cfg
    return None, cfg


def vuelta(gh):
    if gh:
        txt = gh.leer(ENLACES, "")
        ant = json.loads(gh.leer(SALIDA, "{}") or "{}")
        hist = json.loads(gh.leer(HIST, "{}") or "{}")
    else:
        if not os.path.exists(ENLACES):
            return print(f"No existe {ENLACES}")
        txt = open(ENLACES, encoding="utf-8").read()
        ant, hist = leer(SALIDA, {}), leer(HIST, {})
    urls = list(dict.fromkeys(u.strip() for u in txt.splitlines() if u.strip().startswith("http")))
    if not urls:
        return print(f"{ENLACES} está vacío: nada que rastrear")
    previo = {p["link"]: p for p in ant.get("productos", [])} if isinstance(ant, dict) else {}
    alertas = ant.get("alertas", []) if isinstance(ant, dict) else []
    hoy, lista = datetime.date.today().isoformat(), []
    ahora = datetime.datetime.now().astimezone().isoformat(timespec="seconds")

    for u in urls:
        print("Rastreando:", u)
        try:
            p = extraer(u)
        except Exception as e:
            print("  ERROR:", e)
            if u in previo:
                lista.append(previo[u]); print("  (se conserva el dato anterior)")
            time.sleep(PAUSA); continue
        anterior = hist.get(u, [])[-1]["precio"] if hist.get(u) else None
        if anterior and p["n"] < anterior:
            alertas.insert(0, {"link": u, "t": p["t"], "i": p["i"], "antes": anterior, "ahora": p["n"],
                               "o": p["o"], "fecha": ahora})
            print(f"  ¡BAJA! ${anterior:.0f} -> ${p['n']:.0f}")
        h = [x for x in hist.get(u, []) if x["fecha"] != hoy] + [{"fecha": hoy, "precio": p["n"]}]
        hist[u] = h[-90:]
        desc = round(100 * (1 - p["n"] / p["o"])) if p["o"] > p["n"] else 0
        print(f"  ${p['n']:.2f} (antes ${p['o']:.0f}, -{desc}%) fuente: {p.pop('_fuente')} | {p['t'][:40]}")
        if desc >= MIN_DESC:
            lista.append(p)
        else:
            print("  sin descuento suficiente: no se publica")
        time.sleep(PAUSA)

    hist = {u: hist[u] for u in urls if u in hist}
    salida = json.dumps({"actualizado": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
                         "productos": lista, "alertas": alertas[:MAX_ALERTAS]}, ensure_ascii=False, indent=2)
    historial = json.dumps(hist, ensure_ascii=False, indent=1)
    # Copia local siempre (respaldo y modo sin GitHub).
    with open(HIST, "w", encoding="utf-8") as f:
        f.write(historial)
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(salida)
    if gh:
        sha = gh.publicar({SALIDA: salida + "\n", HIST: historial + "\n"}, f"Radar: {len(lista)} ofertas")
        print("  publicado en GitHub" + (f" ({sha[:7]})" if sha else " (sin cambios)"))
    print(f"\nListo: {len(lista)} ofertas en {SALIDA}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # consolas de Windows en cp1252
    gh, cfg = conectar()
    print("Modo:", "GitHub " + gh.base.split("/repos/")[1] if gh else "local")
    if "--debug" in sys.argv:
        txt = gh.leer(ENLACES, "") if gh else open(ENLACES, encoding="utf-8").read()
        return diagnostico(next(u.strip() for u in txt.splitlines() if u.strip().startswith("http")))
    if "--loop" not in sys.argv:
        return vuelta(gh)
    intervalo = max(15, int(cfg.get("intervalo_min", 180)))
    while True:
        print(f"\n=== Vuelta {datetime.datetime.now():%Y-%m-%d %H:%M} ===")
        try:
            vuelta(gh)
        except Exception as e:  # una caída de red no debe tumbar el radar 24/7
            print("  FALLÓ la vuelta:", e)
        print(f"Próxima vuelta en {intervalo} min")
        time.sleep(intervalo * 60)


if __name__ == "__main__":
    main()
