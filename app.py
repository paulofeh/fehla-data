"""
Aplicação web para exibição de um portfolio de projetos em jornalismo de dados
Inclui aplicação para visualização de dados de imóveis da Caixa Econômica Federal
Autor: Paulo Fehlauer
Data: 2024-04-10
Versão: 0.1
Licença: MIT
"""

# Módulos nativos do Python
import os

# Bibliotecas de terceiros
from flask import Flask, render_template, request, redirect, url_for
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import pandas as pd
# import folium (para futuras implementações de mapas interativos)

# Bibliotecas locais
from caixa.modules.planilhas import formata_moeda


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

# Injeção de contexto - padroniza os metadados do site
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

# Rota para mostrar os imóveis de um estado
@app.route("/mostrar_imoveis", methods=['POST'])
def mostrar_imoveis():
    uf_selecionada = request.form.get('uf')
    return redirect(url_for('mostrar_dados_uf', uf=uf_selecionada))

# Rota para mostrar os dados do estado selecionado
@app.route("/imoveis/<uf>")
def mostrar_dados_uf(uf):

    # Obtém os dados da planilha e converte para DataFrame
    sheet = planilha.worksheet(uf)
    dados = sheet.get_all_values()
    df = pd.DataFrame(dados[1:], columns=dados[0])

    # Limpeza e conversão de dados
    # Lista de colunas para converter
    colunas_para_converter = ['Preco', 'Valor_Avaliacao', 'Desconto', 'Area_Total', 'Area_Privativa', 'Area_Terreno']
    for coluna in colunas_para_converter:
        df[coluna] = df[coluna].str.replace(',', '.').astype(float)

    # Filtrar imóveis com Preco >= 100
    # Exclui imóveis com erro de preenchimento no campo Preço
    df_filtrado = df[df['Preco'].astype(float) >= 100]

    # Dados para exibição
    # Obtém os 3 imóveis mais baratos e mais caros, bem como seus preços
    mais_baratos = df_filtrado.nsmallest(3, 'Preco').to_dict('records')
    mais_caros = df_filtrado.nlargest(3, 'Preco').to_dict('records')
    mais_barato_valor = formata_moeda(df_filtrado['Preco'].min())
    mais_caro_valor = formata_moeda(df_filtrado['Preco'].max())

    # Obtém o imóvel com o maior desconto
    mais_descontado = df_filtrado.nlargest(1, 'Desconto').to_dict('records')[0]

    # Obtém a quantidade de imóveis com desconto maior que zero
    # Ignora casos em que o desconto é zero ou negativo
    quantidade_desconto = df_filtrado[df_filtrado['Desconto'] > 0].shape[0]

    # Obtém o preço médio dos imóveis
    preco_medio = df_filtrado['Preco'].mean().round(2)
    preco_medio = formata_moeda(preco_medio)

    # Obtém o tipo de imóvel mais comum
    tipo_comum = df_filtrado['Tipo_Imovel'].mode()[0]

    # Obtém a modalidade de venda mais comum
    modalidade_comum = df_filtrado['Modalidade_venda'].mode()[0]

    # Porcentagem de venda direta
    # Soma as modalidades de Venda Direta Online e Venda Online
    venda_direta = df_filtrado['Modalidade_venda'].str.contains('Venda Direta Online|Venda Online').sum()/len(df_filtrado)*100

    # Estrutura de dados para exibição
    dados = {
        'mais_baratos': mais_baratos,
        'mais_barato_valor': mais_barato_valor,
        'mais_caro_valor': mais_caro_valor,
        'mais_caros': mais_caros,
        'mais_descontado': mais_descontado,
        'quantidade_imoveis': len(df),
        'quantidade_desconto': quantidade_desconto,
        'preco_medio': preco_medio,
        'modalidade': modalidade_comum,
        'venda_direta': f'{venda_direta:.2f}%',
        'tipo_comum': tipo_comum
    }


    """
    # Cria um mapa a partir dos dados de cada estado
    # Removido pois tornou o carregamento da página muito lento
    
    latitude_inicial = df['Latitude'].mean()
    longitude_inicial = df['Longitude'].mean()
    m = folium.Map([latitude_inicial, longitude_inicial], zoom_start=7)

    # Itere sobre as linhas do DataFrame
    for index, row in df.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            tooltip=row['Endereco'],
            popup=row['Descricao'],
            icon=folium.Icon(color='red')
        ).add_to(m)
    
    # Converter o mapa para HTML
    mapa_html = m._repr_html_()

    """

    return render_template("imoveis_uf.html", uf=estados_dict[uf], dados=dados)


if __name__ == '__main__':
	app.run(debug=True)