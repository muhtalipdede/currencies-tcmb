import requests
import pandas as pd
import datetime
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

load_dotenv()

def get_exchange_rates(series, start_date, end_date):
    try:
        api_key = os.environ.get("TCMB_API_KEY")
        if api_key is None:
            raise ValueError("TCMB_API_KEY ortam değişkeni bulunamadı.")
        
        url = f"https://evds2.tcmb.gov.tr/service/evds/series={series}&startDate={start_date}&endDate={end_date}&type=json"
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
    
def write_to_csv(exchange_rate_date, exchange_rate, currency_name):
    try:
        currency_dir = "currency"
        if not os.path.exists(currency_dir):
            os.makedirs(currency_dir)
        file_path = currency_dir + "/" + currency_name + ".csv"
        if not os.path.exists(file_path):
            data = {
                "Tarih": [exchange_rate_date],
                currency_name: [exchange_rate],
            }
            df = pd.DataFrame(data)
            df.to_csv(file_path, index=False)
            return
        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=["Tarih", currency_name])
        
        if exchange_rate_date in df["Tarih"].values:
            print("Veri zaten mevcut.")
            return
        
        exchange_rate_date = datetime.datetime.strptime(exchange_rate_date, "%d-%m-%Y").strftime("%d-%m-%Y")
        new_data = {
            "Tarih": [exchange_rate_date],
            currency_name: [exchange_rate],
        }
        new_df = pd.DataFrame(new_data)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(file_path, index=False)
    except Exception as e:
        print(f"Error: {e}")

def plot_all_csv_files(file_list):
    try:
        for file in file_list:
            file_path = "currency/" + file
            df = pd.read_csv(file_path)
            df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d-%m-%Y")
            df = df.sort_values(by="Tarih")
            df.plot(x="Tarih", y=file.replace(".csv", ""), kind="line")
            image_file_name = file.replace(".csv", ".png")
            image_file_name = "currency/" + image_file_name
            plt.savefig(image_file_name)
            plt.close()
    except Exception as e:
        print(f"Error: {e}")

series_list = ["TP.DK.USD.S.YTL", "TP.DK.USD.A.YTL", "TP.DK.EUR.S.YTL", "TP.DK.EUR.A.YTL", "TP.DK.GBP.S.YTL", "TP.DK.GBP.A.YTL", "TP.DK.CHF.S.YTL", "TP.DK.CHF.A.YTL", "TP.DK.JPY.S.YTL", "TP.DK.JPY.A.YTL"]
def main():
    end_date = datetime.date.today().strftime("%d-%m-%Y")
    start_date = datetime.date.today() - datetime.timedelta(days=1000)
    start_date = start_date.strftime("%d-%m-%Y")
    file_list = []
    for series in series_list:
        exchange_rates = get_exchange_rates(series, start_date, end_date)
        series_name = series.replace(".", "_")
        file_list.append(series_name + ".csv")
        for exchange_rate_item in exchange_rates:
            exchange_rate = exchange_rate_item[series_name]
            exchange_rate_date = exchange_rate_item["Tarih"]
            if exchange_rate is not None and exchange_rate_date is not None:
                write_to_csv(exchange_rate_date, exchange_rate, series_name)
            else:
                print("Veri kaydedilemedi.")

    plot_all_csv_files(file_list)

if __name__ == "__main__":
    main()