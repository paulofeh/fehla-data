# Bibliotecas e configurações
from flask import Flask, render_template, request, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import pandas as pd
import os

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

# Variáveis a serem passadas para os templates
estados = ['AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO']

# Dicionário de estados
estados_dict = {
    'AC': 'Acre',
    'AL': 'Alagoas',
    'AM': 'Amazonas',
    'AP': 'Amapá',
    'BA': 'Bahia',
    'CE': 'Ceará',
    'DF': 'Distrito Federal',
    'ES': 'Espírito Santo',
    'GO': 'Goiás',
    'MA': 'Maranhão',
    'MG': 'Minas Gerais',
    'MS': 'Mato Grosso do Sul',
    'MT': 'Mato Grosso',
    'PA': 'Pará',
    'PB': 'Paraíba',
    'PE': 'Pernambuco',
    'PI': 'Piauí',
    'PR': 'Paraná',
    'RJ': 'Rio de Janeiro',
    'RN': 'Rio Grande do Norte',
    'RO': 'Rondônia',
    'RR': 'Roraima',
    'RS': 'Rio Grande do Sul',
    'SC': 'Santa Catarina',
    'SE': 'Sergipe',
    'SP': 'São Paulo',
    'TO': 'Tocantins'
}

# Definições e rotas do Flask
app = Flask(__name__)

@app.context_processor
def inject_site_metadata():
    return dict(
        titulo_site="fehla.data",
        subtitulo_site="Portfolio de Jornalismo de Dados de Paulo Fehlauer"
    )

@app.route("/")
def home():
	return render_template("home.html")

@app.route("/projetos")
def projetos():
	return render_template("projetos.html")

@app.route("/bio")
def bio():
	return render_template("bio.html")

@app.route("/imoveis")
def imoveis():
    return render_template("imoveis.html", estados=estados_dict.keys())

@app.route("/mostrar_imoveis", methods=['POST'])
def mostrar_imoveis():
    uf_selecionada = request.form.get('uf')
    return redirect(url_for('mostrar_dados_uf', uf=uf_selecionada))

@app.route("/imoveis/<uf>")
def mostrar_dados_uf(uf):

    sheet = planilha.worksheet(uf)
    dados = sheet.get_all_values()
    df = pd.DataFrame(dados[1:], columns=dados[0])

    # Lista de colunas para converter
    colunas_para_converter = ['Preco', 'Valor_Avaliacao', 'Desconto', 'Area_Total', 'Area_Privativa', 'Area_Terreno', 'Latitude', 'Longitude']

    for coluna in colunas_para_converter:
        df[coluna] = df[coluna].str.replace(',', '.').astype(float)

    menor_valor = df['Preco'].astype(float).idxmin()
    maior_valor = df['Preco'].astype(float).idxmax()
    maior_desconto = df['Desconto'].astype(float).idxmax()

    dados = {
        'mais_barato': df.loc[menor_valor],
        'mais_caro': df.loc[maior_valor],
        'mais_descontado': df.loc[maior_desconto],
        'quantidade_imoveis': len(df)
    }

    return render_template("imoveis_uf.html", uf=estados_dict[uf], dados=dados)

if __name__ == '__main__':
	app.run(debug=True)
    