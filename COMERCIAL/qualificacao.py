"""
Qualificacao do lead (tributario ou previdenciario) pela IA.

Entra: o que o lead escreveu no WhatsApp/Instagram (ou o resumo do anuncio) e, se ja houve
conversa por video ou telefone, a transcricao. Sai: um JSON com o que o atendimento precisa
saber antes da reuniao - se o caso tem causa, o que perguntar e o que ja da para pedir de documento.

Fluxo do escritorio (briefing 18/10/2026):
    William: contato do cliente -> atendimento -> chamada para reuniao -> FECHAMENTO (inegociavel)
    Faya:    e-mail ou WhatsApp -> atendimento -> agendamento -> fechamento -> entrega

A IA NAO recusa caso e NAO promete resultado: ela classifica e lista o que falta.
Quem decide se o escritorio pega o caso e a Dra. Faya ou o Dr. William.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402,F401

import ia  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from config.escritorio import ESCRITORIO  # noqa: E402

MODELO = os.getenv('MODELO_QUALIFICACAO', 'claude-sonnet-5')


def _s(d=''):
    return {'type': 'string', 'description': d} if d else {'type': 'string'}


SCHEMA = {
    'type': 'object',
    'additionalProperties': False,
    'required': ['nome', 'area', 'temperatura', 'resumo', 'situacao', 'sinais', 'perguntas',
                 'documentos_pedir', 'riscos', 'proxima_acao'],
    'properties': {
        'nome': _s('como o lead se apresentou (pessoa ou empresa), ou vazio'),
        'area': {'type': 'string', 'enum': ['TRIBUTARIO', 'PREVIDENCIARIO', 'AMBOS', 'NAO INFORMADO']},
        'temperatura': {'type': 'string', 'enum': ['QUENTE', 'MORNO', 'FRIO']},
        'resumo': _s('2 a 4 linhas: quem e, qual o problema, onde esta o caso'),
        'situacao': {
            'type': 'object', 'additionalProperties': False,
            'required': ['quem', 'problema', 'valor_aproximado', 'fase', 'prazo_correndo'],
            'properties': {
                'quem': _s('empresa (regime/atividade) ou pessoa fisica (segurado), como foi dito'),
                'problema': _s('divida ativa, execucao fiscal, autuacao, parcelamento, certidao, beneficio negado etc.'),
                'valor_aproximado': _s('como foi dito, ou vazio'),
                'fase': _s('administrativa, divida ativa, execucao fiscal, INSS, judicial, nao informado'),
                'prazo_correndo': _s('prazo citado pelo lead (citacao, notificacao, indeferimento), ou "nao informado"'),
            },
        },
        'sinais': {'type': 'array', 'items': {
            'type': 'object', 'additionalProperties': False,
            'required': ['sinal', 'base'],
            'properties': {
                'sinal': _s('ex.: debito antigo (possivel prescricao/decadencia), cobranca duplicada, '
                            'multa elevada, bloqueio de conta, certidao travando negocio, '
                            'tempo especial nao reconhecido'),
                'base': _s('o que o lead disse que indica isso'),
            }}},
        'perguntas': {'type': 'array', 'items': _s('pergunta objetiva para a reuniao')},
        'documentos_pedir': {'type': 'array', 'items': _s()},
        'riscos': {'type': 'array', 'items': _s('ex.: prazo fatal proximo, ja tem advogado, '
                                                'debito recente sem tese clara, falta documento essencial')},
        'proxima_acao': _s('o que o atendimento faz agora, em uma frase'),
    },
}

SISTEMA = f"""Voce qualifica leads de Direito TRIBUTARIO (execucao fiscal, divida ativa, gestao de passivo) e PREVIDENCIARIO para o {ESCRITORIO['nome']}.

O lead chega por WhatsApp, Instagram, indicacao ou parceria com outro escritorio. Seu trabalho e preparar o atendimento para a reuniao de fechamento, nao fechar o caso.

Regras:
- Use so o que o lead disse. Nunca invente tributo, valor, data, numero de CDA ou de processo. O que nao foi dito vira pergunta.
- Temperatura: QUENTE = tem divida/processo concreto, descreve valores ou prazo em curso e quer resolver agora (ou prazo fatal proximo).
  MORNO = tem indicio mas falta dado essencial. FRIO = so curiosidade, ou sem divida/beneficio definido.
- O escritorio trabalha com ANALISE DA ORIGEM DOS DEBITOS: pergunte sempre como o debito nasceu (declaracao, auto de infracao, lancamento) e as datas, porque disso dependem decadencia, prescricao e nulidades.
- "riscos" existe para proteger o escritorio: prazo fatal proximo, ja ter advogado constituido, debito muito recente, falta de documento essencial.
- NUNCA diga que o caso nao e do escritorio, nunca prometa resultado e nunca estime economia ou valor de restituicao.
- Perguntas curtas e em linguagem simples, sem jargao: termos como PGFN, e-CAC, inscricao em divida ativa, prescricao, decadencia e nulidade devem vir com uma explicacao de uma linha para o cliente.
- Tom do escritorio: objetivo e empatico, sem formalismo excessivo, deixando o cliente trazer a pauta dele.
"""


def qualificar(texto_lead, transcricao=''):
    conteudo = f'<mensagens_do_lead>\n{texto_lead}\n</mensagens_do_lead>'
    if transcricao:
        conteudo += f'\n\n<transcricao_da_conversa>\n{transcricao}\n</transcricao_da_conversa>'
    conteudo += '\n\nQualifique este lead.'
    return ia.json_por_schema(MODELO, SISTEMA, conteudo, SCHEMA, 6000)


def imprimir(q):
    print(f"\n{q.get('nome') or 'Lead sem nome'}  [{q['temperatura']}]  area: {q.get('area')}")
    print('-' * 70)
    print(q['resumo'])
    v = q.get('situacao') or {}
    print(f"\nQuem: {v.get('quem') or '[CONFERIR]'} | Problema: {v.get('problema') or '[CONFERIR]'}")
    print(f"Valor: {v.get('valor_aproximado') or '[CONFERIR]'} | Fase: {v.get('fase') or '[CONFERIR]'}"
          f" | Prazo correndo: {v.get('prazo_correndo') or '[CONFERIR]'}")
    if q.get('sinais'):
        print('\nSinais:')
        for s in q['sinais']:
            print(f"  - {s['sinal']}  ({s['base']})")
    if q.get('riscos'):
        print('\nAtencao:')
        for r in q['riscos']:
            print(f'  ! {r}')
    print('\nPerguntar na reuniao:')
    for i, p in enumerate(q.get('perguntas') or [], 1):
        print(f'  {i}. {p}')
    if q.get('documentos_pedir'):
        print('\nJa pedir:')
        for d in q['documentos_pedir']:
            print(f'  - {d}')
    print(f"\n=> {q.get('proxima_acao')}\n")


EXEMPLO = """[18:42] Boa tarde, vi o video do Dr. William sobre divida ativa
[18:42] tenho uma loja de materiais de construcao aqui em Feira de Santana, Simples Nacional
[18:43] recebi uma carta da PGFN dizendo que tenho uns 180 mil inscritos em divida ativa
[18:44] sao de 2018 e 2019, eu acho, nao lembro direito o que e
[18:45] semana passada chegou uma citacao de execucao fiscal, falaram que tenho 5 dias
[18:46] preciso da certidao negativa para renovar um contrato com fornecedor
[18:47] tem como voces verem se vale a pena pagar tudo isso?
"""
