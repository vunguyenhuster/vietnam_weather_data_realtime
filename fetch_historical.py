#!/usr/bin/env python3
"""
Fetch historical weather data from Open-Meteo Archive API.
Usage:
  python fetch_historical.py --start 2025-01-01 --end 2026-05-20
  python fetch_historical.py --start 2025-01-01 --end 2026-05-20 --resume
"""

import argparse
import csv
import os
import time
import requests

COORDS_FILE = "cities_coords.csv"
OUTPUT_FILE = "weather_historical.csv"


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


def completed_cities(filepath):
    """Trả về set các city đã có trong file output."""
    if not os.path.exists(filepath):
        return set()
    done = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            done.add(row["city"])
    return done


def fetch_historical(lat, lon, start_date, end_date):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "weather_code",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
        ],
        "timezone": "Asia/Ho_Chi_Minh"
    }
    for attempt in range(5):
        try:
            resp = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=45)
            if resp.status_code == 429:
                wait = (attempt + 1) * 10
                print(f"(429, retry in {wait}s)", end=" ", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            daily = data.get("daily", {})
            rows = []
            dates = daily.get("time", [])
            temps_max = daily.get("temperature_2m_max", [])
            temps_min = daily.get("temperature_2m_min", [])
            temps_mean = daily.get("temperature_2m_mean", [])
            precips = daily.get("precipitation_sum", [])
            codes = daily.get("weather_code", [])
            winds = daily.get("wind_speed_10m_max", [])
            gusts = daily.get("wind_gusts_10m_max", [])
            dirs = daily.get("wind_direction_10m_dominant", [])
            for i, date in enumerate(dates):
                rows.append({
                    "date": date,
                    "temp_max": temps_max[i] if i < len(temps_max) else None,
                    "temp_min": temps_min[i] if i < len(temps_min) else None,
                    "temp_mean": temps_mean[i] if i < len(temps_mean) else None,
                    "precipitation": precips[i] if i < len(precips) else None,
                    "weather_code": codes[i] if i < len(codes) else None,
                    "wind_speed": winds[i] if i < len(winds) else None,
                    "wind_gusts": gusts[i] if i < len(gusts) else None,
                    "wind_direction": dirs[i] if i < len(dirs) else None,
                })
            return rows
        except Exception as e:
            if attempt < 4:
                time.sleep(5)
                continue
            print(f"(ERROR: {e})", end=" ", flush=True)
            return []
    return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--resume", action="store_true", help="Skip cities already in output file")
    args = parser.parse_args()

    cities = load_cities(COORDS_FILE)
    done = completed_cities(OUTPUT_FILE) if args.resume else set()

    if args.resume:
        cities = [c for c in cities if c["city"] not in done]
        if not cities:
            print("All cities already fetched. Nothing to do.")
            return
        print(f"Resuming: {len(cities)} cities remaining")

    mode = 'a' if args.resume else 'w'
    with open(OUTPUT_FILE, mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow([
                "date", "province", "city",
                "temp_max", "temp_min", "temp_mean",
                "precipitation", "weather_code",
                "wind_speed_max", "wind_gusts_max", "wind_direction"
            ])

        for i, city in enumerate(cities):
            label = f"[{i+1}/{len(cities)}] {city['city']}"
            print(f"{label}...", end=" ", flush=True)
            rows = fetch_historical(city["lat"], city["lon"], args.start, args.end)
            for r in rows:
                writer.writerow([
                    r["date"], city["province"], city["city"],
                    r["temp_max"], r["temp_min"], r["temp_mean"],
                    r["precipitation"], r["weather_code"],
                    r["wind_speed"], r["wind_gusts"], r["wind_direction"]
                ])
            f.flush()
            print(f"{len(rows)} days")
            time.sleep(1.0)  # chậm hơn để tránh rate limit

    total = sum(1 for _ in open(OUTPUT_FILE, encoding='utf-8')) - 1
    print(f"\nDone! {total} rows saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
