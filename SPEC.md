# Painel FSC – ASPAFEMP

Painel de uma página (HTML único, abre com duplo clique, sem internet) que resume a área de 20.000 ha
destinada ao manejo florestal para triagem de certificação FSC.

## Entradas
- `SHAPES/AREA_CONTORNO_LOTES.shp.geojson` (10 lotes: 03–09, 12, 13, 15)
- `SHAPES/ZONEAMENTO_SEM_SOBREPOSICAO`, `HIDROGRAFIA_NOS_LOTES_V3`, `CRDU_POLIGONO`
- `DADOS FLORESTA MAUES/.../COMUNIDADES`, `UC_FEDERAL`

## Critério de pronto (conferido em 21/11/2026)
- Soma das áreas = 20.000,01 ha; área elipsoidal recalculada bate por lote.
- 10 lotes no mapa, 114 trechos de hidrografia, tabela ordenável, detalhe por lote.
- Simulador: área líquida = total − APP − infraestrutura − reserva; UPA = líquida / ciclo; volume = UPA × intensidade (conferido: 18.330 ha / 25 anos × 30 m³/ha = 21.996 m³/ano).
- 10 Princípios FSC com marcação salva no navegador (localStorage).
- Sem erro de console; sem rolagem horizontal.

## Limites assumidos
- APP = faixa de 30 m de cada lado dos cursos d'água de 0–10 m da hidrografia IBGE; sem nascentes.
- Faixas do simulador (ciclo 25–35 anos, até 30 m³/ha) vêm da IN MMA 5/2006; conferir norma vigente.
- Não é parecer de auditoria nem estimativa de volume de inventário.

## Versão 2 (21/11/2026): padrão do painel de referência
Visual e estrutura do painel https://navilus-endrio.github.io/painel-fsc-manejo/ (FSC-STD-BRA-02.1-2026):
cabeçalho com logos, hero com KPIs, seções com siglas, 10 Princípios, rodapé de fontes/direitos.
A v1 (padrão genérico FSC-STD-01-001) ficou em `PAINEL_FSC_ASPAFEMP_v1.html`.
Novo: camada PFI (IFL 2020) e área central mínima (Apta, 20% da PFI = 2.895 ha), tomadas do painel de referência.
Limitações: IFL 2020 em vez do mapa de 01/01/2017; aptidão vetorizada da figura (erro ~10 km); shapefile oficial não pedido ao FSC.
O arquivo contém a geometria dos lotes do cliente: não publicar sem aprovação.

## Regerar
`scripts/analise.py` → `scripts/build_data2.py` (gera `dados2.json`; precisa de `ref/big.js` do painel de referência para o PFI)
→ `scripts/build2.py` (injeta CSS `style_ref.css`, logos e dados em `template2.html`).
Os caminhos nos scripts apontam para a pasta SHAPES do cliente e para a pasta temporária de trabalho; ajuste antes de rodar.
