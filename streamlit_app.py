import streamlit as st
import pandas as pd
import math
from pathlib import Path
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Função para plotar o gráfico de pizza
def plot_pie_chart(asset_allocation, selected_cryptos):
    plt.figure(figsize=(6, 6))
    plt.pie(asset_allocation, labels=selected_cryptos, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
    plt.title("Distribuição do Patrimônio em Criptoativos")
    st.pyplot(plt)



# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title='Wallet Cripto',
    page_icon='https://raw.githubusercontent.com/Daviaraujos/analise_investimento/main/logo.png',  # Use seu logo ou emoji.
)

# Lista de criptomoedas disponíveis (com ticker do Yahoo Finance)
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

# -------------------------------------------------------------------------
# Declare useful functions

@st.cache_data
def get_crypto_data(tickers, start_date, end_date):
    """Fetch cryptocurrency data from Yahoo Finance."""
    data = yf.download(tickers, start=start_date, end=end_date)['Close']
    return data

# -------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
'''
# Wallet Cripto

Análise, cotação e insights.
'''

# Add some spacing
''
''

# Get the time range for the slider (the last 5 years)
today = pd.to_datetime("today")
start_date = today - pd.DateOffset(years=5)

# Slider to choose date range
from_date = st.date_input('Data inicial', start_date)
to_date = st.date_input('Data final', today)

# Select cryptocurrencies to analyze
selected_cryptos = st.multiselect(
    'Selecione as criptomoedas para exibir',
    options=list(cryptos.keys()),
    default=['Bitcoin', 'Ethereum', 'Solana']
)

# Check if at least one cryptocurrency is selected
if not selected_cryptos:
    st.warning("Por favor, selecione ao menos uma criptomoeda.")

# Prepare tickers for Yahoo Finance API
tickers = [cryptos[crypto] for crypto in selected_cryptos]

# Fetch the data
crypto_data = get_crypto_data(tickers, from_date, to_date)

# Plot the data dynamically using Streamlit's line_chart
st.header('Evolução das Cotações das Criptomoedas', divider='gray')

# Display the line chart (dynamic, like the original code)
st.line_chart(crypto_data)

# Display selected data for each cryptocurrency
#st.header(f'Visão Geral dos Preços de {from_date} a {to_date}', divider='gray')

cols = st.columns(len(selected_cryptos))

for i, crypto in enumerate(selected_cryptos):
    col = cols[i % len(cols)]
    
    with col:
        first_price = crypto_data[cryptos[crypto]].iloc[0]
        last_price = crypto_data[cryptos[crypto]].iloc[-1]
        
        if math.isnan(first_price):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_price / first_price:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{crypto} Preço',
            value=f'R${last_price:,.2f}'.replace(",", "."),
            delta=growth,
            delta_color=delta_color
        )

# Inputs para o cliente informar o investimento em cada moeda
st.header("Insira seu Investimento em Criptomoedas")

selected_cryptos = st.multiselect(
    "Selecione as criptomoedas em que você investiu",
    list(cryptos.keys()),
    default=['Bitcoin', 'Ethereum', 'Dogecoin']  # Exemplo de valores iniciais
)

# Dicionário para armazenar o valor investido em cada moeda
invested_values = {}

# Solicita o valor investido em cada criptomoeda selecionada
for crypto in selected_cryptos:
    invested_values[crypto] = st.number_input(f"Quanto você investiu em {crypto.capitalize()} (R$):", min_value=0.0, format="%.2f")

# Verifica se o total investido é maior que zero
total_investido = sum(invested_values.values())
if total_investido == 0:
    st.warning("O valor total investido não pode ser zero. Por favor, insira valores válidos.")
else:
    # Calculando a alocação dos ativos (proporção de cada cripto na carteira)
    asset_allocation = [invested_values[crypto] / total_investido for crypto in selected_cryptos]

    # Exibindo o gráfico de pizza para mostrar a distribuição do patrimônio
    plot_pie_chart(asset_allocation, selected_cryptos)

    # Indicadores de rentabilidade
    st.header("Indicadores de Rentabilidade e Performance")

    # Calculando o retorno absoluto e ROI
    return_absolute = total_investido - sum([invested_values[crypto] for crypto in selected_cryptos])
    roi = (total_investido - sum([invested_values[crypto] for crypto in selected_cryptos])) / sum([invested_values[crypto] for crypto in selected_cryptos]) * 100 if total_investido > 0 else 0

    st.metric("Retorno Absoluto", f"R${return_absolute:,.2f}")
    st.metric("Retorno Percentual (ROI)", f"{roi:.2f}%")

    # Risco e Volatilidade
    st.header("Indicadores de Risco e Volatilidade")
    # Exemplo de Desvio Padrão e Máxima Perda (Drawdown), podendo ser calculados com base nos dados históricos das criptos
    st.metric("Desvio Padrão", "5.2%")  # Valor fictício, deve ser calculado com dados históricos
    st.metric("Máxima Perda (Drawdown)", "-20.3%")  # Valor fictício, deve ser calculado

    # Diversificação e Alocação
    st.header("Diversificação e Alocação")
    for crypto in selected_cryptos:
        st.metric(f"Alocação de {crypto.capitalize()}", f"{(invested_values[crypto] / total_investido) * 100:.2f}%")

    # Liquidez e Exposição
    st.header("Liquidez e Exposição")
    st.metric("Proporção de Stablecoins", "10%")  # Exemplo fixo, pode ser calculado
    st.metric("Ativos com Maior Liquidez", "Bitcoin, Ethereum")  # Exemplo fixo

    # Performance Ajustada ao Risco (exemplo de Sharpe Ratio)
    st.header("Eficiência e Performance Ajustada ao Risco")
    st.metric("Sharpe Ratio", "1.2")  # Exemplo fixo
