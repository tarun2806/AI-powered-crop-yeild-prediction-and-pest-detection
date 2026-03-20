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
        self.in_memory_cache = {} # Fallback
        
        try:
            self.redis = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True, socket_connect_timeout=2)
            self.redis.ping()
            print(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"❌ Redis Connection Error: {str(e)}. Falling back to in-memory cache.")
            self.redis = None

    def get_weather(self, district):
        """
        Fetches weather data for a district. Uses Redis for distributed caching, or in-memory fallback.
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
                self.redis = None # Fallback to in-memory for future requests if Redis fails
                
        # Check In-Memory fallback cache
        if not self.redis and cache_key in self.in_memory_cache:
            cache_entry = self.in_memory_cache[cache_key]
            if datetime.now() < cache_entry['expiry']:
                print(f"🌡️ Using In-Memory cached weather for {district}")
                return cache_entry['data']
            else:
                del self.in_memory_cache[cache_key] # Expired

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
            
            # Save to Cache with 30-minute expiration
            if self.redis:
                try:
                    self.redis.setex(cache_key, 1800, json.dumps(processed_data))
                except Exception as e:
                    print(f"⚠️ Redis write error: {e}")
                    self.redis = None
                    self.in_memory_cache[cache_key] = {"data": processed_data, "expiry": datetime.now() + timedelta(minutes=30)}
            else:
                self.in_memory_cache[cache_key] = {"data": processed_data, "expiry": datetime.now() + timedelta(minutes=30)}
                print(f"💾 Saved weather to In-Memory cache for {district}")
            
            return processed_data

        except Exception as e:
            print(f"❌ Weather API Error: {str(e)}. Using safe fallback data.")
            # Hardened Fallback: Return a valid but neutral weather object instead of None
            return {
                'temperature': 25.0,
                'humidity': 60.0,
                'rainfall': 0.0,
                'status': 'fallback'
            }

# Singleton instance
weather_service = WeatherService()
