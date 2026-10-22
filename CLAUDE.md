# Faya Barreiros Advocacia - Central de Automações

> Escritório: **Faya Barreiros Sociedade Individual de Advocacia** (CNPJ 67.928.823/0001-52),
> Av. Tancredo Neves, 1283, Sala 1001, Salvador/BA. Atendimento presencial em Salvador e online para todo o Brasil.
> Advogados: **Dra. Faya Milla Magalhães Mascarenhas Barreiros** (previdenciário, cálculos e serviços avulsos)
> e **Dr. William Ricardo Coelho** (tributário: execução fiscal e gestão de passivo).
> Equipe: Bárbara (secretária: e-mails, prazos, recibos, pasta no drive) e um estagiário (petições, pushs
> processuais, baixa de decisões).
> Ferramentas do escritório: **Notion** (prazos, financeiro, processos), **Tramitação Inteligente** (assinatura
> digital e andamento), **Asaas** (cobrança), **OneDrive/SharePoint** (documentos), PJe, Claude.
> Quer rodar na **nuvem**. Não usa ADVBOX, Google Workspace nem CRM de WhatsApp.

## Estado do projeto
Ambiente montado em **22/10/2026** a partir do briefing de 18/10/2026. Tudo que o briefing não trouxe
está marcado com `[CONFERIR]` ou `[PREENCHER]` e **trava o envio** de propósito.
A lista do que falta é **`docs/ONBOARDING.md`**.

## Regra de ouro
- **A IA não protocola e não envia nada ao cliente nem ao processo sem flag explícita.**
  Toda peça, mensagem e relatório sai para revisão humana (Faya e William revisam, sempre).
- Exceção prevista no briefing: a IA pode **definir a estratégia sozinha** só em casos simples e
  padronizados e em **petições de andamento**. Isso ainda não está habilitado; ligar exige decisão
  dos advogados e um tipo de peça novo em `JUDICIAL/main.py`.
- Nunca inventar dado de cliente, CDA, valor, data, número de processo ou jurisprudência.
  Sem dado: `[CONFERIR]`.
- Prescrição e decadência: só calcular com as datas-chave nos documentos, mostrando a conta.
- Documento com `[CONFERIR]` ou `[PREENCHER]` **nunca** vai para assinatura (trava no código).
- **Inegociáveis do escritório:** a reunião de fechamento com o cliente (William) e o ciclo dos prazos
  das demandas externas de cálculos e serviços avulsos (Faya). A automação apoia esses dois pontos,
  não os substitui.
- Pilar da atuação: **analisar a origem dos débitos antes de qualquer medida.**

## Mapa: etapa do escritório -> módulo
| Etapa | Módulo | Comandos |
|---|---|---|
| Lead chega (WhatsApp, Instagram, indicação), qualificação e agendamento | `COMERCIAL/` | `qualificar`, `transcrever`, `lead`, `painel`, `mensagem` |
| Fechou: contrato, procuração, pasta, cobrança de documentos | `CONTRATACAO/` | `novo`, `enviar`, `acompanhar`, `painel`, `exemplo` |
| Análise e peças: relatório de CDAs, recursos, embargos, exceção, parecer previdenciário | `JUDICIAL/` | `checklist`, `peca --tipo ...`, `tipos` |
| **Motor tributário**: relatório de passivo fiscal federal (16 seções) a partir dos PDFs do e-CAC/Regularize/CDAs; consulta de legislação; prospecção PGFN | `TRIBUTARIO/` | `passivo`, `legislacao`, `prospeccao/` |
| Processo andando: intimações (DJEN), prazos, avisos ao cliente | `CONTROLADORIA/` | `varredura`, `avisos-cliente`, `relatorio-clientes`, `planilha`, `parados`, `finalizar` |
| Honorários, inadimplência, fechamento (Asaas) | `FINANCEIRO/` | `cobranca`, `inadimplencia`, `fechamento`, `honorarios-novos` |

Uso: `python MODULO/main.py <comando>` na pasta do sistema. Quase todo comando aceita `--exemplo`.

## Estrutura
```
NUCLEO/          ambiente (.env, caminhos), ia (Claude), docx_escritorio (timbrado), caminhos
INTEGRACOES/     asaas, zapsign, dapi_whatsapp, comunica_djen (DJEN/PJe), advbox (NÃO usado), meta_ads, gmail
COMERCIAL/       qualificação do lead, transcrição, funil local
CONTRATACAO/     triagem pela IA, documentos, pasta do cliente, envio, acompanhamento
JUDICIAL/        checklist de documentos e minutas (tributário e previdenciário)
TRIBUTARIO/      motor tributário: passivo fiscal federal, base de legislação (CTN, LEF, Leis 10.522/13.988...), prospecção PGFN
CONTROLADORIA/   varredura do DJEN, prazos, avisos e relatório ao cliente
FINANCEIRO/      cobrança (Asaas + WhatsApp), inadimplência, fechamento
BASE_CONHECIMENTO/  DNA_PECAS.md (estilo do briefing aplicado; peças-modelo ainda não chegaram)
DOCS_MODELOS/    contrato, procuração, declaração (PROVISÓRIOS - travam o envio)
config/          escritorio.py, equipe.py, .env (não versionado)
deploy/          instalador Windows, agendador, gerador dos modelos provisórios, cron para servidor
SAIDA/           relatórios gerados (não versionado: tem dado de cliente)
CLIENTES/        pastas dos clientes (não versionado)
```

## Pontos que ainda não casam com a realidade do escritório (decidir antes de implantar)
1. **Tarefas e prazos:** o código de Controladoria/Contratação cria tarefas no ADVBOX. O escritório usa Notion.
   Sem `ADVBOX_API_TOKEN` o sistema apenas lista o que seria feito (modo seguro). Integração com Notion
   (ou com a Tramitação Inteligente) é módulo novo: precisa do token/API e do desenho das abas.
2. **Documentos no OneDrive/SharePoint:** o sistema grava na pasta apontada por `PASTA_CLIENTES_RAIZ`.
   Numa máquina com o OneDrive sincronizado isso já funciona. Em servidor na nuvem, é preciso montar o
   OneDrive (rclone) ou usar a Microsoft Graph API. Ver `docs/DEPLOY_NUVEM.md`.
3. **Assinatura:** o escritório assina dentro da Tramitação Inteligente; o código usa ZapSign. Sem
   `ZAPSIGN_API_TOKEN` os documentos ficam prontos na pasta para assinar do jeito que o escritório já faz.
4. **Áreas:** a esteira de contratação trabalha uma área por vez (`PASTA_AREA` em `config/escritorio.py`,
   hoje `TRIBUTARIO`). A área previdenciária usa a mesma esteira trocando essa linha.

## Primeiros passos na máquina do escritório
```
git clone https://github.com/pabadvogados-hub/faya-barreiros-advocacia.git
cd faya-barreiros-advocacia
deploy\instalar_windows.bat
copy config\.env.example config\.env     (e preencher)
python CONTRATACAO/main.py exemplo        (teste com caso fictício)
```

## O que NÃO fazer
- Não colocar chave de API, token ou senha em arquivo versionado: tudo no `config/.env`.
- Não apagar os `[PREENCHER]` dos modelos sem o texto oficial do escritório - eles são a trava.
- Não subir para este repositório nada com dado real de cliente (nome, CPF, CNPJ, CDA, documento).
  O repositório é **público**: serve para instalar o sistema em qualquer máquina do escritório.
