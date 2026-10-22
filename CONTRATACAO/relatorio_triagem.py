"""
Relatorio de Triagem (Closer -> Gestor Juridico), no timbrado do escritorio.
E o documento guia da fase de contratacao: os demais documentos saem dos dados dele.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402,F401  (carrega .env e caminhos)
from datetime import datetime

from docx.shared import Pt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_escritorio import CONFERIR, lista, novo_documento, paragrafo, secao, tabela, titulo  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from config.escritorio import CHECKLIST_DOCUMENTOS  # noqa: E402


def _v(valor):
    return valor if valor not in (None, '') else CONFERIR


def endereco_completo(q):
    partes = [q.get('logradouro', ''), q.get('numero', ''), q.get('bairro', '')]
    cidade = '/'.join(x for x in (q.get('cidade', ''), q.get('uf', '')) if x)
    txt = ', '.join(x for x in partes if x)
    if cidade:
        txt += f', {cidade}'
    if q.get('cep'):
        txt += f', CEP {q["cep"]}'
    return txt.strip(', ') or CONFERIR


def gerar(caminho, triagem, qualif, prazos, status_docs):
    doc = novo_documento()
    titulo(doc, 'Relatório de Triagem')
    paragrafo(doc, 'Fase de contratação · documento interno do atendimento para a Dra. Faya e o Dr. William',
              tamanho=10).alignment = 1

    paragrafo(doc, _v(qualif.get('nome')), rotulo='Cliente')
    paragrafo(doc, triagem.get('data_reuniao') or CONFERIR, rotulo='Reunião de fechamento')
    paragrafo(doc, triagem.get('closer') or CONFERIR, rotulo='Atendimento')
    paragrafo(doc, datetime.now().strftime('%d/%m/%Y %H:%M'), rotulo='Gerado em')

    # 1. Gatilhos primeiro: e o que o advogado precisa ver antes de tudo
    secao(doc, '1. Gatilhos (o que exige ação rápida)')
    gat = triagem.get('gatilhos') or []
    if gat:
        ordem = {'ALTA': 0, 'MEDIA': 1, 'BAIXA': 2}
        gat = sorted(gat, key=lambda g: ordem.get(g.get('gravidade'), 3))
        tabela(doc, ['Gravidade', 'Gatilho', 'Detalhe'],
               [[g.get('gravidade'), g.get('gatilho'), g.get('detalhe')] for g in gat], [2.2, 5, 8.5])
    else:
        paragrafo(doc, 'Nenhum gatilho identificado na reunião. Confirmar vencimentos no onboarding.')

    secao(doc, '2. Prazos do caso')
    tabela(doc, ['Marco', 'Data limite', 'Responsável'],
           [[p['marco'], p['data'], p['responsavel']] for p in prazos], [7.5, 3.5, 4.7])

    secao(doc, '3. Resumo do caso')
    for par in (triagem.get('resumo_caso') or CONFERIR).split('\n'):
        if par.strip():
            paragrafo(doc, par.strip(), recuo=True)
    c = triagem.get('contribuinte') or {}
    tabela(doc, ['Cliente', 'CNPJ/CPF', 'Regime', 'Atividade', 'Porte', 'Situação'],
           [[c.get('nome'), c.get('documento'), c.get('regime'), c.get('atividade'),
             c.get('porte'), c.get('situacao')]], tamanho=8)
    if c.get('socios_responsaveis'):
        paragrafo(doc, c['socios_responsaveis'], rotulo='Sócios / responsáveis')

    secao(doc, '4. Débitos e sua origem')
    debitos = triagem.get('debitos') or []
    if debitos:
        tabela(doc, ['CDA / processo', 'Tributo', 'Ente', 'Período', 'Valor (aprox.)', 'Fase', 'Origem'],
               [[d.get('identificacao'), d.get('tributo'), d.get('ente'), d.get('periodo'),
                 d.get('valor_aproximado'), d.get('fase'), d.get('origem')] for d in debitos],
               [2.6, 2.2, 2.0, 2.2, 2.2, 2.2, 2.6], tamanho=8)
    else:
        paragrafo(doc, 'Débitos não detalhados na reunião. [CONFERIR] antes da análise: relatório de situação '
                       'fiscal (e-CAC/PGFN), CDAs e processos administrativos.')
    ef = triagem.get('execucao_fiscal') or {}
    if ef.get('existe') == 'SIM':
        tabela(doc, ['Nº do processo', 'Vara / foro', 'Fase', 'Garantia / constrição'],
               [[ef.get('numero'), ef.get('vara_foro'), ef.get('fase'), ef.get('garantia')]], tamanho=8)
    if triagem.get('parcelamentos'):
        paragrafo(doc, triagem['parcelamentos'], rotulo='Parcelamentos e transações')
    pv = triagem.get('previdenciario') or {}
    if any(pv.values()):
        paragrafo(doc, ' ', rotulo='Previdenciário')
        tabela(doc, ['Benefício', 'Situação no INSS', 'Tempo de contribuição', 'Vínculos e provas'],
               [[pv.get('beneficio'), pv.get('situacao_inss'), pv.get('tempo_contribuicao'),
                 pv.get('vinculos_e_provas')]], tamanho=8)

    secao(doc, '5. Teses candidatas')
    verbas = triagem.get('teses_candidatas') or []
    if verbas:
        tabela(doc, ['Força', 'Tese', 'O que sustenta', 'Prova disponível'],
               [[x.get('forca'), x.get('tese'), x.get('fundamento_fatico'), x.get('prova_disponivel')]
                for x in verbas], [1.8, 3.6, 5.3, 5], tamanho=8)
    else:
        paragrafo(doc, 'Nenhuma tese sustentada pelos fatos relatados até aqui. [CONFERIR] na revisão.')

    if triagem.get('linha_do_tempo'):
        paragrafo(doc, ' ', rotulo='Linha do tempo do caso')
        tabela(doc, ['Quando', 'O que aconteceu'],
               [[t.get('data'), t.get('evento')] for t in triagem['linha_do_tempo']], [3.5, 12.2])

    secao(doc, '6. Pontos de atenção do fluxo')
    tabela(doc, ['Ponto', 'Resposta', 'Base'],
           [[p.get('ponto'), p.get('resposta'), p.get('evidencia')] for p in triagem.get('pontos_atencao') or []],
           [6, 2.5, 7.2])

    secao(doc, '7. Gaps (o que falta para seguir)')
    lista(doc, triagem.get('gaps') or ['Nenhum gap apontado.'])

    secao(doc, '8. Checklist de documentos')
    tabela(doc, ['Documento', 'Situação', 'Observação'],
           [[s['nome'], s['situacao'], s.get('observacao', '')] for s in status_docs], [6.5, 3, 6.2])

    secao(doc, '9. Estratégia candidata (quem decide é a advogada que revisa)')
    est = triagem.get('estrategia_candidata') or {}
    for rotulo, chave in (('Ação', 'acao'), ('Órgão / foro', 'orgao_foro'), ('Rito', 'rito'),
                          ('Tutela de urgência', 'tutela_urgencia'), ('Prova a produzir', 'prova_a_produzir'),
                          ('Valor envolvido (estimado)', 'valor_estimado'), ('Observação', 'observacao')):
        if est.get(chave):
            paragrafo(doc, est[chave], rotulo=rotulo)

    secao(doc, '10. Riscos e pontos fortes')
    if triagem.get('riscos'):
        paragrafo(doc, ' ', rotulo='Riscos')
        lista(doc, triagem['riscos'])
    if triagem.get('pontos_fortes'):
        paragrafo(doc, ' ', rotulo='Pontos fortes')
        lista(doc, triagem['pontos_fortes'])

    secao(doc, '11. Perguntas que ficaram em aberto')
    lista(doc, triagem.get('perguntas_onboarding') or ['Confirmar datas de constituição dos débitos e prazos em curso.'])

    h = triagem.get('honorarios') or {}
    if any(h.values()):
        secao(doc, '12. Honorários combinados (para o Financeiro)')
        for rotulo, chave in (('Entrada', 'entrada'), ('Pagamento', 'parcelas'), ('Êxito', 'exito'), ('Observação', 'observacao')):
            if h.get(chave):
                paragrafo(doc, h[chave], rotulo=rotulo)

    if triagem.get('trechos'):
        secao(doc, 'Trechos da reunião')
        for t in triagem['trechos']:
            paragrafo(doc, f"“{t.get('trecho', '')}”", rotulo=t.get('tema', ''), tamanho=10, espaco=1.15)

    avisos = qualif.get('_avisos') or []
    if avisos:
        secao(doc, 'Conferir antes de gerar os documentos')
        lista(doc, avisos)

    p = paragrafo(doc, 'Relatório gerado pela IA a partir da reunião de fechamento. PRONTO PARA REVISÃO DO GESTOR '
                       'JURÍDICO. A IA não decide a estratégia e não protocola nada.',
                  negrito=True, tamanho=10)
    p.paragraph_format.space_before = Pt(18)
    doc.save(caminho)
    return caminho


def status_documentos(triagem, arquivos_por_item):
    """Junta o que foi dito na reuniao com o que ja esta na pasta do cliente."""
    dito = {d.get('id'): d for d in triagem.get('documentos') or []}
    saida = []
    for item in CHECKLIST_DOCUMENTOS:
        na_pasta = arquivos_por_item.get(item['id'], [])
        if na_pasta:
            situacao, obs = 'NA PASTA', ', '.join(na_pasta[:3])
        else:
            d = dito.get(item['id'], {})
            situacao = d.get('status') or 'NAO FALADO'
            obs = d.get('observacao', '')
        if not item.get('obrigatorio') and situacao in ('NAO TEM', 'NAO FALADO'):
            situacao = 'SE HOUVER'
        saida.append({'id': item['id'], 'nome': item['nome'], 'situacao': situacao, 'observacao': obs,
                      'obrigatorio': item.get('obrigatorio', False), 'sensivel': item.get('sensivel', False)})
    return saida
