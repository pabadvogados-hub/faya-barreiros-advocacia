"""
Textos que vao para o cliente pelo WhatsApp (D-API).
Linguagem simples, direta e empatica, sem juridiques e sem formalismo excessivo.
Mensagem curta; termos tecnicos (PGFN, e-CAC, divida ativa) vem com uma explicacao de uma linha.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402,F401  (carrega .env e caminhos)

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from config.escritorio import ESCRITORIO  # noqa: E402

ASSINATURA = ESCRITORIO['nome']

COMO_MANDAR = {
    'pessoais': 'foto do RG ou da CNH (frente e verso) do responsável e dos sócios',
    'empresa': 'o contrato social com as alterações e o cartão do CNPJ',
    'endereco': 'um comprovante de endereço recente (conta de luz, água ou telefone)',
    'situacao_fiscal': ('o relatório de situação fiscal da empresa (no e-CAC, em "Certidões e Situação Fiscal") '
                        'e a consulta de dívida ativa no portal Regularize, da PGFN'),
    'cdas': 'as CDAs (certidões de dívida ativa), autos de infração, notificações e cartas que a empresa recebeu',
    'execucao': 'se já existe processo de execução fiscal: a citação, a petição inicial e as decisões',
    'parcelamentos': 'os extratos e termos de parcelamentos ou transações que a empresa já fez, e as guias pagas',
    'declaracoes': 'as declarações dos últimos anos (DCTF, PGDAS, SPED, DEFIS/DASN, ECF, conforme o regime)',
    'contabil': 'os balanços ou balancetes mais recentes e o faturamento dos últimos 12 meses',
    'cnis': 'o extrato CNIS (aplicativo Meu INSS), a carteira de trabalho e, se tiver, PPP/LTCAT e cartas do INSS',
    'procuracao': 'a procuração assinada (pelo link que mandamos)',
}


def primeiro_nome(nome):
    return (nome or '').split(' ')[0].title() or 'tudo bem'


def lista_faltando(faltando):
    linhas = []
    for i, item in enumerate(faltando, 1):
        if item.get('sensivel'):
            linhas.append(f"{i}. {item['nome']}: não mande por mensagem, a gente pega com você por ligação")
        else:
            linhas.append(f"{i}. {COMO_MANDAR.get(item['id'], item['nome'])}")
    return '\n'.join(linhas)


def assinatura_e_documentos(nome, links, faltando):
    txt = f'Olá, {primeiro_nome(nome)}! Aqui é do {ASSINATURA}.\n\n'
    txt += 'Seus documentos já estão prontos para assinar pelo celular:\n'
    for l in links:
        txt += f"\n{l['documento']}: {l['link']}"
    if faltando:
        txt += ('\n\nPara a gente montar a sua ação, precisamos destes documentos '
                '(pode mandar foto por aqui mesmo):\n\n' + lista_faltando(faltando))
    txt += '\n\nQualquer dúvida, é só responder esta mensagem.'
    return txt


def cobranca_documentos(nome, faltando, toque):
    nome = primeiro_nome(nome)
    if toque == 1:
        abertura = f'Olá, {nome}! Aqui é do {ASSINATURA}. Para darmos andamento no seu caso, ainda faltam:'
    elif toque == 2:
        abertura = (f'{nome}, tudo bem? Seu caso está parado esperando só estes documentos. '
                    'Assim que chegarem, a gente começa a análise:')
    else:
        abertura = (f'{nome}, sem estes documentos a gente não consegue analisar de onde vieram os débitos '
                    'e o que pode ser feito. Se estiver difícil conseguir algum, responde aqui que a gente ajuda:')
    return f'{abertura}\n\n{lista_faltando(faltando)}\n\nPode mandar foto por aqui mesmo.'


def documentos_completos(nome):
    return (f'{primeiro_nome(nome)}, recebemos todos os documentos. Obrigado! Agora o seu caso segue para a '
            f'equipe jurídica e em breve você recebe as novidades por aqui.\n\n{ASSINATURA}')
