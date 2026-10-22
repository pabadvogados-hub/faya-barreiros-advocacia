"""
Funil do comercial em arquivo local (SAIDA/funil.json).

Existe para o escritorio nao depender do CRM proprio (que o Gabriel ainda esta
construindo) para comecar a operar. Quando o CRM estiver pronto, este arquivo vira
a fonte da importacao - as etapas ja sao as mesmas do Kanban combinado na reuniao
de 07/10/2026.

Regra do escritorio: as colunas REVISAO e INICIAL ficam vazias. Conferencia diaria
pela manha; nada de prazo longo parado no quadro.
"""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402

ETAPAS = ['LEAD', 'LIGACAO', 'PROPOSTA', 'CONTRATO ENVIADO', 'ASSINADO',
          'DOCUMENTOS', 'INICIAL', 'REVISAO', 'PROTOCOLADO', 'PERDIDO']
COLUNAS_QUE_FICAM_VAZIAS = ('INICIAL', 'REVISAO')

ARQUIVO = os.path.join(ambiente.SAIDA, 'funil.json')


def _ler():
    try:
        with open(ARQUIVO, encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _gravar(leads):
    os.makedirs(os.path.dirname(ARQUIVO), exist_ok=True)
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)


def _agora():
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def registrar(nome, telefone, etapa='LEAD', **extra):
    etapa = etapa.upper()
    if etapa not in ETAPAS:
        raise SystemExit(f'Etapa invalida. Use uma de: {", ".join(ETAPAS)}')
    leads = _ler()
    chave = ''.join(c for c in str(telefone) if c.isdigit())
    for l in leads:
        if l['telefone'] == chave:
            l['etapa'] = etapa
            l['atualizado'] = _agora()
            l.setdefault('historico', []).append({'etapa': etapa, 'quando': _agora()})
            l.update({k: v for k, v in extra.items() if v})
            _gravar(leads)
            return l, False
    novo = {'nome': nome, 'telefone': chave, 'etapa': etapa, 'criado': _agora(),
            'atualizado': _agora(), 'historico': [{'etapa': etapa, 'quando': _agora()}], **extra}
    leads.append(novo)
    _gravar(leads)
    return novo, True


def painel():
    leads = _ler()
    if not leads:
        print('Funil vazio. Registre o primeiro lead:\n'
              '  python COMERCIAL/main.py lead "Nome" 47999999999')
        return
    print(f'\nFUNIL DO COMERCIAL  ({len(leads)} leads)')
    print('=' * 72)
    for etapa in ETAPAS:
        do_etapa = [l for l in leads if l['etapa'] == etapa]
        if not do_etapa and etapa not in COLUNAS_QUE_FICAM_VAZIAS:
            continue
        marca = '  <- deve ficar vazia' if etapa in COLUNAS_QUE_FICAM_VAZIAS and do_etapa else ''
        print(f'\n{etapa} ({len(do_etapa)}){marca}')
        for l in do_etapa:
            print(f"   {l['nome']:<28} {l['telefone']:<14} desde {l['atualizado']}")
    travadas = [l for l in leads if l['etapa'] in COLUNAS_QUE_FICAM_VAZIAS]
    if travadas:
        print(f'\nATENCAO: {len(travadas)} caso(s) parado(s) em coluna que deveria estar vazia. '
              'Conferencia da manha.')
    print()
