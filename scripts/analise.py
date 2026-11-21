import json, sys, math
src = sys.argv[1]
out = sys.argv[2]
d = json.load(open(src, encoding="utf-8"))
try:
    from pyproj import Geod, Transformer
    geod = Geod(ellps="GRS80")
    tr = Transformer.from_crs(4674, 5880, always_xy=True)  # SIRGAS2000 Brazil Polyconic
except Exception as e:
    print("pyproj missing", e); geod = None; tr = None
try:
    from shapely.geometry import shape
    from shapely.ops import unary_union
    from shapely import transform
except Exception as e:
    print("shapely missing", e); shape = None

res = []
geoms = []
for f in d["features"]:
    p = f["properties"]
    ring = f["geometry"]["coordinates"][0][0]
    lons = [c[0] for c in ring]; lats = [c[1] for c in ring]
    item = {"nome": p["nome"], "lote": p["lotes"], "area_ha": p["area_ha"], "perim_m": p["perim_m"],
            "ring": [[round(c[0], 5), round(c[1], 5)] for c in ring]}
    if geod:
        a, per = geod.polygon_area_perimeter(lons, lats)
        item["area_elip_ha"] = round(abs(a) / 1e4, 2)
        item["perim_elip_m"] = round(per, 1)
        xs, ys = tr.transform(lons, lats)
        s = 0
        for i in range(len(xs) - 1):
            s += xs[i] * ys[i + 1] - xs[i + 1] * ys[i]
        item["area_plana_ha"] = round(abs(s) / 2 / 1e4, 2)
    if shape:
        g = shape(f["geometry"])
        item["valido"] = g.is_valid
        c = g.centroid
        item["centroide"] = [round(c.x, 5), round(c.y, 5)]
        geoms.append(g)
    item["bbox"] = [min(lons), min(lats), max(lons), max(lats)]
    item["vertices"] = len(ring) - 1
    res.append(item)
    print(p["nome"], p["area_ha"], item.get("area_elip_ha"), item.get("area_plana_ha"), p["perim_m"], item.get("perim_elip_m"), item.get("valido"), item["vertices"])

tot = sum(r["area_ha"] for r in res)
print("TOTAL props", round(tot, 2), "elip", round(sum(r.get("area_elip_ha", 0) for r in res), 2))
if shape:
    u = unary_union(geoms)
    print("union type", u.geom_type, "n parts", len(u.geoms) if hasattr(u, "geoms") else 1)
    # overlaps
    for i in range(len(geoms)):
        for j in range(i + 1, len(geoms)):
            inter = geoms[i].intersection(geoms[j])
            if inter.area > 1e-9:
                print("OVERLAP", res[i]["nome"], res[j]["nome"], inter.area)
            elif geoms[i].distance(geoms[j]) < 1e-5:
                print("toca", res[i]["nome"], res[j]["nome"])
    b = u.bounds
    print("bbox total", b, "centroid", u.centroid)
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False)
