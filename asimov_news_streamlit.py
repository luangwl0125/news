import streamlit as st
import os
import time
from datetime import datetime
import pickle
import webbrowser
from math import ceil
import threading

from scraping_sites.site import *

class AsimovNewsStreamlit:
    def __init__(self):
        self.dict_site = {}
        self.all_sites = ['veja', 'r7', 'cnn', 'globo']
        
        # Inicializar dados
        self.news = self._read_file('news') if 'news' in os.listdir() else []
        self._update_file(self.news, 'news')
        self.sites = self._read_file('sites') if 'sites' in os.listdir() else []
        self._update_file(self.sites, 'sites')

        # Inicializar sites
        for site in self.all_sites:
            self.dict_site[site] = Site(site)

    def _update_file(self, lista, mode='news'):
        with open(mode, 'wb') as fp:
            pickle.dump(lista, fp)

    def _read_file(self, mode='news'):
        with open(mode, 'rb') as fp:
            n_list = pickle.load(fp)
            return n_list

    def update_news(self):
        """Atualiza as notícias de todos os sites"""
        for site in self.all_sites:
            self.dict_site[site].update_news()

            for key, value in self.dict_site[site].news.items():
                dict_aux = {}
                dict_aux['data'] = datetime.now()
                dict_aux['fonte'] = site  
                dict_aux['materia'] = key
                dict_aux['link'] = value

                if len(self.news) == 0:
                    self.news.insert(0, dict_aux)
                    continue
                
                add_news = True
                for news in self.news:
                    if dict_aux["materia"] == news["materia"] and dict_aux["fonte"] == news["fonte"]:
                        add_news = False
                        break

                if add_news:
                    self.news.insert(0, dict_aux)
        
        self.news = sorted(self.news, key=lambda d: d['data'], reverse=True)
        self._update_file(self.news, 'news')

    def display_news(self, page=1, items_per_page=10):
        """Exibe as notícias filtradas por página"""
        self.filtered_news = [i for i in self.news if i["fonte"] in self.sites]
        self.max_page = ceil(len(self.filtered_news) / items_per_page)

        if page > self.max_page: 
            page = 1

        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        return self.filtered_news[start_idx:end_idx], self.max_page

def main():
    st.set_page_config(
        page_title="Asimov News",
        page_icon="📰",
        layout="wide"
    )
    
    # Navegação
    st.sidebar.title("📰 Asimov News")
    page = st.sidebar.selectbox(
        "Escolha uma página:",
        ["📰 Notícias", "⚽ Análise Esportiva"]
    )
    
    if page == "📰 Notícias":
        show_news_page()
    elif page == "⚽ Análise Esportiva":
        show_sports_page()

def show_news_page():
    st.title("📰 Últimas Notícias")
    st.markdown("---")
    
    # Inicializar app
    if 'asimov_news' not in st.session_state:
        st.session_state.asimov_news = AsimovNewsStreamlit()
        st.session_state.page = 1
    
    app = st.session_state.asimov_news
    
    # Sidebar para configurações (apenas na página de notícias)
    with st.sidebar:
        st.header("⚙️ Configurações")
        
        # Gerenciar sites ativos
        st.subheader("Sites Ativos")
        for site in app.all_sites:
            if st.checkbox(
                site.upper(), 
                value=site in app.sites,
                key=f"site_{site}"
            ):
                if site not in app.sites:
                    app.sites.append(site)
                    app._update_file(app.sites, 'sites')
            else:
                if site in app.sites:
                    app.sites.remove(site)
                    app._update_file(app.sites, 'sites')
        
        st.markdown("---")
        
        # Botão para atualizar notícias
        if st.button("🔄 Atualizar Notícias"):
            with st.spinner("Atualizando notícias..."):
                app.update_news()
            st.success("Notícias atualizadas!")
            st.rerun()
        
        st.markdown("---")
        st.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Área principal
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Exibir notícias
        news_items, max_page = app.display_news(st.session_state.page)
        
        if not news_items:
            st.info("Nenhuma notícia encontrada. Adicione sites ativos ou atualize as notícias.")
        else:
            for i, article in enumerate(news_items):
                with st.container():
                    st.markdown(f"### {article['materia']}")
                    st.markdown(f"**Fonte:** {article['fonte'].upper()} | **Data:** {article['data'].strftime('%d/%m/%Y %H:%M')}")
                    
                    if st.button(f"🔗 Abrir Link", key=f"link_{i}"):
                        webbrowser.open(article['link'])
                    
                    st.markdown("---")
        
        # Paginação
        if max_page > 1:
            col_prev, col_info, col_next = st.columns([1, 2, 1])
            
            with col_prev:
                if st.button("⬅️ Anterior") and st.session_state.page > 1:
                    st.session_state.page -= 1
                    st.rerun()
            
            with col_info:
                st.markdown(f"**Página {st.session_state.page} de {max_page}**")
            
            with col_next:
                if st.button("Próxima ➡️") and st.session_state.page < max_page:
                    st.session_state.page += 1
                    st.rerun()

def show_sports_page():
    """Exibe a página de análise esportiva"""
    st.title("⚽ Análise Esportiva")
    st.markdown("---")
    
    # Importar dependências necessárias
    try:
        import statistics
        from lxml import html
        from bs4 import BeautifulSoup, Comment
        import pandas as pd
        import requests
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        import plotly.graph_objects as go
        import plotly.express as px
        
        # Dicionários de times
        teams_adress_A = {
            'palmeiras': 'palmeiras/1963', 'internacional': 'internacional/1966', 'flamengo': 'flamengo/5981', 'fluminense': 'fluminense/1961',
            'corinthians': 'corinthians/1957', 'athletico paranaense': 'athletico/1967', 'atletico mineiro': 'atletico-mineiro/1977',
            'america mineiro': 'america-mineiro/1973', 'fortaleza': 'fortaleza/2020', 'botafogo': 'botafogo/1958', 'santos': 'santos/1968',
            'sao paulo': 'sao-paulo/1981', 'bragantino': 'red-bull-bragantino/1999', 'goias': 'goias/1960', 'coritiba': 'coritiba/1982',
            'ceara': 'ceara/2001', 'cuiaba': 'cuiaba/49202', 'atletico goianiense': 'atletico-goianiense/7314', 'avai': 'avai/7315', 'juventude': 'juventude/1980'
        }

        teams_adress_B = {
            'cruzeiro': 'cruzeiro/1954', 'gremio': 'gremio/5926', 'vasco': 'vasco-da-gama/1974', 'bahia': 'bahia/1955', 'ituano': 'ituano/2025',
            'londrina': 'londrina/2022', 'sport': 'sport-recife/1959', 'sampaio correa': 'sampaio-correa/2005', 'criciuma': 'criciuma/1984', 'crb': 'crb/22032',
            'guarani': 'guarani/1972', 'vila nova': 'vila-nova/2021', 'ponte preta': 'ponte-preta/1969', 'tombense': 'tombense/87202', 'chapecoense': 'chapecoense/21845',
            'csa': 'csa/2010', 'novorizontino': 'novorizontino/135514', 'brusque': 'brusque-fc/21884', 'operario': 'operario/39634', 'nautico': 'nautico/2011'
        }

        browsers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome / 86.0.4240.198Safari / 537.36"}
        base_api = 'https://api.sofascore.com/api/v1/team/'
        end_api = '/statistics/overall'
        pd.options.display.max_rows = 150
        
        def escolhe_time(time: str, division: str):
            """Coleta dados estatísticos de um time específico"""
            data_list = []
            cont_data_list = 0

            if division == 'A':
                serie = '325'
                id_time = teams_adress_A[time.lower()][-4:]
                enpoint_17 = '13100'
                enpoint_18 = '16183'
                enpoint_19 = '22931'
                enpoint_20 = '27591'
                enpoint_21 = '36166'
                enpoint_22 = '40557'
            elif division == 'B':
                serie = '390'
                id_time = teams_adress_B[time.lower()][-4:]
                enpoint_17 = ''
                enpoint_18 = '16184'
                enpoint_19 = '22932'
                enpoint_20 = '27593'
                enpoint_21 = '36162'
                enpoint_22 = '40560'

            middle_api = f'/unique-tournament/{serie}/season/'

            url_17 = base_api + id_time + middle_api + enpoint_17 + end_api
            url_18 = base_api + id_time + middle_api + enpoint_18 + end_api
            url_19 = base_api + id_time + middle_api + enpoint_19 + end_api
            url_20 = base_api + id_time + middle_api + enpoint_20 + end_api
            url_21 = base_api + id_time + middle_api + enpoint_21 + end_api
            url_22 = base_api + id_time + middle_api + enpoint_22 + end_api

            urls_list = [url_17, url_18, url_19, url_20, url_21, url_22]

            for url in urls_list:
                if url.endswith(end_api) and not url.endswith('//statistics/overall'):
                    try:
                        api_link = requests.get(url, headers=browsers).json()
                        if not 'error' in api_link:
                            data_list.append(api_link['statistics'])
                            if urls_list.index(url) == 0:
                                data_list[cont_data_list]['ano'] = 2017
                            elif urls_list.index(url) == 1:
                                data_list[cont_data_list]['ano'] = 2018
                            elif urls_list.index(url) == 2:
                                data_list[cont_data_list]['ano'] = 2019
                            elif urls_list.index(url) == 3:
                                data_list[cont_data_list]['ano'] = 2020
                            elif urls_list.index(url) == 4:
                                data_list[cont_data_list]['ano'] = 2021
                            elif urls_list.index(url) == 5:
                                data_list[cont_data_list]['ano'] = 2022
                            cont_data_list += 1
                    except Exception as e:
                        st.warning(f"Erro ao coletar dados para {url}: {str(e)}")

            return data_list

        def build_dataframe(time: str, division: str):
            """Constrói DataFrame com estatísticas do time"""
            team = escolhe_time(time.lower(), division)
            
            if not team:
                return None

            team_dataframe = pd.DataFrame(index=team[0].keys())

            for i in range(len(team)):
                team_dataframe[str(team[i]['ano'])] = team[i].values()
                team_dataframe[str(team[i]['ano'])] = team_dataframe[str(team[i]['ano'])].apply(lambda x: float("{:.0f}".format(x)))

            team_dataframe['Media'] = team_dataframe.mean(axis=1).apply(lambda x: float("{:.1f}".format(x)))

            return team_dataframe

        def build_chart(metric: str, time1: str, time2: str, division1: str, division2: str):
            """Constrói gráfico comparativo entre dois times"""
            df_time1 = build_dataframe(time1.lower(), division1)
            df_time2 = build_dataframe(time2.lower(), division2)
            
            if df_time1 is None or df_time2 is None:
                st.error("Não foi possível obter dados para um ou ambos os times.")
                return None
            
            anos = ['2017', '2018', '2019', '2020', '2021', '2022']
            
            dados_time1 = []
            dados_time2 = []
            
            for ano in anos:
                if ano in df_time1.columns and metric in df_time1.index:
                    dados_time1.append(df_time1[ano][metric])
                else:
                    dados_time1.append(0)
                    
                if ano in df_time2.columns and metric in df_time2.index:
                    dados_time2.append(df_time2[ano][metric])
                else:
                    dados_time2.append(0)

            fig = go.Figure(
                data=[
                    go.Bar(name=time1.title(), x=anos, y=dados_time1, marker_color='#1f77b4'),
                    go.Bar(name=time2.title(), x=anos, y=dados_time2, marker_color='#ff7f0e')
                ]
            )
            
            fig.update_layout(
                title=f"Comparação: {metric}",
                xaxis_title="Ano",
                yaxis_title=metric,
                barmode='group',
                height=500
            )
            
            return fig

        # Interface da página esportiva
        with st.sidebar:
            st.header("🔧 Configurações")
            
            st.subheader("Time 1")
            division1 = st.selectbox("Divisão Time 1:", ["A", "B"], key="div1")
            
            if division1 == "A":
                time1 = st.selectbox("Time 1:", list(teams_adress_A.keys()), key="time1")
            else:
                time1 = st.selectbox("Time 1:", list(teams_adress_B.keys()), key="time1")
            
            st.markdown("---")
            
            st.subheader("Time 2")
            division2 = st.selectbox("Divisão Time 2:", ["A", "B"], key="div2")
            
            if division2 == "A":
                time2 = st.selectbox("Time 2:", list(teams_adress_A.keys()), key="time2")
            else:
                time2 = st.selectbox("Time 2:", list(teams_adress_B.keys()), key="time2")
        
        # Área principal
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader(f"📊 Estatísticas - {time1.title()}")
            
            if st.button(f"Carregar dados do {time1.title()}", key="btn1"):
                with st.spinner(f"Carregando dados do {time1.title()}..."):
                    df1 = build_dataframe(time1, division1)
                    if df1 is not None:
                        st.dataframe(df1, use_container_width=True)
                        st.session_state.df1 = df1
                    else:
                        st.error(f"Não foi possível carregar dados do {time1.title()}")
        
        with col2:
            st.subheader(f"📊 Estatísticas - {time2.title()}")
            
            if st.button(f"Carregar dados do {time2.title()}", key="btn2"):
                with st.spinner(f"Carregando dados do {time2.title()}..."):
                    df2 = build_dataframe(time2, division2)
                    if df2 is not None:
                        st.dataframe(df2, use_container_width=True)
                        st.session_state.df2 = df2
                    else:
                        st.error(f"Não foi possível carregar dados do {time2.title()}")
        
        # Comparação
        st.markdown("---")
        st.subheader("📈 Comparação entre Times")
        
        if 'df1' in st.session_state and 'df2' in st.session_state:
            df1 = st.session_state.df1
            df2 = st.session_state.df2
            
            metricas_disponiveis = list(set(df1.index) & set(df2.index))
            
            if metricas_disponiveis:
                metrica = st.selectbox("Selecione a métrica para comparação:", metricas_disponiveis)
                
                if st.button("Gerar Gráfico Comparativo"):
                    fig = build_chart(metrica, time1, time2, division1, division2)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tabela comparativa
                        st.subheader("📋 Tabela Comparativa")
                        comparacao = pd.DataFrame({
                            'Ano': ['2017', '2018', '2019', '2020', '2021', '2022'],
                            f'{time1.title()}': [df1[ano][metrica] if ano in df1.columns else 0 for ano in ['2017', '2018', '2019', '2020', '2021', '2022']],
                            f'{time2.title()}': [df2[ano][metrica] if ano in df2.columns else 0 for ano in ['2017', '2018', '2019', '2020', '2021', '2022']]
                        })
                        st.dataframe(comparacao, use_container_width=True)
            else:
                st.warning("Não há métricas em comum entre os dois times selecionados.")
        else:
            st.info("Carregue os dados de ambos os times para fazer a comparação.")
        
        # Informações adicionais
        st.markdown("---")
        with st.expander("ℹ️ Sobre os Dados"):
            st.markdown("""
            **Fonte dos Dados:** SofaScore API
            
            **Período:** 2017-2022
            
            **Divisões:**
            - **Série A:** Primeira divisão do Campeonato Brasileiro
            - **Série B:** Segunda divisão do Campeonato Brasileiro
            
            **Observações:**
            - Alguns times podem não ter dados para todos os anos
            - Os dados são atualizados conforme disponibilidade da API
            - Métricas podem variar dependendo da divisão do time
            """)
            
    except ImportError as e:
        st.error(f"Erro ao importar dependências: {str(e)}")
        st.info("Verifique se todas as dependências estão instaladas: `pip install -r requirements.txt`")
    except Exception as e:
        st.error(f"Erro inesperado: {str(e)}")
        st.info("Verifique se todas as dependências estão instaladas corretamente.")

if __name__ == "__main__":
    main() 