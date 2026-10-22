# O que falta para o sistema rodar com a cara do escritório

O ambiente foi montado em 22/10/2026 a partir do **briefing de 18/10/2026**. Está tudo funcionando
com dados fictícios. Esta é a lista do que destrava cada parte. Não precisa responder tudo de uma
vez: cada item liberado já destrava o seu pedaço.

---

## 1. O que trava o envio HOJE (prioridade)

| O que falta | Onde entra | O que destrava |
|---|---|---|
| **2 ou 3 peças de cada advogado** (as melhores: relatório de CDA, recurso administrativo, embargos ou exceção, parecer previdenciário), em .docx ou PDF | viram `BASE_CONHECIMENTO/DNA_PECAS.md` (seção 6) e depois se ativa o marcador `<!-- DNA-ATIVO -->` na última linha | a minuta sai no estilo de cada um e com as teses do escritório; hoje sai como ESTRUTURA PROVISÓRIA, sem jurisprudência (o estilo do briefing já está aplicado) |
| **Papel timbrado oficial** (o briefing diz que a Dra. Faya envia) | `config/timbrado_modelo.docx` e `VISUAL['timbrado_oficial'] = True` | documento sai no timbrado do escritório |
| **Modelos oficiais de contrato, procuração e declaração** (idem) | `DOCS_MODELOS/` | hoje são provisórios com `[PREENCHER]`, que trava o envio para assinatura |
| **Honorários**: modelo (fixo, êxito, entrada + êxito?), percentual, sobre o quê incide | `config/escritorio.py` → `HONORARIOS` e cláusula 2ª do contrato | contrato para de travar |
| **Despesas**: quem paga custas e taxas administrativas | cláusula 4ª do contrato | contrato para de travar |
| **Regra de rescisão** do contrato | cláusula 5ª do contrato | contrato para de travar |

---

## 2. Dados do escritório que faltam

- **CEP** do endereço (Av. Tancredo Neves, 1283, Sala 1001), telefone comercial e site (hoje `[CONFERIR]`).
- **Número de registro da sociedade na OAB.**
- **OABs, conferir:** o briefing trouxe "308.385/SP e 64.723/BA - William OAB 64.518/BA". Está assumido
  Faya = OAB/SP 308.385 e OAB/BA 64.723; William = OAB/BA 64.518. **Confirmar com eles.**
- **Todas as inscrições de OAB que aparecem nas intimações** (`OABS_MONITORADAS` no `.env`; hoje
  `308385/SP,64723/BA,64518/BA`). Sem isso a varredura do DJEN perde publicação.
- **Nome completo de Bárbara (secretária) e do estagiário.**
- Cor da marca do escritório (hoje um azul sóbrio provisório).

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
- Contrato, procuração e declaração preenchidos com os dados do cliente, com trava de envio.
- Pasta do cliente criada e organizada, documento classificado na subpasta certa.
- Cobrança automática dos documentos que faltam, em 3 toques, pelo WhatsApp.
- Peças: relatório de CDA, recurso administrativo, embargos à execução fiscal, exceção de
  pré-executividade, petição de andamento e parecer previdenciário (todas para revisão humana).
- Varredura do DJEN com classificação das publicações e prazos.
- Cobrança de honorários, inadimplência e fechamento pelo Asaas.
- Instalador para Windows e agendador das rotinas.

Conferido em 22/10/2026 sem chave de IA: geração dos modelos e do timbrado provisórios, pasta do cliente, preenchimento dos documentos (com a trava de `[PREENCHER]`), relatório de triagem, mensagens, controladoria e financeiro em modo `--exemplo`. **Não testado com a IA real** (triagem, qualificação e peças): depende da `ANTHROPIC_API_KEY` do escritório.
