# O que falta para o sistema rodar com a cara do escritório

O ambiente foi montado em 22/10/2026 a partir do **briefing de 18/10/2026**. Está tudo funcionando
com dados fictícios. Esta é a lista do que destrava cada parte. Não precisa responder tudo de uma
vez: cada item liberado já destrava o seu pedaço.

---

## 1. Material que o escritório mandou em 18/10/2026 (já aplicado em 23/10/2026)

| Material | Onde ficou | Estado |
|---|---|---|
| Papel timbrado da Dra. Faya (bordô e dourado) | `config/timbrado_faya.docx` | **No ar.** Padrão de todos os documentos do sistema |
| Papel timbrado do Dr. William (azul-marinho e dourado) | `config/timbrado_william.docx` | **No ar.** Peças e relatórios tributários |
| Contrato de honorários previdenciário (êxito; êxito + salários) | `DOCS_MODELOS/PREV_CONTRATO_EXITO*.docx` | **No ar**, virou modelo com campos |
| Procuração ad judicia previdenciária, declaração de hipossuficiência, termo de renúncia (JEF) | `DOCS_MODELOS/` | **No ar** |
| Contrato de gestão do passivo tributário (William) | `DOCS_MODELOS/TRIB_CONTRATO_GESTAO_PASSIVO*.docx` | **No ar** (versão nova e versão "com resultado") |
| 27 petições iniciais e 15 relatórios previdenciários; modelos de peça tributária | `BASE_CONHECIMENTO/DNA_PECAS.md` (só a estrutura e as citações) | **DNA ativo** |
| Legislação previdenciária, CTN, LEF, CTM Salvador, livros | só na máquina do escritório | Não entra no repositório |

Os arquivos que ela mandou eram contratos e peças **de clientes reais**. Viraram modelos com `{{CAMPOS}}` e os
originais ficam só em `MATERIAL_FAYA/` (bloqueada no `.gitignore`; o repositório é público).

**Ainda trava o envio (por desenho):**

| O que falta | Onde entra | O que destrava |
|---|---|---|
| **Procuração do Dr. William** (a que ele usa em contrato tributário) | `DOCS_MODELOS/PROCURACAO_MODELO.docx` (hoje provisória, com `[PREENCHER]`) | procuração tributária sai sem trava |
| **Conta bancária e chave Pix dos contratos** | `config/.env`: `CONTA_BANCARIA` e `CHAVE_PIX` | o contrato tributário deixa de travar; ficam fora do repositório de propósito |
| **Dados do caso no contrato tributário**: valor do débito, ente credor, CDAs, condições dos honorários | `CADASTRO.txt` do cliente (`valor_debito`, `lista_cdas`, `honorarios_condicoes`) | contrato do caso |
| **Estado civil da Dra. Faya** | `config/escritorio.py` -> `TITULAR['estado_civil']` | os contratos dizem "solteira" e a procuração antiga dizia "casada": confirmar |
| **Endereço comercial no contrato do William** | modelo usa o da Av. Tancredo Neves; o contrato antigo dele trazia outro (Av. Manoel Dias, 1911) | confirmar qual vale |
| Teses que o escritório **evita** | `BASE_CONHECIMENTO/DNA_PECAS.md`, seção 4 | peças sem essas teses |
| Conferir as citações da seção 5 do DNA (enunciado e vigência) | `DNA_PECAS.md` | a IA para de marcar `[CONFERIR]` nelas |

**Honorários (já extraídos dos contratos deles, em `config/escritorio.py` -> `HONORARIOS`):**
Dra. Faya: 4 salários de benefício na implantação + 30% sobre os retroativos (R$ 300 de honorários iniciais na
variante "êxito + salários"); autorização de desconto de até 30% do líquido mensal.
Dr. William: entrada + parcelas + êxito de 10% sobre o desconto obtido no administrativo e 20% sobre o débito nas
execuções fiscais; multa de 10% + juros de 1% ao mês + IGP-M; destituição = 2 salários mínimos; rescisão = 50%.

---

## 2. Dados do escritório que faltam

- **Número de registro da sociedade na OAB** e **site** (hoje `[CONFERIR]`).
- CEP (41830-021), telefone (71) 99981-1108 e endereço: **já preenchidos** a partir do timbrado e do contrato.
- **OABs:** conferem com o timbrado (Faya: SP 308.385 e BA 64.723; William: BA 64.518).
- **Todas as inscrições de OAB que aparecem nas intimações** (`OABS_MONITORADAS` no `.env`; hoje
  `308385/SP,64723/BA,64518/BA`).
- **Nome completo de Bárbara (secretária) e do estagiário.**
- **E-mail oficial:** o timbrado da Dra. Faya mostra `fayabarreiros@gmail.com`, o contrato dela `faya.barreiros@uol.com.br`
  e o briefing `faya.calculos@gmail.com`. O sistema usa o do contrato nos documentos (`email_contratos`) e o do
  briefing nas integrações. Confirmar se é isso.

## 3. Acessos (cada um libera um módulo)

| Acesso | Onde | Libera |
|---|---|---|
| `ANTHROPIC_API_KEY` | console.anthropic.com | triagem, qualificação e minutas (**é o único indispensável**) |
| Token do Asaas | Asaas → Integrações | cobrança de honorários |
| D-API (sessão + token), cerca de R$ 90/mês | contratar | WhatsApp: documentos e cobrança automática (o escritório hoje não usa ferramenta de WhatsApp) |
| Token do ZapSign | ZapSign → API | só se quiserem trocar a assinatura da Tramitação Inteligente |
| Meta Ads (leitura) | Gerenciador de Negócios | custo por lead no painel (William faz tráfego pago) |

## 4. Decisões que o briefing deixou em aberto

1. **Notion no lugar de ADVBOX.** O escritório controla prazos, financeiro e processos em abas do Notion
   (Faya e Bárbara alimentam; o estagiário só muda o status). O código de tarefas foi feito para ADVBOX.
   Para o sistema criar prazos e tarefas no Notion é preciso: token de integração do Notion, ID do
   banco de cada aba e os nomes das colunas. Sem isso, nada é criado (modo seguro).
2. **Tramitação Inteligente.** O briefing diz que o plano tem API liberada. Se quiserem que o sistema
   leia processos e andamentos de lá, precisa da documentação/token da API.
3. **OneDrive/SharePoint e a nuvem.** Ver `docs/DEPLOY_NUVEM.md`. Resumo: numa máquina com OneDrive
   sincronizado funciona hoje; em servidor, precisa montar o OneDrive.
4. **Quando a IA pode decidir sozinha.** O briefing libera casos simples e padronizados e petições
   de andamento. Para ligar, os dois precisam listar quais casos são "simples e padronizados".
5. **Prazos internos** (`PRAZOS` em `config/escritorio.py`): cobrança de documentos em D+1, análise
   pronta 5 dias depois dos documentos, revisão em 1 dia. Confirmar.
6. **Checklist de documentos** (`CHECKLIST_DOCUMENTOS`): confirmar o que é obrigatório. Hoje, no
   tributário: documento do responsável, contrato social/CNPJ, situação fiscal (e-CAC/PGFN) e CDAs.
   Previdenciário (CNIS, PPP) entra como opcional.
7. **Pastas do OneDrive.** O briefing descreveu: Previdência x Tributário, e dentro "Clientes do
   Escritório" x "avulsos (cálculos e parcerias)". O sistema cria `TRIBUTARIO/NOME DO CLIENTE/` com 13
   subpastas numeradas. Se quiserem outro desenho, mandar que ajustamos.
8. **Teses que o escritório não gosta de usar** (para a seção 4 do DNA).

## 5. Prioridades que o briefing pediu para os primeiros 30 dias

- **Dra. Faya:** integração entre Claude, PJe e agendas. (A varredura do DJEN já lê as intimações; a
  agenda é o próximo passo e depende da decisão 1 e do calendário que usam.)
- **Dr. William:** captação, qualificação de leads e agendamento dos atendimentos. (A qualificação já
  existe; o agendamento depende de saber qual agenda e qual ferramenta de contato.)
- Gargalos citados: organização de prazos, documentos e demandas avulsas, protocolo no INSS (Faya);
  contratos e demandas repetitivas, pedidos de processo administrativo no e-CAC, agendamento de
  reuniões (William).

## 6. O que já está pronto (22/10/2026)

- Qualificação do lead pela IA, a partir das mensagens do WhatsApp (`COMERCIAL/main.py qualificar --exemplo`).
- Transcrição da reunião (faster-whisper local, sem custo, ou API).
- Funil local com as etapas do Kanban.
- Relatório de triagem a partir da transcrição: débitos e origem, execução fiscal, parcelamentos,
  situação previdenciária, teses candidatas, gatilhos de prazo, gaps e estratégia candidata.
- Contrato, procuração e declaração **oficiais do escritório**, escolhidos pela área do caso (previdenciário ou tributário), preenchidos com os dados do cliente, com trava de envio.
- Pasta do cliente separada por área: `PREVIDENCIARIO/` e `TRIBUTARIO/`.
- Documentos e relatórios no **timbrado oficial** (Dra. Faya por padrão; Dr. William nas peças tributárias).
- Pasta do cliente criada e organizada, documento classificado na subpasta certa.
- Cobrança automática dos documentos que faltam, em 3 toques, pelo WhatsApp.
- Peças: relatório de CDA, recurso administrativo, embargos, exceção de pré-executividade, petição de andamento,
  parecer previdenciário, **petição inicial previdenciária, relatório previdenciário, ação declaratória tributária e
  prescrição intercorrente** (todas para revisão humana, no estilo do DNA real).
- Varredura do DJEN com classificação das publicações e prazos.
- Cobrança de honorários, inadimplência e fechamento pelo Asaas.
- Instalador para Windows e agendador das rotinas.

Conferido em 22/10/2026 sem chave de IA: geração dos modelos e do timbrado provisórios, pasta do cliente, preenchimento dos documentos (com a trava de `[PREENCHER]`), relatório de triagem, mensagens, controladoria e financeiro em modo `--exemplo`. **Não testado com a IA real** (triagem, qualificação e peças): depende da `ANTHROPIC_API_KEY` do escritório.
