# Comece aqui

Guia da equipe. Não precisa saber programar: é copiar o comando e apertar Enter.

## 1. Instalar na máquina (uma vez por computador)

1. Instalar o Python 3.11 ou mais novo: https://www.python.org/downloads/
   **Marcar a caixinha "Add Python to PATH"** na primeira tela.
2. Baixar o sistema:
   ```
   git clone https://github.com/pabadvogados-hub/faya-barreiros-advocacia.git
   cd faya-barreiros-advocacia
   ```
3. Rodar o instalador (clique duplo serve):
   ```
   deploy\instalar_windows.bat
   ```
4. Copiar `config\.env.example` para `config\.env` e preencher o que tiver em mãos.
   Só a `ANTHROPIC_API_KEY` é indispensável para começar.
5. Apontar a pasta dos clientes: em `config\.env`, `PASTA_CLIENTES_RAIZ=` com o caminho da pasta
   do OneDrive sincronizada no computador (ex.: `C:\Users\Bárbara\OneDrive\CLIENTES`).
6. Testar sem tocar em nada real:
   ```
   python CONTRATACAO/main.py exemplo
   ```

Para conferir o que está instalado sem mudar nada: `deploy\instalar_windows.bat /checar`.

## 2. O dia a dia, por pessoa

### Atendimento / Dr. William (lead até o fechamento)

Chegou lead no WhatsApp ou Instagram? Salve a conversa num arquivo .txt e rode:
```
python COMERCIAL/main.py qualificar "conversa.txt"
```
Sai na tela: temperatura do lead, a situação dele (dívida, fase, prazo correndo), **o que perguntar
na reunião**, quais documentos já pedir e os riscos (o principal: prazo fatal próximo).

Gravou a reunião? Transcreva:
```
python COMERCIAL/main.py transcrever "reuniao.mp3" --salvar transcricao.txt
```

Mover o lead no funil e ver o quadro:
```
python COMERCIAL/main.py lead "Carlos da Silva" 71999999999 --etapa PROPOSTA
python COMERCIAL/main.py painel
```

### Quando o cliente fecha

```
python CONTRATACAO/main.py novo "transcricao.txt" "RG.pdf" --cadastro CADASTRO.txt
```
O sistema: lê a reunião, extrai a qualificação do documento, monta o **Relatório de Triagem**
(débitos e origem, execução fiscal, parcelamentos, teses candidatas, gatilhos de prazo), cria a pasta
do cliente, gera contrato, procuração e declaração preenchidos, e lista o que falta.

Conferiu tudo? Envie:
```
python CONTRATACAO/main.py enviar "CAMINHO DA PASTA DO CLIENTE"
```
Isso manda para assinatura (se houver ZapSign configurado), avisa o cliente no WhatsApp (se houver D-API
configurada) e começa a cobrança dos documentos. **Se faltar qualquer dado, o envio trava e diz o que
falta** - é proposital. O escritório assina dentro da Tramitação Inteligente: sem ZapSign, os documentos
ficam prontos na pasta `00 CONTRATACAO` para subir lá.

A cobrança dos documentos continua sozinha, 3 vezes por dia:
```
python CONTRATACAO/main.py acompanhar --enviar
```

### Dra. Faya e Dr. William (análise, peças e revisão)

Ver se o caso já tem documento suficiente:
```
python JUDICIAL/main.py checklist "CARLOS DA SILVA"
```
Ver os tipos de peça:
```
python JUDICIAL/main.py tipos
```
Gerar o relatório de análise de origem dos débitos (CDAs):
```
python JUDICIAL/main.py peca "CARLOS DA SILVA" --tipo relatorio-cda
```
Outros tipos: `recurso-administrativo`, `embargos-execucao`, `excecao-pre-executividade`,
`peticao-andamento`, `parecer-previdenciario`. Dá para orientar a IA com `--instrucao "..."`.

A minuta vai para a pasta do cliente, em `11 PECAS`, com `[CONFERIR]` em tudo que a IA não tinha como
saber e `[INSERIR IMAGEM: ...]` onde a prova é recorte de documento (CDA, tela do e-CAC).
**A automação não protocola.**

### Controladoria: Bárbara e estagiário (intimações e prazos)

```
python CONTROLADORIA/main.py varredura --dias 3
python CONTROLADORIA/main.py parados
python CONTROLADORIA/main.py avisos-cliente
```
A varredura lê o DJEN pelas OABs configuradas em `OABS_MONITORADAS` e monta a lista de prazos. Os prazos
de execução fiscal e de recurso administrativo estão marcados para conferência da advogada.

### Financeiro

```
python FINANCEIRO/main.py cobranca          (prévia; com --enviar manda de verdade)
python FINANCEIRO/main.py inadimplencia
python FINANCEIRO/main.py fechamento
```
Usam a conta Asaas do escritório (`ASAAS_API_TOKEN`).

## 3. Rotinas automáticas

No Windows:
```
deploy\agendar_tarefas_windows.bat
```
Agenda tudo no Agendador de Tarefas: cobrança de documentos 3x ao dia, varredura das intimações às
7h30, conferência da manhã às 8h, cobrança de honorários às 10h e o fechamento no dia 5. Para tirar:
`deploy\agendar_tarefas_windows.bat /remover`. Os registros ficam em `logs\`.

Em servidor na nuvem: `deploy/crontab.exemplo` e `docs/DEPLOY_NUVEM.md`.

## 4. Quando der erro

1. A mensagem de erro quase sempre diz o que falta (uma credencial, um arquivo).
2. `--exemplo` roda qualquer módulo com dados fictícios: serve para saber se o problema é o sistema
   ou o caso.
3. O que ainda falta configurar está em `docs/ONBOARDING.md`.
