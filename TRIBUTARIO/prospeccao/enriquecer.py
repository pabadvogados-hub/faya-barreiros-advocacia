# -*- coding: utf-8 -*-
"""
Enriquecimento cadastral dos candidatos PGFN via BrasilAPI (dados Receita Federal).
Retorna situacao cadastral, telefone, email, CNAE, endereco e socios.
Mantem as N primeiras empresas ATIVAS com telefone.
Uso: python enriquecer.py [N=10]
"""
import json, sys, time, urllib.request

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
cands = json.load(open("candidatos.json", encoding="utf-8"))

def consulta(cnpj_num):
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_num}"
    req = urllib.request.Request(url, headers={"User-Agent": "Faya-Barreiros-prospec/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

out, ativas = [], 0
for d in cands:
    if ativas >= N:
        break
    cnpj_num = "".join(ch for ch in d["cnpj"] if ch.isdigit())
    try:
        rf = consulta(cnpj_num)
    except Exception as e:
        print(f"  ! {d['cnpj']} falhou: {e}")
        time.sleep(1.0)
        continue
    sit = (rf.get("descricao_situacao_cadastral") or "").upper()
    ddd_tel = rf.get("ddd_telefone_1") or ""
    rec = {
        "cnpj": d["cnpj"],
        "nome": d["nome"],
        "uf": d["uf"],
        "divida_pgfn": round(d["total"], 2),
        "inscricoes": d["inscricoes"],
        "ajuizado": d["ajuizado"],
        "situacao_cadastral": rf.get("descricao_situacao_cadastral"),
        "data_situacao": rf.get("data_situacao_cadastral"),
        "porte": rf.get("porte"),
        "abertura": rf.get("data_inicio_atividade"),
        "cnae": rf.get("cnae_fiscal_descricao"),
        "telefone": ddd_tel,
        "email": rf.get("email"),
        "municipio": rf.get("municipio"),
        "logradouro": f"{rf.get('logradouro','')}, {rf.get('numero','')} - {rf.get('bairro','')}",
        "cep": rf.get("cep"),
        "socios": [s.get("nome_socio") for s in (rf.get("qsa") or [])][:3],
    }
    flag = "ATIVA" if sit == "ATIVA" else sit
    print(f"  {d['cnpj']} {d['nome'][:38]:38s} [{flag}] tel={ddd_tel or '-'}")
    if sit == "ATIVA":
        out.append(rec)
        ativas += 1
    time.sleep(0.8)  # respeita rate limit BrasilAPI

json.dump(out, open("empresas_enriquecidas.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(f"\n{len(out)} empresas ATIVAS enriquecidas -> empresas_enriquecidas.json")
