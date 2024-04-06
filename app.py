# Bibliotecas e configurações
from flask import Flask, render_template, jsonify, request
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
    return render_template("imoveis.html", estados=estados)

@app.route('/buscar_dados', methods=['POST'])
def buscar_dados():
    uf_selecionada = request.json['uf']  

    # Acessa a planilha
    sheet = planilha.worksheet(uf_selecionada)

    # Obtenha todos os valores da planilha
    valores = sheet.get_all_values()

    # Conte o número de registros (desconsiderando a linha de cabeçalho)
    numero_registros = len(valores) - 1  # Desconte 1 para a linha de cabeçalho, se aplicável

    dados = {'uf': uf_selecionada, 'dados': [numero_registros]}

    return jsonify(dados)


if __name__ == '__main__':
	app.run(debug=True)
    