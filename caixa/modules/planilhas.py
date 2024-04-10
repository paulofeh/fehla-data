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


def calcula_stats(df):
    """
    Função para calcular estatísticas a partir de um DataFrame de imóveis.
    Retorna um dicionário com as estatísticas calculadas.
    Desenhada para ser utilizada em conjunto com a função adiciona_stats, aproveitando o processamento periódico das planilhas.
    A ser implementado em versões futuras.
    """

    stats = {
        'mais_baratos': df.nsmallest(3, 'Preco').to_dict('records'),
        'mais_caros': df.nlargest(3, 'Preco').to_dict('records'),
        'maior_desconto': df.nlargest(1, 'Desconto').to_dict('records')[0],
        'preco_medio': df['Preco'].mean(),
        'mediana_desconto': df['Desconto'].median(),
        'total_imoveis': df.shape[0]
    }
    
    # Calcula cidade com maior média de desconto
    cidade_desconto = df.groupby('Cidade')['Desconto'].mean().idxmax()
    stats['cidade_maior_media_desconto'] = cidade_desconto
    stats['valor_media_desconto'] = df.groupby('Cidade')['Desconto'].mean().max()
    
    # Ranking de modalidades de venda por contagem (apenas para o cenário nacional)
    if 'Modalidade_venda' in df.columns:
        stats['ranking_modalidades'] = df['Modalidade_venda'].value_counts().to_dict()
    
    return stats


def adiciona_stats(planilha, estatisticas, UF="Nacional"):
    """
    Função para adicionar estatísticas a uma planilha do Google Sheets.
    Desenhada para aproveitar o processamento periódico das planilhas e reduzir o impacto na experiência do usuário.
    A ser implementado em versões futuras.
    """
    sheet = planilha.worksheet('Stats')
    
    # Preparar dados para adicionar
    dados_para_adicionar = [
        [UF, "3 Imóveis Mais Baratos", ", ".join([str(imovel['ID_imovel']) for imovel in estatisticas['mais_baratos']])],
        [UF, "3 Imóveis Mais Caros", ", ".join([str(imovel['ID_imovel']) for imovel in estatisticas['mais_caros']])],
        [UF, "Imóvel com Maior Desconto", estatisticas['maior_desconto']['ID_imovel']],
        [UF, "Preço Médio dos Imóveis", estatisticas['preco_medio']],
        [UF, "Mediana do Desconto", estatisticas['mediana_desconto']],
        [UF, "Cidade com Maior Média de Desconto", estatisticas['cidade_maior_media_desconto']],
        [UF, "Valor da Maior Média de Desconto", estatisticas['valor_media_desconto']],
        [UF, "Total de Imóveis Disponíveis", estatisticas['total_imoveis']]
    ]
    
    if UF == "Nacional":
        for modalidade, contagem in estatisticas['ranking_modalidades'].items():
            dados_para_adicionar.append([UF, f"Modalidade: {modalidade}", contagem])
    
    # Adicionar os dados à aba 'Stats' em lote
    sheet.append_rows(dados_para_adicionar, value_input_option='USER_ENTERED')