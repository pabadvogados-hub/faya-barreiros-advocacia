"""
Analise da reuniao de fechamento pela IA (Claude).

1. triagem(): le a transcricao da reuniao com o cliente (contribuinte ou segurado) e monta o
   RELATORIO DE TRIAGEM que vai para o advogado que revisa (debitos e sua origem, execucao fiscal,
   parcelamentos, situacao previdenciaria, teses candidatas, gatilhos de prazo, gaps de prova,
   estrategia candidata).
2. qualificacao(): extrai os dados do cliente (pessoa fisica ou empresa), com a regra de origem:
   documento oficial (RG/CNH, contrato social, cartao CNPJ) > cadastro > transcricao.

A resposta vem em JSON garantido por schema (structured outputs).
A IA nao decide estrategia nem protocola: tudo sai para revisao humana.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402,F401  (carrega .env e caminhos)

import ia  # noqa: E402  (NUCLEO)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from config.escritorio import CHECKLIST_DOCUMENTOS, ESCRITORIO  # noqa: E402

MODELO_TRIAGEM = os.getenv('MODELO_TRIAGEM', 'claude-opus-5')
MODELO_EXTRACAO = os.getenv('MODELO_EXTRACAO', 'claude-sonnet-5')
DNA = os.path.join(RAIZ, 'BASE_CONHECIMENTO', 'DNA_PECAS.md')

PONTOS_ATENCAO = [
    'Qual a area do caso: tributario (empresa/pessoa com debitos) ou previdenciario (segurado)?',
    'Quais sao os debitos: tributo, ente (Uniao/PGFN, Estado, Municipio), periodo e valor aproximado?',
    'Em que fase esta cada debito: lancamento/autuacao, defesa administrativa, divida ativa, execucao fiscal, parcelado?',
    'Ha execucao fiscal em curso? Numero, vara, citacao, penhora/bloqueio, garantia do juizo?',
    'Ha prazo correndo agora (manifestacao de inconformidade, recurso voluntario, embargos, resposta a notificacao)?',
    'Decadencia: quando foi o fato gerador e quando o credito foi constituido (lancamento ou declaracao)?',
    'Prescricao: qual a data da constituicao definitiva e houve causa de suspensao ou interrupcao (parcelamento, citacao)?',
    'Como o credito foi constituido: declaracao do proprio contribuinte, auto de infracao, lancamento de oficio?',
    'Ha parcelamento ou transacao ativo, rescindido ou em atraso? Qual modalidade?',
    'Qual o regime tributario da empresa (Simples, Presumido, Real, MEI) e o porte? Ha CAPAG calculada?',
    'Ha certidao negativa travando contrato, licitacao, credito ou venda de bem?',
    'Ha responsabilizacao de socios ou administradores (redirecionamento)?',
    'Previdenciario: qual beneficio e pretendido e qual a situacao no INSS (requerimento, indeferimento, exigencia)?',
    'Previdenciario: ha CNIS, CTPS, PPP/LTCAT e vinculos urbanos/rurais a comprovar? Qual o tempo de contribuicao estimado?',
    'Quem e o responsavel pelo caso no escritorio (Faya ou William) e qual a origem do cliente (parceria, trafego, indicacao)?',
]


def _s(desc=''):
    return {'type': 'string', 'description': desc} if desc else {'type': 'string'}


def _obj(props):
    return {'type': 'object', 'properties': props, 'required': list(props), 'additionalProperties': False}


def _lista(item):
    return {'type': 'array', 'items': item}


SCHEMA_TRIAGEM = _obj({
    'data_reuniao': _s('DD/MM/AAAA, ou vazio'),
    'closer': _s('quem conduziu a reuniao pelo escritorio, ou vazio'),
    'area': {'type': 'string', 'enum': ['TRIBUTARIO', 'PREVIDENCIARIO', 'AMBOS', 'NAO INFORMADO']},
    'resumo_caso': _s('3 a 6 paragrafos em linguagem juridica formal, terceira pessoa'),
    'contribuinte': _obj({
        'nome': _s('razao social, nome ou como o cliente se apresentou'),
        'documento': _s('CNPJ ou CPF, se dito'),
        'regime': _s('Simples Nacional, Lucro Presumido, Lucro Real, MEI, pessoa fisica, nao informado'),
        'atividade': _s('ramo de atividade'),
        'porte': _s('faturamento ou porte aproximado, se dito'),
        'situacao': _s('ativa, baixada, inapta, em recuperacao, nao informado'),
        'socios_responsaveis': _s('socios/administradores citados e se ha risco de redirecionamento'),
    }),
    'debitos': _lista(_obj({
        'identificacao': _s('numero da CDA, inscricao, auto de infracao ou processo administrativo, se dito'),
        'tributo': _s(),
        'ente': _s('Uniao/PGFN, Receita Federal, INSS, Estado, Municipio'),
        'periodo': _s('competencias ou exercicio'),
        'valor_aproximado': _s('como foi dito; aproximado se for o caso'),
        'fase': _s('lancamento, defesa administrativa, divida ativa, execucao fiscal, parcelado, extinto'),
        'origem': _s('como o credito nasceu (declaracao, auto de infracao, lancamento de oficio)'),
    })),
    'execucao_fiscal': _obj({
        'existe': {'type': 'string', 'enum': ['SIM', 'NAO', 'NAO INFORMADO']},
        'numero': _s(),
        'vara_foro': _s(),
        'fase': _s('citacao, penhora, bloqueio, embargos, leilao etc.'),
        'garantia': _s('bens ou valores ja constritos ou oferecidos'),
    }),
    'parcelamentos': _s('parcelamentos e transacoes mencionados: modalidade, situacao, parcelas em atraso'),
    'previdenciario': _obj({
        'beneficio': _s('aposentadoria, BPC/LOAS, auxilio, revisao, planejamento etc., ou vazio'),
        'situacao_inss': _s('requerimento, indeferimento, exigencia, nada pedido ainda'),
        'tempo_contribuicao': _s('como foi dito (aproximado)'),
        'vinculos_e_provas': _s('vinculos, CNIS, PPP/LTCAT, periodos especiais ou rurais mencionados'),
    }),
    'teses_candidatas': _lista(_obj({
        'tese': _s('ex.: decadencia, prescricao, nulidade da CDA, ilegitimidade de socio, '
                   'excesso de multa/juros, revisao de parcelamento, reducao de CAPAG, '
                   'reconhecimento de tempo especial, revisao de beneficio'),
        'fundamento_fatico': _s('o que na fala do cliente sustenta essa tese'),
        'prova_disponivel': _s('qual documento comprova ou deve ser obtido'),
        'forca': {'type': 'string', 'enum': ['FORTE', 'MEDIA', 'FRACA']},
    })),
    'gatilhos': _lista(_obj({
        'gatilho': _s('fato que exige acao rapida (prazo correndo, bloqueio, certidao travando negocio)'),
        'detalhe': _s(),
        'gravidade': {'type': 'string', 'enum': ['ALTA', 'MEDIA', 'BAIXA']},
    })),
    'gaps': _lista(_s('informacao ou documento que falta para seguir')),
    'pontos_atencao': _lista(_obj({
        'ponto': _s(),
        'resposta': {'type': 'string', 'enum': ['SIM', 'NAO', 'NAO INFORMADO']},
        'evidencia': _s('trecho curto da reuniao ou justificativa'),
    })),
    'estrategia_candidata': _obj({
        'acao': _s('recurso administrativo, embargos, excecao de pre-executividade, transacao, '
                   'revisao de parcelamento, requerimento no INSS, acao previdenciaria etc.'),
        'orgao_foro': _s('orgao administrativo ou juizo/vara competente, e por que'),
        'rito': _s('administrativo ou judicial; procedimento'),
        'tutela_urgencia': _s('ha pedido urgente? (suspensao de exigibilidade, desbloqueio, certidao)'),
        'prova_a_produzir': _s('o que precisa ser juntado ou requerido'),
        'valor_estimado': _s('faixa de valor envolvido, se der para estimar com o que foi dito'),
        'observacao': _s(),
    }),
    'riscos': _lista(_s()),
    'pontos_fortes': _lista(_s()),
    'perguntas_onboarding': _lista(_s('pergunta para a reuniao de onboarding')),
    'documentos': _lista(_obj({
        'id': {'type': 'string', 'enum': [d['id'] for d in CHECKLIST_DOCUMENTOS]},
        'status': {'type': 'string', 'enum': ['JA ENTREGOU', 'VAI ENVIAR', 'NAO TEM', 'NAO FALADO']},
        'observacao': _s(),
    })),
    'honorarios': _obj({
        'entrada': _s('valor combinado de entrada/pro labore, ou vazio'),
        'parcelas': _s('forma de pagamento combinada, ou vazio'),
        'exito': _s('percentual ou regra de exito combinada, ou vazio'),
        'observacao': _s(),
    }),
    'trechos': _lista(_obj({'tema': _s(), 'trecho': _s('citacao literal curta da transcricao')})),
})

SCHEMA_QUALIFICACAO = _obj({k: _s() for k in (
    'nome', 'cpf', 'rg', 'orgao_emissor', 'data_nascimento', 'nacionalidade', 'estado_civil',
    'profissao', 'telefone', 'email', 'logradouro', 'numero', 'bairro', 'cidade', 'uf', 'cep',
    'conjuge_nome', 'conjuge_cpf', 'origem', 'indicante',
)} | {'observacoes': _s('divergencias entre as fontes, se houver')})


def _dna():
    if os.path.exists(DNA):
        with open(DNA, encoding='utf-8') as f:
            return f.read()
    return ''


def _chamar(modelo, sistema, conteudo, schema, max_tokens):
    return ia.json_por_schema(modelo, sistema, conteudo, schema, max_tokens)


def triagem(transcricao, texto_documentos='', cadastro=None):
    e = ESCRITORIO
    checklist = '\n'.join(f"- {d['id']}: {d['nome']}" for d in CHECKLIST_DOCUMENTOS)
    pontos = '\n'.join(f'- {p}' for p in PONTOS_ATENCAO)
    dna = _dna()
    sistema = f"""Voce e a analista juridica de triagem do {e['nome']} ({e['cidade']}/{e['uf']}), escritorio de DIREITO TRIBUTARIO (execucao fiscal e gestao de passivo) e PREVIDENCIARIO (calculos, planejamento e pareceres).

Seu trabalho substitui o preenchimento manual do RELATORIO DE TRIAGEM que o atendimento entrega ao advogado depois da reuniao de fechamento. O relatorio e o que permite montar a analise ou a peca sem precisar ligar de novo para o cliente. Pilar do escritorio: ANALISAR A ORIGEM DOS DEBITOS antes de qualquer medida.

Regras:
- Use somente o que esta na transcricao, nos documentos e no cadastro. Nunca invente CDA, numero de processo, valor, data, periodo, tributo ou nome. Sem dado, deixe o campo vazio e registre a lacuna em "gaps".
- Valores e datas como foram ditos; se foram aproximados na fala, diga que sao aproximados.
- "gatilhos" sao fatos que pedem acao rapida: prazo de defesa ou recurso correndo, citacao em execucao fiscal (embargos), bloqueio de valores, certidao negativa travando contrato ou licitacao, parcelamento prestes a ser rescindido, prescricao ou decadencia perto de se consumar, indeferimento recente no INSS com prazo de recurso.
- Em "debitos", liste cada debito que o cliente citou, separado. Em "teses_candidatas", liste so o que os FATOS relatados sustentam, com a prova que existe hoje. Tese sem fato e sem prova nao entra: entra em "gaps". Nao conclua que ha prescricao ou decadencia sem as datas-chave: pergunte.
- Responda cada ponto de atencao do fluxo do escritorio, nesta ordem:
{pontos}
- Em "documentos", classifique cada item do checklist do escritorio pelo que foi dito na reuniao:
{checklist}
- A estrategia e CANDIDATA: quem decide e o advogado que revisa (Dra. Faya ou Dr. William). Aponte o caminho que os fatos sustentam e o que ainda falta provar. Nao cite jurisprudencia nem sumula que nao esteja no material de referencia abaixo - se nao houver material, nao cite nenhuma.
- "trechos": ate 12 citacoes literais curtas da transcricao que sustentam os pontos principais.
- Escreva em portugues, linguagem formal, terceira pessoa, referindo-se ao cliente como "o Contribuinte" (tributario) ou "o Segurado" (previdenciario).
"""
    if dna:
        sistema += f'\n<referencia_do_escritorio>\nPadrao de pecas e teses do escritorio (extraido das pecas reais):\n{dna}\n</referencia_do_escritorio>\n'

    conteudo = f'<transcricao_reuniao>\n{transcricao}\n</transcricao_reuniao>'
    if texto_documentos:
        conteudo += f'\n\n<documentos_do_cliente>\n{texto_documentos}\n</documentos_do_cliente>'
    if cadastro:
        conteudo += f'\n\n<cadastro_do_atendimento>\n{json.dumps(cadastro, ensure_ascii=False, indent=1)}\n</cadastro_do_atendimento>'
    conteudo += '\n\nMonte o Relatorio de Triagem deste caso.'
    return _chamar(MODELO_TRIAGEM, sistema, conteudo, SCHEMA_TRIAGEM, 32000)


def qualificacao(transcricao, texto_documentos='', cadastro=None):
    sistema = """Voce extrai a qualificacao completa de um cliente (pessoa fisica ou o responsavel de uma empresa) para contrato, procuracao e declaracao.
Fontes e prioridade:
1. Documento oficial (CNH, RG, certidao, contrato social, cartao CNPJ): nome completo, CPF, RG e orgao emissor, data de nascimento, nacionalidade; para empresa, razao social e CNPJ em 'observacoes'.
2. Cadastro do atendimento: telefone, e-mail, endereco, estado civil, profissao, origem e indicante.
3. Transcricao da reuniao: so para o que nao estiver nas fontes acima.
Nunca invente. Campo sem fonte fica vazio. Nome sempre completo, como no documento. CPF no formato 000.000.000-00, data DD/MM/AAAA, CEP 00000-000, UF com 2 letras.
Se as fontes divergirem (ex.: nome diferente no cadastro e na CNH), use o documento oficial e explique em "observacoes"."""
    conteudo = f'<transcricao_reuniao>\n{transcricao[:60000]}\n</transcricao_reuniao>'
    if texto_documentos:
        conteudo += f'\n\n<documentos_do_cliente>\n{texto_documentos}\n</documentos_do_cliente>'
    if cadastro:
        conteudo += f'\n\n<cadastro_do_atendimento>\n{json.dumps(cadastro, ensure_ascii=False, indent=1)}\n</cadastro_do_atendimento>'
    dados = _chamar(MODELO_EXTRACAO, sistema, conteudo, SCHEMA_QUALIFICACAO, 4000)

    # o cadastro do Closer manda nos dados de contato (o modelo pode ter lido errado)
    for campo in ('telefone', 'email', 'estado_civil', 'profissao', 'origem', 'indicante'):
        if cadastro and cadastro.get(campo):
            dados[campo] = cadastro[campo]
    return validar(dados)


# ============================================================
# VALIDACOES
# ============================================================

def cpf_valido(cpf):
    n = re.sub(r'\D', '', cpf or '')
    if len(n) != 11 or n == n[0] * 11:
        return False
    for i in (9, 10):
        soma = sum(int(n[j]) * ((i + 1) - j) for j in range(i))
        dig = (soma * 10) % 11 % 10
        if dig != int(n[i]):
            return False
    return True


def validar(dados):
    avisos = []
    cpf = dados.get('cpf', '')
    if cpf:
        n = re.sub(r'\D', '', cpf)
        if cpf_valido(cpf):
            dados['cpf'] = f'{n[:3]}.{n[3:6]}.{n[6:9]}-{n[9:]}'
        else:
            avisos.append(f'CPF {cpf} nao confere (digito verificador)')
            dados['cpf'] = f'{cpf} [CONFERIR]'
    cep = re.sub(r'\D', '', dados.get('cep', ''))
    if cep:
        dados['cep'] = f'{cep[:5]}-{cep[5:]}' if len(cep) == 8 else f"{dados['cep']} [CONFERIR]"
    for campo in ('nome', 'cpf', 'rg', 'estado_civil', 'profissao', 'logradouro', 'cidade', 'uf', 'cep'):
        if not dados.get(campo):
            avisos.append(f'sem {campo}')
    if dados.get('nome') and len(dados['nome'].split()) < 2:
        avisos.append('nome parece incompleto')
        dados['nome'] = f"{dados['nome']} [CONFERIR]"
    dados['_avisos'] = avisos
    return dados
