"""
Pessoas do escritorio -> cargos da automacao.

O escritorio NAO usa ADVBOX (usa Notion para prazos/processos e Tramitacao Inteligente para
assinatura e andamento). Os campos `advbox_id` ficam vazios de proposito: sem ID, nenhuma tarefa e
criada no ADVBOX e o sistema apenas lista o que seria feito. Se um dia o escritorio adotar o ADVBOX
ou outra ferramenta com API, e aqui que cada pessoa e ligada ao usuario dela
(`python INTEGRACOES/advbox_integration.py` lista usuarios e IDs).

Nomes e funcoes tirados do briefing de 18/10/2026.
"""

CARGOS = {
    # Dra. Faya: titular da sociedade; revisa e decide. Previdenciario + calculos; tributario de parcerias.
    'TITULAR':      {'nome': 'Faya Barreiros', 'advbox_id': ''},
    # Dr. William: tributario; capta, qualifica lead, agenda atendimento e fecha a reuniao
    'COMERCIAL':    {'nome': 'William Ricardo Coelho', 'advbox_id': ''},
    # Revisao de pecas antes do protocolo: Faya e William (regra do briefing)
    'ADV_REVISAO':  {'nome': 'William Ricardo Coelho', 'advbox_id': ''},
    # Barbara (secretaria): e-mails, prazos, recibos, pasta no drive, agenda de prazos judiciais
    'PROTOCOLO':    {'nome': 'Barbara (secretaria)', 'advbox_id': ''},
    'FINANCEIRO':   {'nome': 'Barbara (secretaria)', 'advbox_id': ''},
    # Estagiario: elabora peticoes, confere pushs processuais, baixa decisoes; so muda status das demandas
    'ESTAGIO':      {'nome': 'Estagiario', 'advbox_id': ''},
    'TI':           {'nome': '[CONFERIR]', 'advbox_id': ''},
}

# Quem aparece como remetente das tarefas criadas pela automacao
REMETENTE_TAREFAS = 'TITULAR'

# Tarefas que a contratacao abre (so com --criar-tarefas e IDs preenchidos acima).
# 'tipo' e o nome (ou parte) do tipo de tarefa cadastrado na ferramenta do escritorio.
TAREFAS_CONTRATACAO = [
    {'marco': 'documentos', 'cargo': 'COMERCIAL', 'tipo': 'SOLICITAR DOCUMENTOS',
     'texto': 'Cobrar do cliente os documentos que faltam: {faltando}. Pasta: {pasta}'},
    {'marco': 'inicial', 'cargo': 'ADV_REVISAO', 'tipo': 'ELABORAR PECA',
     'texto': 'Relatorio/peca pronto para revisao. Resumo do caso e arquivo na pasta: {pasta}'},
    {'marco': 'protocolo', 'cargo': 'PROTOCOLO', 'tipo': 'PROTOCOLO',
     'texto': 'Protocolar a peca revisada. Apos o protocolo, lancar o numero do processo no Notion.'},
]

# Em outro escritorio a regra era "so depois do numero do processo". Aqui nao ha ADVBOX:
# mantida False para o sistema nao travar nada por causa disso.
SO_ADVBOX_COM_NUMERO_PROCESSO = False
