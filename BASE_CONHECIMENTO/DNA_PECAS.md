# DNA das peças do escritório

> **Atualizado em 23/10/2026** com o material que a Dra. Faya e o Dr. William enviaram em 18/10/2026
> (27 petições iniciais e 15 relatórios previdenciários da Faya; modelos de peça tributária do William).
> O texto das peças **não está neste repositório**: elas trazem nome, CPF e número de processo de clientes
> reais e o repositório é público. Ficam na máquina do escritório (`MATERIAL_FAYA/`, fora do git).
> Aqui ficam só a **estrutura**, os **tipos de ação** e as **citações que as próprias peças usam**.
>
> O sistema trata este arquivo como DNA completo por causa do marcador `DNA-ATIVO` na última linha.
> Regra que continua valendo: **a IA só cita jurisprudência que está na seção 5.** O resto sai com
> `[CONFERIR: jurisprudência]`.

---

## 1. Estilo

**Dra. Faya Barreiros** (previdenciário e cálculos)
- Estrutura petições e relatórios em **tópicos**, de forma organizada.
- Usa **quadros e tabelas** e **imagens/recortes dos documentos** (CNIS, PPP, carta de concessão).
- Tom formal e direto.
- A petição inicial previdenciária segue sempre os mesmos blocos, nesta ordem:
  1. Endereçamento (Vara Federal ou Juizado Especial Federal) e qualificação
  2. Nome da ação e fundamento legal
  3. **Da justiça gratuita** (Lei 1.060/50 e declaração de hipossuficiência) - em 19 de 27 peças
  4. **Da tramitação preferencial** (idoso, pessoa com deficiência ou doença grave) - só quando cabe
  5. **Da audiência de mediação e conciliação** (manifestação sobre o art. 334 do CPC) - em 18 de 27
  6. **Do esgotamento da via administrativa**, quando há requerimento e indeferimento
  7. **Dos fatos**, com quadro de vínculos e períodos
  8. **Do direito**
  9. **Da tutela de urgência**, só se houver
  10. **Do valor da causa**, com a conta
  11. **Dos pedidos** ("a total procedência da ação para: ...")
  12. **Da autenticidade dos documentos colacionados à peça prefacial** - em 18 de 27
  13. **Índice da instrução** (lista dos documentos anexados)
- O relatório previdenciário segue: Dados do segurado (e do benefício) -> Metodologia aplicada ->
  Vínculos e períodos (quadro) -> Indicadores no CNIS e providências de regularização -> Conferência de tempo
  (INSS x escritório) -> Renda mensal inicial, coeficiente e fator previdenciário -> Conclusão -> Honorários.
- Termo de renúncia para fixar o Juizado Especial Federal (60 salários mínimos) acompanha a inicial quando cabe
  (modelo em `DOCS_MODELOS/PREV_TERMO_RENUNCIA_JEF.docx`).

**Dr. William Ricardo Coelho** (tributário)
- Relatórios e análises com **imagens e dados das CDAs**.
- Argumentação **técnica**: fato gerador, base de cálculo, "letra da lei"; evita interpretação subjetiva.
- A peça judicial segue: Endereçamento -> Dos fatos -> Do direito / Dos fundamentos jurídicos ->
  Da concessão da tutela antecipada -> Dos pedidos -> Valor da causa -> **Documentos comprobatórios anexados**.
- Tom didático quando a peça é para o cliente.

**Comum**
- Linguagem técnico-jurídica, sem excesso de formalismo e sem latim; peças objetivas, narração clara dos fatos
  e subsunção dos fatos ao direito.
- Pilar: **analisar a origem dos débitos antes de qualquer medida.**
- Resultados que o escritório mostra ao cliente: reduzir juros e multas, alterar a CAPAG, destravar
  parcelamentos, extinguir débitos por decadência, prescrição e nulidades.
- Termos que precisam de explicação simples para o cliente: PGFN, e-CAC, Receita Federal, inscrição em dívida
  ativa, prescrição, decadência, nulidades.

## 2. Legislação que o escritório usa

- Código Tributário Nacional
- Lei de Execução Fiscal (Lei 6.830/1980)
- Lei de Custeio da Previdência Social (Lei 8.212/1991)
- Lei do Regime Geral de Previdência Social (Lei 8.213/1991)
- Lei da Assistência Social (Lei 8.742/1993)
- Decreto Regulamentador da Previdência Social (Decreto 3.048/1999)
- Emenda Constitucional 103/2019 e Emenda Constitucional 113/2021
- Instrução Normativa PRES/INSS 128/2022 e IN INSS 74
- Lei Complementar 142/2013 (aposentadoria da pessoa com deficiência)
- Lei Complementar 123/2006 (Simples Nacional)
- Decretos 53.831/64, 83.080/79 e 10.410/2020 (atividade especial e regulamento da EC 103)
- Lei 10.259/2001 (Juizado Especial Federal) e Lei 10.741/2003 (Estatuto da Pessoa Idosa)
- Lei Complementar 116/2003 (ISS) e as leis municipais de ISS, IPTU e ITBI de Salvador (CTM Salvador)

(A Dra. Faya mandou os PDFs da legislação previdenciária e o Dr. William, a LEF, o CTN e o CTM de Salvador.
Ficam em `MATERIAL_FAYA/`; a base tributária que o sistema já consulta está em `TRIBUTARIO/legislacao/`.)

## 3. Teses e tipos de ação que o escritório trabalha

**Previdenciário (Dra. Faya)** - tipos de inicial que ela já tem pronta:
- Concessão: aposentadoria especial (ruído e outros agentes), por tempo com conversão, por pontos (direito
  adquirido), da pessoa com deficiência (inclusive visão monocular), por incapacidade permanente, por
  incapacidade com adicional de 25%, auxílio-doença (inclusive fibromialgia), auxílio-acidente, BPC deficiente,
  pensão por morte (união estável; filho maior inválido).
- Revisão: acréscimo do adicional de 25%, aposentadoria por incapacidade (regra pré-reforma e cálculo
  pré-reforma pós-reforma), atividade concomitante, conversão de tempo especial, conversão de aposentadoria
  pós-reforma para pré-reforma, inclusão de período de RT, retroação da DIB, atualização de CNIS.
- Outras: devolução de INSS acima do teto, devolução de RMC, suspensão de descontos indevidos, isenção de IR,
  cobrança de honorários e de licença-prêmio.
- Relatórios: análise previdenciária, conferência de RMI, contribuições acima do teto, parecer de análise de
  revisão, de liquidação, de recálculo de RMI, de revisão PCD, de tempo especial e de viabilidade;
  planejamento previdenciário (com conversões, detalhado e de professor); prestação de contas; recálculo de RMI
  com verba trabalhista.

**Tributário (Dr. William)** - modelos que ele usa:
- Ação declaratória ou anulatória: ISS, ITBI (momento do fato gerador), IPTU, ICMS, desbloqueio e liberação de
  mercadoria, IPVA por falta de transferência (administrativo e judicial).
- Execução fiscal: embargos, exceção de pré-executividade, ilegitimidade passiva, retirada do nome do sócio da
  CDA, suspensão de CDA ilíquida, limitação de multa confiscatória, **prescrição intercorrente** (administrativa
  e judicial).
- Cadastro e Receita: recusa na emissão de CNPJ (administrativa e judicial), vedação à suspensão de inscrição
  estadual, reclassificação da capacidade de pagamento (CAPAG) junto à Receita Federal.
- Argumento recorrente nas peças de ISS, ITBI e IPTU: o fato gerador e a base de cálculo se definem pela letra
  da lei (norma constitucional e lei complementar), sem alargamento por lei local.
- Argumento recorrente em defesa administrativa: **ausência de notificação** (contraditório e ampla defesa) e
  falta de indicação do valor do crédito e do prazo para recolhimento ou impugnação.

## 4. Teses que o escritório evita
[a preencher - o escritório ainda não informou. Perguntar à Dra. Faya e ao Dr. William.]

## 5. Jurisprudência e normas que as peças do escritório citam

> Lista tirada das peças-modelo (contagem = em quantas peças aparece). **É o que o escritório já usa, mas o
> sistema não conferiu a vigência nem o enunciado.** Ao citar, a IA reproduz só a referência como está aqui e
> marca `[CONFERIR: enunciado e vigência]`. Se o tema da peça não estiver nesta lista, não cita nada.

Previdenciário (petições iniciais):
- Lei 1.060/50 (justiça gratuita) - 20 peças; art. 334 do CPC (audiência de conciliação) - 8
- Lei 8.213/91 - 9; EC 103/2019 - 6; Decreto 3.048/99 - 3; Lei 10.741/2003 (preferência) - 6
- Lei 10.259/2001 (JEF) - 2; Decreto 53.831/64 - 2; Decreto 2.172/97, 4.882/2003, 83.080/79 - 1 cada
- RE 870947 (Tema 810) - 2; RE 639.337 - 2; RE 664.335 - 1; Tema 318 - 2; Tema Repetitivo 269 (STJ) - 1;
  REsp 1585467 - 1; Súmula 7/STJ - 1; Súmula 377/STJ - 1
- Lei Complementar 142/2013 - 3; Lei 14.126/2021 - 1; Lei 11.457/07 - 2

Previdenciário (relatórios):
- EC 103/2019 - 9; Lei 8.213/91 - 3; art. 103 da Lei 8.213/91 (decadência da revisão) - 2
- Lei 9.876/99 (fator previdenciário e regra de cálculo) - 2; IN PRES/INSS 128/2022 - 2
- Súmula 66 e Súmula 75 da TNU - 1 cada; Tema 277 da TNU - 1; Tema 350 e Tema 555 - 1 cada; Tema 1013 - 1
- Lei 13.135/2015, 13.183/2015, 10.887/2004, EC 26/2020 - 1 cada

Tributário:
- Lei Complementar 116/2003 (ISS) - 4; Súmula Vinculante 31 do STF - 2; Súmulas 546, 547 e 283 do STF - 1 a 3
- art. 174 do CTN e Súmula 314 do STJ (prescrição intercorrente); art. 40 da Lei 6.830/80 - 2
- arts. 33, 38, 148, 149 e 150 do CTN; art. 156 da CF; Lei Complementar 70/91
- RE 601.314 - 2; RE 796.376 - 2; RE 1.245.097; RE 1.937.821; REsp 1.340.553 - 2; Tema 1.113 e Tema 796
- art. 85, §2º do CPC (honorários); art. 489 do CPC (fundamentação)

## 6. Peças reais
As peças ficam só na máquina do escritório, em `MATERIAL_FAYA/` (fora do repositório). O sistema não as cola
aqui de propósito: o repositório é público e as peças têm dado de cliente. Para o sistema aprender com uma
peça nova, acrescente a **estrutura** e as **citações** nas seções 1, 3 e 5, nunca o texto com nome e CPF.

<!-- DNA-ATIVO -->
