import requests
from bs4 import BeautifulSoup
import csv

url='https://www.otomoto.pl/osobowe'

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"}
response = requests.get(url, headers=headers)

def save_data(data):
    path = "data/page1.txt"
    with open(path, "w") as f:
        f.write(data)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, "html.parser")
    # Przetwarzaj stronę
    save_data(str(soup))
    ceny = soup.find_all('h3')
    for tag in ceny:
        print(tag.get_text())
else:
    print("Error:", response.status_code)