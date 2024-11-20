import csv
from playwright.sync_api import sync_playwright

car_models = ['lexus', 'ligier', 'lincoln',
              'lotus', 'lti', 'maserati', 'maybach', 'mazda', 'mclaren', 'mercedes-benz', 'mercury', 'mg', 'microcar',
              'mini', 'mitsubishi', 'nissan', 'nysa', 'oldsmobile', 'opel', 'peugeot', 'piaggio', 'plymouth',
              'polonez', 'pontiac', 'porsche', 'renault', 'rolls-royce', 'rover', 'saab', 'saturn', 'seat',
              'shuanghuan', 'skoda', 'smart', 'ssangyong', 'subaru', 'suzuki', 'syrena', 'talbot', 'tarpan',
              'tata', 'tavria', 'tesla', 'toyota', 'trabant', 'triumph', 'uaz', 'vauxhall', 'volkswagen',
              'volvo', 'marka_warszawa', 'wartburg', 'wolga', 'zaporozec', 'zuk', 'inny', 'abarth', 'casalini',
              'ds-automobiles', 'ram', 'cupra', 'alpine', 'bac', 'vanderhall']


# Funkcja do inicjalizacji przeglądarki
def initialize_browser():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    page = browser.new_page()
    return browser, page, playwright


# Funkcja do inicjalizacji pliku CSV
def initialize_csv(file_path, fieldnames):
    file = open(file_path, mode='a', newline='', encoding='utf-8')
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    # writer.writeheader()
    return file, writer


# Funkcja do zbierania wszystkich linków ofert
def collect_all_offer_links(page, car_model):
    base_url = f"https://www.otomoto.pl/osobowe/{car_model}?search%5Bfilter_enum_damaged%5D=0&search%5Border%5D=0"
    page_number = 1
    all_links = set()

    while True:
        print(f"Pobieram linki z strony: {page_number} dla modelu {car_model}")
        page.goto(f"{base_url}&page={page_number}")

        # Pobieramy linki z bieżącej strony
        links = page.locator("a")
        current_links = set()
        for link in links.element_handles():
            href = link.get_attribute("href")
            if href and "otomoto.pl/osobowe/oferta" in href:
                current_links.add(href)

        # Jeśli nie ma nowych linków, kończymy iterację
        if not current_links or current_links.issubset(all_links):
            break

        all_links.update(current_links)
        page_number += 1  # Przechodzimy do następnej strony

    return all_links


# Funkcja do pobierania szczegółów oferty
def get_offer_details(page, offer_url):
    page.goto(offer_url)

    # Klikamy "zgadzam się" na cookies, jeśli to konieczne
    if page.locator("css=#onetrust-accept-btn-handler").is_visible():
        page.click("css=#onetrust-accept-btn-handler")

    page.click("css=[id='content-technical-specs-section__toggle']")

    details = {}
    array = ['year', 'model', 'version', 'door_count', 'nr_seats', 'color', 'gearbox',
             'engine_capacity', 'engine_power', 'transmission', 'fuel_type', 'body_type']

    for item in array:
        locator = page.locator(f'div[data-testid={item}] > div > p:nth-of-type(2)')
        details[item] = locator.text_content().strip() if locator.is_visible() else None

    # Pobieranie dodatkowych informacji
    page.click("css=[id='content-condition-history-section__toggle']")
    
    array2 = ['new_used', 'mileage', 'no_accident', 'country_origin', 'has_registration', 'registered']
    for item in array2:
        locator = page.locator(f'div[data-testid={item}] > div > p:nth-of-type(2)')
        details[item] = locator.text_content().strip() if locator.is_visible() else None

    # Pobieranie ceny
    price_locator = page.locator("h3.offer-price__number")
    details['price'] = price_locator.text_content().strip() if price_locator.is_visible() else None

    return details


# Funkcja do przetwarzania danych z linków
def collect_data_from_links(page, file, writer, car_model, offer_links):
    for link in offer_links:
        print(f"Zbieranie danych z oferty: {link}")
        try:
            details = get_offer_details(page, link)
            details['car_model'] = car_model
            writer.writerow(details)  # Zapisujemy dane do pliku CSV
            file.flush()  # Wymuszenie zapisu na bieżąco
        except Exception as e:
            print(f"Błąd przy zbieraniu danych z oferty {link}: {e}")

# Funkcja główna
def collect_data_to_csv():
    # Inicjalizacja przeglądarki i pliku CSV
    browser, page, playwright = initialize_browser()
    fieldnames = ['car_model', 'year', 'model', 'version', 'door_count', 'nr_seats',
                  'color', 'gearbox', 'engine_capacity', 'engine_power', 'transmission',
                  'fuel_type', 'body_type', 'new_used', 'mileage', 'no_accident',
                  'country_origin', 'has_registration', 'registered', 'price']
    file, writer = initialize_csv('otomoto_data.csv', fieldnames)

    try:
        # Iteracja przez modele samochodów
        for car_model in car_models:
            print(f"Rozpoczynam zbieranie danych dla modelu: {car_model}")

            # Krok 1: Zbieranie linków
            offer_links = collect_all_offer_links(page, car_model)
            print(f"Znaleziono {len(offer_links)} ofert dla modelu {car_model}")

            # Krok 2: Pobieranie danych z linków
            collect_data_from_links(page, file, writer, car_model, offer_links)

    finally:
        # Zamykamy przeglądarkę i plik
        browser.close()
        file.close()
        playwright.stop()


# Wywołanie funkcji
collect_data_to_csv()