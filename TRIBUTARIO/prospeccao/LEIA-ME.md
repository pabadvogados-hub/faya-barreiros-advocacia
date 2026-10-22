# Prospecção de empresas com dívida ativa (Dados Abertos da PGFN)

Scripts para achar empresas devedoras na base pública da PGFN, cruzar com o cadastro da Receita
(BrasilAPI) e gerar uma lista com situação, porte, atividade e contato.

**Fonte:** https://dadosabertos.pgfn.gov.br/ (um ZIP por trimestre; a base "Não Previdenciário" passa de 1 GB).
CNPJ completo para pessoa jurídica; sem captcha. Pessoa física vem mascarada.

**Insight:** dívida **não ajuizada** (só cobrança administrativa) é o melhor lead: ainda há margem para
transação ou parcelamento antes da execução fiscal.

## Como rodar
Rode dentro de uma pasta de trabalho (os arquivos de saída vão para a pasta atual), por exemplo `SAIDA/prospeccao`:
```
python TRIBUTARIO/prospeccao/filtrar_zip_stream.py <arquivo.zip> 100000 1000000 BA   # faixa de valor e UF (opcionais)
python TRIBUTARIO/prospeccao/enriquecer.py 30                                         # 30 empresas ATIVAS
python TRIBUTARIO/prospeccao/gerar_relatorio.py                                       # relatorio.md + contatos.csv
python TRIBUTARIO/prospeccao/buscar_cnpj.py 12345678 <zip_url> apelido                # todas as inscrições de um CNPJ
```
Precisa de internet e de espaço em disco para o ZIP baixado.

## Cuidados antes de usar a lista (peça aos advogados para conferir)
- **Publicidade e captação na advocacia:** o Provimento 205/2021 da OAB limita a abordagem direta e não
  solicitada de potenciais clientes. Use a lista para entender o mercado e direcionar conteúdo e anúncios,
  e confirme com a Dra. Faya e o Dr. William antes de qualquer contato ativo.
- **LGPD:** a lista contém dados de empresas (públicos), mas sócios e telefones são dados pessoais.
  Não suba a lista nem o `candidatos.json` para o GitHub (o `.gitignore` do projeto bloqueia `SAIDA/`).
