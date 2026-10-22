# -*- coding: utf-8 -*-
"""Gera relatorio.md + contatos.csv a partir de empresas_enriquecidas.json"""
import json, csv

emp = json.load(open("empresas_enriquecidas.json", encoding="utf-8"))

def fone(t):
    t = "".join(ch for ch in (t or "") if ch.isdigit())
    if len(t) < 10:
        return t or "-"
    ddd, num = t[:2], t[2:]
    if len(num) == 9:
        return f"({ddd}) {num[:5]}-{num[5:]}"
    return f"({ddd}) {num[:4]}-{num[4:]}"

# CSV de contatos
with open("contatos.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";")
    w.writerow(["Empresa", "CNPJ", "UF", "Municipio", "Divida_PGFN",
                "Ajuizado", "Situacao", "Porte", "Telefone", "Email",
                "CNAE", "Socio_principal"])
    for e in emp:
        w.writerow([e["nome"], e["cnpj"], e["uf"], e["municipio"],
                    f'{e["divida_pgfn"]:.2f}', "SIM" if e["ajuizado"] else "NAO",
                    e["situacao_cadastral"], e["porte"], fone(e["telefone"]),
                    e["email"] or "", e["cnae"], (e["socios"] or [""])[0]])

# Markdown
total = sum(e["divida_pgfn"] for e in emp)
L = []
L.append("# Lista de Prospeccao Tributaria - PGFN Divida Ativa da Uniao")
L.append("")
L.append("**Fonte:** Dados Abertos PGFN (dadosabertos.pgfn.gov.br) - trimestre usado na filtragem")
L.append("**Criterio:** Pessoa Juridica (devedor Principal), ATIVA na Receita, divida total faixa de valor escolhida")
L.append(f"**Total das empresas:** R$ {total:,.2f}")
L.append("")
for i, e in enumerate(emp, 1):
    L.append(f"## {i}. {e['nome']}")
    L.append("")
    L.append(f"- **CNPJ:** {e['cnpj']}")
    L.append(f"- **Divida na PGFN:** R$ {e['divida_pgfn']:,.2f}  ({e['inscricoes']} inscricoes)")
    L.append(f"- **Cobranca judicial:** {'SIM (ja ajuizada)' if e['ajuizado'] else 'NAO - so administrativa (negociavel via transacao)'}")
    L.append(f"- **Situacao cadastral:** {e['situacao_cadastral']} (desde {e['data_situacao']})")
    L.append(f"- **Porte / Abertura:** {e['porte']} / {e['abertura']}")
    L.append(f"- **Atividade (CNAE):** {e['cnae']}")
    L.append(f"- **Telefone:** {fone(e['telefone'])}")
    L.append(f"- **E-mail:** {e['email'] or '(nao informado na Receita)'}")
    L.append(f"- **Endereco:** {e['logradouro']}, {e['municipio']}/{e['uf']} - CEP {e['cep']}")
    L.append(f"- **Socio(s):** {', '.join(e['socios']) or '(n/d)'}")
    L.append("")
open("relatorio.md", "w", encoding="utf-8").write("\n".join(L))
print("Gerado: relatorio.md + contatos.csv")
print(f"Total divida das empresas: R$ {total:,.2f}")
