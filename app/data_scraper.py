import csv
from playwright.sync_api import sync_playwright
car_models = ['acura',
'aixam',
'alfa-romeo',
'aston-martin',
'audi',
'austin',
'autobianchi',
'bentley',
'bmw',
'brilliance',
'buick',
'cadillac',
'chatenet',
'chevrolet',
'chrysler',
'citroen',
'dacia',
'daewoo',
'daihatsu',
'dfsk',
'dkw',
'dodge',
'faw',
'ferrari',
'fiat',
'ford',
'gaz',
'gmc',
'grecav',
'holden',
'honda',
'hummer',
'hyundai',
'infiniti',
'isuzu',
'iveco',
'jaguar',
'jeep',
'kia',
'lada',
'lamborghini',
'lancia',
'land-rover',
'lexus',
'ligier',
'lincoln',
'lotus',
'lti',
'maserati',
'maybach',
'mazda',
'mclaren',
'mercedes-benz',
'mercury',
'mg',
'microcar',
'mini',
'mitsubishi',
'nissan',
'nysa',
'oldsmobile',
'opel',
'peugeot',
'piaggio',
'plymouth',
'polonez',
'pontiac',
'porsche',
'renault',
'rolls-royce',
'rover',
'saab',
'saturn',
'seat',
'shuanghuan',
'skoda',
'smart',
'ssangyong',
'subaru',
'suzuki',
'syrena',
'talbot',
'tarpan',
'tata',
'tavria',
'tesla',
'toyota',
'trabant',
'triumph',
'uaz',
'vauxhall',
'volkswagen',
'volvo',
'marka_warszawa',
'wartburg',
'wolga',
'zaporozec',
'zuk',
'inny',
'abarth',
'casalini',
'ds-automobiles',
'ram',
'cupra',
'alpine',
'bac',
'vanderhall']

# Funkcja do zbierania danych z pojedynczej oferty
def get_offer_details(page, offer_url):
    page.goto(offer_url)  # Przechodzimy na stronę oferty
    page.click("css=[data-testid='accordion-toggle-button']")  # Rozwijamy sekcję z detalami
    details = {}
    array = ['year', 'model', 'version', 'door_count', 'nr_seats', 'color', 'gearbox', 'engine_capacity', 'engine_power', 'transmission', 'fuel_type', 'body_type']
    
    for item in array:
        locator = page.locator(f'div[data-testid={item}] > div > p:nth-of-type(2)')
        if locator.is_visible():
            details[item] = locator.text_content().strip()  # Zbieramy wartość, usuwając zbędne białe znaki
        else:
            details[item] = None  # Jeśli nie ma wartości, zapisujemy None
        
    # Pobieranie ceny
    price_locator = page.locator("h3.offer-price__number")
    if price_locator.is_visible():
        details['price'] = price_locator.text_content().strip()  # Zbieramy cenę
    else:
        details['price'] = None  # Jeśli ceny nie ma, przypisujemy None

    return details

# Funkcja główna, która zbiera dane z kilku linków i zapisuje je do CSV
def collect_data_to_csv():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Uruchom przeglądarkę w trybie widocznym
        page = browser.new_page()

        # Przygotowanie pliku CSV
        with open('data/otomoto_data.csv', mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=['car_model', 'year', 'model', 'version', 'door_count', 'nr_seats', 'color', 'gearbox', 'engine_capacity', 'engine_power', 'transmission', 'fuel_type', 'body_type', 'price'])
            writer.writeheader()  # Zapisz nagłówki w pliku CSV

            for car_model in car_models:
                print(f'Zbieram dane dla modelu: {car_model}')
                page.goto(f"https://www.otomoto.pl/osobowe/{car_model}")  # Strona, którą analizujemy
                
                # Klikamy w przycisk zgody na cookies, tylko raz na stronie głównej
                if page.locator("css=#onetrust-accept-btn-handler").is_visible():
                    page.click("css=#onetrust-accept-btn-handler")
                
                # Znajdź wszystkie linki na stronie
                links = page.locator("a")

                # Zbieramy linki, które zawierają 'otomoto.pl/osobowe/oferta'
                filtered_links = set()
                for link in links.element_handles():
                    href = link.get_attribute("href")
                    if href and "otomoto.pl/osobowe/oferta" in href:
                        filtered_links.add(href)

                # Iterujemy przez wszystkie linki i zbieramy dane
                for link in filtered_links:
                    print(f'Zbieranie danych z: {link}')
                    details = get_offer_details(page, link)  # Zbieramy dane z oferty
                    details['car_model'] = car_model  # Dodajemy nazwę modelu do danych
                    writer.writerow(details)  # Zapisz dane do pliku CSV

        browser.close()  # Zamykanie przeglądarki po zakończeniu zbierania danych

# Wywołanie funkcji
collect_data_to_csv()