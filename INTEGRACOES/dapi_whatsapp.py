"""
WhatsApp pela D-API (api.d-api.cloud) - canal proprio do escritorio.

O escritorio contrata a propria instancia (cerca de R$ 90/mes) e coloca no config/.env:

    DAPI_SESSION=NOME-DA-SESSAO
    DAPI_TOKEN=...

Nada e enviado sem essas duas variaveis preenchidas: as funcoes devolvem
(False, {'erro': 'D-API nao configurada'}) e quem chamou avisa na tela.

Uso:
    from dapi_whatsapp import enviar_texto, enviar_documento
    ok, resp = enviar_texto('47988068764', 'Bom dia!')

Teste rapido da linha:
    python INTEGRACOES/dapi_whatsapp.py status
    python INTEGRACOES/dapi_whatsapp.py teste 47988068764
"""
import base64
import os
import re
import sys

import requests

BASE = 'https://api.d-api.cloud/api/v1'
TIMEOUT = 30

MIME = {
    'pdf': 'application/pdf',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'doc': 'application/msword',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
    'mp4': 'video/mp4', 'ogg': 'audio/ogg',
}


# ------------------------------------------------------------------ credenciais

def _cred():
    sessao = (os.getenv('DAPI_SESSION') or '').strip()
    token = (os.getenv('DAPI_TOKEN') or '').strip()
    if not sessao or not token or 'AQUI' in (sessao + token).upper():
        return '', ''
    return sessao, token


def configurada():
    return all(_cred())


# ------------------------------------------------------------------ destino

def destino(telefone):
    """Numero no formato da D-API: so digitos com DDI 55. Grupo vira ...@g.us."""
    t = str(telefone or '').strip()
    if not t:
        return ''
    if t.endswith('-group'):
        return t[:-len('-group')] + '@g.us'
    if '@' in t:
        if t.endswith(('@c.us', '@s.whatsapp.net')):
            return re.sub(r'\D', '', t.split('@')[0])
        return t
    d = re.sub(r'\D', '', t)
    if len(d) in (10, 11):          # DDD + numero, sem DDI
        d = '55' + d
    return d


# ------------------------------------------------------------------ http

def _post(caminho, corpo, timeout=TIMEOUT):
    sessao, token = _cred()
    if not sessao:
        return False, {'erro': 'D-API nao configurada (DAPI_SESSION/DAPI_TOKEN no config/.env)'}, 0
    corpo = dict(corpo, sessionId=sessao)
    try:
        r = requests.post(f'{BASE}/{caminho}', json=corpo, timeout=timeout,
                          headers={'Authorization': token, 'Content-Type': 'application/json'})
    except requests.RequestException as e:
        return False, {'erro': f'{type(e).__name__}: {e}'}, 0
    try:
        j = r.json()
    except ValueError:
        j = {'raw': r.text[:500]}
    if not isinstance(j, dict):
        j = {'raw': j}
    ok = r.ok and j.get('success') is not False
    return ok, j, r.status_code


def _como_url(conteudo, nome='arquivo', ext=''):
    """Aceita URL, data: ou caminho de arquivo local (vira base64)."""
    s = str(conteudo or '')
    if s.startswith(('http://', 'https://', 'data:')):
        return s
    if os.path.exists(s):
        ext = (ext or s.rsplit('.', 1)[-1]).lower().lstrip('.')
        with open(s, 'rb') as f:
            dados = base64.b64encode(f.read()).decode()
        return f'data:{MIME.get(ext, "application/octet-stream")};base64,{dados}'
    raise ValueError(f'nao e URL nem arquivo existente: {nome}')


# ------------------------------------------------------------------ envio

def enviar_texto(telefone, texto):
    if not str(texto or '').strip():
        return False, {'erro': 'texto vazio'}
    d = destino(telefone)
    if not d:
        return False, {'erro': 'telefone vazio ou invalido'}
    ok, j, st = _post('messages/send/text', {'to': d, 'text': str(texto)})
    return (ok, j) if ok else (False, dict(j, http_status=st))


def enviar_documento(telefone, documento, nome_arquivo='arquivo.pdf', legenda=''):
    d = destino(telefone)
    if not d:
        return False, {'erro': 'telefone vazio ou invalido'}
    ext = (nome_arquivo.rsplit('.', 1)[-1] if '.' in nome_arquivo else 'pdf').lower()
    try:
        url = _como_url(documento, nome_arquivo, ext)
    except ValueError as e:
        return False, {'erro': str(e)}
    ok, j, st = _post('messages/send/document', {
        'to': d, 'document': url, 'fileName': nome_arquivo,
        'mimetype': MIME.get(ext, 'application/octet-stream')})
    if not ok:
        return False, dict(j, http_status=st)
    if str(legenda or '').strip():
        enviar_texto(d, legenda)
    return ok, j


def enviar_imagem(telefone, imagem, legenda=''):
    d = destino(telefone)
    if not d:
        return False, {'erro': 'telefone vazio ou invalido'}
    try:
        url = _como_url(imagem, 'imagem', 'jpg')
    except ValueError as e:
        return False, {'erro': str(e)}
    ok, j, st = _post('messages/send/image', {'to': d, 'image': url, 'caption': legenda or ''})
    return (ok, j) if ok else (False, dict(j, http_status=st))


def status_sessao():
    sessao, token = _cred()
    if not sessao:
        return False, {'erro': 'D-API nao configurada (DAPI_SESSION/DAPI_TOKEN no config/.env)'}
    try:
        r = requests.get(f'{BASE}/sessions/{sessao}/status', timeout=20,
                         headers={'Authorization': token})
        return r.ok, (r.json() if r.content else {})
    except requests.RequestException as e:
        return False, {'erro': f'{type(e).__name__}: {e}'}
    except ValueError:
        return r.ok, {'raw': r.text[:300]}


if __name__ == '__main__':
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
    import ambiente  # noqa: F401  (carrega o .env)

    comando = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if comando == 'status':
        print('D-API configurada:', configurada())
        print(status_sessao())
    elif comando == 'teste' and len(sys.argv) > 2:
        print(enviar_texto(sys.argv[2], 'Teste do sistema do escritorio. Se chegou, a linha esta no ar.'))
    else:
        print(__doc__)
