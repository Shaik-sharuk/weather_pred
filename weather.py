from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Replace with your OpenWeatherMap API key
API_KEY = "Enter your api key"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

@app.route('/')
def home():
    """Render the home page."""
    return render_template("index.html")

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        weather_info = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],  # Feels like temperature
            "humidity": data["main"]["humidity"],
            "weather": data["weather"][0]["description"],
            "icon": f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
            "wind_speed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "visibility": data.get("visibility", "N/A"),
            "snow": data.get("snow", {}).get("1h", 0),  # Snow percentage
            "fog_visibility": "Low" if data.get("visibility", 10000) < 2000 else "Clear",
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime('%Y-%m-%d %H:%M:%S'),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime('%Y-%m-%d %H:%M:%S'),
        }

        return jsonify(weather_info)

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Unable to fetch weather data: {str(e)}"}), 500

@app.route('/forecast', methods=['GET'])
def get_forecast():
    """Fetch 5-day weather forecast data for a specified city."""
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(FORECAST_URL, params=params)
        response.raise_for_status()
        data = response.json()

        forecast = []
        daily_forecast = {}
        
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            forecast_entry = {
                "time": entry["dt_txt"],
                "temperature": entry["main"]["temp"],
                "feels_like": entry["main"]["feels_like"],
                "humidity": entry["main"]["humidity"],
                "weather": entry["weather"][0]["description"],
                "rain": entry.get("rain", {}).get("3h", 0),
                "icon": f"https://openweathermap.org/img/wn/{entry['weather'][0]['icon']}@2x.png"
            }
            
            forecast.append(forecast_entry)
            
            if date not in daily_forecast:
                daily_forecast[date] = []
            daily_forecast[date].append(forecast_entry)

        return jsonify({
            "forecast": forecast,
            "daily_forecast": daily_forecast
        })
    
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Unable to fetch forecast data: {str(e)}"}), 500
    except KeyError as e:
        return jsonify({"error": f"Invalid data received from the API: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
