import requests
import pandas as pd
import datetime
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

def get_exchange_rates(start_date, end_date):
    try:
        api_key = os.environ.get("TCMB_API_KEY")
        if api_key is None:
            raise ValueError("TCMB_API_KEY ortam değişkeni bulunamadı.")
        
        url = f"https://evds2.tcmb.gov.tr/service/evds/series=TP.DK.USD.S.YTL&startDate={start_date}&endDate={end_date}&type=json"
        print(url)
        headers = {
            "key": api_key,
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status() 
        data = response.json()
        
        if "error" in data:
            raise ValueError(data["error"]["message"])
        
        return data["items"]
    except Exception as e:
        print(f"Error: {e}")
        return None
    
def write_to_csv(exchange_rate_date, exchange_rate):
    try:
        file_path = "usd_try.csv"
        if not os.path.exists(file_path):
            data = {
                "Tarih": [exchange_rate_date],
                "USD/TRY": [exchange_rate],
            }
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            return
        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=["Tarih", "USD/TRY"])
        
        if exchange_rate_date in df["Tarih"].values:
            print("Veri zaten mevcut.")
            return
        
        exchange_rate_date = datetime.datetime.strptime(exchange_rate_date, "%d-%m-%Y").strftime("%d-%m-%Y")
        new_data = {
            "Tarih": [exchange_rate_date],
            "USD/TRY": [exchange_rate],
        }
        new_df = pd.DataFrame(new_data)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error: {e}")

def main():
    end_date = datetime.date.today().strftime("%d-%m-%Y")
    start_date = datetime.date.today() - datetime.timedelta(days=30)
    start_date = start_date.strftime("%d-%m-%Y")
    exchange_rates = get_exchange_rates(start_date, end_date)
    for exchange_rate_item in exchange_rates:
        print(exchange_rate_item)
        exchange_rate = exchange_rate_item["TP_DK_USD_S_YTL"]
        exchange_rate_date = exchange_rate_item["Tarih"]
        if exchange_rate is not None and exchange_rate_date is not None:
            write_to_csv(exchange_rate_date, exchange_rate)
            print("Veri başarıyla kaydedildi.")
        else:
            print("Veri kaydedilemedi.")

    ## plot usd_try.csv and save as usd_try.png
    df = pd.read_csv("usd_try.csv")
    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d-%m-%Y")
    df = df.sort_values(by="Tarih")
    df.plot(x="Tarih", y="USD/TRY", kind="line")
    plt.savefig("usd_try.png")

if __name__ == "__main__":
    main()