"""
Regras financeiras do escritorio: regua de cobranca, conciliacao e fechamento.

O briefing nao trouxe regras de comissao, exclusoes de faturamento nem regua propria. Os valores
abaixo sao o padrao sugerido (lembrete antes do vencimento e cobranca em D+1, D+5 e D+15) e podem
ser ajustados pela equipe sem mexer no codigo.
"""
import unicodedata

# Cada passo cobre dias_do_vencimento entre 'dia' e 'ate' (negativo = antes do vencimento).
# 'tipo': 'lembrete' (a vencer) ou 'vencida'. Cada toque sai uma vez por cobranca.
REGUA_COBRANCA = [
    {'id': 'LEMBRETE_3D', 'dia': -3, 'ate': -1, 'tipo': 'lembrete'},
    {'id': 'VENCE_HOJE', 'dia': 0, 'ate': 0, 'tipo': 'lembrete'},
    {'id': 'VENCIDA_D1', 'dia': 1, 'ate': 4, 'tipo': 'vencida'},
    {'id': 'VENCIDA_D5', 'dia': 5, 'ate': 14, 'tipo': 'vencida'},
    {'id': 'VENCIDA_D15', 'dia': 15, 'ate': 29, 'tipo': 'vencida'},
]

# Tolerancia (dias) entre a data do recebimento e a do lancamento na conciliacao.
TOLERANCIA_DIAS_CONCILIACAO = 5

# Comissoes: {'chave': {'rotulo': 'Fulano', 'percentual': 0.10}}. O briefing nao previu comissao.
COMISSOES = {}

# Textos que, aparecendo no nome/descricao do recebimento, tiram o valor do faturamento do escritorio
# (ex.: repasse a parceiro que apenas passa pela conta). Vazio por padrao. [CONFERIR] com o escritorio.
EXCLUIR_DO_FATURAMENTO = []


def _norm(texto):
    t = unicodedata.normalize('NFD', texto or '')
    return ''.join(c for c in t if unicodedata.category(c) != 'Mn').lower()


def excluir_do_faturamento(texto):
    t = _norm(texto)
    return any(_norm(x) in t for x in EXCLUIR_DO_FATURAMENTO)


def eh_distribuicao(categoria):
    """Distribuicao de lucros e pro labore dos socios nao entram como despesa operacional."""
    t = _norm(categoria)
    return 'distribuicao' in t or 'lucro' in t or 'pro labore' in t or 'pro-labore' in t


def comissao_da_cobranca(descricao, nome):
    """Chaves de COMISSOES que se aplicam a uma cobranca recebida (nenhuma por padrao)."""
    return []
