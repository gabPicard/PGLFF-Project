import sys
from pathlib import Path
from datetime import datetime
import json
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.data.fetch_yf import get_history
from src.evaluation.metrics import (
    annualized_volatility,
    max_drawdown,
    total_return,
    daily_returns
)
from src.portfolio.portfolio_engine import (
    compute_portfolio_returns,
    compute_cumulative_value,
    portfolio_stats
)
from src.portfolio.weights import equal_weights


def load_config():
    config_path = ROOT / "config.yaml"
    
    default_config = {
        "report_assets": ["AAPL", "MSFT", "GLD", "BTC-USD"],
        "portfolio_assets": ["AAPL", "MSFT", "GLD"],
        "period": "3mo",
        "interval": "1d"
    }
    
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"Warning: Could not load config.yaml: {e}")
            print("Using default configuration.")
    
    return default_config


def generate_asset_report(ticker, period="3mo", interval="1d"):
    try:
        df = get_history(ticker, period=period, interval=interval)
        
        if df is None or df.empty:
            return {
                "ticker": ticker,
                "status": "error",
                "error": "No data available"
            }
        
        latest = df.iloc[-1]
        first = df.iloc[0]
        
        price_series = df['price']
        vol = annualized_volatility(price_series)
        mdd = max_drawdown(price_series)
        tot_return = total_return(price_series)
        
        daily_ret = (latest['price'] - df.iloc[-2]['price']) / df.iloc[-2]['price'] if len(df) > 1 else 0
        
        report = {
            "ticker": ticker,
            "status": "success",
            "timestamp": latest.name.isoformat(),
            "open_price": float(first['price']),
            "close_price": float(latest['price']),
            "latest_price": float(latest['price']),
            "daily_return": float(daily_ret),
            "total_return": float(tot_return),
            "annualized_volatility": float(vol),
            "max_drawdown": float(mdd),
            "data_points": len(df),
            "period": period
        }
        
        return report
        
    except Exception as e:
        return {
            "ticker": ticker,
            "status": "error",
            "error": str(e)
        }


def generate_portfolio_report(tickers, period="3mo", interval="1d"):
    try:
        dfs = []
        valid_tickers = []
        
        for ticker in tickers:
            df = get_history(ticker, period=period, interval=interval)
            if df is not None and not df.empty:
                df = df.rename(columns={"price": ticker})
                dfs.append(df)
                valid_tickers.append(ticker)
        
        if not dfs:
            return {
                "status": "error",
                "error": "No valid data for any ticker"
            }
        
        prices = pd.concat(dfs, axis=1, join="inner")
        
        weights = equal_weights(valid_tickers)
        portfolio_rets = compute_portfolio_returns(prices, weights)
        portfolio_value = compute_cumulative_value(portfolio_rets, initial_value=10000)
        stats = portfolio_stats(portfolio_value)
        
        report = {
            "status": "success",
            "tickers": valid_tickers,
            "weights": {t: float(w) for t, w in weights.items()},
            "total_return": float(stats["total_return"]),
            "annualized_volatility": float(stats["annual_vol"]),
            "sharpe_ratio": float(stats["sharpe"]),
            "max_drawdown": float(stats["max_drawdown"]),
            "initial_value": 10000.0,
            "final_value": float(portfolio_value.iloc[-1]),
            "period": period
        }
        
        return report
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def save_report(report_data, report_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"daily_report_{timestamp}.json"
    filepath = report_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"Report saved to: {filepath}")
    return filepath


def main():
    print("=" * 60)
    print("Daily Report Generation")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    config = load_config()
    print(f"\nConfiguration loaded:")
    print(f"  Report Assets: {config['report_assets']}")
    print(f"  Portfolio Assets: {config['portfolio_assets']}")
    print(f"  Period: {config['period']}")
    print(f"  Interval: {config['interval']}")
    
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    
    print("\n" + "-" * 60)
    print("Generating Asset Reports...")
    print("-" * 60)
    
    asset_reports = []
    for ticker in config['report_assets']:
        print(f"\nProcessing {ticker}...")
        report = generate_asset_report(
            ticker, 
            period=config['period'], 
            interval=config['interval']
        )
        asset_reports.append(report)
        
        if report['status'] == 'success':
            print(f"  ✓ Close: ${report['close_price']:.2f}")
            print(f"  ✓ Daily Return: {report['daily_return']*100:.2f}%")
            print(f"  ✓ Volatility: {report['annualized_volatility']*100:.2f}%")
            print(f"  ✓ Max Drawdown: {report['max_drawdown']*100:.2f}%")
        else:
            print(f"  ✗ Error: {report['error']}")
    
    print("\n" + "-" * 60)
    print("Generating Portfolio Report...")
    print("-" * 60)
    
    portfolio_report = generate_portfolio_report(
        config['portfolio_assets'],
        period=config['period'],
        interval=config['interval']
    )
    
    if portfolio_report['status'] == 'success':
        print(f"  ✓ Portfolio Value: ${portfolio_report['final_value']:.2f}")
        print(f"  ✓ Total Return: {portfolio_report['total_return']*100:.2f}%")
        print(f"  ✓ Sharpe Ratio: {portfolio_report['sharpe_ratio']:.2f}")
        print(f"  ✓ Volatility: {portfolio_report['annualized_volatility']*100:.2f}%")
        print(f"  ✓ Max Drawdown: {portfolio_report['max_drawdown']*100:.2f}%")
    else:
        print(f"  ✗ Error: {portfolio_report['error']}")
    
    full_report = {
        "report_date": datetime.now().isoformat(),
        "report_type": "daily",
        "assets": asset_reports,
        "portfolio": portfolio_report,
        "config": config
    }
    
    print("\n" + "-" * 60)
    print("Saving Report...")
    print("-" * 60)
    filepath = save_report(full_report, report_dir)
    
    print("\n" + "=" * 60)
    print("Daily Report Generation Complete!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
