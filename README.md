# 📰 Asimov News - Webapp Streamlit

Um agregador de notícias que coleta e exibe as últimas notícias dos principais portais brasileiros em uma interface web moderna.

## 🚀 Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Executar o Webapp

```bash
streamlit run asimov_news_streamlit.py
```

O webapp será aberto automaticamente no seu navegador em `http://localhost:8501`

## 📋 Requisitos

- Python 3.8+
- Dependências listadas em `requirements.txt`:
  - `streamlit>=1.28.0` - Framework web
  - `requests>=2.31.0` - Requisições HTTP
  - `beautifulsoup4>=4.12.0` - Parsing HTML
  - `lxml>=4.9.0` - Parser XML/HTML
  - `pandas>=2.0.0` - Manipulação de dados
  - `plotly>=5.15.0` - Gráficos interativos
  - `selenium>=4.15.0` - Automação web
  - `webdriver-manager>=4.0.0` - Gerenciamento de drivers

## 🎯 Funcionalidades

### 📰 Página de Notícias

- **Sites Suportados:**
  - **G1/Globo** - Notícias gerais
  - **Veja** - Revista semanal
  - **R7** - Portal de notícias
  - **CNN Brasil** - Notícias internacionais

- **Recursos:**
  - ✅ Interface web moderna e responsiva
  - ✅ Seleção de sites ativos via sidebar
  - ✅ Atualização manual de notícias
  - ✅ Paginação automática
  - ✅ Links diretos para as matérias
  - ✅ Persistência de dados (sites ativos e notícias)
  - ✅ Exibição de data/hora das notícias

### ⚽ Página de Análise Esportiva

- **Times Suportados:**
  - **Série A:** Palmeiras, Internacional, Flamengo, Fluminense, Corinthians, Athletico Paranaense, Atlético Mineiro, América Mineiro, Fortaleza, Botafogo, Santos, São Paulo, Bragantino, Goiás, Coritiba, Ceará, Cuiabá, Atlético Goianiense, Avaí, Juventude
  - **Série B:** Cruzeiro, Grêmio, Vasco, Bahia, Ituano, Londrina, Sport, Sampaio Corrêa, Criciúma, CRB, Guarani, Vila Nova, Ponte Preta, Tombense, Chapecoense, CSA, Novorizontino, Brusque, Operário, Náutico

- **Recursos:**
  - ✅ Comparação de estatísticas entre times
  - ✅ Gráficos interativos com Plotly
  - ✅ Dados históricos de 2017-2022
  - ✅ Métricas detalhadas por temporada
  - ✅ Tabelas comparativas
  - ✅ Interface intuitiva para seleção de times

## 🛠️ Estrutura do Projeto

```
Asimov News/
├── asimov_news_streamlit.py       # Webapp principal (inclui notícias e análise esportiva)
├── asimov_news.py                 # Versão CLI original
├── analise_esportiva.py           # Versão CLI da análise esportiva
├── requirements.txt               # Dependências
├── scraping_sites/
│   └── site.py                   # Módulo de scraping
├── news                          # Cache de notícias (gerado automaticamente)
└── sites                         # Cache de sites ativos (gerado automaticamente)
```

## 🔧 Como Usar

### 📰 Página de Notícias

1. **Primeira execução**: O app criará automaticamente os arquivos de cache
2. **Selecionar sites**: Use a sidebar para ativar/desativar sites
3. **Atualizar notícias**: Clique no botão "🔄 Atualizar Notícias"
4. **Navegar**: Use os botões de paginação para ver mais notícias
5. **Abrir links**: Clique em "🔗 Abrir Link" para ver a matéria completa

### ⚽ Página de Análise Esportiva

1. **Selecionar times**: Escolha dois times para comparação na sidebar
2. **Definir divisões**: Selecione a divisão de cada time (Série A ou B)
3. **Carregar dados**: Clique nos botões para carregar estatísticas de cada time
4. **Comparar**: Selecione uma métrica e gere o gráfico comparativo
5. **Analisar**: Visualize tabelas e gráficos interativos

## ⚠️ Observações

### 📰 Notícias

- O scraping é feito respeitando os termos de uso dos sites
- As notícias são atualizadas apenas manualmente para evitar sobrecarga
- Os dados são persistidos localmente nos arquivos `news` e `sites`
- O webapp funciona offline após a primeira atualização

### ⚽ Análise Esportiva

- Os dados são coletados da API do SofaScore
- Alguns times podem não ter dados para todos os anos
- As estatísticas são atualizadas conforme disponibilidade da API
- Gráficos interativos permitem análise detalhada das métricas

## 🐛 Solução de Problemas

### Erro de conexão

- Verifique sua conexão com a internet
- Alguns sites podem estar temporariamente indisponíveis

### Erro de dependências

```bash
pip install --upgrade -r requirements.txt
```

### Limpar cache

- Delete os arquivos `news` e `sites` para resetar as configurações
