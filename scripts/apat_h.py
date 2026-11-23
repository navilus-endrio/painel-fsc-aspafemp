import json,shapefile,pyproj
from shapely.geometry import shape
from shapely.ops import transform,unary_union
S=r"C:\Users\endrio\OneDrive\Documentos\1 Brandão Engenharia e Projetos\ASPAFEMP\SHAPES"
b=open("ref/big.js",encoding="utf-8").read()
i=b.index('const PFI_GEO=')+14;dep=0
for j in range(i,len(b)):
    c=b[j]
    if c=='{':dep+=1
    elif c=='}':
        dep-=1
        if dep==0:break
pg=json.loads(b[i:j+1]);print(pg.keys(),pg['classes'].keys())
ifl=shape(pg['ifl']).buffer(0);cls={k:shape(v).buffer(0) for k,v in pg['classes'].items()}
to=pyproj.Transformer.from_crs(4674,5880,always_xy=True).transform
a5=lambda g:transform(to,g).area/1e4
ell=pyproj.Geod(ellps='GRS80')
ha=lambda g:abs(ell.geometry_area_perimeter(g)[0])/1e4
utm=pyproj.Transformer.from_crs(4674,31981,always_xy=True).transform
for n in ['APAT_20000HA','APAT_REDUZIDA_20000HA','AREA_CONTORNO_LOTES']:
    r=shapefile.Reader(S+"\\"+n,encodingErrors='replace')
    g=unary_union([shape(s.__geo_interface__).buffer(0) for s in r.shapes()])
    A=a5(g);print('\n==',n,'area elip ha',round(ha(g),1))
    for k,c in cls.items():
        x=g.intersection(c);print(' classe',k,round(a5(x)/A*100,1),'%')
    x=g.intersection(ifl);pf=a5(x)/A;print(' PFI %',round(pf*100,1),'ha',round(pf*ha(g)))
    gu=transform(utm,g)
    for k,c in cls.items():
        print(' dist ao limite da classe',k,'km',round(gu.boundary.distance(transform(utm,c.boundary))/1000,1) if True else '')
    print(' dist a borda do IFL km',round(gu.distance(transform(utm,ifl.boundary))/1000,1))
