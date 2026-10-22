---
name: triagem-tributaria
description: Transforma a conversa ou a reuniao com um cliente (empresa com debitos ou segurado) em triagem util - debitos e sua origem, fase, execucao fiscal, parcelamentos, teses candidatas com a prova de cada uma, gatilhos de prazo e o que ainda falta perguntar.
---

# Triagem de caso tributario ou previdenciario

Use quando chegar uma conversa de WhatsApp/Instagram, a transcricao de uma reuniao ou um relato solto
sobre uma empresa com debitos fiscais ou um segurado com problema no INSS.

## Como fazer
1. Se houver arquivo, prefira rodar o que ja existe:
   `python COMERCIAL/main.py qualificar "arquivo.txt"` (lead) ou
   `python CONTRATACAO/main.py novo ...` (ja fechou).
2. Se for analise direta no chat, siga a mesma ordem do relatorio:

- **Quem**: empresa (regime, atividade, porte, situacao, socios) ou segurado.
- **Debitos**: cada um separado - CDA/inscricao, tributo, ente (PGFN/Receita, Estado, Municipio, INSS),
  periodo, valor, fase (lancamento, defesa administrativa, divida ativa, execucao fiscal, parcelado) e
  COMO NASCEU (declaracao do proprio contribuinte, auto de infracao, lancamento de oficio).
- **Execucao fiscal**: numero, vara, citacao, penhora/bloqueio, garantia.
- **Parcelamentos e transacoes**: modalidade, situacao, atraso.
- **Previdenciario**: beneficio pretendido, situacao no INSS, tempo de contribuicao, CNIS, PPP/LTCAT.
- **Teses candidatas**: so o que os FATOS sustentam, cada uma com a prova que existe hoje e a forca
  (FORTE / MEDIA / FRACA). Tese sem fato e sem prova vira pergunta, nao vira pedido.
- **Gatilhos**: prazo de embargos/recurso correndo, bloqueio, certidao travando negocio,
  parcelamento a rescindir, prescricao/decadencia perto de consumar.
- **Gaps**: o que falta perguntar, em perguntas curtas e simples.

## Regras
- Nunca inventar tributo, valor, data, numero de CDA ou de processo. Faltou: `[CONFERIR: o que falta]`.
- Nao concluir prescricao ou decadencia sem as datas-chave (fato gerador, constituicao do credito, citacao).
- Nao citar jurisprudencia que nao esteja em `BASE_CONHECIMENTO/DNA_PECAS.md`.
- Nao estimar economia, restituicao ou valor de condenacao.
- Quem decide se o escritorio pega o caso e a Dra. Faya ou o Dr. William; a triagem organiza, nao recusa.
