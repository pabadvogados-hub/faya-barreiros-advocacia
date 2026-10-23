"""
Motor tributario - analise de passivo fiscal federal e consulta de legislacao.

    python TRIBUTARIO/main.py passivo "RAZAO SOCIAL" --cnpj 00.000.000/0001-00
    python TRIBUTARIO/main.py passivo "RAZAO SOCIAL" --pasta-docs "C:/caminho/dos/pdfs"
    python TRIBUTARIO/main.py passivo "RAZAO SOCIAL" --simular      (so mostra o que seria lido; nao chama a IA)
    python TRIBUTARIO/main.py legislacao "prescricao" [--sigla CTN]
    python TRIBUTARIO/main.py legislacao --listar

O `passivo` le os documentos do cliente (e-CAC, Regularize/PGFN, CDAs, extratos de parcelamento e
transacao, execucao fiscal, CAPAG) e gera o RELATORIO TECNICO-ESTRATEGICO de 16 secoes
(TRIBUTARIO/prompts/system_prompt_tributarista.md), em .md e .docx no timbrado, na pasta
`11 PECAS` do cliente. O relatorio SEMPRE sai para revisao da Dra. Faya e do Dr. William:
a automacao nao protocola e nao envia nada ao cliente.

Sem --pasta-docs, le as subpastas de situacao fiscal do cliente (04 a 09) em
PASTA_CLIENTES_RAIZ/TRIBUTARIO/NOME DO CLIENTE/.

Prospeccao de empresas devedoras (Dados Abertos da PGFN): ver TRIBUTARIO/prospeccao/LEIA-ME.md.
"""
import argparse
import os
import re
import sqlite3
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402

RAIZ = ambiente.RAIZ
sys.path.insert(0, os.path.join(RAIZ, 'CONTRATACAO'))
sys.path.insert(0, RAIZ)

AQUI = os.path.dirname(os.path.abspath(__file__))
PROMPT = os.path.join(AQUI, 'prompts', 'system_prompt_tributarista.md')
LEG_DB = os.path.join(AQUI, 'legislacao', 'legislacao_tributaria.db')
MODELO = os.getenv('MODELO_PECAS', 'claude-opus-5')
PASTAS_FISCAIS = ('04', '05', '06', '07', '08', '09')   # situacao fiscal ... contabil (config/escritorio.py)
MAX_CHARS_ARQUIVO = 120_000
MAX_CHARS_DOSSIE = 600_000
EXT_LEITURA = ('.pdf', '.txt', '.md', '.docx', '.jpg', '.jpeg', '.png', '.tif', '.tiff')


# ---------------------------------------------------------------- documentos

def arquivos_do_cliente(nome):
    import pasta_cliente as pc
    base = os.path.join(pc.raiz_clientes(), pc.PASTA_AREA, pc.nome_pasta(nome))
    if not os.path.isdir(base):
        raise SystemExit(f'Nao achei a pasta do cliente: {base}\n'
                         'Use --pasta-docs com a pasta dos PDFs, ou crie a pasta com CONTRATACAO/main.py novo.')
    achados = []
    for pasta, _, arqs in os.walk(base):
        rel = os.path.relpath(pasta, base).replace('\\', '/')
        partes = rel.split('/')
        if not any(p[:2] in PASTAS_FISCAIS and p[2:3] == ' ' for p in partes):
            continue
        for a in sorted(arqs):
            if a.lower().endswith(EXT_LEITURA):
                achados.append(os.path.join(pasta, a))
    return base, achados


def arquivos_da_pasta(pasta):
    pasta = os.path.abspath(os.path.expanduser(pasta))
    if not os.path.isdir(pasta):
        raise SystemExit(f'Pasta nao encontrada: {pasta}')
    achados = []
    for dp, _, arqs in os.walk(pasta):
        for a in sorted(arqs):
            if a.lower().endswith(EXT_LEITURA):
                achados.append(os.path.join(dp, a))
    return pasta, achados


def montar_dossie(arquivos, simular=False):
    from extrator import ler_arquivo
    blocos, resumo, total = [], [], 0
    for caminho in arquivos:
        nome = os.path.basename(caminho)
        if simular:
            resumo.append((nome, os.path.getsize(caminho), None))
            continue
        texto = (ler_arquivo(caminho) or '').strip()
        if len(texto) < 40:
            resumo.append((nome, os.path.getsize(caminho), 0))
            blocos.append(f'==================== {nome} ====================\n'
                          '[ARQUIVO SEM TEXTO LEGIVEL: provavelmente escaneado. Pedir versao em PDF pesquisavel '
                          'ou instalar o OCR (Tesseract).]')
            continue
        if len(texto) > MAX_CHARS_ARQUIVO:
            texto = texto[:MAX_CHARS_ARQUIVO] + '\n[... arquivo cortado por tamanho ...]'
        if total + len(texto) > MAX_CHARS_DOSSIE:
            blocos.append(f'==================== {nome} ====================\n[NAO LIDO: limite do dossie atingido]')
            resumo.append((nome, os.path.getsize(caminho), -1))
            continue
        total += len(texto)
        resumo.append((nome, os.path.getsize(caminho), len(texto)))
        blocos.append(f'==================== {nome} ====================\n{texto}')
    return '\n\n'.join(blocos), resumo


# ---------------------------------------------------------------- docx

def _inline(texto):
    return re.sub(r'\*\*(.+?)\*\*', r'\1', texto).replace('`', '')


def markdown_para_docx(texto, titulo_doc):
    import docx_escritorio as d
    doc = d.novo_documento('william')   # timbrado do Dr. William (area tributaria)
    d.titulo(doc, titulo_doc)
    linhas = texto.splitlines()
    i = 0
    while i < len(linhas):
        l = linhas[i].rstrip()
        s = l.strip()
        if not s:
            i += 1
            continue
        if s.startswith('|') and i + 1 < len(linhas) and set(linhas[i + 1].strip()) <= set('|-: '):
            cab = [_inline(c.strip()) for c in s.strip('|').split('|')]
            i += 2
            corpo = []
            while i < len(linhas) and linhas[i].strip().startswith('|'):
                corpo.append([_inline(c.strip()) for c in linhas[i].strip().strip('|').split('|')])
                i += 1
            corpo = [(r + [''] * len(cab))[:len(cab)] for r in corpo]
            d.tabela(doc, cab, corpo, tamanho=8)
            continue
        if s.startswith('#'):
            d.secao(doc, _inline(s.lstrip('#').strip()))
        elif re.match(r'^[-*]\s+', s):
            itens = []
            while i < len(linhas) and re.match(r'^\s*[-*]\s+', linhas[i]):
                itens.append(_inline(re.sub(r'^\s*[-*]\s+', '', linhas[i])))
                i += 1
            d.lista(doc, itens)
            continue
        elif s.startswith('>>>') or re.match(r'^-{3,}$', s):
            pass
        else:
            d.paragrafo(doc, _inline(s))
        i += 1
    return doc


# ---------------------------------------------------------------- comandos

def cmd_passivo(args):
    import ia
    if args.pasta_docs:
        base, arquivos = arquivos_da_pasta(args.pasta_docs)
        pasta_saida = args.saida or ambiente.pasta_saida('tributario', re.sub(r'[^\w ]+', '', args.cliente).strip() or 'cliente')
    else:
        base, arquivos = arquivos_do_cliente(args.cliente)
        pasta_saida = args.saida or os.path.join(base, '11 PECAS')
    if not arquivos:
        raise SystemExit('Nenhum documento (PDF, DOCX, TXT, imagem) encontrado nas pastas fiscais do cliente.')

    print(f'\n=== PASSIVO FISCAL: {args.cliente} ===')
    print(f'Pasta lida: {base}')
    dossie, resumo = montar_dossie(arquivos, simular=args.simular)
    print(f'{len(arquivos)} arquivo(s):')
    for nome, tam, chars in resumo:
        if chars is None:
            print(f'  - {nome}  ({tam / 1024:.0f} KB)')
        elif chars == 0:
            print(f'  - {nome}  SEM TEXTO (escaneado?)')
        elif chars < 0:
            print(f'  - {nome}  NAO LIDO (limite do dossie)')
        else:
            print(f'  - {nome}  {chars:,} caracteres')
    if args.simular:
        print('\nSimulacao: a IA nao foi chamada.')
        return

    sistema = open(PROMPT, encoding='utf-8').read()
    ref = ambiente.ler_base('DNA_PECAS.md').strip()
    if '<!-- DNA-ATIVO -->' in ref:
        sistema += f'\n<pecas_do_escritorio>\n{ref}\n</pecas_do_escritorio>\n'
    cab = f'CLIENTE: {args.cliente}' + (f'\nCNPJ: {args.cnpj}' if args.cnpj else '')
    conteudo = (f'{cab}\n\nA seguir, os documentos extraidos da pasta do cliente. Analise integralmente e elabore o '
                f'relatorio tecnico-estrategico completo no formato das 16 secoes obrigatorias.\n\n'
                f'==== DOSSIE DOCUMENTAL ====\n\n{dossie}')
    if args.instrucao:
        conteudo += f'\n\nInstrucao adicional da advogada: {args.instrucao}'

    print(f'\nGerando o relatorio com {args.modelo} ({len(dossie):,} caracteres de dossie)...')
    texto = ia.texto_longo(sistema, conteudo, modelo=args.modelo, max_tokens=48000)

    os.makedirs(pasta_saida, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M')
    nome = re.sub(r'[<>:"/\\|?*]', '', args.cliente).strip()
    md = os.path.join(pasta_saida, f'{nome} - Relatorio Passivo Fiscal - {stamp}.md')
    with open(md, 'w', encoding='utf-8') as f:
        f.write(texto)
    docx_caminho = md[:-3] + '.docx'
    markdown_para_docx(texto, f'Relatório técnico-estratégico · Passivo fiscal federal\n{args.cliente}').save(docx_caminho)

    print(f'\nRelatorio gravado:\n  {docx_caminho}\n  {md}')
    pend = texto.count('[CONFERIR')
    print(f'{pend} ponto(s) [CONFERIR] para a revisao.' if pend else 'Nenhum [CONFERIR] marcado: revisar assim mesmo.')
    print('Revisao: Dra. Faya e Dr. William. A automacao nao protocola nem envia ao cliente.')


def _siglas(con):
    return [r[0] for r in con.execute('select sigla from legislacao order by sigla')]


def cmd_legislacao(args):
    if not os.path.exists(LEG_DB):
        raise SystemExit(f'Base de legislacao nao encontrada: {LEG_DB}')
    con = sqlite3.connect(LEG_DB)
    if args.listar or not args.termo:
        for sigla, nome, n in con.execute('select sigla, nome, length(texto) from legislacao order by sigla'):
            print(f'{sigla:<8} {nome}  ({n:,} caracteres)')
        return
    termo = args.termo.lower()
    achou = 0
    for sigla, nome, texto in con.execute('select sigla, nome, texto from legislacao order by sigla'):
        if args.sigla and sigla.upper() != args.sigla.upper():
            continue
        baixo = texto.lower()
        pos = 0
        while achou < args.max:
            pos = baixo.find(termo, pos)
            if pos < 0:
                break
            ini, fim = max(0, pos - 220), min(len(texto), pos + 420)
            trecho = re.sub(r'\s+', ' ', texto[ini:fim])
            print(f'[{sigla}] ...{trecho}...\n')
            achou += 1
            pos = fim
    if not achou:
        print('Nada encontrado. Use --listar para ver as leis da base.')


def main():
    ap = argparse.ArgumentParser(description='Motor tributario', formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('passivo', help='relatorio de passivo fiscal federal (16 secoes)')
    p.add_argument('cliente')
    p.add_argument('--cnpj')
    p.add_argument('--pasta-docs', help='pasta com os PDFs (em vez da pasta do cliente)')
    p.add_argument('--saida', help='pasta de saida (padrao: 11 PECAS do cliente)')
    p.add_argument('--modelo', default=MODELO)
    p.add_argument('--instrucao', default='', help='orientacao extra para a IA')
    p.add_argument('--simular', action='store_true', help='lista os arquivos e nao chama a IA')
    p.set_defaults(func=cmd_passivo)

    l = sub.add_parser('legislacao', help='busca nas leis tributarias da base (CTN, LEF, Leis 10.522, 13.988...)')
    l.add_argument('termo', nargs='?')
    l.add_argument('--sigla')
    l.add_argument('--max', type=int, default=8)
    l.add_argument('--listar', action='store_true')
    l.set_defaults(func=cmd_legislacao)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
