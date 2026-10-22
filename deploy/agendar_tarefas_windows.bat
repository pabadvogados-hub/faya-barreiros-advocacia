@echo off
REM =============================================================================
REM  Agenda TODAS as rotinas automaticas no Agendador de Tarefas do Windows,
REM  na pasta "Faya Barreiros" do Agendador. Logs em logs\ (um arquivo por rotina).
REM
REM    deploy\agendar_tarefas_windows.bat            cria ou atualiza (pode rodar de novo)
REM    deploy\agendar_tarefas_windows.bat /listar    mostra o que esta agendado
REM    deploy\agendar_tarefas_windows.bat /remover   apaga todas as rotinas "Faya Barreiros"
REM    acrescente /sem-pausa para nao esperar uma tecla no final
REM
REM  IMPORTANTE:
REM  - Rodar na maquina que fica LIGADA no escritorio, com o usuario que usa o sistema.
REM  - As rotinas rodam com o usuario conectado. Para rodar com a sessao bloqueada/
REM    deslogada: Agendador > pasta Faya Barreiros > tarefa > Propriedades > "Executar
REM    estando o usuario conectado ou nao".
REM  - Se as rotinas forem para a VPS (docs\DEPLOY_NUVEM.md), rode /remover aqui:
REM    as duas maquinas juntas mandariam mensagem em dobro para o cliente.
REM  - Modulo que ainda nao existe na maquina e pulado sem erro (rodar_rotina.bat).
REM =============================================================================
setlocal EnableExtensions
cd /d "%~dp0.."
set "PASTA=%cd%"
set "MODO=criar"
set "SEMPAUSA="
if /I "%~1"=="/sem-pausa" set "SEMPAUSA=1"
if /I "%~2"=="/sem-pausa" set "SEMPAUSA=1"
if /I "%~1"=="/remover" set "MODO=remover"
if /I "%~1"=="/listar" (
  schtasks /Query /FO CSV /NH | findstr /I /C:"Faya Barreiros"
  goto fim
)
if not exist "%PASTA%\logs" mkdir "%PASTA%\logs"
set ERROS=0

if "%MODO%"=="criar" (
  echo Agendando as rotinas em "%PASTA%" ...
  REM remove as tarefas antigas do agendar_acompanhamento_windows.bat, agora na pasta Faya Barreiros
  for %%H in (09 13 17) do schtasks /Delete /F /TN "Faya Barreiros Contratacao %%H" >nul 2>&1
) else (
  echo Removendo as rotinas da pasta Faya Barreiros do Agendador...
)

REM            NOME NO AGENDADOR                          FREQ     DIAS                  HORA   LOG                              COMANDO
call :tarefa "Contratacao - acompanhar 09h"               DAILY    ""                    09:00  contratacao_acompanhar           "CONTRATACAO\main.py acompanhar --enviar"
call :tarefa "Contratacao - acompanhar 13h"               DAILY    ""                    13:00  contratacao_acompanhar           "CONTRATACAO\main.py acompanhar --enviar"
call :tarefa "Contratacao - acompanhar 17h"               DAILY    ""                    17:00  contratacao_acompanhar           "CONTRATACAO\main.py acompanhar --enviar"
call :tarefa "Controladoria - varredura"                  DAILY    ""                    07:30  controladoria_varredura          "CONTROLADORIA\main.py varredura --dias 3"
call :tarefa "Comercial - conferencia da manha"             WEEKLY   "MON,TUE,WED,THU,FRI" 08:00  comercial_painel                 "COMERCIAL\main.py painel"
call :tarefa "Controladoria - relatorio clientes dia 01"  MONTHLY  "1"                   08:00  controladoria_relatorio_clientes "CONTROLADORIA\main.py relatorio-clientes --dias 15"
call :tarefa "Controladoria - relatorio clientes dia 16"  MONTHLY  "16"                  08:00  controladoria_relatorio_clientes "CONTROLADORIA\main.py relatorio-clientes --dias 15"
call :tarefa "Financeiro - cobranca honorarios"           WEEKLY   "MON,TUE,WED,THU,FRI" 10:00  financeiro_cobranca              "FINANCEIRO\main.py cobranca --enviar"
call :tarefa "Financeiro - inadimplencia"                 WEEKLY   "MON"                 08:00  financeiro_inadimplencia         "FINANCEIRO\main.py inadimplencia"
call :tarefa "Financeiro - honorarios novos"              WEEKLY   "MON,TUE,WED,THU,FRI" 18:00  financeiro_honorarios_novos      "FINANCEIRO\main.py honorarios-novos"
call :tarefa "Financeiro - fechamento mes anterior"       MONTHLY  "5"                   08:00  financeiro_fechamento            "FINANCEIRO\main.py fechamento"

echo.
if "%MODO%"=="remover" (
  echo Pronto. Rotinas removidas.
  goto fim
)
if %ERROS% GTR 0 (
  echo ATENCAO: %ERROS% tarefa^(s^) nao foram criadas. Rode como Administrador
  echo ^(botao direito no arquivo ^> Executar como administrador^).
) else (
  echo Pronto. Conferir em: Agendador de Tarefas ^> Biblioteca ^> Faya Barreiros
)
echo Logs de cada rotina: %PASTA%\logs\
echo Rodar uma rotina agora, para testar:  schtasks /Run /TN "Faya Barreiros\Financeiro - inadimplencia"
goto fim

REM -----------------------------------------------------------------------------
REM :tarefa  NOME  FREQUENCIA  DIAS  HORA  LOG  COMANDO
REM -----------------------------------------------------------------------------
:tarefa
if "%MODO%"=="remover" (
  schtasks /Delete /F /TN "Faya Barreiros\%~1" >nul 2>&1 && echo   removida  %~1
  goto :eof
)
set "DIAS="
if not "%~3"=="" set "DIAS=/D %~3"
schtasks /Create /F /TN "Faya Barreiros\%~1" /SC %~2 %DIAS% /ST %~4 /TR "\"%PASTA%\deploy\rodar_rotina.bat\" %~5 %~6" >nul
if errorlevel 1 (
  echo   FALHOU    %~1
  set /a ERROS+=1
) else (
  echo   OK        %~1  [%~2 %~3 %~4]
)
goto :eof

:fim
if not defined SEMPAUSA pause
endlocal
