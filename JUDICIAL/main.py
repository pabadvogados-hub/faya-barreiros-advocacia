"""
Judicial - da pasta pronta ate a minuta (ou o relatorio) na mesa da advogada.

    python JUDICIAL/main.py checklist "NOME DO CLIENTE"
    python JUDICIAL/main.py peca  "NOME DO CLIENTE" --tipo relatorio-cda
    python JUDICIAL/main.py peca  --exemplo --tipo recurso-administrativo
    python JUDICIAL/main.py tipos

Tipos de peca (os que o briefing pediu: recursos administrativos e judiciais no tributario;
pareceres e relatorios no previdenciario):
    relatorio-cda               analise da origem dos debitos: CDAs, fato gerador, prescricao, decadencia, nulidades
    recurso-administrativo      manifestacao de inconformidade / recurso voluntario (DRJ, CARF, orgaos estaduais e municipais)
    embargos-execucao           embargos a execucao fiscal (Lei 6.830/80)
    excecao-pre-executividade   excecao de pre-executividade
    peticao-andamento           peticao simples de andamento (prazo, juntada, manifestacao)
    parecer-previdenciario      parecer consultivo / relatorio de planejamento previdenciario
    peticao-inicial-previdenciaria   inicial contra o INSS/JEF (concessao, revisao, BPC, pensao, incapacidade)
    relatorio-previdenciario    conferencia de tempo e de RMI, analise de revisao, recalculo (relatorio da Dra. Faya)
    acao-declaratoria-tributaria     acao declaratoria/anulatoria com tutela (ISS, ITBI, IPTU, ICMS, multa, CDA)
    prescricao-intercorrente    pedido de reconhecimento da prescricao intercorrente (administrativo ou judicial)

A peca NUNCA e protocolada pela automacao e NUNCA sai do escritorio: ela e gravada na pasta do
cliente (11 PECAS) para a revisao da Dra. Faya e do Dr. William.
Regra de ouro do briefing: a IA so decide a estrategia sozinha em casos simples e padronizados e
em peticoes de andamento. Todo o resto sai para revisao.

TRAVA DO DNA: a peca so sai sem o aviso de ESTRUTURA PROVISORIA quando BASE_CONHECIMENTO/DNA_PECAS.md
tem o marcador DNA-ATIVO (ativo desde 23/10/2026, a partir das pecas-modelo da Dra. Faya e do Dr. William).
Jurisprudencia: so a da secao 5 do DNA; o resto sai com [CONFERIR: jurisprudencia].
"""
import argparse
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402

import ia  # noqa: E402

sys.path.insert(0, ambiente.RAIZ)
sys.path.insert(0, os.path.join(ambiente.RAIZ, 'CONTRATACAO'))
from config.escritorio import CHECKLIST_DOCUMENTOS, ESCRITORIO, SOCIO, TITULAR  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tipos_modelo import TIPOS_PREV_E_TRIB  # noqa: E402

MODELO = os.getenv('MODELO_PECAS', 'claude-opus-5')
AVISO_PROVISORIO = (
    '>>> ESTRUTURA PROVISORIA <<<\n'
    'Esta peca foi montada SEM as pecas-modelo do escritorio (BASE_CONHECIMENTO/DNA_PECAS.md sem pecas reais).\n'
    'Ela traz os fatos e os pedidos organizados, mas NAO tem o estilo nem a jurisprudencia do escritorio.\n'
    'Mande 2 ou 3 pecas suas (uma da Dra. Faya e uma do Dr. William) conforme docs/ONBOARDING.md e a proxima ja sai com a sua cara.\n'
)

# Estilo declarado no briefing. Vale mesmo antes das pecas-modelo chegarem.
ESTILO_FAYA = (
    'Dra. Faya: estrutura peticoes e relatorios em TOPICOS, de forma organizada, com QUADROS e TABELAS e com '
    'imagens/recortes dos documentos apresentados na instrucao. Tom formal e direto.'
)
ESTILO_WILLIAM = (
    'Dr. William: relatorios e analises com imagens e dados das CDAs; argumentacao TECNICA, centrada no fato '
    'gerador e na letra da lei, sem interpretacao subjetiva. Tom didatico quando a peca e para o cliente.'
)

TIPOS = {
    'relatorio-cda': {
        'titulo': 'RELATORIO DE ANALISE DE ORIGEM DOS DEBITOS',
        'autor': ESTILO_WILLIAM, 'advogado': 'william',
        'estrutura': (
            'I - IDENTIFICACAO DO CONTRIBUINTE E DOS DEBITOS (quadro: CDA/inscricao, tributo, periodo, valor original, '
            'valor atual, situacao)\n'
            'II - ORIGEM DE CADA DEBITO (fato gerador, base legal, forma de constituicao do credito)\n'
            'III - ANALISE DE DECADENCIA E PRESCRICAO (datas-chave de cada debito, causas de suspensao/interrupcao '
            'que constem dos documentos)\n'
            'IV - NULIDADES E VICIOS FORMAIS (requisitos da CDA, motivacao, notificacao)\n'
            'V - SITUACAO DE PARCELAMENTOS E TRANSACOES (o que existe e o que cabe)\n'
            'VI - CONCLUSAO E CAMINHOS POSSIVEIS (defesa, transacao, parcelamento), sem decidir pelo cliente'),
    },
    'recurso-administrativo': {
        'titulo': 'RECURSO ADMINISTRATIVO',
        'autor': ESTILO_WILLIAM, 'advogado': 'william',
        'estrutura': (
            'I - ENDERECAMENTO E QUALIFICACAO\nII - TEMPESTIVIDADE\nIII - SINTESE DO PROCESSO E DA DECISAO RECORRIDA\n'
            'IV - PRELIMINARES (nulidades, decadencia, prescricao)\nV - MERITO (fato gerador, base de calculo, '
            'legislacao aplicavel)\nVI - PEDIDOS'),
    },
    'embargos-execucao': {
        'titulo': 'EMBARGOS A EXECUCAO FISCAL',
        'autor': ESTILO_WILLIAM, 'advogado': 'william',
        'estrutura': (
            'I - ENDERECAMENTO E QUALIFICACAO\nII - TEMPESTIVIDADE E GARANTIA DO JUIZO\nIII - SINTESE DA EXECUCAO\n'
            'IV - PRELIMINARES E NULIDADES DA CDA\nV - PRESCRICAO, DECADENCIA E MERITO\nVI - EFEITO SUSPENSIVO '
            '(se cabivel)\nVII - PEDIDOS E PROVAS'),
    },
    'excecao-pre-executividade': {
        'titulo': 'EXCECAO DE PRE-EXECUTIVIDADE',
        'autor': ESTILO_WILLIAM, 'advogado': 'william',
        'estrutura': (
            'I - CABIMENTO (materia cognoscivel de oficio e prova pre-constituida)\nII - SINTESE DA EXECUCAO\n'
            'III - DA MATERIA ARGUIDA (prescricao, decadencia, nulidade da CDA, ilegitimidade etc., so o que a '
            'prova dos autos sustenta)\nIV - PEDIDOS'),
    },
    'peticao-andamento': {
        'titulo': 'PETICAO',
        'autor': ESTILO_FAYA, 'advogado': 'faya',
        'estrutura': 'Peca curta e objetiva: enderecamento, referencia ao ato, requerimento claro, fecho.',
    },
    'parecer-previdenciario': {
        'titulo': 'PARECER / RELATORIO PREVIDENCIARIO',
        'autor': ESTILO_FAYA, 'advogado': 'faya',
        'estrutura': (
            'I - DADOS DO SEGURADO E OBJETO DA CONSULTA\nII - HISTORICO CONTRIBUTIVO (quadro com vinculos, '
            'periodos, tempo de contribuicao, carencia - a partir do CNIS e da CTPS)\nIII - REGRAS APLICAVEIS '
            '(direito adquirido, regras de transicao da EC 103/2019, Lei 8.213/91, Decreto 3.048/99, IN 128/2022)\n'
            'IV - SIMULACOES/CENARIOS (so com dados dos documentos; calculo de RMI so se houver planilha)\n'
            'V - CONCLUSAO E RECOMENDACAO'),
    },
}

TIPOS.update(TIPOS_PREV_E_TRIB)   # tipos montados a partir das pecas-modelo (JUDICIAL/tipos_modelo.py)


def dna():
    return ambiente.ler_base('DNA_PECAS.md').strip()


def tem_pecas_reais():
    """O DNA so conta como completo quando alguem colou as pecas reais e ativou o marcador DNA-ATIVO."""
    return '<!-- DNA-ATIVO -->' in dna()


def caso_do_cliente(nome):
    import pasta_cliente as pc
    caso = None
    for area in dict.fromkeys([pc.PASTA_AREA, *pc.PASTA_AREAS.values()]):   # tributario e previdenciario
        base = os.path.join(pc.raiz_clientes(), area, pc.nome_pasta(nome))
        caso = pc.ler_caso(base)
        if caso:
            break
    if not caso:
        raise SystemExit(f'Nao achei o caso.json em {pc.caminho_caso(base)}.\n'
                         'Rode antes: python CONTRATACAO/main.py novo ...')
    return base, caso


def cmd_tipos(_args):
    for k, v in TIPOS.items():
        print(f'{k:<28} {v["titulo"]}')


def cmd_checklist(args):
    base, caso = caso_do_cliente(args.cliente)
    triagem = caso.get('triagem') or {}
    status = {d['id']: d.get('status') for d in (triagem.get('documentos') or [])}
    print(f"\nCHECKLIST - {caso.get('qualificacao', {}).get('nome', args.cliente)}")
    print('=' * 72)
    faltam = []
    for d in CHECKLIST_DOCUMENTOS:
        st = status.get(d['id'], 'NAO FALADO')
        marca = 'ok ' if st == 'JA ENTREGOU' else '-- '
        if st != 'JA ENTREGOU' and d['obrigatorio']:
            faltam.append(d['nome'])
        print(f"{marca}{d['nome']:<70} {st}")
    print()
    if faltam:
        print(f'FALTAM {len(faltam)} documento(s) obrigatorio(s) antes de montar a analise:')
        for f in faltam:
            print(f'  - {f}')
    else:
        print('Documentacao completa. Pode gerar a peca:')
        print(f'  python JUDICIAL/main.py peca "{args.cliente}" --tipo relatorio-cda')
    print()


def sistema_da_peca(tipo):
    t = TIPOS[tipo]
    return f"""Voce redige a minuta de {t['titulo']} para o {ESCRITORIO['nome']} ({ESCRITORIO['cidade']}/{ESCRITORIO['uf']}),
escritorio de Direito Tributario (execucao fiscal e gestao de passivo) e Previdenciario.
Advogados que revisam e assinam: {TITULAR['nome']} e {SOCIO['nome']}.

Pilar do escritorio: ANALISAR A ORIGEM DOS DEBITOS antes de qualquer medida. Resultados que o escritorio
busca: reduzir juros e multas, alterar a CAPAG, destravar parcelamentos e extinguir debitos por decadencia,
prescricao e nulidades.

Estilo declarado pelo escritorio: {t['autor']}
Linguagem tecnico-juridica, sem excesso de formalismo e sem latim; pecas objetivas, narracao clara dos fatos e
subsuncao dos fatos ao direito.

Estrutura obrigatoria:
{t['estrutura']}

Regras inviolaveis:
- Use SOMENTE os fatos do relatorio de triagem, da qualificacao e dos documentos. Nunca invente CDA, valor, data,
  numero de processo, tributo ou periodo. Faltou dado? escreva [CONFERIR: o que falta] no lugar.
- Nao invente jurisprudencia, sumula, tema repetitivo ou numero de lei. Cite apenas o que estiver no material de
  referencia do escritorio ou for dispositivo de lei que voce tem certeza (CTN, Lei 6.830/80, Lei 8.213/91, Lei 8.212/91,
  EC 103/2019, Decreto 3.048/99). Sem material: nao cite jurisprudencia e escreva [CONFERIR: jurisprudencia] no topico.
- Datas de prescricao e decadencia: so calcule quando as datas-chave estiverem nos documentos; mostre a conta em quadro.
  Se faltar a data, [CONFERIR: data].
- Nao calcule valor de condenacao, de RMI ou de debito atualizado sem planilha: escreva [CONFERIR: calculo].
- Onde couber quadro ou tabela, monte em Markdown. Onde a prova e imagem (recorte de CDA, tela do e-CAC),
  deixe o marcador [INSERIR IMAGEM: o que mostrar].
"""


def cmd_peca(args):
    if args.tipo not in TIPOS:
        raise SystemExit(f'Tipo invalido. Opcoes: {", ".join(TIPOS)}')
    if args.exemplo:
        caso = {
            'qualificacao': {'nome': 'EMPRESA EXEMPLO COMERCIO LTDA', 'cpf': '00.000.000/0001-00',
                             'profissao': 'comercio varejista', 'cidade': 'Salvador', 'uf': 'BA'},
            'triagem': {
                'resumo_caso': 'Empresa com duas inscricoes em divida ativa da PGFN e uma execucao fiscal em curso.',
                'debitos': [
                    {'cda': '00 0 00 000000-00', 'tributo': 'Simples Nacional', 'periodo': '2017-2018',
                     'valor_original': 'R$ 48.000,00', 'origem': 'declaracao entregue e nao paga (PGDAS)'},
                    {'cda': '00 6 00 000000-00', 'tributo': 'IRPJ', 'periodo': '2016',
                     'valor_original': 'R$ 22.500,00', 'origem': 'lancamento de oficio, notificacao em 03/2018'},
                ],
                'gaps': ['Data da notificacao do segundo debito nao confirmada', 'Sem balancete do ultimo exercicio'],
            },
        }
        base = ambiente.pasta_saida('exemplo')
    else:
        base, caso = caso_do_cliente(args.cliente)

    referencia = dna()
    sistema = sistema_da_peca(args.tipo)
    if tem_pecas_reais():
        sistema += f'\n<pecas_do_escritorio>\n{referencia}\n</pecas_do_escritorio>\n'
    else:
        sistema += ('\nNAO ha pecas reais do escritorio no DNA. Nao cite nenhuma jurisprudencia '
                    'e deixe [CONFERIR: jurisprudencia] em cada topico do direito.\n')

    conteudo = ('<qualificacao>\n' + json.dumps(caso.get('qualificacao', {}), ensure_ascii=False, indent=1) +
                '\n</qualificacao>\n\n<relatorio_de_triagem>\n' +
                json.dumps(caso.get('triagem', {}), ensure_ascii=False, indent=1) +
                f'\n</relatorio_de_triagem>\n\nRedija a minuta: {TIPOS[args.tipo]["titulo"]}.')
    if args.instrucao:
        conteudo += f'\n\nInstrucao adicional da advogada: {args.instrucao}'

    print('Gerando a minuta (pode levar alguns minutos)...\n')
    texto = ia.texto_longo(sistema, conteudo, modelo=MODELO, max_tokens=32000)
    if not tem_pecas_reais():
        texto = AVISO_PROVISORIO + '\n' + texto

    pasta = base if args.exemplo else os.path.join(base, '11 PECAS')
    os.makedirs(pasta, exist_ok=True)
    nome = f"{args.tipo}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
    destino = os.path.join(pasta, nome)
    with open(destino, 'w', encoding='utf-8') as f:
        f.write(texto)
    print(f'Minuta gravada em:\n  {destino}\n')
    pendencias = texto.count('[CONFERIR')
    if pendencias:
        print(f'{pendencias} ponto(s) marcado(s) com [CONFERIR] para a revisao.')
    print(f'Revisao: {TITULAR["nome"]} e {SOCIO["nome"]}. A automacao nao protocola.')


def main():
    ap = argparse.ArgumentParser(description='Judicial', formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sub = ap.add_subparsers(dest='comando', required=True)

    t = sub.add_parser('tipos', help='lista os tipos de peca')
    t.set_defaults(func=cmd_tipos)

    c = sub.add_parser('checklist', help='o que falta para montar a analise/peca')
    c.add_argument('cliente')
    c.set_defaults(func=cmd_checklist)

    p = sub.add_parser('peca', help='minuta de peca ou relatorio')
    p.add_argument('cliente', nargs='?')
    p.add_argument('--tipo', required=True, help='ver "tipos"')
    p.add_argument('--instrucao', default='', help='orientacao extra para a IA')
    p.add_argument('--exemplo', action='store_true')
    p.set_defaults(func=cmd_peca)

    args = ap.parse_args()
    if args.comando == 'peca' and not args.exemplo and not args.cliente:
        raise SystemExit('Informe o nome do cliente, ou use --exemplo.')
    args.func(args)


if __name__ == '__main__':
    main()
