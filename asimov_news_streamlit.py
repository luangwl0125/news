import streamlit as st
import os
import time
from datetime import datetime
import pickle
import webbrowser
from math import ceil
import threading

from scraping_sites.site import *

import requests

API_TOKEN = "a0244139fd9442bd819669867ba661d7"
HEADERS = {"X-Auth-Token": API_TOKEN}

def get_brasileirao_standings():
    url = "https://api.football-data.org/v4/competitions/BSA/standings"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    if "standings" in data:
        return data['standings'][0]['table']
    return []

def get_brasileirao_teams():
    url = "https://api.football-data.org/v4/competitions/BSA/teams"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    if "teams" in data:
        return data['teams']
    return []

def get_team_stats(team_id):
    url = f"https://api.football-data.org/v4/teams/{team_id}/matches?season=2024"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    return data

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
    
    st.sidebar.title("📰 Asimov News")
    page = st.sidebar.selectbox(
        "Escolha uma página:",
        ["📰 Notícias", "🏆 Estatísticas Brasileirão"]
    )
    
    if page == "📰 Notícias":
        show_news_page()
    elif page == "🏆 Estatísticas Brasileirão":
        show_brasileirao_stats_page()

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

def show_brasileirao_stats_page():
    st.title("🏆 Brasileirão Série A - Estatísticas e Comparações")
    st.markdown("---")

    # Tabela de classificação
    st.subheader("Classificação Atual")
    standings = get_brasileirao_standings()
    if standings:
        tabela = []
        for pos in standings:
            tabela.append({
                "Posição": pos['position'],
                "Time": pos['team']['name'],
                "Pontos": pos['points'],
                "Vitórias": pos['won'],
                "Empates": pos['draw'],
                "Derrotas": pos['lost'],
                "Saldo de Gols": pos['goalDifference']
            })
        st.table(tabela)
    else:
        st.error("Não foi possível obter a classificação.")

    st.markdown("---")
    st.subheader("Estatísticas de um Time")

    teams = get_brasileirao_teams()
    team_options = {team['name']: team['id'] for team in teams}
    team_name = st.selectbox("Selecione um time:", list(team_options.keys()))
    if team_name:
        team_id = team_options[team_name]
        if st.button("Ver estatísticas do time"):
            stats = get_team_stats(team_id)
            if "matches" in stats:
                st.write(f"Total de jogos em 2024: {len(stats['matches'])}")
                for match in stats['matches'][:5]:
                    st.write(f"{match['utcDate']} - {match['homeTeam']['name']} x {match['awayTeam']['name']} | Placar: {match['score']['fullTime']}")
            else:
                st.error("Não foi possível obter estatísticas do time.")

    st.markdown("---")
    st.subheader("Comparação entre Times")

    team1 = st.selectbox("Time 1:", list(team_options.keys()), key="team1")
    team2 = st.selectbox("Time 2:", list(team_options.keys()), key="team2")

    if team1 and team2 and st.button("Comparar times"):
        t1 = next((t for t in standings if t['team']['name'] == team1), None)
        t2 = next((t for t in standings if t['team']['name'] == team2), None)
        if t1 and t2:
            comparacao = {
                "Time": [team1, team2],
                "Pontos": [t1['points'], t2['points']],
                "Vitórias": [t1['won'], t2['won']],
                "Empates": [t1['draw'], t2['draw']],
                "Derrotas": [t1['lost'], t2['lost']],
                "Saldo de Gols": [t1['goalDifference'], t2['goalDifference']]
            }
            st.table(comparacao)
        else:
            st.error("Não foi possível comparar os times selecionados.")

if __name__ == "__main__":
    main() 