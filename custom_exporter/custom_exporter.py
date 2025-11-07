from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import requests
import json
import os
from datetime import datetime

# OpenWeather API конфигурация
OPENWEATHER_API_KEY = "e4ecf8a5a819a950418178e4bd8339a3"
CITY = "Moscow"
OPENWEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={OPENWEATHER_API_KEY}&units=metric"

# Alpha Vantage API конфигурация
ALPHA_VANTAGE_API_KEY = "F7ZAYLZGUJ8KZLPA"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={}&to_currency=RUB&apikey={}"

# Создаем метрики
weather_temperature = Gauge('weather_temperature', 'Current temperature in Celsius', ['city'])
weather_humidity = Gauge('weather_humidity', 'Current humidity percentage', ['city'])
weather_pressure = Gauge('weather_pressure', 'Current atmospheric pressure in hPa', ['city'])
weather_wind_speed = Gauge('weather_wind_speed', 'Current wind speed in m/s', ['city'])
weather_visibility = Gauge('weather_visibility', 'Current visibility in meters', ['city'])
weather_clouds = Gauge('weather_clouds', 'Current cloudiness percentage', ['city'])
weather_feels_like = Gauge('weather_feels_like', 'Feels like temperature', ['city'])

currency_rate_usd = Gauge('currency_rate_usd', 'USD to RUB exchange rate')
currency_rate_eur = Gauge('currency_rate_eur', 'EUR to RUB exchange rate')
currency_rate_gbp = Gauge('currency_rate_gbp', 'GBP to RUB exchange rate')

api_requests_total = Counter('api_requests_total', 'Total API requests made', ['api_name'])
api_errors_total = Counter('api_errors_total', 'Total API errors', ['api_name'])
request_duration = Histogram('api_request_duration_seconds', 'API request duration')

def get_weather_data():
    """Получение данных о погоде"""
    start_time = time.time()
    try:
        response = requests.get(OPENWEATHER_URL, timeout=10)
        api_requests_total.labels(api_name='openweather').inc()
        request_duration.observe(time.time() - start_time)
        
        if response.status_code == 200:
            data = response.json()
            
            weather_temperature.labels(city=CITY).set(data['main']['temp'])
            weather_humidity.labels(city=CITY).set(data['main']['humidity'])
            weather_pressure.labels(city=CITY).set(data['main']['pressure'])
            weather_wind_speed.labels(city=CITY).set(data['wind']['speed'])
            weather_visibility.labels(city=CITY).set(data.get('visibility', 0))
            weather_clouds.labels(city=CITY).set(data['clouds']['all'])
            weather_feels_like.labels(city=CITY).set(data['main']['feels_like'])
        else:
            api_errors_total.labels(api_name='openweather').inc()
            print(f"Weather API error: {response.status_code}")
            
    except Exception as e:
        api_errors_total.labels(api_name='openweather').inc()
        print(f"Weather API exception: {e}")

def get_currency_rates():
    """Получение курсов валют"""
    currencies = [
        ('USD', currency_rate_usd),
        ('EUR', currency_rate_eur),
        ('GBP', currency_rate_gbp)
    ]
    
    for currency_code, metric in currencies:
        start_time = time.time()
        try:
            url = ALPHA_VANTAGE_URL.format(currency_code, ALPHA_VANTAGE_API_KEY)
            response = requests.get(url, timeout=10)
            api_requests_total.labels(api_name='alphavantage').inc()
            request_duration.observe(time.time() - start_time)
            
            if response.status_code == 200:
                data = response.json()
                rate = data.get('Realtime Currency Exchange Rate', {}).get('5. Exchange Rate')
                if rate:
                    metric.set(float(rate))
            else:
                api_errors_total.labels(api_name='alphavantage').inc()
                print(f"Currency API error for {currency_code}: {response.status_code}")
                
        except Exception as e:
            api_errors_total.labels(api_name='alphavantage').inc()
            print(f"Currency API exception for {currency_code}: {e}")

if __name__ == '__main__':
    # Запуск HTTP сервера на порту 8000
    start_http_server(8000)
    print("Custom exporter started on port 8000")
    
    # Основной цикл сбора метрик
    while True:
        get_weather_data()
        get_currency_rates()
        time.sleep(20)  # Обновление каждые 20 секунд