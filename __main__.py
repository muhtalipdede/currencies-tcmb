import requests
import pandas as pd
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_exchange_rate():
    try:
        api_key = os.environ.get("TCMB_API_KEY")
        if api_key is None:
            raise ValueError("TCMB_API_KEY ortam değişkeni bulunamadı.")
        
        today = datetime.date.today().strftime("%d-%m-%Y")
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        yesterday = yesterday.strftime("%d-%m-%Y")
        url = f"https://evds2.tcmb.gov.tr/service/evds/series=TP.DK.USD.S.YTL&startDate={yesterday}&endDate={today}&type=json"
        print(url)
        headers = {
            "key": api_key,
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        data = response.json()
        print(data)
        return float(data["items"][-1]["TP_DK_USD_S_YTL"])
    except requests.exceptions.RequestException as e:
        print(f"Veri çekme hatası: {e}")
        return None
    
def write_to_csv(exchange_rate):
    today = datetime.date.today().strftime("%Y-%m-%d")
    df = pd.DataFrame({"Tarih": [today], "USD/TRY": [exchange_rate]})

    file_path = "usd_try.csv"

    if os.path.exists(file_path):
        existing_df = pd.read_csv(file_path)
        if today in existing_df["Tarih"].values:
            existing_df.loc[existing_df["Tarih"] == today, "USD/TRY"] = exchange_rate
        else:
            existing_df = existing_df.append(df, ignore_index=True)
        existing_df.to_csv(file_path, mode='w', header=True, index=False)
    else:
        df.to_csv(file_path, mode='w', header=True, index=False)

def main():
    exchange_rate = get_exchange_rate()
    if exchange_rate is not None:
        write_to_csv(exchange_rate)
        print("Veri başarıyla kaydedildi.")
    else:
        print("Veri kaydedilemedi.")

if __name__ == "__main__":
    main()