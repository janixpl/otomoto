import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import root_mean_squared_error
from sklearn.impute import SimpleImputer
import os

# Funkcja do przekształcania liczbowych danych tekstowych
def process_numeric_column(col):
    if col.str.contains('km').any():  # Jeśli kolumna zawiera "km"
        return col.str.replace(' km', '').str.replace(' ', '').astype(float)
    elif col.str.contains('cm3').any():  # Jeśli kolumna zawiera "cm3"
        return col.str.replace(' cm3', '').str.replace(' ', '').astype(float)
    elif col.str.contains('KM').any():  # Jeśli kolumna zawiera "KM"
        return col.str.replace(' KM', '').str.replace(' ', '').astype(float)
    elif col.str.contains(',').any():  # Sprawdzamy czy są przecinki
        # Usuwamy spacje jako separator tysięcy, zamieniamy przecinki na kropki
        return col.str.replace(' ', '').str.replace(',', '.').astype(float)
    else:
        return pd.to_numeric(col, errors='coerce')  # Konwertujemy na liczby (jeśli możliwe)

# Wczytanie danych
data = pd.read_csv('data/otomoto_data.csv')

# Konwersja kolumn liczbowych
numeric_columns = ['engine_capacity', 'engine_power', 'mileage', 'price']
for col in numeric_columns:
    data[col] = process_numeric_column(data[col])

# Konwersja kolumn kategorycznych na liczby (np. Label Encoding)
categorical_columns = ['car_model', 'model', 'version', 'color', 'gearbox', 'transmission', 'fuel_type',
                       'body_type', 'new_used', 'no_accident', 'country_origin', 'has_registration', 'registered']
for col in categorical_columns:
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col].astype(str))  # Upewniamy się, że kolumny są traktowane jako tekst

# Przygotowanie danych
X = data[['car_model', 'year', 'model', 'version', 'door_count',
            'color', 'gearbox', 'engine_capacity', 'engine_power', 'transmission',
            'fuel_type', 'body_type', 'new_used', 'mileage', 'no_accident',
            'country_origin', 'has_registration', 'registered']]  # cechy

y = data['price']  # cel

print(data.isna().sum())

# Usuwamy wiersze z brakującymi danymi w ważnych kolumnach przed podziałem
important_columns = ['engine_capacity', 'engine_power', 'door_count']
X_clean = X.dropna(subset=important_columns)
y_clean = y[X_clean.index]

# Teraz dzielimy dane na treningowe i testowe
X_train, X_test, y_train, y_test = train_test_split(X_clean, y_clean, test_size=0.2, random_state=42)

# Rozpoczynamy eksperyment w MLflow
mlflow.set_experiment("otomoto_price_prediction")  # Tworzy eksperyment o nazwie 'otomoto_price_prediction'

# Tworzymy ścieżkę zapisu w volume (np. /app/output)
output_path = "/app/output"

with mlflow.start_run():  # Rozpoczyna nowy eksperyment (run)
    
    # Stworzenie modelu
    model = LinearRegression()
    
    # Trening modelu
    model.fit(X_train, y_train)
    
    # Predykcja i obliczanie metryk
    y_pred = model.predict(X_test)
    rmse = root_mean_squared_error(y_test, y_pred)  # Używamy funkcji RMS w sklearn
    
    # Logowanie parametru
    mlflow.log_param("model_type", "LinearRegression")
    
    # Logowanie metryk
    mlflow.log_metric("rmse", rmse)
    
    # Logowanie modelu
    mlflow.sklearn.log_model(model, "model")
    
    # Logowanie pliku z wynikami (opcjonalnie)
    results_filename = os.path.join(output_path, 'rmse_results.txt')
    with open(results_filename, 'w') as f:
        f.write(f"RMSE: {rmse}")
    
    # Logowanie pliku CSV z danymi
    data_filename = os.path.join(output_path, 'otomoto_data_clean.csv')
    data.to_csv(data_filename, index=False)
    
    print(f"RMSE: {rmse}")

mlflow_tracking_uri = "sqlite:///mlflow.db"

# Uruchomienie MLflow UI
try:
    print("Uruchamianie MLflow UI...")
    os.system(f"mlflow ui --backend-store-uri {mlflow_tracking_uri} --default-artifact-root {output_path} --host 0.0.0.0 --port 5001")
    print("MLflow UI jest dostępne pod adresem: http://localhost:5001")
except Exception as e:
    print(f"Nie udało się uruchomić MLflow UI: {e}")