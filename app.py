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

    # Aqui você pode acessar a planilha e passar os dados para o template
    sheet = planilha.worksheet(uf)
    dados = sheet.get_all_values()
    df = pd.DataFrame(dados[1:], columns=dados[0])

    df['Valor_Avaliacao'] = df['Valor_Avaliacao'].str.replace(',', '.').astype(float)
    df['Preco'] = df['Preco'].str.replace(',', '.').astype(float)
    menor_valor = df['Preco'].astype(float).idxmin()
    mais_barato = df.loc[menor_valor]

    return render_template("imoveis_uf.html", uf=estados_dict[uf], dados=mais_barato)

if __name__ == '__main__':
	app.run(debug=True)
    