from os.path import isdir, isfile, join, splitext
from pandas import DataFrame, Series
from argparse import ArgumentParser
from time import perf_counter
from os import listdir
import pandas as pd

def get_files(directory: str) -> list[str]:
    files = []
    if isinstance(directory, str):
        if not isdir(directory): raise FileNotFoundError(f'{directory} não é um diretório.')

        for path in listdir(directory):
            if not isfile(join(directory, path)): continue

            if splitext(path)[1].lower() != '.csv' and path[:-4] != '.xls' and path[:-5] != '.xlsx':
                raise ValueError(f'{path} tem uma extensão de arquino inapropriada.')

            files.append(join(directory, path))

    else: raise TypeError(f'{directory} não é um caminho.')

    return files

def read_file(file: str) -> DataFrame:
    global old_format

    if splitext(file)[1].lower() == '.csv':
        with open(file, 'r') as file_:
            cache = file_.readline()

        if '|' in cache:
            old_format = True
            df = pd.read_csv(file, sep = '|', encoding = 'latin-1', low_memory = True, usecols = old_cols)

        else:
            old_format = False
            df = pd.read_csv(file, sep = ';', encoding = 'latin-1', low_memory = True, usecols = new_cols)

    else:
        df = pd.read_excel(file, low_memory = True, usecols = new_cols)
    
    return df

def get_year_from_file(file_name: str) -> int:
    lindex = 0

    for i, char in enumerate(file_name):
        if char.isnumeric():
            lindex = file_name.index(char)
            break

        elif i + 1== len(file_name):
            raise IndexError(f'Incapaz de encontrar o índice inicial em "{file_name}".')
    
    rindex = lindex + 4
    return int(file_name[lindex : rindex])

def get_out(out: str) -> str:
    try:
        out = out.replace('.xls', '').replace('.xlsx', '').replace('.csv', '').replace('.XLS', '').replace('.XLSX', '').replace('.CSV', '')
        return out + '.csv'
    
    except TypeError:
        raise TypeError(f'Saída {out} não é um diretório.')


UFS = ('ES',)  # Os estados que quer.

# Colunas que serão mantidas.
new_cols = ('SG_UF', 'NO_MUNICIPIO', 'NO_ENTIDADE', 'IN_ESP', 'IN_ESP_CE', )
old_cols = ('SIGLA', 'MUNIC', 'MASCARA', 'ESP_EXCL', 'ESP_T_ES', )

# A ordem das colunas para serem salvas no final.
order = ('ANO', 'SG_UF', 'NO_MUNICIPIO', 'NO_ENTIDADE', 'IN_ESP', 'IN_ESP_CE', )

# Tradutor da formatação velha para a antiga.
translator = {'SIGLA': 'SG_UF', 
              'MUNIC': 'NO_MUNICIPIO', 
              'MASCARA': 'NO_ENTIDADE', 
              'ESP_EXCL': 'IN_ESP',
              'ESP_T_ES': 'IN_ESP_CE'}

old_format = False  # Guarda se a planilha em leitura é do formato antigo ou novo.
first_pass = True  # Guarda a linha onde foi salva a última entrada do Dataframe + 1

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('dir', type = str)
    parser.add_argument('out', type = str)
    args = parser.parse_args()

    files = get_files(args.dir)
    out = get_out(args.out)

    # Começo da leitura
    for file in files:
        start_time = perf_counter()
        df = read_file(file)
        original_size = len(df.index)
        year = get_year_from_file(file) 

        try:
            if old_format:
                df = df[df['SIGLA'].isin(UFS)]  # Tira todas as linhas que não são dos estados que quer.

            else:
                df = df[df['SG_UF'].isin(UFS)]  # Idem.

        except KeyError:
            if old_format:
                raise KeyError(f'Arquivo: {file} não tem a coluna SIGLA.')
            
            else:
                raise KeyError(f'Arquivo: {file} não tem a coluna SG_UF.')
        
        if old_format:
            df.rename(columns = translator, inplace = True)  # Renomeia as colunas com nomes de formatação antiga.
            df.replace({'n': 0, 's': 1}, inplace = True)  # Normaliza os dados (a formatação antiga usa n/s em vez de 0/1)
        
        year_series = Series([year] * len(df.index))  # Dia uma série do tamanho do DataFrame que só contém o ano.
        df.reset_index(inplace = True, drop = True)  # Resseta os índices (necessário após apagar um monte de linhas lá em acima)
        df['ANO'] = year_series
        df = df.reindex(columns = order)  # Se certifica que estão na ordem correta.

        # É necessário usar um arquivo `.csv` porque `.xlsx` é muito pesado e lento.
        if first_pass:
            df.to_csv(out, sep = ';', index = False)
            first_pass = False
            
        else:  # Depois da primeira leitura, ele concatena, e não cria um do zero.
            df.to_csv(out, mode = 'a', sep = ';', index = False, header = False)

        end_time = perf_counter()
        print(f'Arquivo "{file}" foi reduzido de {original_size} para {len(df.index)} linhas e consolidado em {end_time - start_time:.2f} segundos.')
