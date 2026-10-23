"""
Tipos de peca montados a partir das pecas-modelo enviadas pela Dra. Faya e pelo Dr. William em 18/10/2026.

A ordem dos blocos segue o que as pecas deles repetem (ver BASE_CONHECIMENTO/DNA_PECAS.md, secao 1).
O texto das pecas reais NAO esta no repositorio (tem dado de cliente): so a estrutura.
"""
from textwrap import dedent

ESTILO_FAYA = (
    'Dra. Faya: estrutura peticoes e relatorios em TOPICOS, de forma organizada, com QUADROS e TABELAS e com '
    'imagens/recortes dos documentos apresentados na instrucao. Tom formal e direto.'
)
ESTILO_WILLIAM = (
    'Dr. William: relatorios e analises com imagens e dados das CDAs; argumentacao TECNICA, centrada no fato '
    'gerador e na letra da lei, sem interpretacao subjetiva. Tom didatico quando a peca e para o cliente.'
)


def _linhas(txt):
    return '\n'.join(l for l in dedent(txt).strip().splitlines())


TIPOS_PREV_E_TRIB = {
    'peticao-inicial-previdenciaria': {
        'titulo': 'PETICAO INICIAL PREVIDENCIARIA',
        'autor': ESTILO_FAYA,
        'advogado': 'faya',
        'estrutura': _linhas("""
            ENDERECAMENTO (Vara Federal ou Juizado Especial Federal, conforme o valor da causa) e QUALIFICACAO
            NOME DA ACAO e fundamento legal
            DA JUSTICA GRATUITA (Lei 1.060/50 e declaracao de hipossuficiencia)
            DA TRAMITACAO PREFERENCIAL (so se idoso, pessoa com deficiencia ou doenca grave: Lei 10.741/2003)
            DA AUDIENCIA DE MEDIACAO E CONCILIACAO (manifestacao do autor, art. 334 do CPC)
            DO ESGOTAMENTO DA VIA ADMINISTRATIVA (requerimento, indeferimento, numero do beneficio)
            DOS FATOS (cronologico, com quadro de vinculos e periodos e recortes do CNIS, PPP e laudos)
            DO DIREITO (regra aplicavel; tempo de contribuicao, carencia, qualidade de segurado; renda mensal inicial)
            DA TUTELA DE URGENCIA (so se houver urgencia e probabilidade do direito)
            DO VALOR DA CAUSA (com a conta)
            DOS PEDIDOS (total procedencia para: ..., parcelas vencidas, juros e correcao, honorarios)
            DA AUTENTICIDADE DOS DOCUMENTOS COLACIONADOS A PECA PREFACIAL
            INDICE DA INSTRUCAO (lista dos documentos)
        """),
    },
    'relatorio-previdenciario': {
        'titulo': 'RELATORIO PREVIDENCIARIO',
        'autor': ESTILO_FAYA,
        'advogado': 'faya',
        'estrutura': _linhas("""
            DADOS DO SEGURADO (e DADOS DO BENEFICIO, se houver)
            DA METODOLOGIA APLICADA (fontes: CNIS, CTPS, carta de concessao, processo administrativo; regras e indices)
            DOS VINCULOS E PERIODOS DE TRABALHO (quadro)
            DOS INDICADORES NO CNIS (pendencias e providencias para regularizacao)
            DA CONFERENCIA DE TEMPO (tempo apurado pelo INSS x tempo apurado pelo escritorio)
            DA RENDA MENSAL INICIAL, DO COEFICIENTE E DO FATOR PREVIDENCIARIO (so com planilha de calculo)
            DA CONCLUSAO (viabilidade, cenarios e proximo passo)
            DOS HONORARIOS (so se houver proposta)
        """),
    },
    'acao-declaratoria-tributaria': {
        'titulo': 'ACAO DECLARATORIA COM PEDIDO DE TUTELA',
        'autor': ESTILO_WILLIAM,
        'advogado': 'william',
        'estrutura': _linhas("""
            ENDERECAMENTO (Vara da Fazenda Publica) e QUALIFICACAO
            DOS FATOS (fato gerador, lancamento ou cobranca, datas)
            DO DIREITO (fato gerador e base de calculo pela letra da lei; norma constitucional e complementar do tributo)
            DA AUSENCIA DE NOTIFICACAO (contraditorio e ampla defesa no procedimento administrativo), so se os fatos mostrarem
            DA CONCESSAO DA TUTELA ANTECIPADA
            DOS PEDIDOS
            DO VALOR DA CAUSA
            DOCUMENTOS COMPROBATORIOS ANEXADOS (lista)
        """),
    },
    'prescricao-intercorrente': {
        'titulo': 'PEDIDO DE RECONHECIMENTO DE PRESCRICAO INTERCORRENTE',
        'autor': ESTILO_WILLIAM,
        'advogado': 'william',
        'estrutura': _linhas("""
            ENDERECAMENTO e QUALIFICACAO (administrativo ou judicial)
            SINTESE DA INICIAL OU DO PROCESSO
            DOS FATOS (data da constituicao, do ultimo ato e da paralisacao, em quadro com a conta do prazo)
            DO DIREITO (art. 174 do CTN e art. 40 da Lei 6.830/80; entendimento dos tribunais so o da secao 5 do DNA)
            DOS PEDIDOS
        """),
    },
}
