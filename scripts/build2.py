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
