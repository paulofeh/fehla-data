""" 
Buscador de planilhas de leilões da Caixa Econômica Federal
Autor: Paulo Fehlauer
Data: 2024-03-13
Versão: 0.1
Licença: MIT
Descrição: Este script é um buscador de planilhas de leilões da Caixa Econômica Federal. 
O script acessa a página de leilões da Caixa, baixa a planilha de leilões disponíveis por UF e a salva em uma planilha do Google Sheets com a seguinte lógica de atualizações:
1. Cria no Sheets uma planilha para cada estado + Arquivados + Controle (deve ser executada somente 1 vez)
2. Para cada estado da lista:
    1. Baixa a planilha de leilões da Caixa
    2. Importa o Sheets para um dataframe
    3. Trata os dados da planilha, limpando e organizando as colunas
    4. Compara os dados da planilha com os dados do sheets (a partir do ID do imóvel)
        1. Se um registro estiver na planilha mas não no sheets, adiciona a um dataframe Novos
        2. Se um registro estiver no sheets mas não na planilha, adiciona a um dataframe Arquivados
    5. Busca as coordenadas geográficas dos imóveis do dataframe Novos
    6. Salva os dataframes Novos e Arquivados no Google Sheets, conforme a lógica a seguir:
        1. Se não houver registros em df_novos nem em df_arquivados, não há a necessidade de atualizar o sheets
        2. Se houver registros em df_novos, mas não em df_arquivados, basta adicionar os registros de df_novos ao final da planilha do estado
        3. Se não houver registros em df_novos, mas houver em df_arquivados, devemos adicionar esses registros ao final da planilha 'Arquivados' , excluí-los de df_sheets e substituir a planilha respectiva no sheets
        4. Se houver registros tanto em df_novos quanto em df_arquivados, devemos adicionar os registros de df_arquivados ao final da planilha 'Arquivados' , excluí-los de df_sheets, concatenar df_sheets com df_novos e substituir a planilha respectiva no sheets
3. O script deve ser executado periodicamente para manter as planilhas atualizadas
"""

# Bibliotecas padrão
import os
import time

# Bibliotecas de terceiros
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import pandas as pd

# Bibliotecas locais
from modules.planilhas import baixa_planilha, trata_planilha
from modules.geoloc import processar_lotes

# Credenciais e autenticação
load_dotenv()

arquivo_credenciais = "imoveis-da-caixa-293ec7fa1219.json"
conteudo_credenciais = os.environ.get("GSPREAD_CREDENTIALS")
with open (arquivo_credenciais, "w") as f:
    f.write(conteudo_credenciais)
conta = ServiceAccountCredentials.from_json_keyfile_name(arquivo_credenciais)
api = gspread.authorize(conta)
sheets_api = os.environ.get("SHEETS_API")
planilha = api.open_by_key(sheets_api)


# Variáveis
estados = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']
colunas = ['ID_imovel', 'UF', 'Cidade', 'Bairro', 'Endereco', 'Preco', 'Valor_Avaliacao', 'Desconto', 'Descricao', 'Modalidade_venda', 'Link_acesso', 'Tipo_Imovel', 'Area_Total', 'Area_Privativa', 'Area_Terreno','Data_Inclusao', 'Latitude', 'Longitude']


# Execução
# Cria no Sheets uma planilha para cada estado + Arquivados
"""
Executa a criação das planilhas no Google Sheets
for UF in estados:
    worksheet = planilha.add_worksheet(title=UF, rows=100, cols=20)
    print(f"Worksheet '{UF}' created successfully.")
worksheet = planilha.add_worksheet(title='Arquivados', rows=100, cols=20)
print(f"Worksheet 'Arquivados' created successfully.")
"""

# Itera sobre os estados da lista
for UF in estados:
    # Baixa a planilha de leilões da Caixa
    df_caixa = baixa_planilha(UF)
    if df_caixa is None:
        continue

    # Importa o Sheets para um dataframe
    df_sheets = planilha.worksheet(UF).get_all_records()

    # Verifica se o dataframe do Sheets está vazio
    if not df_sheets:
        print(f"Dataframe do Sheets para o estado {UF} está vazio.")
        df_sheets = pd.DataFrame(columns=colunas)
        planilha.worksheet(UF).update([df_sheets.columns.values.tolist()] + df_sheets.values.tolist())
    else:
        df_sheets = pd.DataFrame(df_sheets)

    # Trata os dados da planilha, limpando e organizando as colunas
    df_caixa = trata_planilha(df_caixa)

    # Compara os dados da planilha com os dados do sheets (a partir do ID do imóvel)
    # Se um registro estiver na planilha mas não no sheets, adiciona a um dataframe Novos
    df_novos = df_caixa[~df_caixa['ID_imovel'].isin(df_sheets['ID_imovel'])]
    print(f"Novos registros encontrados para o estado {UF}: {len(df_novos)}")

    # Se um registro estiver no sheets mas não na planilha, adiciona a um dataframe Arquivados
    df_arquivados = df_sheets[~df_sheets['ID_imovel'].isin(df_caixa['ID_imovel'])]
    print(f"Registros arquivados encontrados para o estado {UF}: {len(df_arquivados)}")

    # Se o dataframe Novos não estiver vazio, busca as coordenadas geográficas dos imóveis
    if not df_novos.empty:
        # Cria uma cópia do DataFrame para evitar o aviso SettingWithCopyWarning
        df_novos = df_novos.copy()
        # Cria uma coluna temporária com o endereço completo
        df_novos.loc[:, 'Endereco_Completo'] = df_novos.apply(lambda row: ', '.join([str(row['Endereco']), str(row['Bairro']), str(row['Cidade']), str(row['UF'])]), axis=1)

        # Define o tamanho do lote (usado para contornar limitações de uso da API do Google Maps)
        tamanho_lote = 2000

        # Divide o DataFrame em lotes menores e processa cada lote separadamente
        for i in range(0, len(df_novos), tamanho_lote):
            df_lote = df_novos.iloc[i:i+tamanho_lote]
            latitudes_lote, longitudes_lote = processar_lotes(df_lote)
            
            # Adiciona as latitudes e longitudes processadas ao DataFrame original
            df_novos.loc[df_lote.index, 'Latitude'] = latitudes_lote
            df_novos.loc[df_lote.index, 'Longitude'] = longitudes_lote

            # Aguarda 60 segundos para evitar limitações de uso da API
            time.sleep(60)

        # Remove a coluna temporária 'Endereco_Completo'
        df_novos = df_novos.drop(columns=['Endereco_Completo'])

    # Salva os dataframes Novos e Arquivados no Google Sheets
    # Se não houver registros em df_novos nem em df_arquivados, não há a necessidade de atualizar o sheets
    if df_novos.empty and df_arquivados.empty:
        print(f"Não há registros para atualizar no estado {UF}.")
        continue

    # Se houver registros em df_novos, mas não em df_arquivados, basta adicionar os registros de df_novos ao final da planilha do estado
    elif not df_novos.empty and df_arquivados.empty:
        planilha.worksheet(UF).append_rows(df_novos.values.tolist())
        print(f"Dataframes atualizados para o estado {UF}.")
        continue

    # Se não houver registros em df_novos, mas houver em df_arquivados, devemos adicionar esses registros ao final da planilha 'Arquivados' , excluí-los de df_sheets e substituir a planilha respectiva no sheets
    elif df_novos.empty and not df_arquivados.empty:
        planilha.worksheet('Arquivados').append_rows([df_arquivados.columns.values.tolist()] + df_arquivados.values.tolist())
        df_sheets = df_sheets[~df_sheets['ID_imovel'].isin(df_arquivados['ID_imovel'])]
        planilha.worksheet(UF).clear()
        planilha.worksheet(UF).update([df_sheets.columns.values.tolist()] + df_sheets.values.tolist())
        print(f"Dataframes atualizados para o estado {UF}.")
        continue

    # Se houver registros tanto em df_novos quanto em df_arquivados, devemos adicionar os registros de df_arquivados ao final da planilha 'Arquivados' , excluí-los de df_sheets, concatenar df_sheets com df_novos e substituir a planilha respectiva no sheets
    else:
        planilha.worksheet('Arquivados').append_rows([df_arquivados.columns.values.tolist()] + df_arquivados.values.tolist())
        df_sheets = df_sheets[~df_sheets['ID_imovel'].isin(df_arquivados['ID_imovel'])]
        df_sheets = pd.concat([df_sheets, df_novos], ignore_index=True)
        planilha.worksheet(UF).clear()
        planilha.worksheet(UF).update([df_sheets.columns.values.tolist()] + df_sheets.values.tolist())
        print(f"Dataframes atualizados para o estado {UF}.")
        continue