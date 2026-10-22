"""
Comercial - do lead ate o contrato assinado.

    python COMERCIAL/main.py qualificar "ARQUIVO_COM_AS_MENSAGENS.txt"
    python COMERCIAL/main.py qualificar --exemplo
    python COMERCIAL/main.py transcrever "ligacao.mp3" [--salvar transcricao.txt]
    python COMERCIAL/main.py lead "Joao da Silva" 47999999999 [--etapa LIGACAO]
    python COMERCIAL/main.py painel
    python COMERCIAL/main.py mensagem 47999999999 "texto"   (--enviar para sair de verdade)

Depois que o cliente aceita, a contratacao segue em:
    python CONTRATACAO/main.py novo "TRANSCRICAO.txt" "CNH.pdf" --cadastro CADASTRO.txt
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'NUCLEO'))
import ambiente  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ambiente.RAIZ, 'INTEGRACOES'))

import funil  # noqa: E402
import qualificacao  # noqa: E402


def cmd_qualificar(args):
    if args.exemplo:
        texto = qualificacao.EXEMPLO
        print('(exemplo: lead ficticio)')
    else:
        if not args.arquivo or not os.path.exists(args.arquivo):
            raise SystemExit('Informe o arquivo com as mensagens do lead, ou use --exemplo.')
        with open(args.arquivo, encoding='utf-8') as f:
            texto = f.read()
    transcricao = ''
    if args.transcricao and os.path.exists(args.transcricao):
        with open(args.transcricao, encoding='utf-8') as f:
            transcricao = f.read()
    q = qualificacao.qualificar(texto, transcricao)
    qualificacao.imprimir(q)
    if args.salvar:
        import json
        with open(args.salvar, 'w', encoding='utf-8') as f:
            json.dump(q, f, ensure_ascii=False, indent=2)
        print(f'Salvo em {args.salvar}')


def cmd_transcrever(args):
    import transcricao as t
    texto = t.transcrever(args.audio)
    print(texto)
    if args.salvar:
        with open(args.salvar, 'w', encoding='utf-8') as f:
            f.write(texto)
        print(f'\nSalvo em {args.salvar}')


def cmd_lead(args):
    reg, novo = funil.registrar(args.nome, args.telefone, args.etapa)
    print(('Lead criado: ' if novo else 'Lead atualizado: ') + f"{reg['nome']} -> {reg['etapa']}")


def cmd_mensagem(args):
    import dapi_whatsapp as wa
    if not args.enviar:
        print('--- previa (nada foi enviado) ---')
        print(f'Para: {wa.destino(args.telefone)}')
        print(args.texto)
        print('\nPara enviar de verdade, repita o comando com --enviar')
        return
    if not wa.configurada():
        raise SystemExit('D-API nao configurada: DAPI_SESSION e DAPI_TOKEN no config/.env')
    ok, resp = wa.enviar_texto(args.telefone, args.texto)
    print('Enviada.' if ok else f'NAO enviada: {resp}')


def main():
    ap = argparse.ArgumentParser(description='Comercial', formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog=__doc__)
    sub = ap.add_subparsers(dest='comando', required=True)

    q = sub.add_parser('qualificar', help='classifica o lead e prepara a ligacao')
    q.add_argument('arquivo', nargs='?')
    q.add_argument('--transcricao', help='transcricao da ligacao, se ja houve')
    q.add_argument('--salvar', help='grava o resultado em JSON')
    q.add_argument('--exemplo', action='store_true', help='roda com um lead ficticio')
    q.set_defaults(func=cmd_qualificar)

    t = sub.add_parser('transcrever', help='transcreve a gravacao da ligacao')
    t.add_argument('audio')
    t.add_argument('--salvar')
    t.set_defaults(func=cmd_transcrever)

    l = sub.add_parser('lead', help='registra ou move o lead no funil')
    l.add_argument('nome')
    l.add_argument('telefone')
    l.add_argument('--etapa', default='LEAD', help=f"uma de: {', '.join(funil.ETAPAS)}")
    l.set_defaults(func=cmd_lead)

    p = sub.add_parser('painel', help='mostra o funil')
    p.set_defaults(func=lambda a: funil.painel())

    m = sub.add_parser('mensagem', help='manda mensagem pelo WhatsApp do escritorio')
    m.add_argument('telefone')
    m.add_argument('texto')
    m.add_argument('--enviar', action='store_true')
    m.set_defaults(func=cmd_mensagem)

    args = ap.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
