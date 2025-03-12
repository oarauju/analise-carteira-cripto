import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path

# Configuração inicial da página
st.set_page_config(
    page_title="Wallet Cripto",
    page_icon="https://raw.githubusercontent.com/Daviaraujos/analise_investimento/main/logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado com paleta de cores claras (Apple + OpenAI)
st.markdown("""
    <style>
    .main {
        background-color: #F5F5F7;
        color: #1D1D1F;
    }
    .stApp {
        background-color: #F5F5F7;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1D1D1F;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .stSelectbox, .stDateInput, .stNumberInput {
        background-color: #FFFFFF;
        color: #1D1D1F;
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #10A37F;
    }
    .stSelectbox > div > div, .stDateInput > div > div, .stNumberInput > div > div {
        background-color: #FFFFFF !important;
        color: #1D1D1F !important;
    }
    .stMetric {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border: 1px solid #E8ECEF;
    }
    .stDataFrame {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 10px;
        border: 1px solid #E8ECEF;
    }
    .stExpander {
        background-color: #FFFFFF;
        border-radius: 12px;
        border: 1px solid #E8ECEF;
    }
    .stSidebar .stSelectbox, .stSidebar .stDateInput {
        background-color: #FFFFFF;
        border: 1px solid #10A37F;
    }
    </style>
""", unsafe_allow_html=True)

# Lista de criptomoedas disponíveis (ticker do Yahoo Finance)
cryptos = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "XRP": "XRP-USD",
    "Cardano": "ADA-USD",
    "Solana": "SOL-USD",
    "Polkadot": "DOT-USD",
    "Dogecoin": "DOGE-USD",
    "Polygon": "MATIC-USD",
    "Litecoin": "LTC-USD",
    "Chainlink": "LINK-USD",
    "Uniswap": "UNI-USD",
    "Shiba Inu": "SHIB-USD",
    "Avalanche": "AVAX-USD",
    "Cosmos": "ATOM-USD",
    "Algorand": "ALGO-USD",
    "VeChain": "VET-USD",
    "Tezos": "XTZ-USD",
    "Filecoin": "FIL-USD",
    "Stellar": "XLM-USD"
}

# Função para buscar dados históricos
@st.cache_data
def get_crypto_data(tickers, start_date, end_date):
    """Busca dados históricos de criptomoedas via Yahoo Finance."""
    try:
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True)
        if isinstance(data, pd.DataFrame) and not data.empty:
            if len(tickers) > 1:
                if 'Close' in data.columns.levels[0]:
                    return data['Close']
                else:
                    return data
            else:
                return data['Close'].to_frame(name=tickers[0])
        else:
            st.warning(f"Nenhum dado retornado para os tickers {tickers} no período {start_date} a {end_date}.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return pd.DataFrame()

# Função para calcular o Sharpe Ratio
def calculate_sharpe_ratio(crypto_data, risk_free_rate=0.02):
    daily_returns = crypto_data.pct_change().dropna()
    if daily_returns.empty:
        return np.nan
    mean_daily_return = daily_returns.mean()
    std_daily_return = daily_returns.std()
    sharpe_ratio = (mean_daily_return - risk_free_rate / 252) / std_daily_return
    return sharpe_ratio * np.sqrt(252)

# Função para calcular o Drawdown máximo
def calculate_max_drawdown(crypto_data):
    roll_max = crypto_data.cummax()
    daily_drawdown = crypto_data / roll_max - 1.0
    return daily_drawdown.min() * 100

# Interface principal
st.title("Wallet Cripto")
st.markdown("**Análise, Cotação e Insights para sua Carteira de Criptomoedas**")

# Inputs de data e seleção de criptomoedas na barra lateral
with st.sidebar:
    st.header("Configurações")
    today = pd.to_datetime("today").date()
    start_date_default = (pd.to_datetime(today) - pd.DateOffset(years=5)).date()
    
    from_date = st.date_input("Data Inicial", start_date_default)
    to_date = st.date_input("Data Final", today)
    
    selected_cryptos = st.multiselect(
        "Selecione as Criptomoedas",
        options=list(cryptos.keys()),
        default=["Bitcoin", "Ethereum", "Solana"]
    )

if not selected_cryptos:
    st.warning("Por favor, selecione ao menos uma criptomoeda.")
else:
    tickers = [cryptos[crypto] for crypto in selected_cryptos]
    crypto_data = get_crypto_data(tickers, from_date, to_date)

    if crypto_data.empty:
        st.error("Nenhum dado disponível para o período selecionado.")
    else:
        # Dashboard principal
        # Gráfico de evolução das cotações
        st.header("Evolução das Cotações")
        fig = go.Figure()
        for ticker in crypto_data.columns:
            fig.add_trace(go.Scatter(
                x=crypto_data.index,
                y=crypto_data[ticker],
                name=ticker,
                line=dict(width=2, color="#10A37F")  # Verde vibrante da OpenAI
            ))
        fig.update_layout(
            template="plotly_white",
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            xaxis_title="Data",
            yaxis_title="Preço (USD)",
            plot_bgcolor="#FFFFFF",
            paper_bgcolor="#F5F5F7",
            font=dict(color="#1D1D1F")
        )
        st.plotly_chart(fig, use_container_width=True)

        # Métricas por criptomoeda
        st.header("Desempenho Individual")
        cols = st.columns(min(len(selected_cryptos), 4))
        for i, crypto in enumerate(selected_cryptos):
            ticker = cryptos[crypto]
            with cols[i % len(cols)]:
                if ticker in crypto_data.columns:
                    first_price = crypto_data[ticker].iloc[0]
                    last_price = crypto_data[ticker].iloc[-1]
                    growth = (last_price / first_price - 1) * 100 if not pd.isna(first_price) else 0
                    growth_str = f"{growth:.2f}%"
                    delta_color = "normal" if growth > 0 else "inverse" if growth < 0 else "off"
                    st.metric(
                        label=f"{crypto}",
                        value=f"R${last_price:,.2f}".replace(",", "."),
                        delta=growth_str,
                        delta_color=delta_color
                    )

        # Inputs de investimento e alocação
        st.header("Sua Carteira de Criptomoedas")
        invested_values = {}
        with st.expander("Inserir Investimentos"):
            for crypto in selected_cryptos:
                invested_values[crypto] = st.number_input(
                    f"Investimento em {crypto} (R$)",
                    min_value=0.0,
                    value=0.0,
                    step=10.0,
                    format="%.2f"
                )

        total_investido = sum(invested_values.values())
        if total_investido > 0:
            # Cálculo do valor atual da carteira
            current_values = {
                crypto: invested_values[crypto] / crypto_data[cryptos[crypto]].iloc[0] * crypto_data[cryptos[crypto]].iloc[-1]
                for crypto in selected_cryptos if invested_values[crypto] > 0
            }
            total_current = sum(current_values.values())

            # Gráfico de alocação (gráfico de pizza)
            st.header("Distribuição do Patrimônio")
            labels = [crypto for crypto in selected_cryptos if invested_values[crypto] > 0]
            asset_allocation = [invested_values[crypto] / total_investido for crypto in selected_cryptos if invested_values[crypto] > 0]
            fig_pie = px.pie(
                names=labels,
                values=asset_allocation,
                title="Distribuição do Patrimônio em Criptoativos",
                template="plotly_white",
                height=400,
                color_discrete_sequence=["#10A37F", "#34C759", "#007AFF", "#E8ECEF", "#F5F5F7"]  # Paleta clara
            )
            fig_pie.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#F5F5F7",
                font=dict(color="#1D1D1F")
            )
            st.plotly_chart(fig_pie, use_container_width=True)

            # Rentabilidade
            st.header("Rentabilidade da Carteira")
            roi = (total_current - total_investido) / total_investido * 100
            delta_color = "normal" if roi > 0 else "inverse" if roi < 0 else "off"
            st.metric("Valor Atual Total", f"R${total_current:,.2f}".replace(",", "."), f"{roi:.2f}%", delta_color=delta_color)

            # Risco e volatilidade
            st.header("Risco e Volatilidade")
            cols = st.columns(2)
            for i, crypto in enumerate(selected_cryptos):
                if invested_values[crypto] > 0:
                    ticker = cryptos[crypto]
                    sharpe = calculate_sharpe_ratio(crypto_data[ticker])
                    drawdown = calculate_max_drawdown(crypto_data[ticker])
                    with cols[i % 2]:
                        sharpe_color = "normal" if sharpe > 1 else "inverse" if sharpe < 0 else "off"
                        drawdown_color = "inverse" if drawdown < -20 else "normal" if drawdown > -10 else "off"
                        st.metric(f"Sharpe Ratio - {crypto}", f"{sharpe:.2f}" if not pd.isna(sharpe) else "n/a", delta_color=sharpe_color)
                        st.metric(f"Max Drawdown - {crypto}", f"{drawdown:.2f}%", delta_color=drawdown_color)

            # Correlação entre ativos
            st.header("Correlação entre Ativos")
            correlation_matrix = crypto_data.corr()
            fig_heatmap = px.imshow(
                correlation_matrix,
                text_auto=True,
                color_continuous_scale=["#FF3B30", "#E8ECEF", "#34C759"],  # Vermelho, neutro, verde
                title="Matriz de Correlação",
                template="plotly_white",
                height=400
            )
            fig_heatmap.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#F5F5F7",
                font=dict(color="#1D1D1F")
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
