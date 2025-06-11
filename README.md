# **🌎 GeoPredictor: Análise e Previsão Urbana Inteligente com IA**

![GeoPredictor Screenshot - Mapa 3D com dados](https://raw.githubusercontent.com/seu-usuario/seu-repositorio/main/docs/screenshot_map.png)
*(**Importante:** Substitua esta URL pela URL de um screenshot real do seu mapa, hospedado no seu repositório GitHub, por exemplo, dentro de uma pasta `docs/`!)*

## **💡 Visão Geral do Projeto**

O **GeoPredictor** é um inovador Software as a Service (SaaS) projetado para fornecer insights preditivos sobre padrões urbanos e ambientais em diversas cidades. Utilizando o poder do processamento de dados geoespaciais e temporais, combinado com a inteligência artificial generativa do Google Gemini (modelo `gemini-2.0-flash`), a ferramenta visa auxiliar gestores urbanos, profissionais de segurança, turismo e meio ambiente na tomada de decisões proativas e na otimização de recursos.

A aplicação é desenvolvida em Python usando o framework [Streamlit](https://streamlit.io/), oferecendo uma interface de usuário intuitiva e interativa com visualizações de dados 3D imersivas em um globo interativo.

## **✨ Funcionalidades Principais**

* **Seleção de Cidades:** Permite ao usuário escolher entre uma lista pré-definida de cidades brasileiras para análise. Para João Pessoa, PB, a simulação de dados é mais específica, utilizando coordenadas aproximadas de locais reais de interesse.
* **Visualização Espaço-Temporal 3D:** Exibe dados simulados de tráfego intenso, concentração turística e risco de alagamento em um mapa-múndi interativo (globo) renderizado com Pydeck. As visualizações são em 3D (colunas e pontos coloridos) com cores vibrantes que indicam a intensidade de cada ocorrência.
* **Filtros Dinâmicos:** Filtra os dados exibidos por data, faixa de horário e tipo de ocorrência, permitindo uma análise granular e focada.
* **Dados Simulados Detalhados:** Gera conjuntos de dados de exemplo que simulam padrões urbanos e ambientais ao longo de vários dias e horários. Para João Pessoa, as simulações se baseiam em localizações geográficas mais próximas de pontos conhecidos (avenidas, praias, áreas de risco).
* **Insights Preditivos com IA (Google Gemini):**
    * **Análise de Padrões:** A IA processa os dados filtrados e descreve de forma concisa o que está acontecendo ou o que é esperado acontecer na cidade e período selecionados.
    * **Previsão Futura:** Fornece previsões sobre como a situação pode evoluir nas próximas 2-4 horas.
    * **Recomendações Acionáveis:** Gera sugestões específicas e práticas para os órgãos responsáveis (Ex: Secretarias de Trânsito, Defesa Civil, Turismo) para gerenciar a situação ou otimizar recursos.
* **Interface Intuitiva e Responsiva:** Construído com Streamlit para uma experiência de usuário simples, rápida e adaptável a diferentes tamanhos de tela.

## **🎯 Casos de Uso Potenciais**

* **Gestão de Tráfego:** Prever congestionamentos em horários de pico ou durante eventos e sugerir rotas alternativas ou ajustes de semáforos.
* **Segurança Pública:** Identificar "hotspots" de ocorrências e otimizar o planejamento de patrulhamento.
* **Planejamento de Eventos e Turismo:** Antecipar a concentração de pessoas em áreas turísticas ou de eventos para melhor alocação de serviços e infraestrutura.
* **Defesa Civil:** Prever riscos de alagamento com base em dados simulados de chuva e histórico de áreas vulneráveis, auxiliando na emissão de alertas e ações preventivas.
* **Otimização de Serviços Urbanos:** Melhorar a alocação de equipes de limpeza, saúde e manutenção em áreas de maior necessidade.

## **🛠️ Tecnologias Utilizadas**

* **Python 3.8+:** Linguagem de programação principal.
* **[Streamlit](https://streamlit.io/):** Framework para construção rápida de aplicações web interativas (SaaS).
* **[Pydeck](https://pydeck.gl/):** Biblioteca Python para visualização de dados geoespaciais em 3D sobre mapas interativos.
* **[Google Gemini API](https://ai.google.dev/models/gemini):** Acesso aos modelos de IA generativa do Google (especificamente `gemini-2.0-flash`) para análise de texto e geração de insights.
* **[Pandas](https://pandas.pydata.org/):** Poderosa biblioteca para manipulação e análise de dados.
* **[NumPy](https://numpy.org/):** Suporte para operações numéricas.
* **[python-dotenv](https://pypi.org/project/python-dotenv/):** Para carregamento seguro de variáveis de ambiente.
* **[Matplotlib.colors](https://matplotlib.org/stable/api/colors_api.html):** Utilizado internamente para auxiliar no mapeamento de cores.

## **🚀 Como Configurar e Executar Localmente**

Siga estas etapas detalhadas para ter o GeoPredictor rodando em sua máquina:

### **Pré-requisitos**

* Python 3.8+ instalado.
* Conexão à internet (necessária para acessar a API do Google Gemini e o mapa base do Mapbox).
* Uma chave da API do Google Gemini. Você pode obtê-la gratuitamente em [Google AI Studio](https://aistudio.google.com/app/apikey).

### **Passos de Instalação**

1.  **Crie a Pasta do Projeto:**
    ```bash
    mkdir geopredictor_saas
    cd geopredictor_saas
    ```

2.  **Crie e Ative o Ambiente Virtual:**
    É altamente recomendado usar um ambiente virtual para isolar as dependências do seu projeto.
    ```bash
    python3 -m venv streamlit_env
    ```
    **Ative o ambiente virtual:**
    * **No Windows (usando Git Bash ou WSL):**
        ```bash
        source streamlit_env/Scripts/activate
        ```
    * **No macOS/Linux:**
        ```bash
        source streamlit_env/bin/activate
        ```
    (Você saberá que está ativo se `(streamlit_env)` aparecer no início da sua linha de comando.)

3.  **Crie o Arquivo `requirements.txt`:**
    Crie um arquivo chamado `requirements.txt` na raiz da pasta `geopredictor_saas` e adicione o seguinte conteúdo:
    ```
    streamlit
    pandas
    numpy
    pydeck
    python-dotenv
    google-generativeai
    matplotlib
    ```

4.  **Instale as Dependências:**
    Com o ambiente virtual ativado, execute este comando para instalar todas as bibliotecas necessárias:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Configure a Chave da API do Google Gemini:**
    Crie um arquivo chamado `.env` na raiz da pasta `geopredictor_saas`. **Este arquivo é sensível e não deve ser compartilhado publicamente (e.g., commitado para o GitHub)!**
    Adicione sua chave da API nele:
    ```
    GOOGLE_API_KEY='SUA_CHAVE_AQUI'
    ```
    **Substitua `'SUA_CHAVE_AQUI'` pela sua chave real da API do Google Gemini.**

6.  **Crie o Arquivo `app.py`:**
    Crie um arquivo chamado `app.py` na raiz da pasta `geopredictor_saas` e cole **todo o código Python fornecido na nossa última interação**.

### **Como Executar a Aplicação**

Com o ambiente virtual ativado e todos os arquivos configurados, execute o seguinte comando no terminal:

```bash
streamlit run app.py

## **🖥️ Uso da Aplicação**

### **Interagindo com a Interface**

1.  **Seleção de Cidade:** No menu lateral (sidebar à esquerda), escolha a cidade que deseja analisar. O mapa 3D se centralizará nessa localização.
2.  **Filtros de Data e Horário:** Ajuste a data (dentro do período simulado de 04 a 10 de junho de 2025) e a faixa de horário para visualizar os padrões específicos nesse período.
3.  **Tipos de Ocorrência:** Marque ou desmarque as caixas de seleção na sidebar para exibir ou ocultar as camadas de "Tráfego Intenso", "Concentração Turística" e "Risco de Alagamento" no mapa.
4.  **Interação com o Mapa:**
    * **Girar o Globo 3D:** Clique e arraste o mapa.
    * **Ampliar/Reduzir (Zoom):** Use o scroll do mouse.
    * **Mover o Mapa (Pan):** Pressione `Shift` e clique e arraste.
    * **Tooltips:** Passe o mouse sobre as colunas ou pontos para ver os detalhes (nome do local, tipo, intensidade e horário).
5.  **Gerar Insights:** Clique no botão "Gerar Insights Preditivos para o Período Selecionado". A IA da Google Gemini analisará os dados filtrados e fornecerá uma análise detalhada, previsão futura e recomendações acionáveis.

## **📊 Estrutura de Dados Simulados**

Os dados são gerados em tempo real na aplicação para demonstrar as funcionalidades e são adaptados para a cidade selecionada. Eles contêm as seguintes colunas essenciais:

* `lat`, `lon`: Coordenadas geográficas (latitude e longitude) dos pontos onde as ocorrências simuladas são registradas.
* `intensity`: Nível de intensidade da ocorrência (escalado de 1 a 10), representando o grau de tráfego, concentração de pessoas ou risco de alagamento. Valores mais altos indicam maior intensidade.
* `type`: Categoria da ocorrência, podendo ser:
    * `Tráfego Intenso`
    * `Concentração Turística`
    * `Risco de Alagamento`
* `location_name`: Nome descritivo da localização simulada (ex: "Av. Epitácio Pessoa (Centro)", "Praia Central", "Bairro Baixo 1").
* `timestamp`: Data e hora exata da ocorrência simulada.
* `day_of_week`, `day_of_week_name`: Dia da semana da ocorrência (número e nome para melhor legibilidade).
* `rain_forecast_mm`: Simulação de previsão de chuva em milímetros para o dia e local (usado principalmente para o cálculo do risco de alagamento).

Para a cidade de **João Pessoa, PB**, são utilizadas coordenadas aproximadas de locais reais e conhecidos para simular padrões mais fiéis à geografia e dinâmica da cidade. Para as demais cidades, a simulação utiliza offsets genéricos a partir do centro da cidade para criar áreas de interesse distintas e visualmente dispersas.