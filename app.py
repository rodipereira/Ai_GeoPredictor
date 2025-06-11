import streamlit as st
import pandas as pd
import pydeck as pdk
import os
from dotenv import load_dotenv
import google.generativeai as genai
import datetime
import numpy as np

# Carregar variáveis de ambiente (onde a chave da API Gemini estará)
load_dotenv()

# Configurar a API do Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash') # Modelo que funcionou para você
    except Exception as e:
        st.error(f"Erro ao configurar a API da Gemini: {e}. Verifique sua chave e acesso ao modelo 'gemini-2.0-flash'.")
        model = None
else:
    st.error("Chave da API do Google Gemini não configurada. Crie um arquivo .env com GOOGLE_API_KEY='sua_chave_aqui'.")
    model = None

# --- Título e Descrição do Aplicativo ---
st.set_page_config(layout="wide")
st.title("🌎 GeoPredictor: Análise e Previsão Urbana Inteligente")
st.markdown("""
Bem-vindo ao **GeoPredictor**! Esta ferramenta inovadora utiliza dados espaciais e temporais, combinados com Inteligência Artificial (Google Gemini), para analisar padrões urbanos e ambientais em **diversas cidades**. Explore o globo interativo, descubra insights preditivos e tome decisões proativas.
""")

# --- Sidebar para Controles e Filtros ---
st.sidebar.header("⚙️ Controles e Filtros")

# Dicionário de cidades e suas coordenadas centrais e zoom padrão
CITIES = {
    "João Pessoa, PB": {"lat": -7.1197, "lon": -34.8450, "zoom": 12},
    "Recife, PE": {"lat": -8.0476, "lon": -34.8769, "zoom": 11},
    "Natal, RN": {"lat": -5.7950, "lon": -35.2110, "zoom": 11},
    "São Paulo, SP": {"lat": -23.5505, "lon": -46.6333, "zoom": 10},
    "Rio de Janeiro, RJ": {"lat": -22.9068, "lon": -43.1729, "zoom": 11},
    "Brasília, DF": {"lat": -15.7797, "lon": -47.9297, "zoom": 10},
    "Salvador, BA": {"lat": -12.9714, "lon": -38.5014, "zoom": 11},
    "Curitiba, PR": {"lat": -25.4284, "lon": -49.2733, "zoom": 11},
    "Sergipe, SE": {"lat": -10.9472, "lon": -37.0731, "zoom": 11},
    "Lagarto, SE": {"lat": -10.9031, "lon": -37.6464, "zoom": 12},
}

selected_city_name = st.sidebar.selectbox("Selecione a Cidade", list(CITIES.keys()))
selected_city_coords = CITIES[selected_city_name]
center_lat = selected_city_coords["lat"]
center_lon = selected_city_coords["lon"]
initial_zoom = selected_city_coords.get("zoom", 10)

# Mapear dia da semana para nome (para melhor legibilidade)
day_names = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# --- Geração de Dados Simulados Dinâmicos e Espalhados ---
@st.cache_data
def generate_simulated_data(city_lat, city_lon, city_name, start_date_sim, end_date_sim):
    data_records = []
    
    # Funções auxiliares para gerar intensidade com base no dia/hora
    def get_traffic_intensity(hour, day_of_week):
        intensity = 0.2
        if day_of_week < 5: # Dias úteis (Seg-Sex)
            if 7 <= hour <= 9 or 17 <= hour <= 19: # Horários de pico
                intensity = 0.9
            elif 12 <= hour <= 14: # Almoço
                intensity = 0.6
        else: # Fim de semana
            if 10 <= hour <= 18: # Maior fluxo de lazer
                intensity = 0.4
        return min(intensity + np.random.rand() * 0.3, 1.0) # Adiciona aleatoriedade

    def get_tourist_intensity(hour, day_of_week):
        intensity = 0.1
        if day_of_week >= 5: # Fim de semana
            if 9 <= hour <= 18: # Horário de maior movimento
                intensity = 0.9
        else: # Dias úteis
            if 10 <= hour <= 17: # Alguns turistas
                intensity = 0.4
        return min(intensity + np.random.rand() * 0.3, 1.0)

    def get_flood_risk_intensity(hour, day_of_week, rain_forecast_mm):
        intensity = 0.1 # Base sem chuva
        if rain_forecast_mm > 0:
            if rain_forecast_mm > 30 and (6 <= hour <= 10 or 16 <= hour <= 20):
                intensity = 0.9
            elif rain_forecast_mm > 15:
                intensity = 0.6
            else:
                intensity = 0.3
        return min(intensity + np.random.rand() * 0.2, 1.0)

    # --- LOCALIZAÇÕES BASE ESPECÍFICAS PARA JOÃO PESSOA (Em fase de testes) ---
    # Usaremos estas coordenadas se a cidade selecionada for "João Pessoa, PB"
    jp_traffic_locations = [
        {"name": "Av. Epitácio Pessoa (Centro)", "lat": -7.1166, "lon": -34.8385},
        {"name": "Av. Ruy Carneiro (Miramar)", "lat": -7.1200, "lon": -34.8450},
        {"name": "BR-230 (Acesso Gauchinha)", "lat": -7.1350, "lon": -34.8850},
        {"name": "Av. Beira Rio (Bancários)", "lat": -7.1000, "lon": -34.8700},
    ]

    jp_tourist_locations = [
        {"name": "Praia de Tambaú", "lat": -7.1187, "lon": -34.8090},
        {"name": "Praia de Cabo Branco", "lat": -7.1300, "lon": -34.7950},
        {"name": "Farol do Cabo Branco", "lat": -7.1490, "lon": -34.7930},
        {"name": "Parque da Lagoa (Centro)", "lat": -7.1070, "lon": -34.8800},
    ]

    jp_flood_locations = [
        {"name": "Bessa (próximo à BR)", "lat": -7.0900, "lon": -34.8500},
        {"name": "Bancários (área baixa)", "lat": -7.1000, "lon": -34.8700},
        {"name": "Padre Zé (trechos)", "lat": -7.1250, "lon": -34.8600},
    ]

    # --- LOCALIZAÇÕES BASE GENÉRICAS para outras Cidades (ajustadas para melhor dispersão) ---
    # Estes são offsets relativos ao centro da cidade selecionada
    generic_traffic_offsets = [
        {"name": "Av. Principal Norte", "lat_offset": 0.02, "lon_offset": 0.01}, # +- 2.2km N, 1.1km E
        {"name": "Av. Principal Sul", "lat_offset": -0.015, "lon_offset": 0.005}, # +- 1.6km S, 0.5km E
        {"name": "Anel Viário Leste", "lat_offset": 0.005, "lon_offset": -0.025}, # +- 0.5km N, 2.7km W
    ]
    generic_tourist_offsets = [
        {"name": "Ponto Turístico Principal", "lat_offset": 0.01, "lon_offset": -0.03}, # +- 1.1km N, 3.3km W
        {"name": "Praça Histórica Central", "lat_offset": -0.005, "lon_offset": 0.002}, # +- 0.5km S, 0.2km E
    ]
    generic_flood_offsets = [
        {"name": "Área de Baixo Relevo 1", "lat_offset": 0.008, "lon_offset": -0.018}, # +- 0.8km N, 2km W
        {"name": "Região Próxima ao Rio", "lat_offset": -0.012, "lon_offset": 0.01}, # +- 1.3km S, 1.1km E
    ]


    current_date_iter = start_date_sim
    while current_date_iter <= end_date_sim:
        day_of_week = current_date_iter.weekday()
        rain_forecast = np.random.choice([0, 5, 15, 40], p=[0.6, 0.2, 0.15, 0.05])

        for hour in range(0, 24):
            # Escolhe os pontos base dependendo da cidade
            if city_name == "João Pessoa, PB":
                traffic_bases = jp_traffic_locations
                tourist_bases = jp_tourist_locations
                flood_bases = jp_flood_locations
            else:
                # Se não for JP, usa os offsets genéricos a partir do centro da cidade selecionada
                traffic_bases = [{"name": p["name"], "lat": city_lat + p["lat_offset"], "lon": city_lon + p["lon_offset"]} for p in generic_traffic_offsets]
                tourist_bases = [{"name": p["name"], "lat": city_lat + p["lat_offset"], "lon": city_lon + p["lon_offset"]} for p in generic_tourist_offsets]
                flood_bases = [{"name": p["name"], "lat": city_lat + p["lat_offset"], "lon": city_lon + p["lon_offset"]} for p in generic_flood_offsets]

            # Gerar pontos de tráfego
            for loc in traffic_bases:
                lat_jitter = (np.random.rand() - 0.5) * 0.002 # Variação muito pequena para manter perto do local base
                lon_jitter = (np.random.rand() - 0.5) * 0.002
                data_records.append({
                    'lat': loc['lat'] + lat_jitter,
                    'lon': loc['lon'] + lon_jitter,
                    'intensity': get_traffic_intensity(hour, day_of_week) * 10,
                    'type': 'Tráfego Intenso',
                    'location_name': loc['name'],
                    'area': f"Área de Tráfego",
                    'timestamp': datetime.datetime.combine(current_date_iter, datetime.time(hour, 0)),
                    'day_of_week': day_of_week,
                    'rain_forecast_mm': rain_forecast
                })
            
            # Gerar pontos turísticos
            for loc in tourist_bases:
                lat_jitter = (np.random.rand() - 0.5) * 0.001 
                lon_jitter = (np.random.rand() - 0.5) * 0.001
                data_records.append({
                    'lat': loc['lat'] + lat_jitter,
                    'lon': loc['lon'] + lon_jitter,
                    'intensity': get_tourist_intensity(hour, day_of_week) * 10,
                    'type': 'Concentração Turística',
                    'location_name': loc['name'],
                    'area': f"Área Turística",
                    'timestamp': datetime.datetime.combine(current_date_iter, datetime.time(hour, 0)),
                    'day_of_week': day_of_week,
                    'rain_forecast_mm': rain_forecast
                })
            
            # Gerar pontos de risco de alagamento
            for loc in flood_bases:
                lat_jitter = (np.random.rand() - 0.5) * 0.001 
                lon_jitter = (np.random.rand() - 0.5) * 0.001
                data_records.append({
                    'lat': loc['lat'] + lat_jitter,
                    'lon': loc['lon'] + lon_jitter,
                    'intensity': get_flood_risk_intensity(hour, day_of_week, rain_forecast) * 10,
                    'type': 'Risco de Alagamento',
                    'location_name': loc['name'],
                    'area': f"Área de Alagamento",
                    'timestamp': datetime.datetime.combine(current_date_iter, datetime.time(hour, 0)),
                    'day_of_week': day_of_week,
                    'rain_forecast_mm': rain_forecast
                })
        current_date_iter += datetime.timedelta(days=1)

    df = pd.DataFrame(data_records)
    df['day_of_week_name'] = df['day_of_week'].map(lambda x: day_names[x])
    return df

# --- Filtros de Data e Hora ---
st.sidebar.subheader("Filtrar por Data e Hora")
simulated_start_date = datetime.date(2025, 6, 4)
simulated_end_date = datetime.date(2025, 6, 10) 

selected_date = st.sidebar.date_input(
    "Selecione a Data", 
    value=simulated_end_date, 
    min_value=simulated_start_date, 
    max_value=simulated_end_date
)

current_hour = datetime.datetime.now().hour
selected_hour_range = st.sidebar.slider(
    "Selecione o Horário (horas)",
    0, 23, (current_hour, min(current_hour + 1, 23))
)

st.sidebar.subheader("Tipos de Ocorrência")
selected_types_checkboxes = [
    st.sidebar.checkbox("Tráfego Intenso", value=True),
    st.sidebar.checkbox("Concentração Turística", value=True),
    st.sidebar.checkbox("Risco de Alagamento", value=True)
]
type_names = ['Tráfego Intenso', 'Concentração Turística', 'Risco de Alagamento']
active_types = [name for i, name in enumerate(type_names) if selected_types_checkboxes[i]]

data = generate_simulated_data(center_lat, center_lon, selected_city_name, simulated_start_date, simulated_end_date)

filtered_data = data[
    (data['timestamp'].dt.date == selected_date) &
    (data['timestamp'].dt.hour >= selected_hour_range[0]) &
    (data['timestamp'].dt.hour <= selected_hour_range[1]) &
    (data['type'].isin(active_types))
].copy()

filtered_data_typed = {
    'Tráfego Intenso': filtered_data[filtered_data['type'] == 'Tráfego Intenso'],
    'Concentração Turística': filtered_data[filtered_data['type'] == 'Concentração Turística'],
    'Risco de Alagamento': filtered_data[filtered_data['type'] == 'Risco de Alagamento'],
}

# --- Seção do Mapa 3D (Globo) ---
st.header("📊 Visualização Espaço-Temporal no Globo Interativo")
st.markdown(f"Explore o **globo interativo** de **{selected_city_name}** para visualizar os padrões. Use os controles na barra lateral para filtrar os dados por tipo, data e horário.")

view_state = pdk.ViewState(
    latitude=center_lat,
    longitude=center_lon,
    zoom=initial_zoom,
    pitch=50,
    bearing=0
)

layers = []

# --- Funções para mapear intensidade para cores (AGORA MAIS DIRETAS E VIBRANTES) ---
# Retorna uma lista RGBA (0-255) com base na intensidade
def get_traffic_color(intensity):
    if intensity >= 7: return [255, 0, 0, 230]      # Vermelho vibrante (Alto Tráfego)
    elif intensity >= 4: return [255, 140, 0, 200]  # Laranja (Médio Tráfego)
    else: return [0, 200, 0, 180]                   # Verde (Baixo Tráfego)

def get_tourist_color(intensity):
    if intensity >= 7: return [0, 0, 200, 230]      # Azul escuro (Muito Turista)
    elif intensity >= 4: return [0, 100, 255, 200]  # Azul (Turista Moderado)
    else: return [100, 200, 255, 180]               # Azul claro (Pouco Turista)

def get_flood_risk_color(intensity):
    if intensity >= 8: return [178, 34, 34, 230]    # Vermelho Tijolo (Risco Crítico)
    elif intensity >= 5: return [255, 69, 0, 200]   # Vermelho Laranja (Alto Risco)
    elif intensity >= 2: return [255, 215, 0, 180]  # Amarelo Ouro (Risco Moderado)
    else: return [30, 144, 255, 160]                # Azul (Baixo Risco)

# --- Camadas com Tooltips Aprimorados e Cores Bonitas ---

# Camada para Tráfego Intenso (ColumnLayer)
if 'Tráfego Intenso' in active_types and not filtered_data_typed['Tráfego Intenso'].empty:
    traffic_data = filtered_data_typed['Tráfego Intenso']
    layers.append(
        pdk.Layer(
            "ColumnLayer",
            traffic_data,
            get_position=["lon", "lat"],
            get_fill_color=get_traffic_color,
            get_elevation="intensity * 50", # Altura da coluna
            radius=40, # Largura da coluna
            extruded=True,
            pickable=True,
            auto_highlight=True,
            opacity=0.9,
            tooltip={
                "html": "<b>{location_name}</b><br/>"
                        "Tipo: {type}<br/>"
                        "Intensidade: {intensity:.1f} / 10<br/>"
                        "Horário: {timestamp.slice(11,16)}",
                "style": {"backgroundColor": "rgba(50, 50, 50, 0.8)", "color": "white", "font-size": "14px", "padding": "10px", "border-radius": "5px"} # Estilo melhorado
            }
        )
    )

# Camada para Concentração Turística (ScatterplotLayer)
if 'Concentração Turística' in active_types and not filtered_data_typed['Concentração Turística'].empty:
    tourist_data = filtered_data_typed['Concentração Turística']
    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            tourist_data,
            get_position=["lon", "lat"],
            get_color=get_tourist_color,
            get_radius="intensity * 8 + 20", # Raio varia com a intensidade
            pickable=True,
            auto_highlight=True,
            opacity=0.8,
            tooltip={
                "html": "<b>{location_name}</b><br/>"
                        "Tipo: {type}<br/>"
                        "Pessoas: {intensity:.1f} / 10<br/>"
                        "Horário: {timestamp.slice(11,16)}",
                "style": {"backgroundColor": "rgba(50, 50, 50, 0.8)", "color": "white", "font-size": "14px", "padding": "10px", "border-radius": "5px"} # Estilo melhorado
            }
        )
    )

# Camada para Risco de Alagamento (ColumnLayer)
if 'Risco de Alagamento' in active_types and not filtered_data_typed['Risco de Alagamento'].empty:
    flood_data = filtered_data_typed['Risco de Alagamento']
    layers.append(
        pdk.Layer(
            "ColumnLayer",
            flood_data,
            get_position=["lon", "lat"],
            get_elevation="intensity * 60",
            radius=40,
            get_fill_color=get_flood_risk_color,
            extruded=True,
            pickable=True,
            auto_highlight=True,
            opacity=0.9,
            tooltip={
                "html": "<b>{location_name}</b><br/>"
                        "Tipo: {type}<br/>"
                        "Risco: {intensity:.1f} / 10<br/>"
                        "Previsão Chuva: {rain_forecast_mm}mm<br/>"
                        "Horário: {timestamp.slice(11,16)}",
                "style": {"backgroundColor": "rgba(50, 50, 50, 0.8)", "color": "white", "font-size": "14px", "padding": "10px", "border-radius": "5px"} # Estilo melhorado
            }
        )
    )

# Renderizar o mapa Pydeck com as camadas dinâmicas
if layers:
    r = pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11", # Tema escuro para o mapa base
        tooltip={ # Este tooltip global é um fallback, os das camadas são preferíveis
            "html": "<b>{location_name}</b><br/>Tipo: {type}<br/>Intensidade: {intensity:.1f}",
            "style": {"backgroundColor": "rgba(50, 50, 50, 0.8)", "color": "white", "font-size": "14px", "padding": "10px", "border-radius": "5px"}
        }
    )
    st.pydeck_chart(r)
else:
    st.info("Nenhum dado selecionado ou filtrado para exibição no mapa. Ajuste seus filtros na barra lateral!")

# --- Seção de Insights da IA ---
st.subheader("✨ Insights Preditivos da IA")
st.info(f"Aqui, a Inteligência Artificial (Google Gemini) gerará análises e previsões com base nos dados filtrados para **{selected_city_name}**. Os insights serão **acionáveis** para a gestão urbana.")

if st.button("Gerar Insights Preditivos para o Período Selecionado"):
    if model:
        with st.spinner(f"Analisando padrões em {selected_city_name} e gerando insights com a Gemini..."):
            if filtered_data.empty:
                st.warning("Não há dados para o período e filtros selecionados para gerar insights. Ajuste seus filtros e tente novamente.")
            else:
                summary_data = []
                for data_type, df in filtered_data_typed.items():
                    if not df.empty:
                        avg_intensity = df['intensity'].mean()
                        max_intensity = df['intensity'].max()
                        locations = df['location_name'].unique().tolist()
                        areas = df['area'].unique().tolist()
                        
                        summary_data.append(
                            f"- Tipo: {data_type}\n"
                            f"  Locais Afetados: {', '.join(locations)}\n"
                            f"  Áreas Geográficas: {', '.join(areas)}\n"
                            f"  Intensidade Média: {avg_intensity:.1f} (de 10)\n"
                            f"  Pico de Intensidade: {max_intensity:.1f} (de 10)\n"
                        )
                
                day_name_for_ai = day_names[selected_date.weekday()]
                current_rain_forecast = data[data['timestamp'].dt.date == selected_date]['rain_forecast_mm'].iloc[0] if not data.empty else 0


                prompt_text = (
                    f"Você é um analista de dados urbanos para a cidade de **{selected_city_name}**, utilizando um sistema de previsão com IA.\n"
                    f"A data de análise é {selected_date.strftime('%d/%m/%Y')} e o período de interesse é das {selected_hour_range[0]}h às {selected_hour_range[1]}h. "
                    f"O dia da semana é {day_name_for_ai}. A previsão de chuva simulada para este dia é de {current_rain_forecast}mm.\n\n"
                    f"**Dados Observados para o Período e Local Selecionados:**\n"
                    f"{'Não há ocorrências significativas para este período e localização.' if not summary_data else ' '.join(summary_data)}\n\n"
                    f"Com base nesses dados e no conhecimento de padrões urbanos típicos (tráfego de pico, fluxo turístico, áreas de alagamento) para uma cidade como {selected_city_name}: \n"
                    f"1. **Análise dos Padrões:** Descreva de forma concisa o que está acontecendo ou o que é esperado acontecer em **{selected_city_name}** durante o período selecionado, destacando as áreas e tipos de ocorrência mais relevantes.\n"
                    f"2. **Previsão Futura:** Com base nos padrões históricos (implícitos no dataset simulado) e nos dados atuais, preveja como a situação pode evoluir nas **próximas 2-4 horas** em **{selected_city_name}**.\n"
                    f"3. **Recomendações Acionáveis:** Forneça 2-3 recomendações específicas e práticas para os órgãos responsáveis (Ex: Secretaria de Trânsito, Defesa Civil, Secretaria de Turismo, etc.) para gerenciar a situação ou otimizar recursos em **{selected_city_name}**.\n"
                    f"Formate sua resposta em seções claras: **Análise dos Padrões**, **Previsão Futura** e **Recomendações Acionáveis**."
                )

                try:
                    response = model.generate_content(prompt_text)
                    st.markdown(f"**Análise da Gemini para {selected_city_name} em {selected_date.strftime('%d/%m/%Y')} das {selected_hour_range[0]}h às {selected_hour_range[1]}h ({day_name_for_ai}):**")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Erro ao chamar a API da Gemini. Verifique sua chave ou cota de uso: {e}")
                    st.warning("Tente ajustar os filtros ou o prompt se o erro persistir. Certifique-se de que a chave da API está correta e que você tem conexão com a internet.")

# --- Rodapé ---
st.markdown("---")
st.markdown("Construído com ❤️ usando Streamlit, Pydeck e Google Gemini API.")