# Rodar o sistema na nuvem

O briefing diz: "preferimos na nuvem". Duas coisas pesam nessa decisão e vale resolver antes de contratar o servidor.

## O ponto principal: os documentos estão no OneDrive/SharePoint

O sistema lê e grava as pastas dos clientes num caminho de disco (`PASTA_CLIENTES_RAIZ`). Um servidor na
nuvem não enxerga o OneDrive do escritório sozinho. Caminhos possíveis:

| Caminho | Como | Quando faz sentido |
|---|---|---|
| **Computador do escritório ligado** (hoje) | OneDrive sincronizado + `PASTA_CLIENTES_RAIZ` apontando para ele | Para começar já, sem custo. Fica dependente da máquina ligada. |
| **Servidor Linux + rclone** | `rclone mount` do OneDrive/SharePoint em `/mnt/clientes` | Nuvem de verdade, com os documentos onde já estão. Exige autorizar o rclone na conta Microsoft. |
| **Microsoft Graph API** | módulo novo que lê e grava no SharePoint | Mais robusto, mas é desenvolvimento novo (não existe neste repositório). |

Recomendação: começar no computador do escritório (instalador pronto) e, rodando estável, migrar para o
servidor com rclone.

## Servidor Linux (VPS)

1. Ubuntu 22.04 ou mais novo, Python 3.11+, `git`, `ffmpeg` (só se for transcrever áudio).
2. ```
   git clone https://github.com/pabadvogados-hub/faya-barreiros-advocacia.git
   cd faya-barreiros-advocacia
   python3 -m venv .venv && . .venv/bin/activate
   pip install -r requirements.txt
   cp config/.env.example config/.env   # preencher
   ```
3. Montar o OneDrive (rclone) e apontar `PASTA_CLIENTES_RAIZ=/mnt/clientes/CLIENTES` no `.env`.
4. Rotinas: `crontab -e` e colar o conteúdo de `deploy/crontab.exemplo` (ajustando o caminho).
5. **Não rodar as rotinas nos dois lugares** (Windows e servidor): o cliente receberia mensagem em dobro.
   Se for para o servidor, `deploy\agendar_tarefas_windows.bat /remover` na máquina do escritório.

## Segurança

- `config/.env` só no servidor/máquina do escritório, com permissão restrita. Nunca no repositório.
- O repositório é público e tem só código: nenhum dado de cliente deve ser colocado nele.
- Os dados de clientes (CNPJ, CDAs, CNIS) são dados pessoais: LGPD vale. Backup e acesso só da equipe.
