import json, re
from shapely.geometry import shape, mapping
from shapely.ops import unary_union, transform
from pyproj import Transformer
S=r"C:\Users\endrio\AppData\Local\Temp\claude\db1dbea7476bf8ec\8cd27e34-02fd-4579-b0ae-9b111d428750\scratchpad"
to=Transformer.from_crs(4674,5880,always_xy=True).transform
d=json.load(open(S+r"\dados.json",encoding="utf-8"))
for k in ('rotas','crdu','upf','sede'): d.pop(k,None)
fix=lambda s: s.encode('cp1252').decode('utf-8') if 'Ã' in s else s
for z in d['zoneamento']: z['zona']=fix(z['zona'])
for l in d['lotes']:
    l['zonas']={fix(k):v for k,v in l['zonas'].items()}
    for k in ('area_plana_ha','perim_elip_m','valido'): l.pop(k,None)
b=open(S+r"\ref\big.js",encoding="utf-8").read()
i=b.index('const PFI_GEO=')+len('const PFI_GEO='); dep=0
for j in range(i,len(b)):
    c=b[j]
    if c=='{': dep+=1
    elif c=='}':
        dep-=1
        if dep==0: break
pg=json.loads(b[i:j+1])
ifl=shape(pg['ifl']).buffer(0)
cls={k:shape(v).buffer(0) for k,v in pg['classes'].items()}
src=json.load(open(r"C:\Users\endrio\OneDrive\Documentos\1 Brandão Engenharia e Projetos\ASPAFEMP\SHAPES\AREA_CONTORNO_LOTES.shp.geojson",encoding="utf-8"))
lots={f['properties']['lotes']:shape(f['geometry']) for f in src['features']}
for l in d['lotes']:
    g=lots[l['lote']]; a=transform(to,g).area
    x=g.intersection(ifl); r=(transform(to,x).area/a) if not x.is_empty else 0
    l['pfi_ha']=round(r*l['area_ha'],1)
    l['classe']=[c for c in ('1','3','2') if g.intersection(cls[c]).area/g.area>0.5][0]
    print(l['lote'],l['pfi_ha'],l['classe'])
allg=unary_union(list(lots.values())); win=allg.buffer(0.15)
p=ifl.intersection(win).simplify(0.0004)
d['pfi']=mapping(p)
tot=sum(l['pfi_ha'] for l in d['lotes']); print('PFI total',tot, tot/sum(l['area_ha'] for l in d['lotes']))
json.dump(d,open(S+r"\dados2.json","w",encoding="utf-8"),ensure_ascii=False,separators=(',',':'))
import os; print(os.path.getsize(S+r"\dados2.json"))
