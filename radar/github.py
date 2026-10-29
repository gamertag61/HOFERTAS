"""Repositorio de GitHub como bus de datos: solo requests contra la API REST."""
import base64

import requests


class GitHub:
    def __init__(self, repo, token, rama="main"):
        self.repo, self.rama = repo, rama
        self.base = f"https://api.github.com/repos/{repo}"
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                               "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "radar-precios"})

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

    def publicar(self, archivos, mensaje, borrar=()):
        """Sube varios archivos (y borra otros) en un solo commit: un solo rebuild de Pages."""
        padre = self._r("GET", f"/git/ref/heads/{self.rama}")["object"]["sha"]
        arbol = self._r("GET", f"/git/commits/{padre}")["tree"]["sha"]
        existentes = {e["path"] for e in self._r("GET", f"/git/trees/{arbol}")["tree"]}
        entradas = [{"path": p, "mode": "100644", "type": "blob", "content": c} for p, c in archivos.items()]
        entradas += [{"path": p, "mode": "100644", "type": "blob", "sha": None} for p in borrar if p in existentes]
        nuevo = self._r("POST", "/git/trees", json={"base_tree": arbol, "tree": entradas})
        if nuevo["sha"] == arbol:
            return None
        c = self._r("POST", "/git/commits", json={"message": mensaje, "tree": nuevo["sha"], "parents": [padre]})
        self._r("PATCH", f"/git/refs/heads/{self.rama}", json={"sha": c["sha"]})
        return c["sha"]
