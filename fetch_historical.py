#!/usr/bin/env python3
"""
Fetch hourly historical weather data from Open-Meteo Archive API.
Usage:
  python fetch_historical.py --start 2025-01-01 --end 2026-05-20
  python fetch_historical.py --start 2025-01-01 --end 2026-05-20 --resume
"""

import argparse
import csv
import os
import sys
import time
import requests

sys.stdout.reconfigure(encoding='utf-8')

COORDS_FILE = "cities_coords.csv"
OUTPUT_FILE = "weather_hourly.csv"

HOURLY_VARIABLES = [
    # Nhiệt độ & độ ẩm
    "temperature_2m", "relative_humidity_2m", "apparent_temperature",
    "dew_point_2m", "vapour_pressure_deficit", "wet_bulb_temperature_2m",
    # Mưa & tuyết
    "precipitation", "rain", "snowfall",
    # Mã thời tiết & mây
    "weather_code", "cloud_cover", "cloud_cover_low",
    "cloud_cover_mid", "cloud_cover_high",
    # Áp suất
    "pressure_msl", "surface_pressure",
    # Gió
    "wind_speed_10m", "wind_speed_100m",
    "wind_direction_10m", "wind_direction_100m",
    "wind_gusts_10m",
    # Bức xạ & nắng
    "is_day", "sunshine_duration",
    "shortwave_radiation", "direct_radiation",
    "diffuse_radiation", "direct_normal_irradiance",
    "terrestrial_radiation", "terrestrial_radiation_instant",
    # Bốc hơi & đất
    "et0_fao_evapotranspiration",
    "soil_temperature_0_to_7cm", "soil_moisture_0_to_7cm",
    # Khí quyển
    "total_column_integrated_water_vapour", "boundary_layer_height",
]


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
    if not os.path.exists(filepath):
        return set()
    done = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            done.add(row["city"])
    return done


def fetch_hourly(lat, lon, start_date, end_date):
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": HOURLY_VARIABLES,
        "timezone": "Asia/Ho_Chi_Minh"
    }
    for attempt in range(5):
        try:
            resp = requests.get("https://archive-api.open-meteo.com/v1/archive", params=params, timeout=60)
            if resp.status_code == 429:
                wait = (attempt + 1) * 15
                print(f"(429, wait {wait}s)", end=" ", flush=True)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            data = resp.json()
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])
            if not times:
                return []
            rows = []
            for i, t in enumerate(times):
                row = {"time": t}
                for var in HOURLY_VARIABLES:
                    values = hourly.get(var, [])
                    row[var] = values[i] if i < len(values) else None
                rows.append(row)
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
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    cities = load_cities(COORDS_FILE)
    done = completed_cities(OUTPUT_FILE) if args.resume else set()

    if args.resume:
        cities = [c for c in cities if c["city"] not in done]
        if not cities:
            print("All cities already fetched.")
            return
        print(f"Resuming: {len(cities)} cities remaining")

    # Build header
    header = ["time", "province", "city"] + HOURLY_VARIABLES

    mode = 'a' if args.resume else 'w'
    with open(OUTPUT_FILE, mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(header)

        for i, city in enumerate(cities):
            label = f"[{i+1}/{len(cities)}] {city['city']}"
            print(f"{label}...", end=" ", flush=True)
            rows = fetch_hourly(city["lat"], city["lon"], args.start, args.end)
            for r in rows:
                row_data = [r["time"], city["province"], city["city"]]
                for var in HOURLY_VARIABLES:
                    row_data.append(r.get(var))
                writer.writerow(row_data)
            f.flush()
            print(f"{len(rows)} hours")
            if len(rows) == 0:
                print("  (cooling down 30s before next city)")
                time.sleep(30)
            else:
                time.sleep(2.0)

    total = sum(1 for _ in open(OUTPUT_FILE, encoding='utf-8')) - 1
    print(f"\nDone! {total} rows -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
