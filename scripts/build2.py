import json, os, re, shutil
D = os.path.dirname(os.path.abspath(__file__))
P = r"C:\Users\endrio\OneDrive\Documentos\1 Brandão Engenharia e Projetos\ASPAFEMP\PAINEL_FSC"
r = lambda f: open(os.path.join(D, f), encoding='utf-8').read()
d = json.load(open(os.path.join(D, 'dados2.json'), encoding='utf-8'))
L = d['lotes']
tot = sum(l['area_ha'] for l in L)
pfi = sum(l['pfi_ha'] for l in L)
app = sum(l['app_ha'] for l in L)
br = lambda x, n=0: f"{x:,.{n}f}".replace(",", "X").replace(".", ",").replace("X", ".")
l03 = [l for l in L if l['lote'] == '03'][0]
from shapely.geometry import Polygon
from shapely.ops import unary_union, transform
import pyproj
_u = unary_union([Polygon(l['ring']).buffer(2e-6) for l in L]).buffer(-2e-6)
_utm = pyproj.Transformer.from_crs(4674, 31981, always_xy=True).transform
_polys = [Polygon(pl.exterior) for pl in (list(_u.geoms) if _u.geom_type == 'MultiPolygon' else [_u])]
_u = unary_union(_polys)
d['uniao'] = {'polys': [[[ [round(x, 5), round(y, 5)] for x, y in [pl.exterior.coords][0] ]] + [[[round(x, 5), round(y, 5)] for x, y in h.coords] for h in pl.interiors] for pl in _polys],
              'perim_km': round(transform(_utm, _u).length / 1000, 1), 'partes': len(_polys),
              'furos': sum(len(pl.interiors) for pl in _polys), 'vertices': sum(len(pl.exterior.coords) - 1 for pl in _polys)}
print('uniao', d['uniao']['perim_km'], d['uniao']['partes'], d['uniao']['furos'], d['uniao']['vertices'])

import shapefile
from shapely.geometry import shape as _shape
_sf = shapefile.Reader(r"C:\Users\endrio\OneDrive\Documentos\1 Brandão Engenharia e Projetos\ASPAFEMP\SHAPES\HIDROGRAFIAS E APPS\APP'S_APAT_ASPAFEMP.shp")
_ap = unary_union([_shape(s.__geo_interface__) for s in _sf.shapes()]).buffer(0)
_to4674 = pyproj.Transformer.from_crs(31981, 4674, always_xy=True).transform
_app = transform(_to4674, _ap).intersection(_u)
_a5880 = pyproj.Transformer.from_crs(4674, 5880, always_xy=True).transform
for l in L:
    l['app_ha'] = round(transform(_a5880, _app.intersection(Polygon(l['ring']))).area / 1e4, 2)
app = sum(l['app_ha'] for l in L)
_app = _app.simplify(0.00001)
_pa = list(_app.geoms) if _app.geom_type == 'MultiPolygon' else [_app]
d['app'] = [[[[round(x, 5), round(y, 5)] for x, y in pl.exterior.coords]] + [[[round(x, 5), round(y, 5)] for x, y in h.coords] for h in pl.interiors] for pl in _pa if pl.geom_type == 'Polygon']
print('app ha (shape oficial, recortada)', round(app, 1), [l['app_ha'] for l in L])
_sm = shapefile.Reader(r"C:\Users\endrio\OneDrive\Documentos\1 Brandão Engenharia e Projetos\ASPAFEMP\SHAPES\HIDROGRAFIAS E APPS\MASSAS_D'AGUA_APAT_ASPAFEMP.shp")
_mas = transform(_to4674, unary_union([_shape(s.__geo_interface__) for s in _sm.shapes()]).buffer(0)).intersection(_u).simplify(0.00001)
d['massas'] = [[[[round(x, 5), round(y, 5)] for x, y in pl.exterior.coords]] + [[[round(x, 5), round(y, 5)] for x, y in h.coords] for h in pl.interiors] for pl in (list(_mas.geoms) if _mas.geom_type == 'MultiPolygon' else [_mas]) if pl.geom_type == 'Polygon']
d['massas_ha'] = round(transform(_a5880, _mas).area / 1e4, 1)
print('massas ha', d['massas_ha'], len(d['massas']))
t = r('template2.html')
t = t.replace('/*CSS*/', r('ref/style.css')).replace('/*LOGO1*/', r('logo1.txt').strip()).replace('/*LOGO2*/', r('logo2.txt').strip())
t = t.replace('/*DATA*/', json.dumps(d, ensure_ascii=False, separators=(',', ':')))
for k, v in {
    '__PFI_PCT__': br(pfi / tot * 100, 1), '__PFI_HA__': br(pfi), '__CORE_HA__': br(pfi * .2),
    '__CORE_PCT__': br(pfi * .2 / tot * 100, 1), '__APP_HA__': br(app), '__APP_PCT__': br(app / tot * 100, 1),
    '__PFI03__': str(round(l03['pfi_ha'] / l03['area_ha'] * 100)),
}.items():
    t = t.replace(k, v)
out = os.path.join(P, 'PAINEL_FSC_ASPAFEMP.html')
v1 = os.path.join(P, 'PAINEL_FSC_ASPAFEMP_v1.html')
if os.path.exists(out) and not os.path.exists(v1):
    shutil.copy2(out, v1)
open(out, 'w', encoding='utf-8').write(t)
print(len(t), re.findall(r'__[A-Z0-9_]+__', t))
