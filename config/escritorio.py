"""
Identidade e regras do escritorio.

Tudo que e do escritorio (nome, timbrado, prazos, checklist, pastas) mora aqui,
para a equipe ajustar sem mexer no codigo.

Montado a partir do briefing preenchido em 18/10/2026 (formulario do Casal da IA).
Campos marcados com [CONFERIR] nao vieram no briefing ou vieram ambiguos. Enquanto houver
[CONFERIR] em campo usado por um documento, o envio para assinatura trava de proposito
(ver NUCLEO/docx_escritorio.py e CONTRATACAO/envio.py).
"""

ESCRITORIO = {
    'nome': 'Faya Barreiros Sociedade Individual de Advocacia',
    'razao_social': 'FAYA BARREIROS SOCIEDADE INDIVIDUAL DE ADVOCACIA',
    'cnpj': '67.928.823/0001-52',
    'oab_sociedade': '[CONFERIR]',     # registro da sociedade na OAB
    'endereco': 'Av. Tancredo Neves, 1283, Sala 1001, Salvador/BA, CEP [CONFERIR]',
    'endereco_timbrado': 'Av. Tancredo Neves, 1283 - Sala 1001',
    'cidade': 'Salvador',
    'uf': 'BA',
    'telefone': '[CONFERIR]',          # telefone fixo/comercial que vai no rodape
    'whatsapp': '(71) 99981-1108',     # Dra. Faya
    'email': 'faya.calculos@gmail.com',
    'site': '[CONFERIR]',
    'instagram': '@fayabarreiros / @williamcoelho.tributario',
}

# Os dois titulares. A Dra. Faya assina o contrato pelo escritorio (a sociedade e dela);
# o Dr. William atua na area tributaria e tem a propria carteira de clientes.
TITULAR = {
    'nome': 'Faya Milla Magalhães Mascarenhas Barreiros',
    'oab': 'OAB/SP 308.385 e OAB/BA 64.723',   # [CONFERIR] a ordem das inscricoes no briefing era ambigua
    'email': 'faya.calculos@gmail.com',
}

SOCIO = {
    'nome': 'William Ricardo Coelho',
    'oab': 'OAB/BA 64.518',
    'email': 'williamcoelho.tributario@gmail.com',
    'whatsapp': '(71) 99720-2036',
}

# Advogados que constam na procuracao (outorgados).
OUTORGADOS = [
    {'nome': 'FAYA MILLA MAGALHÃES MASCARENHAS BARREIROS', 'oab': 'OAB/SP 308.385 e OAB/BA 64.723'},
    {'nome': 'WILLIAM RICARDO COELHO', 'oab': 'OAB/BA 64.518'},
]

# Visual do timbrado. Enquanto o escritorio nao mandar o timbrado oficial (o briefing diz que
# ela envia o timbrado e os modelos), estes valores sao um padrao sobrio e o documento sai
# com o aviso de timbrado provisorio.
VISUAL = {
    'fonte': 'Times New Roman',
    'fonte_rodape': 'Calibri',
    'tamanho': 12,
    'cor_destaque': '1F3864',   # azul sobrio - [CONFERIR] cor da marca
    'cor_texto': '20201F',
    'espacamento': 1.5,
    'recuo_primeira_linha_cm': 1.25,
    'timbrado_oficial': False,  # vira True quando config/timbrado_modelo.docx for o do escritorio
}

# Prazos internos do fluxo. [CONFERIR] com o escritorio: o briefing nao deu numeros.
# O que o briefing deu: o CICLO DOS PRAZOS de calculos e servicos avulsos e inegociavel (Faya)
# e a reuniao de fechamento com o cliente e inegociavel (William).
PRAZOS = {
    'primeiro_contato_dias_apos_lead': 0,   # William atende o lead e chama para reuniao
    'documentos_dias_apos_contrato': 1,     # comeca a cobranca de documentos
    'analise_dias_apos_documentos': 5,      # relatorio de analise da origem dos debitos pronto
    'revisao_dias': 1,                      # revisao humana (Faya e William) antes de protocolar
}

# Checklist de documentos. O carro-chefe e TRIBUTARIO (execucao fiscal e gestao de passivo);
# os itens de previdenciario entram como opcionais para a mesma esteira servir aos clientes de
# calculo e planejamento previdenciario.
# 'pasta' e a subpasta onde o documento fica guardado; 'palavras' reconhece o arquivo pelo nome.
CHECKLIST_DOCUMENTOS = [
    {'id': 'pessoais', 'nome': 'Documento do responsavel (RG/CNH e CPF) e dos socios', 'pasta': '01 DOCUMENTOS PESSOAIS',
     'palavras': ['cnh', 'rg', 'cpf', 'identidade', 'habilitacao'], 'obrigatorio': True},
    {'id': 'empresa', 'nome': 'Contrato social e alteracoes, cartao CNPJ', 'pasta': '02 DOCUMENTOS DA EMPRESA',
     'palavras': ['contrato social', 'alteracao', 'cnpj', 'cartao', 'estatuto', 'mei', 'ccmei'], 'obrigatorio': True},
    {'id': 'endereco', 'nome': 'Comprovante de endereco', 'pasta': '03 COMPROVANTE DE ENDERECO',
     'palavras': ['endereco', 'residencia', 'conta de luz', 'energia', 'agua'], 'obrigatorio': False},
    {'id': 'situacao_fiscal', 'nome': 'Relatorio de situacao fiscal (e-CAC/PGFN), certidoes e consulta de divida ativa',
     'pasta': '04 SITUACAO FISCAL',
     'palavras': ['situacao fiscal', 'ecac', 'e-cac', 'pgfn', 'regularize', 'certidao', 'cnd', 'divida ativa',
                  'inscricao'], 'obrigatorio': True},
    {'id': 'cdas', 'nome': 'CDAs, autos de infracao, notificacoes e processos administrativos',
     'pasta': '05 CDAS E PROCESSOS ADMINISTRATIVOS',
     'palavras': ['cda', 'certidao de divida', 'auto de infracao', 'notificacao', 'lancamento', 'intimacao',
                  'processo administrativo', 'carf', 'drj', 'inconformidade'], 'obrigatorio': True},
    {'id': 'execucao', 'nome': 'Execucao fiscal: peticao inicial, citacao, penhoras e decisoes',
     'pasta': '06 EXECUCAO FISCAL',
     'palavras': ['execucao fiscal', 'citacao', 'penhora', 'sisbajud', 'bacenjud', 'embargos', 'decisao',
                  'sentenca', 'peticao inicial'], 'obrigatorio': False},
    {'id': 'parcelamentos', 'nome': 'Parcelamentos e transacoes existentes (extratos, termos, guias pagas)',
     'pasta': '07 PARCELAMENTOS E TRANSACOES',
     'palavras': ['parcelamento', 'transacao', 'refis', 'pert', 'simples', 'darf', 'guia', 'adesao'],
     'obrigatorio': False},
    {'id': 'declaracoes', 'nome': 'Declaracoes e apuracoes (DCTF, DCOMP, PGDAS, SPED, DEFIS/DASN, ECF)',
     'pasta': '08 DECLARACOES E APURACOES',
     'palavras': ['dctf', 'dcomp', 'pgdas', 'sped', 'defis', 'dasn', 'ecf', 'ecd', 'gfip', 'esocial', 'efd'],
     'obrigatorio': False},
    {'id': 'contabil', 'nome': 'Balancos, balancetes, DRE e faturamento (base da analise de CAPAG)',
     'pasta': '09 CONTABIL E FATURAMENTO',
     'palavras': ['balanco', 'balancete', 'dre', 'faturamento', 'contabil', 'capag', 'notas fiscais'],
     'obrigatorio': False},
    {'id': 'cnis', 'nome': 'CNIS e extrato previdenciario (clientes previdenciarios)', 'pasta': '10 PREVIDENCIARIO',
     'palavras': ['cnis', 'extrato previdenciario', 'meu inss', 'carta de concessao', 'ppp', 'ltcat', 'ctps',
                  'indeferimento', 'carta de exigencia', 'inss'], 'obrigatorio': False},
    {'id': 'procuracao', 'nome': 'Procuracao, contrato e declaracao assinados', 'pasta': '00 CONTRATACAO',
     'palavras': ['procuracao', 'contrato', 'declaracao'], 'obrigatorio': True},
]

# Estrutura da pasta do cliente. Segue o desenho do briefing: pastas separadas por area
# (previdenciario x tributario) e, dentro, clientes do escritorio x avulsos (calculos e parcerias).
# A esteira de contratacao trabalha numa area por vez: a area padrao e TRIBUTARIO (carro-chefe).
PASTA_AREA = 'TRIBUTARIO'
SUBPASTAS_CLIENTE = [
    '00 CONTRATACAO',
    '01 DOCUMENTOS PESSOAIS',
    '02 DOCUMENTOS DA EMPRESA',
    '03 COMPROVANTE DE ENDERECO',
    '04 SITUACAO FISCAL',
    '05 CDAS E PROCESSOS ADMINISTRATIVOS',
    '06 EXECUCAO FISCAL',
    '07 PARCELAMENTOS E TRANSACOES',
    '08 DECLARACOES E APURACOES',
    '09 CONTABIL E FATURAMENTO',
    '10 PREVIDENCIARIO',
    '11 PECAS',
    '12 PROTOCOLOS',
]

# Honorarios padrao. [CONFERIR]: o briefing nao falou de honorarios.
HONORARIOS = {
    'modelo': '[CONFERIR]',
    'percentual_exito': 0,      # [CONFERIR]
    'entrada': 0,
    'observacao': 'Modelo de honorarios nao informado no briefing (honorarios + exito?). [CONFERIR]',
}
