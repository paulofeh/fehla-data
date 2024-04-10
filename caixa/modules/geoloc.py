"""
Funções para obter as coordenadas geográficas de um endereço
Acabou não sendo utilizada no projeto final	por impactar muito no tempo de execução
"""

from geopy import geocoders
import os
from dotenv import load_dotenv

load_dotenv()
maps_api = os.environ.get("MAPS_API")
g = geocoders.GoogleV3(api_key=maps_api)

def obtem_coordenadas(address):
    """
    Função para obter as coordenadas geográficas de um endereço
    """
    location = g.geocode(address, timeout=10)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None
    

def processar_lotes(df):
    """
    Função para processar em lotes os registros de um DataFrame, a fim de contornar limitações de uso da API do Google Maps
    """

    latitudes = []
    longitudes = []
    
    for index, row in df.iterrows():
        latitude, longitude = obtem_coordenadas(row['Endereco_Completo'])
        latitudes.append(latitude)
        longitudes.append(longitude)
    
    return latitudes, longitudes