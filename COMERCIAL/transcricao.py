"""
Transcricao da ligacao do comercial.

A ligacao e gravada (celular, softphone ou o proprio WhatsApp) e o arquivo de audio
entra aqui. A transcricao alimenta a ficha e o relatorio de triagem - e o que evita
ligar duas vezes para o mesmo cliente.

Dois caminhos, nesta ordem:
1. faster-whisper local (sem custo, roda na maquina do escritorio).
   pip install faster-whisper
2. API da OpenAI (whisper-1), se OPENAI_API_KEY estiver no config/.env.

Uso:
    python COMERCIAL/main.py transcrever "C:/ligacoes/joao.mp3"
    python COMERCIAL/main.py transcrever "ligacao.ogg" --salvar transcricao.txt
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402,F401

MODELO_LOCAL = os.getenv('WHISPER_MODELO', 'small')


def _local(caminho):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None
    modelo = WhisperModel(MODELO_LOCAL, device='cpu', compute_type='int8')
    segmentos, _ = modelo.transcribe(caminho, language='pt', vad_filter=True)
    linhas = []
    for s in segmentos:
        minuto = int(s.start // 60)
        segundo = int(s.start % 60)
        linhas.append(f'[{minuto:02d}:{segundo:02d}] {s.text.strip()}')
    return '\n'.join(linhas)


def _api(caminho):
    chave = os.getenv('OPENAI_API_KEY')
    if not chave:
        return None
    import requests
    with open(caminho, 'rb') as f:
        r = requests.post('https://api.openai.com/v1/audio/transcriptions',
                          headers={'Authorization': f'Bearer {chave}'},
                          files={'file': f},
                          data={'model': 'whisper-1', 'language': 'pt'},
                          timeout=600)
    if not r.ok:
        raise RuntimeError(f'API de transcricao: {r.status_code} {r.text[:200]}')
    return r.json().get('text', '')


def transcrever(caminho):
    if not os.path.exists(caminho):
        raise SystemExit(f'Audio nao encontrado: {caminho}')
    texto = _local(caminho)
    if texto:
        return texto
    texto = _api(caminho)
    if texto:
        return texto
    raise SystemExit(
        'Nenhum caminho de transcricao disponivel.\n'
        '  Opcao 1 (recomendada, sem custo): pip install faster-whisper\n'
        '  Opcao 2: colocar OPENAI_API_KEY no config/.env')
