# -*- coding: utf-8 -*-
"""
Busca TODAS as inscricoes de um CNPJ (raiz) nos ZIPs de Dados Abertos PGFN.
Baixa o zip (se ainda nao em data/) e varre os CSVs streaming.
Uso: python buscar_cnpj.py <raiz_cnpj_8digitos> <zip_url> <apelido>
Gera data/achados_<apelido>.json
"""
import csv, sys, json, io, zipfile, os, urllib.request

RAIZ = sys.argv[1]                # ex 09599981
URL  = sys.argv[2]
APEL = sys.argv[3]
os.makedirs("data", exist_ok=True)
local = os.path.join("data", os.path.basename(URL))

if not os.path.exists(local) or os.path.getsize(local) < 1000:
    print(f"baixando {URL} ...", flush=True)
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=600) as r, open(local, "wb") as f:
        total = int(r.headers.get("Content-Length", 0)); got = 0; mark = 0
        while True:
            chunk = r.read(1 << 20)
            if not chunk:
                break
            f.write(chunk); got += len(chunk)
            if got - mark > 50 << 20:
                mark = got
                print(f"  {got/1e6:.0f}/{total/1e6:.0f} MB", flush=True)
    print("download ok", flush=True)

csv.field_size_limit(50_000_000)
achados = []
with zipfile.ZipFile(local) as z:
    for m in [x for x in z.namelist() if x.lower().endswith(".csv")]:
        with z.open(m) as raw:
            txt = io.TextIOWrapper(raw, encoding="latin-1", newline="")
            r = csv.DictReader(txt, delimiter=";")
            for row in r:
                doc = (row.get("CPF_CNPJ") or "")
                digits = "".join(c for c in doc if c.isdigit())
                if digits.startswith(RAIZ):
                    achados.append({k: (v or "").strip() for k, v in row.items()})
        print(f"  varrido {m} -> {len(achados)} inscricoes ate agora", flush=True)

json.dump(achados, open(f"data/achados_{APEL}.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
tot = sum(float((a.get("VALOR_CONSOLIDADO") or "0").replace(",", ".") or 0) for a in achados)
print(f"\n{APEL}: {len(achados)} inscricoes | total R$ {tot:,.2f}")
