
import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import plotly.express as px

st.set_page_config(
    page_title="Stock Comparison Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Stock Comparison Dashboard")
st.write("Apple vs Microsoft vs NVIDIA")
st.write("Created by: Naomi Joa")
st.caption("Developed for CPS*5745")

st.divider()

# Company options
companies = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA"
}

# Shared filters
st.sidebar.header("Dashboard Filters")

selected = st.sidebar.multiselect(
    "Select Companies",
    options=list(companies.keys()),
    default=list(companies.keys())
)

today = date.today()

start_date = st.sidebar.date_input(
    "Start Date",
    value=today - timedelta(days=365),
    max_value=today
)

end_date = st.sidebar.date_input(
    "End Date",
    value=today,
    max_value=today
)

if not selected:
    st.warning("Please select at least one company.")
    st.stop()

if start_date >= end_date:
    st.error("Start date must be before end date.")
    st.stop()

# Retrieve stock data
@st.cache_data(ttl=3600)
def load_data(tickers, start, end):
    data = yf.download(
        list(tickers),
        start=start,
        end=end + timedelta(days=1),
        auto_adjust=True,
        progress=False,
        threads=False
    )
    return data

tickers = tuple(companies[name] for name in selected)

with st.spinner("Loading stock market data..."):
    try:
        stock_data = load_data(
            tickers,
            start_date,
            end_date
        )
    except Exception as e:
        st.error(f"Unable to retrieve stock data: {e}")
        st.stop()

if stock_data.empty:
    st.error("No stock data available for this date range.")
    st.stop()

st.success("Stock data loaded successfully!")

st.subheader("Selected Companies")
st.write(", ".join(selected))

st.subheader("Selected Date Range")
st.write(f"{start_date} to {end_date}")

st.subheader("Latest Available Stock Data")
st.dataframe(stock_data.tail(), use_container_width=True)



# Prepare stock data for visualizations
close_prices = stock_data["Close"].copy()

if isinstance(close_prices, pd.Series):
    close_prices = close_prices.to_frame(name=tickers[0])

filtered_data = close_prices.reset_index().melt(
    id_vars="Date",
    var_name="Ticker",
    value_name="Close"
)

ticker_to_company = {
    ticker: name for name, ticker in companies.items()
}

filtered_data["Company"] = filtered_data["Ticker"].map(
    ticker_to_company
)

filtered_data = filtered_data.dropna(subset=["Close"])



# ==========================================
# CHART 1: STOCK PRICE COMPARISON
# ==========================================

st.subheader("1. Stock Price Comparison")

fig_price = px.line(
    filtered_data,
    x="Date",
    y="Close",
    color="Company",
    title="Historical Adjusted Closing Stock Prices",
    labels={
        "Date": "Date",
        "Close": "Adjusted Closing Price (USD)",
        "Company": "Company"
    }
)

st.plotly_chart(fig_price, use_container_width=True)


# ==========================================
# CHART 2: TRADING VOLUME COMPARISON
# ==========================================

st.subheader("2. Trading Volume Comparison")

volume_data = stock_data["Volume"].copy()

if isinstance(volume_data, pd.Series):
    volume_data = volume_data.to_frame(name=tickers[0])

volume_data = volume_data.reset_index().melt(
    id_vars="Date",
    var_name="Ticker",
    value_name="Volume"
)

volume_data["Company"] = volume_data["Ticker"].map(
    ticker_to_company
)

volume_data = volume_data.dropna(subset=["Volume"])

fig_volume = px.bar(
    volume_data,
    x="Date",
    y="Volume",
    color="Company",
    barmode="group",
    title="Daily Trading Volume Comparison",
    labels={
        "Date": "Date",
        "Volume": "Shares Traded",
        "Company": "Company"
    }
)

st.plotly_chart(fig_volume, use_container_width=True)


# ==========================================
# CHART 3: DAILY RETURNS HISTOGRAM
# ==========================================

st.subheader("3. Daily Returns Distribution")

returns_data = filtered_data.sort_values(
    ["Company", "Date"]
).copy()

returns_data["Daily Return (%)"] = (
    returns_data.groupby("Company")["Close"]
    .pct_change() * 100
)

returns_data = returns_data.dropna(
    subset=["Daily Return (%)"]
)

fig_returns = px.histogram(
    returns_data,
    x="Daily Return (%)",
    color="Company",
    barmode="overlay",
    nbins=50,
    opacity=0.65,
    title="Distribution of Daily Stock Returns",
    labels={
        "Daily Return (%)": "Daily Return (%)",
        "Company": "Company"
    }
)

fig_returns.update_layout(
    xaxis_title="Daily Return (%)",
    yaxis_title="Number of Trading Days"
)

st.plotly_chart(fig_returns, use_container_width=True)


# ==========================================
# CHART 4: STOCK VOLATILITY BOX PLOT
# ==========================================

st.subheader("4. Stock Volatility Comparison")

fig_box = px.box(
    returns_data,
    x="Company",
    y="Daily Return (%)",
    color="Company",
    points="outliers",
    title="Daily Stock Return Volatility",
    labels={
        "Company": "Company",
        "Daily Return (%)": "Daily Return (%)"
    }
)

st.plotly_chart(fig_box, use_container_width=True)


# ==========================================
# CHART 5: NORMALIZED STOCK PERFORMANCE
# ==========================================

st.subheader("5. Normalized Stock Performance")

normalized_data = filtered_data.sort_values(
    ["Company", "Date"]
).copy()

normalized_data["Normalized Price"] = (
    normalized_data.groupby("Company")["Close"]
    .transform(lambda x: x / x.iloc[0] * 100)
)

fig_normalized = px.line(
    normalized_data,
    x="Date",
    y="Normalized Price",
    color="Company",
    title="Normalized Stock Performance (Starting at 100)",
    labels={
        "Date": "Date",
        "Normalized Price": "Indexed Performance (Base = 100)",
        "Company": "Company"
    }
)

fig_normalized.add_hline(
    y=100,
    line_dash="dash",
    line_color="gray"
)

st.plotly_chart(fig_normalized, use_container_width=True)


# ==========================================
# KEY FINDINGS AND EXPLANATION
# ==========================================


# ==========================================
# KEY FINDINGS AND ANALYSIS
# ==========================================


# ==========================================
# KEY FINDINGS AND ANALYSIS
# ==========================================

st.divider()
st.header("Key Findings and Analysis")

st.write(
    "This dashboard compares the selected companies "
    "using historical stock market data."
)

if not filtered_data.empty:
    analysis = filtered_data.sort_values(
        ["Company", "Date"]
    ).copy()

    # Calculate daily returns
    analysis["Daily Return (%)"] = (
        analysis.groupby("Company")["Close"]
        .pct_change() * 100
    )

    # Calculate overall stock performance
    performance = analysis.groupby("Company")["Close"].agg(
        ["first", "last"]
    )

    performance["Return (%)"] = (
        (performance["last"] / performance["first"] - 1)
        * 100
    )

    best_stock = performance["Return (%)"].idxmax()
    best_return = performance.loc[
        best_stock, "Return (%)"
    ]

    st.subheader("1. Stock Price Comparison")
    st.write(
        f"**{best_stock}** had the highest percentage "
        f"return during the selected period, "
        f"with a return of **{best_return:.2f}%**."
    )

    st.subheader("2. Trading Volume")
    st.write(
        "Trading volume compares daily market activity "
        "among the selected companies and helps identify "
        "differences in investor trading activity."
    )

    st.subheader("3. Daily Returns Distribution")
    st.write(
        "The daily returns distribution shows how "
        "frequently positive and negative returns occur "
        "for each company."
    )

    st.subheader("4. Volatility Comparison")

    volatility = (
        analysis.groupby("Company")["Daily Return (%)"]
        .std()
        .dropna()
    )

    if not volatility.empty:
        most_volatile = volatility.idxmax()
        highest_volatility = volatility.max()

        st.write(
            f"**{most_volatile}** experienced the "
            f"highest daily return volatility, "
            f"with a standard deviation of "
            f"**{highest_volatility:.2f} "
            f"percentage points**."
        )
    else:
        st.write(
            "More trading days are needed "
            "to calculate volatility."
        )

    st.subheader("5. Normalized Stock Performance")
    st.write(
        "Normalized performance compares stocks "
        "from a common starting value of 100, "
        "making relative growth easier to evaluate."
    )

    st.info(
        "The findings automatically update when "
        "the selected companies or date range changes."
    )

else:
    st.warning(
        "No stock data is available for "
        "the selected filters."
    )

st.caption(
    "Data source: Yahoo Finance via yfinance. "
    "Historical prices may be adjusted "
    "for corporate actions."
)
