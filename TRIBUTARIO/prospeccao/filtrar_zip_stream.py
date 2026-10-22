# -*- coding: utf-8 -*-
"""
Agregador streaming - le os CSVs DIRETO de dentro do .zip (sem extrair 8GB pro disco).
Filtra PJ (devedor Principal), agrega divida por CNPJ, exclui entes nao-prospect.
Uso: python filtrar_zip_stream.py <arquivo.zip> [valor_min] [valor_max] [UF]
"""
import csv, sys, json, io, zipfile

ZIP = sys.argv[1]
VMIN = float(sys.argv[2]) if len(sys.argv) > 2 else 100_000
VMAX = float(sys.argv[3]) if len(sys.argv) > 3 else float("inf")
UF = sys.argv[4].upper() if len(sys.argv) > 4 else None

EXCLUI = ("MUNICIPIO", "MASSA FALIDA", "FALIDA", "FALIDO", "ESPOLIO",
          "PREFEITURA", "ESTADO DE", "ESTADO DO", "UNIAO", "FAZENDA PUBLICA",
          "CAMARA MUNICIPAL", "FUNDACAO UNIVERSIDADE", "AUTARQUIA",
          "EM RECUPERACAO JUDIC", "EM LIQUIDACAO", "DEPARTAMENTO ESTADUAL",
          "SECRETARIA", "INSTITUTO NACIONAL", "CONSELHO REGIONAL")

def excluido(n):
    n = n.upper()
    return any(k in n for k in EXCLUI)

csv.field_size_limit(50_000_000)
agg = {}
linhas = 0

with zipfile.ZipFile(ZIP) as z:
    membros = [m for m in z.namelist() if m.lower().endswith(".csv")]
    for mi, m in enumerate(membros, 1):
        with z.open(m) as raw:
            txt = io.TextIOWrapper(raw, encoding="latin-1", newline="")
            r = csv.DictReader(txt, delimiter=";")
            for row in r:
                linhas += 1
                if row.get("TIPO_PESSOA", "").strip() != "Pessoa jur\xeddica":
                    continue
                if (row.get("TIPO_DEVEDOR") or "").strip().upper() != "PRINCIPAL":
                    continue
                uf = (row.get("UF_DEVEDOR") or "").strip()
                if UF and uf != UF:
                    continue
                cnpj = (row.get("CPF_CNPJ") or "").strip()
                if "/" not in cnpj:   # garante CNPJ (PJ), descarta mascarado
                    continue
                try:
                    v = float(row.get("VALOR_CONSOLIDADO") or 0)
                except ValueError:
                    v = 0.0
                d = agg.get(cnpj)
                if d is None:
                    d = agg[cnpj] = {"cnpj": cnpj, "nome": (row.get("NOME_DEVEDOR") or "").strip(),
                                     "uf": uf, "total": 0.0, "inscricoes": 0, "ajuizado": False}
                d["total"] += v
                d["inscricoes"] += 1
                if (row.get("INDICADOR_AJUIZADO") or "").strip().upper() == "SIM":
                    d["ajuizado"] = True
        print(f"  [{mi}/{len(membros)}] {m} ok - {len(agg):,} CNPJs ate agora", flush=True)

cands = [d for d in agg.values()
         if VMIN <= d["total"] <= VMAX and not excluido(d["nome"])]
cands.sort(key=lambda d: d["total"], reverse=True)
print(f"\nLinhas lidas: {linhas:,} | PJ unicas: {len(agg):,} | na faixa: {len(cands):,}")
json.dump(cands, open("candidatos.json", "w", encoding="utf-8"), ensure_ascii=False)
for i, d in enumerate(cands[:25], 1):
    aj = "AJUIZ" if d["ajuizado"] else "adm."
    print(f"{i:2d}. {d['nome'][:46]:46s} {d['cnpj']} {d['uf']} R$ {d['total']:>14,.2f} ({d['inscricoes']}x {aj})")
