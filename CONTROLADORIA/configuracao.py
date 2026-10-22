"""
Regras da Controladoria (fases 5 e 6) do Faya Barreiros Advocacia.

Tudo que o escritorio pode querer ajustar sem mexer no codigo mora aqui:
antecedencia do prazo interno, pasta de arquivo, periodicidade do relatorio ao
cliente e o que cada tipo de publicacao pede (prazo padrao da CLT, cargo
responsavel, providencia e peca sugerida).

Variaveis do config/.env que mudam o comportamento:
    OABS_MONITORADAS=308385/SP,64723/BA,64518/BA              OABs consultadas no DJEN. Incluir TODAS as inscricoes
                                          que aparecem nas intimacoes do escritorio.
    PRAZO_INTERNO_DIAS_ANTES=3            prazo interno = D-3 (dias uteis) do fatal
    PASTA_ARQUIVO_CLIENTES=               onde vao as pastas encerradas (fase 6)
    FERIADOS_EXTRAS=                      feriados locais DD/MM ou DD/MM/AAAA, separados por virgula
    RELATORIO_CLIENTE_DIAS=30             periodicidade do relatorio de andamento ao cliente
"""
import os

# Prazo interno: quantos DIAS UTEIS antes do prazo fatal a tarefa vence no ADVBOX.
DIAS_ANTES_FATAL = int(os.getenv('PRAZO_INTERNO_DIAS_ANTES', '3') or 3)

# Processo sem movimentacao ha mais que isso = "parado" (possivel falta de custas/juntada).
DIAS_PARADO = 30

# Relatorio periodico ao cliente (15 ou 30 dias).
RELATORIO_CLIENTE_DIAS = int(os.getenv('RELATORIO_CLIENTE_DIAS', '30') or 30)

# Fases do ADVBOX que contam como encerradas (nome ou parte do nome da fase).
FASES_ENCERRADAS = ('ARQUIV', 'ENCERR', 'RENUNCI', 'BAIXAD', 'FINALIZ', 'EXTINT')

# Classes em que o cliente estaria no POLO PASSIVO quando o texto da publicacao nao diz (a regra
# principal e ler "Advogados do(a) EXECUTADO: ..."). No tributario o cliente costuma ser o executado;
# no previdenciario, o autor.
CLASSES_POLO_PASSIVO = ('EXECUÇÃO FISCAL', 'EXECUCAO FISCAL', 'COBRANÇA', 'COBRANCA', 'MONITÓRIA', 'MONITORIA')

# ------------------------------------------------------------------
# O QUE CADA TIPO DE PUBLICACAO PEDE
# ------------------------------------------------------------------
# prazo_dias: prazo padrao (CPC, dias uteis) quando o texto nao traz "prazo de N dias".
#             Embargos de declaracao: 5. Manifestacao simples: 5. Emenda a inicial: 15 (CPC art. 321).
#             Embargos a execucao fiscal: 30 dias (Lei 6.830/80, art. 16) - CONFERIR a contagem com a advogada.
#             Defesa/recurso administrativo fiscal: 30 dias (Decreto 70.235/72) - corridos; conferir.
#             Recurso inominado em JEF: 10 dias. Apelacao: 15 dias uteis.
#             (None = sem prazo fatal; so acompanhamento/ciencia).
# cargo:      chave de config/equipe.py (CARGOS) que recebe a tarefa.
# tipo_tarefa: nomes (ou parte) do tipo de tarefa no ADVBOX, em ordem de preferencia.
# peca / comando: sugestao para o advogado. A IA nao protocola.
#   ATENCAO: os comandos do modulo JUDICIAL precisam existir com esses nomes; ajustar aqui.
# aviso_cliente: gera mensagem ao cliente no comando avisos-cliente.
# gravidade: ALTA / MEDIA / BAIXA na planilha e no relatorio. Qualquer item vira ALTA quando o
#            prazo fatal esta a 5 dias uteis ou menos (audiencia: 10 dias corridos).
ACOES = {
    'LIMINAR_DEFERIDA': {
        'rotulo': 'Liminar / tutela deferida',
        'prazo_dias': None, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['ACOMPANHAMENTO', 'PRAZO'],
        'providencia': 'Avisar o cliente e acompanhar o cumprimento (suspensão da exigibilidade, baixa de restrições, '
                       'emissão de certidão). Se não cumprirem: petição de descumprimento com pedido de multa.',
        'peca': 'Petição de ciência / descumprimento (se houver)', 'comando': '',
        'aviso_cliente': True, 'gravidade': 'MEDIA', 'acompanhar_dias': 10,
    },
    'LIMINAR_INDEFERIDA': {
        'rotulo': 'Liminar / tutela indeferida',
        'prazo_dias': 8, 'cargo': 'TITULAR', 'tipo_tarefa': ['RECURSO', 'AGRAVO', 'PRAZO'],
        'providencia': 'Avaliar agravo de instrumento (art. 1.015, I, CPC) com a Dra. Faya / o Dr. William. '
                       'Conferir se cabe pedido de reconsideração com documento novo.',
        'peca': 'Agravo de Instrumento', 'comando': 'python JUDICIAL/main.py agravo "{pasta}"',
        'aviso_cliente': False, 'gravidade': 'ALTA',
    },
    'SENTENCA_FAVORAVEL': {
        'rotulo': 'Sentença favorável ao cliente',
        'prazo_dias': 5, 'cargo': 'TITULAR', 'tipo_tarefa': ['PRAZO', 'ACOMPANHAMENTO'],
        'providencia': 'Avisar o cliente. Conferir se cabem embargos de declaração (5 dias úteis) e '
                       'aguardar recurso da parte contrária (contrarrazões) ou cumprimento.',
        'peca': 'Embargos de Declaração (só se houver omissão/contradição)', 'comando': '',
        'aviso_cliente': True, 'gravidade': 'MEDIA',
    },
    'SENTENCA_DESFAVORAVEL': {
        'rotulo': 'Sentença desfavorável ao cliente',
        'prazo_dias': 8, 'cargo': 'TITULAR', 'tipo_tarefa': ['RECURSO', 'APELA', 'PRAZO'],
        'providencia': 'Avaliar apelação (15 dias úteis) ou transação. Decisão da advogada '
                       'responsável com o cliente.',
        'peca': 'Apelação', 'comando': '',
        'aviso_cliente': True, 'gravidade': 'ALTA',
    },
    'SENTENCA': {
        'rotulo': 'Sentença (resultado a conferir)',
        'prazo_dias': 5, 'cargo': 'TITULAR', 'tipo_tarefa': ['PRAZO', 'RECURSO'],
        'providencia': 'Ler a sentença e confirmar se é favorável. Prazo de embargos de declaração (5) '
                       'e de apelação (15) correm juntos.',
        'peca': 'Embargos de Declaração ou Apelação (conforme resultado)', 'comando': '',
        'aviso_cliente': True, 'gravidade': 'ALTA',
    },
    'REPLICA': {
        'rotulo': 'Intimação para réplica (contestação/impugnação da parte contrária)',
        'prazo_dias': 5, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['REPLICA', 'RÉPLICA', 'PRAZO'],
        'providencia': 'Elaborar réplica/impugnação à contestação (arts. 350 e 351 CPC).',
        'peca': 'Réplica / Impugnação à Contestação', 'comando': 'python JUDICIAL/main.py replica "{pasta}"',
        'aviso_cliente': False, 'gravidade': 'MEDIA',
    },
    'MANIFESTACAO': {
        'rotulo': 'Intimação para manifestação',
        'prazo_dias': 5, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['PRAZO', 'MANIFESTA'],
        'providencia': 'Manifestar-se no prazo (sem prazo no texto: 5 dias úteis, art. 218, §3º, CPC). '
                       'Conferir o que o juízo pediu.',
        'peca': 'Petição de manifestação', 'comando': '',
        'aviso_cliente': False, 'gravidade': 'MEDIA',
    },
    'CUSTAS_EMENDA': {
        'rotulo': 'Custas / emenda / juntada de documento',
        'prazo_dias': 15, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['PRAZO', 'CUSTAS', 'JUNTADA'],
        'providencia': 'Recolher custas ou emendar/juntar o que o juízo pediu (emenda: 15 dias úteis, '
                       'art. 321 CPC). Processo trava sem isso: prioridade.',
        'peca': 'Petição de emenda / juntada / comprovante de custas', 'comando': '',
        'aviso_cliente': False, 'gravidade': 'ALTA',
    },
    'AUDIENCIA': {
        'rotulo': 'Audiência designada',
        'prazo_dias': None, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['AUDIENCIA', 'AUDIÊNCIA', 'PRAZO'],
        'providencia': 'Avisar o cliente (dia, hora, local/link), preparar a audiência e pôr na agenda.',
        'peca': 'Preparação de audiência', 'comando': '',
        'aviso_cliente': True, 'gravidade': 'MEDIA',
    },
    'PERICIA': {
        'rotulo': 'Perícia',
        'prazo_dias': 10, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['PERICIA', 'PERÍCIA', 'PRAZO'],
        'providencia': 'Avisar o cliente. Quesitos e assistente técnico em 15 dias úteis (art. 465, §1º, '
                       'CPC); conferir honorários periciais e data da vistoria.',
        'peca': 'Quesitos / indicação de assistente técnico', 'comando': '',
        'aviso_cliente': True, 'gravidade': 'MEDIA',
    },
    'CONTESTACAO_JUNTADA': {
        'rotulo': 'Contestação juntada',
        'prazo_dias': 5, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['REPLICA', 'RÉPLICA', 'PRAZO'],
        'providencia': 'Preparar a réplica (o prazo corre da intimação; conferir se já houve).',
        'peca': 'Réplica / Impugnação à Contestação', 'comando': 'python JUDICIAL/main.py replica "{pasta}"',
        'aviso_cliente': False, 'gravidade': 'MEDIA',
    },
    'EXECUCAO_PENHORA': {
        'rotulo': 'Execução fiscal / citação / penhora / bloqueio',
        'prazo_dias': 30, 'cargo': 'TITULAR', 'tipo_tarefa': ['PRAZO', 'EMBARGOS'],
        'providencia': 'URGENTE: execução fiscal citada = embargos em 30 dias (Lei 6.830/80, art. 16, após a garantia do juízo) '
                       'ou exceção de pré-executividade se a matéria for de ordem pública e provada de plano; '
                       'conferir bloqueio SISBAJUD/penhora e opção de transação/parcelamento. Em execução comum, '
                       'embargos em 15 dias úteis (CPC, art. 915).',
        'peca': 'Embargos à Execução Fiscal / Exceção de Pré-Executividade', 'comando': 'python JUDICIAL/main.py peca "{pasta}" --tipo embargos-execucao',
        'aviso_cliente': False, 'gravidade': 'ALTA',
    },
    'RECURSO': {
        'rotulo': 'Recurso (da parte contrária ou decisão em recurso)',
        'prazo_dias': 15, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['RECURSO', 'CONTRARRAZ', 'PRAZO'],
        'providencia': 'Se a parte contrária recorreu: contrarrazões (15 dias úteis; embargos de declaração: 5). '
                       'Se é acórdão/decisão do tribunal: ler e avaliar recurso.',
        'peca': 'Contrarrazões', 'comando': '',
        'aviso_cliente': False, 'gravidade': 'MEDIA',
    },
    'EMBARGOS_DECLARACAO': {
        'rotulo': 'Embargos de declaração julgados',
        'prazo_dias': 8, 'cargo': 'TITULAR', 'tipo_tarefa': ['RECURSO', 'PRAZO'],
        'providencia': 'O prazo do recurso contra a decisão embargada volta a correr por inteiro '
                       '(art. 1.026 CPC). Decidir se recorre (agravo/apelação) ou se aguarda.',
        'peca': 'Recurso cabível contra a decisão embargada', 'comando': '',
        'aviso_cliente': False, 'gravidade': 'MEDIA',
    },
    'TRANSITO_JULGADO': {
        'rotulo': 'Trânsito em julgado',
        'prazo_dias': None, 'cargo': 'TITULAR', 'tipo_tarefa': ['ACOMPANHAMENTO', 'PRAZO'],
        'providencia': 'Conferir cumprimento da decisão (baixa de restrições, extinção/arquivamento do débito). '
                       'Cumprido: fase 6 (python CONTROLADORIA/main.py finalizar "PASTA").',
        'peca': 'Cumprimento de sentença (se não cumprirem)', 'comando': '',
        'aviso_cliente': True, 'gravidade': 'MEDIA',
    },
    'DESPACHO': {
        'rotulo': 'Despacho de mero expediente',
        'prazo_dias': None, 'cargo': 'ADV_REVISAO', 'tipo_tarefa': ['ACOMPANHAMENTO'],
        'providencia': 'Ciência. Conferir se o despacho não pede providência do escritório.',
        'peca': '', 'comando': '',
        'aviso_cliente': False, 'gravidade': 'BAIXA',
    },
    'REVISAO_MANUAL': {
        'rotulo': 'Não classificado (revisão manual)',
        'prazo_dias': None, 'cargo': 'TITULAR', 'tipo_tarefa': ['ACOMPANHAMENTO', 'PRAZO'],
        'providencia': 'REVISÃO MANUAL: ler a publicação inteira e definir a providência e o prazo.',
        'peca': '', 'comando': '',
        'aviso_cliente': False, 'gravidade': 'MEDIA',
    },
}

# Marcadores que a automacao grava no texto da tarefa do ADVBOX (evita duplicar).
TAG_TAREFA = '[CONTROLADORIA]'

# Cores da planilha de clientes (cabecalho no laranja do timbrado).
try:
    from config.escritorio import VISUAL as _VISUAL
    _COR = _VISUAL.get('cor_destaque', 'C45911')
except Exception:
    _COR = 'C45911'
VISUAL_PLANILHA = {'cabecalho': _COR, 'ALTA': 'F8CBAD', 'MEDIA': 'FFE699', 'BAIXA': 'E2EFDA'}


def pasta_arquivo():
    """Pasta para onde vao as pastas de clientes encerradas (fase 6)."""
    destino = os.getenv('PASTA_ARQUIVO_CLIENTES')
    if destino:
        return destino
    from pasta_cliente import raiz_clientes  # CONTRATACAO (so leitura da configuracao)
    return os.path.join(raiz_clientes(), 'ARQUIVO')
