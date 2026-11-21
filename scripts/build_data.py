import json, os, shapefile
from shapely.geometry import shape, mapping, LineString, MultiLineString
from shapely.ops import unary_union, transform
from pyproj import Transformer

B = r"C:\Users\endrio\OneDrive\Documentos\1 Brandão Engenharia e Projetos\ASPAFEMP\SHAPES"
S = r"C:\Users\endrio\AppData\Local\Temp\claude\db1dbea7476bf8ec\8cd27e34-02fd-4579-b0ae-9b111d428750\scratchpad"
to_utm = Transformer.from_crs(4674, 31981, always_xy=True).transform
to_ll = Transformer.from_crs(31981, 4674, always_xy=True).transform

def read(name):
    r = shapefile.Reader(os.path.join(B, name), encoding="cp1252")
    fields = [f[0] for f in r.fields[1:]]
    out = []
    for sr in r.shapeRecords():
        out.append((dict(zip(fields, sr.record)), shape(sr.shape.__geo_interface__)))
    return out

lots = json.load(open(os.path.join(S, "lotes.json"), encoding="utf-8"))
lotgeo = shape({"type": "Polygon", "coordinates": []}) if False else None
from shapely.geometry import Polygon
lp = {l["lote"]: Polygon(l["ring"]) for l in lots}
# use full precision from source geojson
src = json.load(open(os.path.join(B, "AREA_CONTORNO_LOTES.shp.geojson"), encoding="utf-8"))
lp = {f["properties"]["lotes"]: shape(f["geometry"]) for f in src["features"]}
lp_utm = {k: transform(to_utm, g) for k, g in lp.items()}
allg = unary_union(list(lp.values()))
win = allg.buffer(0.15)

# zoning
zon = read("ZONEAMENTO_SEM_SOBREPOSICAO.shp")
zon_out = []
zon_share = {k: {} for k in lp}
for rec, g in zon:
    z = rec["Zona"]
    clip = g.intersection(win)
    if not clip.is_empty:
        zon_out.append({"zona": z, "geom": mapping(clip.simplify(0.0004))})
    for k, lg in lp_utm.items():
        gi = transform(to_utm, g.intersection(lp[k]))
        zon_share[k][z] = round(gi.area / 1e4, 2)

# hydro
hyd = read("HIDROGRAFIA_NOS_LOTES_V3.shp")
print("hydro types", set(r["HIDRO"] for r, _ in hyd))
# hydro prj is UTM 21S already?
hl = []
for rec, g in hyd:
    hl.append((rec["HIDRO"], g))
b0 = hl[0][1].bounds
print("hydro bounds", b0)
hydro_in_utm = b0[0] > 1000
hy_utm = [(t, g if hydro_in_utm else transform(to_utm, g)) for t, g in hl]
app_by_lot = {}
hyd_len = {}
for k, lg in lp_utm.items():
    segs = [g.intersection(lg) for t, g in hy_utm]
    segs = [s for s in segs if not s.is_empty]
    ln = sum(s.length for s in segs) / 1000
    buf = unary_union([s.buffer(30) for s in segs]) if segs else None
    app = buf.intersection(lg).area / 1e4 if buf is not None else 0
    app_by_lot[k] = round(app, 2); hyd_len[k] = round(ln, 2)
hyd_ll = []
for t, g in hy_utm:
    gl = transform(to_ll, g)
    gl = gl.intersection(win)
    if not gl.is_empty:
        hyd_ll.append({"tipo": t, "geom": mapping(gl.simplify(0.0002))})

# UPFs
upf = read("UPF_2000HA.shp")
upf_out = []
for rec, g in upf:
    upf_out.append({"nome": rec["nome"], "area_ha": rec["area_ha"], "centroide": [round(g.centroid.x, 5), round(g.centroid.y, 5)]})
    # best-match lot
    best = max(lp, key=lambda k: g.intersection(lp[k]).area)
    upf_out[-1]["lote_mais_sobreposto"] = best
    upf_out[-1]["sobreposicao_pct"] = round(g.intersection(lp[best]).area / g.area * 100, 1)

# access routes + sede
rotas = []
for n in ["ROTA_ACESSO.shp", "ROTA_ACESSO_2.shp"]:
    for rec, g in read(n):
        rotas.append({"trecho": rec["trecho"], "km": rec["km"], "geom": mapping(g.simplify(0.002))})
sede = [mapping(g) for _, g in read("SEDE_MAUES.shp")]
crdu = read("CRDU_POLIGONO.shp")[0]
crdu_g = crdu[1]
print("crdu contains lots?", crdu_g.contains(allg), "overlap pct", crdu_g.intersection(allg).area / allg.area)
apat = read("APAT_REDUZIDA_20000HA.shp")[0][1]
print("apat vs lots", apat.symmetric_difference(allg).area / allg.area)

res = {"lotes": [], "zoneamento": zon_out, "hidro": hyd_ll, "upf": upf_out, "rotas": rotas, "sede": sede,
       "crdu": {"doc": crdu[0]["documento"], "area_ha": round(crdu[0]["area_ha"], 1), "geom": mapping(crdu_g.simplify(0.003))},
       "bbox": list(allg.bounds)}
for l in lots:
    k = l["lote"]
    r = dict(l)
    r["app_ha"] = app_by_lot[k]; r["hidro_km"] = hyd_len[k]; r["zonas"] = zon_share[k]
    res["lotes"].append(r)
    print(k, "APP", r["app_ha"], "hidro_km", r["hidro_km"], {z: v for z, v in r["zonas"].items() if v > 0})
json.dump(res, open(os.path.join(S, "dados.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("size", os.path.getsize(os.path.join(S, "dados.json")))
print("UPF", upf_out)
