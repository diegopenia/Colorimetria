"""Reanálisis colorimétrico de los Lienzos A y B (artículo para Eureka).

Uso: python reanalisis.py <carpeta_con_A.jpg_y_B.jpg> <carpeta_salida>

Diferencias frente al cuaderno original:
  - parte de las fotografías originales (JPG de 13 Mpx) reducidas a 1/4;
  - corrige la dominante de color de la foto con el propio papel (balance de blancos);
  - trabaja en CIELAB (D65) y no en RGB;
  - no usa un filtro de fondo fijo: separa zonas con una máscara dibujada a mano
    (figura, elementos asociados, texto, resto del lienzo) y clasifica como
    «sin color» los píxeles con croma C*ab menor que un umbral;
  - informa croma media, proporción sin color, familias de tono, paleta K-means
    en CIELAB y diferencias de color ΔE2000 entre tonos de la paleta;
  - repite todo con varias semillas, valores de K y umbrales de croma.
"""
import sys, os, json, itertools
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from skimage import color
from sklearn.cluster import KMeans

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
ESC = 4  # factor de reducción

# ---------------- máscaras (coordenadas en la imagen reducida a 1/4) ----------------
MASK = {
 "A": {
  "figura": {"poly": [[(360,390),(345,400),(300,450),(255,520),(210,600),(235,625),(290,545),(320,500),(300,650),(270,760),(240,850),(290,870),(330,860),(345,920),(330,1000),(390,990),(395,900),(410,860),(425,880),(450,990),(510,990),(470,890),(480,870),(545,870),(530,760),(510,640),(560,580),(590,640),(610,630),(570,540),(530,450),(515,400),(490,385)]],
             "ellipse": [(365,212,507,396)]},
  "elementos": {"poly": [[(335,0),(580,0),(560,80),(480,232),(400,232),(340,90)]],
                "rect": [(110,540,285,670),(535,595,680,712),(180,930,600,1054)]},
  "texto": {},
  "excluir": {},
 },
 "B": {
  "figura": {"poly": [[(300,188),(250,220),(225,290),(212,380),(225,440),(250,450),(215,520),(62,685),(240,720),(230,748),(270,752),(265,880),(230,915),(238,945),(332,945),(332,880),(355,880),(358,948),(452,958),(442,900),(405,880),(410,754),(477,752),(445,612),(502,562),(497,510),(470,450),(472,330),(452,230),(402,192)]]},
  "elementos": {"rect": [(470,18,612,162),(12,182,152,328),(552,322,718,512)]},
  "texto": {"rect": [(28,2,432,108),(492,532,774,952)]},
  "excluir": {"poly": [[(0,885),(95,885),(95,945),(0,945)]]},
 },
}
ORDEN = ["excluir", "texto", "elementos", "figura"]  # la última capa gana
ZONAS = ["figura", "elementos", "texto", "resto"]
NOMBRES = {"figura": "Figura", "elementos": "Elementos asociados", "texto": "Texto", "resto": "Resto del lienzo", "total": "Lienzo completo"}


def mascara(k, size):
    lab = Image.new("L", size, 0)  # 0 = resto
    code = {"excluir": 9, "texto": 3, "elementos": 2, "figura": 1}
    d = ImageDraw.Draw(lab)
    for z in ORDEN:
        spec = MASK[k].get(z, {})
        for p in spec.get("poly", []):
            d.polygon(p, fill=code[z])
        for e in spec.get("ellipse", []):
            d.ellipse(e, fill=code[z])
        for r in spec.get("rect", []):
            d.rectangle(r, fill=code[z])
    return np.array(lab)


def carga(k):
    im = ImageOps.exif_transpose(Image.open(os.path.join(SRC, f"{k}.jpg"))).convert("RGB")
    im = im.resize((im.width // ESC, im.height // ESC), Image.LANCZOS)
    return np.asarray(im).astype(float) / 255.0


def balance(rgb, zmap):
    """balance de blancos von Kries con el papel: píxeles claros y poco saturados fuera de figura y elementos"""
    lab = color.rgb2lab(rgb)
    C = np.hypot(lab[..., 1], lab[..., 2])
    papel = (zmap == 0) & (lab[..., 0] > np.percentile(lab[..., 0][zmap == 0], 60)) & (C < np.percentile(C[zmap == 0], 50))
    ref = np.median(rgb[papel], axis=0)
    out = np.clip(rgb * (ref.mean() / ref), 0, 1)
    return out, ref, int(papel.sum())


FAMILIAS = ["rojo", "naranja", "amarillo", "verde", "azul", "violeta", "rosa/magenta", "marrón"]


def familia(L, a, b):
    h = (np.degrees(np.arctan2(b, a)) + 360) % 360
    C = np.hypot(a, b)
    f = np.full(L.shape, "", dtype=object)
    f[(h >= 345) | (h < 15)] = "rosa/magenta"
    f[(h >= 15) & (h < 50)] = "rojo"
    f[(h >= 50) & (h < 75)] = "naranja"
    f[(h >= 75) & (h < 110)] = "amarillo"
    f[(h >= 110) & (h < 200)] = "verde"
    f[(h >= 200) & (h < 310)] = "azul"
    f[(h >= 310) & (h < 345)] = "violeta"
    cafe = (h >= 20) & (h < 95) & (L < 70) & (C < 35)
    f[cafe] = "marrón"
    return f


def hexlab(c):
    rgb = np.clip(color.lab2rgb(np.array(c, dtype=float).reshape(1, 1, 3)).reshape(3), 0, 1)
    return "#%02X%02X%02X" % tuple(int(round(v * 255)) for v in rgb)


def paleta(labpx, K, seed, n=40000):
    rng = np.random.default_rng(seed)
    x = labpx if len(labpx) <= n else labpx[rng.choice(len(labpx), n, replace=False)]
    km = KMeans(n_clusters=K, n_init=4, random_state=seed).fit(x)
    lab_c = km.cluster_centers_
    w = np.bincount(km.labels_, minlength=K) / len(x)
    o = np.argsort(-w)
    lab_c, w = lab_c[o], w[o]
    de = [color.deltaE_ciede2000(lab_c[i][None], lab_c[j][None])[0] for i, j in itertools.combinations(range(K), 2)]
    return lab_c, w, float(np.mean(de)), float(np.min(de))


res, filas_rob, paletas_ref = {}, [], {}
for k in "AB":
    rgb0 = carga(k)
    zmap = mascara(k, (rgb0.shape[1], rgb0.shape[0]))
    rgb, ref, npap = balance(rgb0, zmap)
    lab = color.rgb2lab(rgb)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, b)
    fam = familia(L, a, b)
    np.save(os.path.join(OUT, f"zonas_{k}.npy"), zmap)
    Image.fromarray((rgb * 255).astype(np.uint8)).save(os.path.join(OUT, f"lienzo_{k}_balanceado.png"))
    zsel = {"figura": zmap == 1, "elementos": zmap == 2, "texto": zmap == 3, "resto": zmap == 0, "total": zmap != 9}
    res[k] = {"papel_rgb_ref": [round(v, 3) for v in ref], "pix_papel_ref": npap, "zonas": {}}
    for z, m in zsel.items():
        if m.sum() == 0:
            continue
        entry = {"n_px": int(m.sum()), "por_umbral": {}}
        for T in (10, 15, 20):
            col = m & (C >= T)
            fams = {f: float(np.mean(fam[col] == f)) if col.sum() else 0 for f in FAMILIAS}
            entry["por_umbral"][T] = {
                "prop_sin_color": float(1 - col.sum() / m.sum()),
                "croma_media_total": float(C[m].mean()),
                "croma_media_coloreados": float(C[col].mean()) if col.sum() else None,
                "familias": fams,
            }
        res[k]["zonas"][z] = entry
        # robustez de la paleta
        if z in ("figura", "elementos", "total"):
            for T in (10, 15, 20):
                px = lab[m & (C >= T)]
                if len(px) < 500:
                    continue
                for K in (4, 6, 8):
                    for seed in range(10):
                        lab_c, w, de_m, de_min = paleta(px, K, seed)
                        filas_rob.append(dict(lienzo=k, zona=z, umbral=T, K=K, semilla=seed,
                                              color1=hexlab(lab_c[0]), pct1=round(100 * w[0], 2),
                                              C1=round(float(np.hypot(*lab_c[0][1:])), 1),
                                              dE_medio=round(de_m, 2), dE_min=round(de_min, 2)))
                        if T == 15 and K == 6 and seed == 0:
                            paletas_ref[f"{k}_{z}"] = [(hexlab(c), round(100 * float(ww), 1), round(float(np.hypot(*c[1:])), 1)) for c, ww in zip(lab_c, w)]

json.dump(res, open(os.path.join(OUT, "metricas_por_zona.json"), "w"), indent=1, ensure_ascii=False)
json.dump(paletas_ref, open(os.path.join(OUT, "paletas_K6_umbral15.json"), "w"), indent=1, ensure_ascii=False)
import csv
with open(os.path.join(OUT, "robustez_paletas.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(filas_rob[0].keys())); w.writeheader(); w.writerows(filas_rob)
print("listo")
