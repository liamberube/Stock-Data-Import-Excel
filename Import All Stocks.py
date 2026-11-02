import os
import pandas as pd
import requests

# 1. Create target directory
os.makedirs("Data", exist_ok=True)

# 2. Configure request session & browser headers
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.nasdaq.com",
    "Referer": "https://www.nasdaq.com/",
}


def fetch_screener_download(exchange_code):
    """Fetches full stock records (including Sector and IPO Year) via download=true endpoint."""
    url = f"https://api.nasdaq.com/api/screener/stocks?download=true&exchange={exchange_code}"
    response = session.get(url, headers=headers)

    if response.status_code == 200:
        json_data = response.json()
        rows = json_data.get("data", {}).get("rows", [])
        df = pd.DataFrame(rows)
        if not df.empty:
            df["primaryExchange"] = exchange_code
        return df
    else:
        print(f"Failed to fetch {exchange_code}: HTTP {response.status_code}")
        return pd.DataFrame()


# 3. Fetch data for both NASDAQ and NYSE
print("Fetching NASDAQ stock list...")
df_nasdaq = fetch_screener_download("NASDAQ")

print("Fetching NYSE stock list...")
df_nyse = fetch_screener_download("NYSE")

# 4. Concatenate datasets
df_combined = pd.concat([df_nasdaq, df_nyse], ignore_index=True)

if not df_combined.empty:
    # 5. Clean marketCap string values to numeric floats
    if "marketCap" in df_combined.columns:
        df_combined["marketCap_numeric"] = (
            df_combined["marketCap"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("$", "", regex=False)
            .replace("", None)
            .astype(float)
        )
else:
    raise ValueError("No data retrieved.")

print("Cleaning The DataFrames")
#Keeping only Usedull columns
df_combined = df_combined[['symbol', 'name','volume','marketCap_numeric','country','ipoyear','industry','sector']]
#Removing Useless Stocks
df_combined = df_combined[df_combined["marketCap_numeric"] > 10000000000]
df_combined = df_combined[df_combined["ipoyear"] < "2016"]
df_combined = df_combined.dropna()
df_combined.to_csv("Data/Stock_data_shorter.csv", index_label=False)