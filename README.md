# Consolidador-Microdados-INEP
Automação para apagar todas as colunas desnecessárias e consolidar várias planilhas de microdados do INEP em uma só.

### Como utilizar:
- Edite as tuplas `old_cols` e `new_cols` para os respectivos valores que deseja manter nas respectivas formatações antigas e novas do INEP.
- Configure a tupla `order` para a ordem que deseja que as colunas acima apareçam na planilha final.
- Configure o dicionário `translator` com a correspondência `old_cols` -> `new_cols`.
- Acione o programa com os dois argumentos seguintes: o nome da pasta onde estão as planilhas extraídas no INEP, e o nome do arquivo `.csv` onde os dados serão consolidados.
