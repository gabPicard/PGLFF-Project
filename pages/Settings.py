import streamlit as st
import yaml
from pathlib import Path

st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Settings & Configuration")
st.markdown("Manage assets for daily reports and default portfolio settings")

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"


def load_config():
    """Load configuration from config.yaml"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return None


def save_config(config):
    """Save configuration to config.yaml"""
    try:
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception as e:
        st.error(f"Error saving config: {e}")
        return False


config = load_config()


if config is None:
    st.error("Could not load configuration file. Please check that config.yaml exists.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Report Assets", 
    "💼 Portfolio Assets", 
    "📈 Default Tickers",
    "⚙️ Report Settings"
])

with tab1:
    st.header("Assets for Daily Reports")
    st.markdown("Configure which assets are included in the automated daily reports.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Report Assets")
        report_assets = config.get('report_assets', [])
        
        if report_assets:
            for i, asset in enumerate(report_assets):
                col_asset, col_delete = st.columns([4, 1])
                with col_asset:
                    st.text(f"📌 {asset}")
                with col_delete:
                    if st.button("🗑️", key=f"delete_report_{i}"):
                        report_assets.remove(asset)
                        config['report_assets'] = report_assets
                        if save_config(config):
                            st.success(f"Removed {asset}")
                            st.rerun()
        else:
            st.info("No report assets configured")
    
    with col2:
        st.subheader("Add New Asset")
        new_report_asset = st.text_input(
            "Ticker Symbol",
            key="new_report_asset",
            placeholder="e.g., AAPL, BTC-USD"
        ).upper().strip()
        
        if st.button("➕ Add to Report Assets", type="primary"):
            if new_report_asset:
                if new_report_asset not in report_assets:
                    report_assets.append(new_report_asset)
                    config['report_assets'] = report_assets
                    if save_config(config):
                        st.success(f"Added {new_report_asset} to report assets!")
                        st.rerun()
                else:
                    st.warning(f"{new_report_asset} is already in the list")
            else:
                st.warning("Please enter a ticker symbol")

with tab2:
    st.header("Assets for Portfolio Analysis")
    st.markdown("Configure which assets are included in the portfolio analysis of daily reports.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Portfolio Assets")
        portfolio_assets = config.get('portfolio_assets', [])
        
        if portfolio_assets:
            for i, asset in enumerate(portfolio_assets):
                col_asset, col_delete = st.columns([4, 1])
                with col_asset:
                    st.text(f"💼 {asset}")
                with col_delete:
                    if st.button("🗑️", key=f"delete_portfolio_{i}"):
                        portfolio_assets.remove(asset)
                        config['portfolio_assets'] = portfolio_assets
                        if save_config(config):
                            st.success(f"Removed {asset}")
                            st.rerun()
        else:
            st.info("No portfolio assets configured")
    
    with col2:
        st.subheader("Add New Asset")
        new_portfolio_asset = st.text_input(
            "Ticker Symbol",
            key="new_portfolio_asset",
            placeholder="e.g., AAPL, MSFT"
        ).upper().strip()
        
        if st.button("➕ Add to Portfolio Assets", type="primary"):
            if new_portfolio_asset:
                if new_portfolio_asset not in portfolio_assets:
                    portfolio_assets.append(new_portfolio_asset)
                    config['portfolio_assets'] = portfolio_assets
                    if save_config(config):
                        st.success(f"Added {new_portfolio_asset} to portfolio assets!")
                        st.rerun()
                else:
                    st.warning(f"{new_portfolio_asset} is already in the list")
            else:
                st.warning("Please enter a ticker symbol")

with tab3:
    st.header("Default Tickers for Portfolio Page")
    st.markdown("Configure which tickers appear by default in the Portfolio Analysis page.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Current Default Tickers")
        default_tickers = config.get('default_tickers', [])
        
        if default_tickers:
            for i, ticker in enumerate(default_tickers):
                col_ticker, col_delete = st.columns([4, 1])
                with col_ticker:
                    st.text(f"🎯 {ticker}")
                with col_delete:
                    if st.button("🗑️", key=f"delete_default_{i}"):
                        default_tickers.remove(ticker)
                        config['default_tickers'] = default_tickers
                        if save_config(config):
                            st.success(f"Removed {ticker}")
                            st.rerun()
        else:
            st.info("No default tickers configured")
    
    with col2:
        st.subheader("Add New Ticker")
        new_default_ticker = st.text_input(
            "Ticker Symbol",
            key="new_default_ticker",
            placeholder="e.g., GOOGL, AMZN"
        ).upper().strip()
        
        if st.button("➕ Add to Default Tickers", type="primary"):
            if new_default_ticker:
                if new_default_ticker not in default_tickers:
                    default_tickers.append(new_default_ticker)
                    config['default_tickers'] = default_tickers
                    if save_config(config):
                        st.success(f"Added {new_default_ticker} to default tickers!")
                        st.rerun()
                else:
                    st.warning(f"{new_default_ticker} is already in the list")
            else:
                st.warning("Please enter a ticker symbol")

with tab4:
    st.header("Report Generation Settings")
    st.markdown("Configure time period and interval for daily reports.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Historical Period")
        current_period = config.get('period', '3mo')
        
        period_options = {
            "1 Day": "1d",
            "5 Days": "5d",
            "1 Month": "1mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y",
            "5 Years": "5y",
            "10 Years": "10y",
            "Year to Date": "ytd",
            "Max": "max"
        }
        
        period_labels = list(period_options.keys())
        period_values = list(period_options.values())
        try:
            current_index = period_values.index(current_period)
        except ValueError:
            current_index = 3
        
        selected_period_label = st.selectbox(
            "Select Period",
            period_labels,
            index=current_index,
            key="period_select"
        )
        
        new_period = period_options[selected_period_label]
        
        if new_period != current_period:
            if st.button("💾 Update Period", key="update_period"):
                config['period'] = new_period
                if save_config(config):
                    st.success(f"Period updated to {selected_period_label}")
                    st.rerun()
    
    with col2:
        st.subheader("Data Interval")
        current_interval = config.get('interval', '1d')
        
        interval_options = {
            "1 Minute": "1m",
            "2 Minutes": "2m",
            "5 Minutes": "5m",
            "15 Minutes": "15m",
            "30 Minutes": "30m",
            "60 Minutes": "60m",
            "90 Minutes": "90m",
            "1 Hour": "1h",
            "1 Day": "1d",
            "5 Days": "5d",
            "1 Week": "1wk",
            "1 Month": "1mo",
            "3 Months": "3mo"
        }
        
        interval_labels = list(interval_options.keys())
        interval_values = list(interval_options.values())
        try:
            current_index = interval_values.index(current_interval)
        except ValueError:
            current_index = 8
        
        selected_interval_label = st.selectbox(
            "Select Interval",
            interval_labels,
            index=current_index,
            key="interval_select"
        )
        
        new_interval = interval_options[selected_interval_label]
        
        if new_interval != current_interval:
            if st.button("💾 Update Interval", key="update_interval"):
                config['interval'] = new_interval
                if save_config(config):
                    st.success(f"Interval updated to {selected_interval_label}")
                    st.rerun()

st.markdown("---")
st.subheader("📄 Current Configuration")

with st.expander("View Full Configuration (YAML)"):
    st.code(yaml.dump(config, default_flow_style=False, sort_keys=False), language="yaml")

st.markdown("---")
