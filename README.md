# Faya Barreiros Advocacia - sistema de automações

Sistema do escritório **Faya Barreiros Sociedade Individual de Advocacia** (Salvador/BA), da
Dra. Faya (previdenciário e cálculos) e do Dr. William Coelho (tributário), para o fluxo que vai do
lead que chega ao relatório ou à minuta na mesa do advogado: **análise da origem dos débitos**,
recursos administrativos e judiciais, execução fiscal e pareceres previdenciários.
Inclui o **motor tributário** (`TRIBUTARIO/`): relatório de passivo fiscal federal a partir dos documentos do e-CAC, Regularize e CDAs, e base de legislação tributária.

- **Como instalar e usar:** [`docs/COMECE_AQUI.md`](docs/COMECE_AQUI.md)
- **O que ainda falta configurar:** [`docs/ONBOARDING.md`](docs/ONBOARDING.md)
- **Rodar na nuvem:** [`docs/DEPLOY_NUVEM.md`](docs/DEPLOY_NUVEM.md)
- **Regras do projeto:** [`CLAUDE.md`](CLAUDE.md)

```
git clone https://github.com/pabadvogados-hub/faya-barreiros-advocacia.git
cd faya-barreiros-advocacia
deploy\instalar_windows.bat
copy config\.env.example config\.env
python CONTRATACAO/main.py exemplo
```

Este repositório tem **só o código**. Nenhum dado de cliente, nenhuma credencial e nenhuma peça
real do escritório ficam aqui: pastas de cliente, `config/.env` e saídas são bloqueadas pelo
`.gitignore`.

A automação **não protocola** e **não envia nada** sem a pessoa mandar.
