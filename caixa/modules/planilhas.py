"""
Funções para baixar e tratar planilhas de leilões da Caixa Econômica Federal.
"""

import requests
import pandas as pd
from io import StringIO
from datetime import datetime


def baixa_planilha(UF):
    """
    Função para baixar a planilha de leilões da Caixa de um estado específico.
    """

    url = f'https://venda-imoveis.caixa.gov.br/listaweb/Lista_imoveis_{UF}.csv'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    print(f"Baixando planilha de leilões da Caixa para o estado {UF}...")
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"Erro {response.status_code}: Não foi possível acessar a planilha {UF}.")
        return None
    else:
        print(f"Planilha {UF} baixada com sucesso.")
        # Assume que o conteúdo original está em cp1252 e o converte para uma string UTF-8
        content_utf8 = response.content.decode('iso-8859-1')
        content_utf8_clean = "\n".join(line for line in content_utf8.splitlines() if line.strip('; \n\r'))
        # Verificar se o conteúdo parece ser um CSV
        if content_utf8_clean.strip().startswith('<!DOCTYPE html>'):
            print("Não é um CSV válido, parece ser uma página HTML.")
            return None
        else:
            print("Conteúdo parece ser um CSV válido.")

            # Usa StringIO para transformar a string UTF-8 em um objeto similar a arquivo
            data = StringIO(content_utf8_clean)
            try:
                df = pd.read_csv(data, header=1, sep=';', encoding='utf-8', on_bad_lines='skip')
                print("CSV convertido com sucesso.")     
            except pd.errors.ParserError as e:
                print(f"Erro ao analisar o CSV: {e}")
                return None
    return df


def trata_planilha(df):
    """
    Função para tratar os dados da planilha de leilões da Caixa, limpando e organizando as colunas e formatando os dados para análise
    """

    df.rename(columns={' N° do imóvel': 'ID_imovel', 'Endereço': 'Endereco', 'Preço': 'Preco', 'Valor de avaliação': 'Valor_Avaliacao', 'Descrição': 'Descricao', 'Modalidade de venda': 'Modalidade_venda', 'Link de acesso': 'Link_acesso'}, inplace=True)

    # Extrair o tipo de imóvel (a primeira palavra da string)
    df['Tipo_Imovel'] = df['Descricao'].str.extract(r'^(\w+)')

    # Extrair a área total e converter para float
    df['Area_Total'] = df['Descricao'].str.extract(r', (\d+\.\d+) de área total').astype(float)

    # Extrair a área privativa e converter para float
    df['Area_Privativa'] = df['Descricao'].str.extract(r', (\d+\.\d+) de área privativa').astype(float)

    # Extrair a área do terreno e converter para float
    df['Area_Terreno'] = df['Descricao'].str.extract(r', (\d+\.\d+) de área do terreno').astype(float)

    # Converter Preco e Valor_Avaliacao para float
    # Certifique-se de que as colunas estão no formato string antes de usar o acessor .str
    df['Preco'] = df['Preco'].astype(str)
    df['Valor_Avaliacao'] = df['Valor_Avaliacao'].astype(str)
    df['Preco'] = df['Preco'].str.replace('.', '').str.replace(',', '.').astype(float)
    df['Valor_Avaliacao'] = df['Valor_Avaliacao'].str.replace('.', '').str.replace(',', '.').astype(float)

    # Garante que o valor do desconto esteja correto
    df['Desconto'] = (df['Valor_Avaliacao'] - df['Preco']) / df['Valor_Avaliacao']*100

    # Adiciona a data de inclusão do registro no dataframe
    df['Data_Inclusao'] = datetime.now().strftime('%Y-%m-%d')

    return df
