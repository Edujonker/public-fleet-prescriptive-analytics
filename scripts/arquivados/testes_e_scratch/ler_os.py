import pandas as pd

# Nome do arquivo CSV
nome_arquivo = 'Geral_de_OS_23439885_202609110934.csv'

try:
    # No Brasil, é comum os CSVs usarem ';' como separador e 'latin1' ou 'utf-8' para acentos.
    # Se os dados ficarem bagunçados, troque sep=';' para sep=','
    df = pd.read_csv(nome_arquivo, sep=';', encoding='utf-8')
except UnicodeDecodeError:
    # Se houver erro de leitura de caracteres (acentos), tenta com outra codificação padrão
    df = pd.read_csv(nome_arquivo, sep=';', encoding='latin1')
except FileNotFoundError:
    print(f"Erro: O arquivo '{nome_arquivo}' não foi encontrado na pasta atual.")
    exit()

# 1. Informações gerais (Quantidade de linhas, colunas e tipos de dados)
print("\n" + "="*50)
print("1. INFORMAÇÕES GERAIS DO ARQUIVO")
print("="*50)
df.info()

# 2. Lista de todas as colunas
print("\n" + "="*50)
print("2. COLUNAS PRESENTES NO ARQUIVO")
print("="*50)
for i, coluna in enumerate(df.columns, start=1):
    print(f"{i}. {coluna}")

# 3. Estatísticas básicas (apenas para as colunas com números)
print("\n" + "="*50)
print("3. ESTATÍSTICAS BÁSICAS (Mínimo, Máximo, Média, etc.)")
print("="*50)
print(df.describe())

# 4. Amostra dos dados
print("\n" + "="*50)
print("4. PRIMEIRAS 5 LINHAS DO ARQUIVO")
print("="*50)
print(df.head())