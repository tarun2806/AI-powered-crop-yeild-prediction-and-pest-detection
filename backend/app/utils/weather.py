import requests
import os
import redis
import json
from datetime import datetime, timedelta

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        
        try:
            self.redis = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True)
            print(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"❌ Redis Connection Error: {str(e)}")
            self.redis = None

    def get_weather(self, district):
        """
        Fetches weather data for a district. Uses Redis for distributed caching.
        """
        cache_key = f"weather:{district}"
        
        # Check Redis cache
        if self.redis:
            try:
                cached_data = self.redis.get(cache_key)
                if cached_data:
                    print(f"🌡️ Using Redis cached weather for {district}")
                    return json.loads(cached_data)
            except Exception as e:
                print(f"⚠️ Redis read error: {e}")

        if not self.api_key:
            print("⚠️ OpenWeather API Key missing.")
            return None

        try:
            params = {
                'q': f"{district},IN",
                'appid': self.api_key,
                'units': 'metric'
            }
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            
            weather_raw = response.json()
            processed_data = {
                'temperature': weather_raw['main'].get('temp'),
                'humidity': weather_raw['main'].get('humidity'),
                'rainfall': weather_raw.get('rain', {}).get('1h', 0) * 24 
            }
            
            # Save to Redis with 30-minute expiration
            if self.redis:
                try:
                    self.redis.setex(cache_key, 1800, json.dumps(processed_data))
                except Exception as e:
                    print(f"⚠️ Redis write error: {e}")
            
            return processed_data

        except Exception as e:
            print(f"❌ Weather API Error: {str(e)}")
            return None

# Singleton instance
weather_service = WeatherService()
