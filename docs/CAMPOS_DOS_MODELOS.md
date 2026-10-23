# Campos dos modelos (DOCS_MODELOS/)

Os modelos .docx são preenchidos trocando `{{CAMPO}}` pelo valor do caso. Para usar um modelo
oficial do escritório, basta salvar o .docx em `DOCS_MODELOS/` com o mesmo nome e trocar os dados
variáveis por estes marcadores.

## Do cliente
| Campo | De onde vem |
|---|---|
| `{{NOME}}` | CNH/RG (maiúsculo) |
| `{{CPF}}` | CNH/RG, validado pelo dígito |
| `{{RG}}` / `{{ORGAO_EMISSOR}}` | CNH/RG |
| `{{NACIONALIDADE}}` | CNH/RG |
| `{{ESTADO_CIVIL}}` / `{{PROFISSAO}}` | cadastro do comercial |
| `{{ENDERECO_COMPLETO}}` | cadastro |
| `{{TELEFONE}}` / `{{EMAIL}}` | cadastro |

## Do caso
| Campo | De onde vem |
|---|---|
| `{{ENTE_CREDOR}}` | cadastro, ou o(s) ente(s) credor(es) que a triagem identificou nos débitos |
| `{{OBJETO}}` | montado a partir do ente credor e da area (tributario/previdenciario) |
| `{{NUMERO_CONTRATO}}` | sequencial automático por ano |
| `{{HONORARIOS_ENTRADA}}` / `{{HONORARIOS_PAGAMENTO}}` / `{{HONORARIOS_EXITO}}` | cadastro ou triagem |

## Do escritório
| Campo | De onde vem |
|---|---|
| `{{OUTORGADOS}}` | `config/escritorio.py` → `OUTORGADOS` |
| `{{TITULAR_NOME}}` / `{{TITULAR_OAB}}` | `config/escritorio.py` → `TITULAR` |
| `{{ESCRITORIO_CNPJ}}` / `{{ESCRITORIO_ENDERECO}}` / `{{ESCRITORIO_EMAIL}}` | `config/escritorio.py` |
| `{{CIDADE_UF}}` / `{{DATA_EXTENSO}}` | automático |

## Previdenciário (Dra. Faya)
`{{DATA_NASCIMENTO}}`, `{{OBJETO}}` (ex.: PEDIDO ADMINISTRATIVO DE CONCESSÃO DO BENEFÍCIO DE APOSENTADORIA),
`{{OBJETO_ACAO}}` (procuração), `{{HONORARIOS_IMPLANTACAO}}`, `{{HONORARIOS_EXITO}}`, `{{HONORARIOS_INICIAIS}}`,
`{{TITULAR_EMAIL}}`, `{{TITULAR_ESTADO_CIVIL}}`, `{{CIDADE}}`.
Os honorários vêm de `config/escritorio.py` -> `HONORARIOS['PREVIDENCIARIO']`; o `CADASTRO.txt` sobrescreve.

## Tributário (Dr. William)
`{{CNPJ}}`, `{{REPRESENTANTE_NOME}}`, `{{REPRESENTANTE_QUALIFICACAO}}`, `{{REPRESENTANTE_CPF}}`, `{{LISTA_CDAS}}`
(sai da triagem), `{{VALOR_DEBITO}}`, `{{ENTE_CREDOR}}`, `{{HONORARIOS_CONDICOES}}`, `{{PRAZO_ADESAO}}`,
`{{CONTA_BANCARIA}}` e `{{CHAVE_PIX}}` (vêm do `config/.env`).
No modelo `..._COM_RESULTADO`: `{{DEBITO_TOTAL_ORIGINAL}}`, `{{DESCONTO_OBTIDO}}`, `{{TOTAL_A_PAGAR}}`,
`{{PARCELAS_ENTRADA}}`, `{{PARCELAS_BASICAS}}`, `{{NUMERO_PARCELAS}}`, `{{TABELA_PROCESSOS}}`, `{{BASE_ADMINISTRATIVA}}`,
`{{BASE_JUDICIAL}}`, `{{TOTAL_HONORARIOS}}`.

## Qual modelo sai (CONTRATACAO/documentos.py)
| Área (do cadastro ou da triagem) | Documentos |
|---|---|
| PREVIDENCIARIO | `PREV_CONTRATO_EXITO` (ou `_EXITO_SALARIOS` se o cadastro disser `Contrato: exito e salarios`), procuração previdenciária, declaração de hipossuficiência, e o termo de renúncia (JEF) se `Juizado federal: sim` |
| TRIBUTARIO (e AMBOS) | `TRIB_CONTRATO_GESTAO_PASSIVO` (ou `_COM_RESULTADO` se `Contrato: com resultado`) e procuração (provisória) |

Campo sem valor vira `[PREENCHER CAMPO]` e **trava o envio para assinatura**.
