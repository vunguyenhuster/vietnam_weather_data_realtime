#!/usr/bin/env python3
"""
Vietnam Realtime Weather Data Collection (using Open-Meteo)
- Local/VPS: python data_collector.py          (loop mode, every 2-4 min)
- GitHub Actions: python data_collector.py --once  (single pass)
"""

import argparse
import csv
import os
import sys
import time
import requests
from datetime import datetime, timezone

# ========== CONFIG ==========
COORDS_FILE = "cities_coords.csv"
WEATHER_FILE = "weather_realtime.csv"
COLLECTION_INTERVAL_SECONDS = 150
REQUEST_DELAY = 0.2

# ========== WEATHER COLLECTION ==========
def load_cities(filepath):
    cities = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            cities.append({
                "city": row["city"],
                "province": row.get("province", ""),
                "lat": float(row["latitude"]),
                "lon": float(row["longitude"])
            })
    return cities


def fetch_weather(lat, lon):
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": [
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation", "weather_code", "cloud_cover",
            "pressure_msl", "wind_speed_10m", "wind_direction_10m",
            "wind_gusts_10m", "is_day"
        ],
        "timezone": "Asia/Ho_Chi_Minh"
    }
    try:
        resp = requests.get("https://api.open-meteo.com/v1/forecast", params=params, timeout=15)
        resp.raise_for_status()
        return resp.json().get("current", {})
    except Exception as e:
        print(f"API error ({lat},{lon}): {e}")
        return None


def ensure_header(weather_file):
    if not os.path.exists(weather_file):
        with open(weather_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "time", "province", "city",
                "temperature", "humidity", "feels_like",
                "precipitation", "weather_code", "cloudcover",
                "pressure", "wind_speed", "wind_direction",
                "wind_gust", "is_day"
            ])


def collect_once(cities, weather_file):
    now_utc = datetime.now(timezone.utc).isoformat()
    rows_written = 0
    for city in cities:
        current = fetch_weather(city["lat"], city["lon"])
        if current:
            with open(weather_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    now_utc, city["province"], city["city"],
                    current.get("temperature_2m"),
                    current.get("relative_humidity_2m"),
                    current.get("apparent_temperature"),
                    current.get("precipitation"),
                    current.get("weather_code"),
                    current.get("cloud_cover"),
                    current.get("pressure_msl"),
                    current.get("wind_speed_10m"),
                    current.get("wind_direction_10m"),
                    current.get("wind_gusts_10m"),
                    current.get("is_day")
                ])
            rows_written += 1
        time.sleep(REQUEST_DELAY)
    return rows_written


def run_once():
    if not os.path.exists(COORDS_FILE):
        print(f"ERROR: {COORDS_FILE} not found. Run geocoding first.")
        sys.exit(1)

    cities = load_cities(COORDS_FILE)
    ensure_header(WEATHER_FILE)
    n = collect_once(cities, WEATHER_FILE)
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collected {n}/{len(cities)} cities.")
    print(f"Total rows in {WEATHER_FILE}: {sum(1 for _ in open(WEATHER_FILE, encoding='utf-8')) - 1}")


def run_loop():
    if not os.path.exists(COORDS_FILE):
        print(f"ERROR: {COORDS_FILE} not found. Run geocoding first.")
        sys.exit(1)

    cities = load_cities(COORDS_FILE)
    ensure_header(WEATHER_FILE)

    print(f"Starting loop: {len(cities)} cities, every {COLLECTION_INTERVAL_SECONDS}s.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            n = collect_once(cities, WEATHER_FILE)
            total = sum(1 for _ in open(WEATHER_FILE, encoding='utf-8')) - 1
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {n}/{len(cities)} cities. Total rows: {total}")
            time.sleep(COLLECTION_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nStopped.")


# ========== MAIN ==========
if __name__ == "__main__":
    # Fix Windows UTF-8 output
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    parser = argparse.ArgumentParser(description="Vietnam weather collector")
    parser.add_argument("--once", action="store_true", help="Run once and exit (for GitHub Actions)")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_loop()
