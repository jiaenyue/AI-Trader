import glob
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Major cryptocurrencies against USDT (using USD as proxy on Alpha Vantage)
crypto_symbols_usdt = [
    "BTC",   # Bitcoin/USDT
    "ETH",   # Ethereum/USDT
    "XRP",   # Ripple/USDT
    "SOL",   # Solana/USDT
    "ADA",   # Cardano/USDT
    "SUI",   # Sui/USDT
    "LINK",  # Chainlink/USDT
    "AVAX",  # Avalanche/USDT
    "LTC",   # Litecoin/USDT
    "DOT",   # Polkadot/USDT
]

# Merge all crypto daily price JSON files, write one line per file to crypto_merged.jsonl
current_dir = os.path.dirname(__file__)
pattern = os.path.join(current_dir, "coin", "daily_prices_*.json")
files = sorted(glob.glob(pattern))

output_file = os.path.join(current_dir, "crypto_merged.jsonl")

print(f"Found {len(files)} crypto files to merge")
print(f"Output file: {output_file}")

with open(output_file, "w", encoding="utf-8") as fout:
    for fp in files:
        basename = os.path.basename(fp)
        print(f"Processing: {basename}")

        # Only process files that contain our crypto symbols
        if not any(symbol in basename for symbol in crypto_symbols_usdt):
            print(f"  Skipping: {basename} (not in crypto symbols list)")
            continue

        with open(fp, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Rename fields: "1. open" -> "1. buy price"；"4. close" -> "4. sell price"
        # For the latest date, only keep "1. buy price"
        try:
            # Find all keys starting with "Time Series"
            series = None
            for key, value in data.items():
                if key.startswith("Time Series"):
                    series = value
                    break

            if isinstance(series, dict) and series:
                # First rename fields for all dates
                for d, bar in list(series.items()):
                    if not isinstance(bar, dict):
                        continue
                    if "1. open" in bar:
                        bar["1. buy price"] = bar.pop("1. open")
                    if "4. close" in bar:
                        bar["4. sell price"] = bar.pop("4. close")

                # Then process latest date, keep only buy price
                latest_date = max(series.keys())
                latest_bar = series.get(latest_date, {})
                if isinstance(latest_bar, dict):
                    buy_val = latest_bar.get("1. buy price")
                    series[latest_date] = {"1. buy price": buy_val} if buy_val is not None else {}

                # Update Meta Data description
                meta = data.get("Meta Data", {})
                if isinstance(meta, dict):
                    meta["1. Information"] = "Daily Prices (buy price, high, low, sell price) and Volumes"

        except Exception as e:
            print(f"  Error processing {basename}: {e}")
            # If structure error, write as-is
            pass

        # Write to merged file
        fout.write(json.dumps(data, ensure_ascii=False) + "\n")
        print(f"  Added to merged file")

print(f"\nCrypto merge complete! Output saved to: {output_file}")
processed_count = len([f for f in files if any(symbol in os.path.basename(f) for symbol in crypto_symbols_usdt)])
print(f"Total symbols processed: {processed_count}")