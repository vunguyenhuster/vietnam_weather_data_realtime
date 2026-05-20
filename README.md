# Vietnam Weather Data Collector

Thu thập dữ liệu thời tiết **84 thành phố Việt Nam** từ [Open-Meteo API](https://open-meteo.com/) (miễn phí, không cần API key).

## Dữ liệu

| File | Mô tả | Độ phân giải | Thời gian |
|---|---|---|---|
| `weather_realtime.csv` | Điều kiện thời tiết hiện tại (realtime) | Mỗi 2.5 phút | Thời gian thực |
| `weather_hourly.csv` | Dữ liệu lịch sử hàng giờ | Hàng giờ (hourly) | 1/1/2025 → 19/5/2026 |

### weather_realtime.csv — 13 cột

`time`, `province`, `city`, `temperature`, `humidity`, `feels_like`, `precipitation`, `weather_code`, `cloudcover`, `pressure`, `wind_speed`, `wind_direction`, `wind_gust`, `is_day`

### weather_hourly.csv — 37 cột (3 key + 34 biến thời tiết)

**Nhiệt độ & độ ẩm:** `temperature_2m`, `relative_humidity_2m`, `apparent_temperature`, `dew_point_2m`, `vapour_pressure_deficit`, `wet_bulb_temperature_2m`

**Mưa & tuyết:** `precipitation`, `rain`, `snowfall`

**Mây:** `weather_code`, `cloud_cover`, `cloud_cover_low`, `cloud_cover_mid`, `cloud_cover_high`

**Áp suất:** `pressure_msl`, `surface_pressure`

**Gió:** `wind_speed_10m`, `wind_speed_100m`, `wind_direction_10m`, `wind_direction_100m`, `wind_gusts_10m`

**Bức xạ & nắng:** `is_day`, `sunshine_duration`, `shortwave_radiation`, `direct_radiation`, `diffuse_radiation`, `direct_normal_irradiance`, `terrestrial_radiation`, `terrestrial_radiation_instant`

**Đất & bốc hơi:** `et0_fao_evapotranspiration`, `soil_temperature_0_to_7cm`, `soil_moisture_0_to_7cm`

**Khí quyển:** `total_column_integrated_water_vapour`, `boundary_layer_height`

## 84 thành phố

Toàn bộ 63 tỉnh thành Việt Nam, bao gồm 5 thành phố trực thuộc trung ương (Hà Nội, Hồ Chí Minh, Hải Phòng, Đà Nẵng, Cần Thơ) và 79 thành phố trực thuộc tỉnh. Danh sách đầy đủ trong [`cities_coords.csv`](cities_coords.csv).

## Cài đặt

```bash
pip install -r requirements.txt
```

Yêu cầu: Python 3.8+ và `requests>=2.28`.

## Sử dụng

### Thu thập dữ liệu realtime

```bash
# Chạy liên tục, mỗi 2.5 phút thu thập 1 lần
python data_collector.py

# Chạy 1 lần duy nhất
python data_collector.py --once
```

Dữ liệu được ghi vào `weather_realtime.csv` ở chế độ append.

### Tải dữ liệu lịch sử hàng giờ

```bash
# Tải toàn bộ dữ liệu lịch sử
python fetch_historical.py --start 2025-01-01 --end 2026-05-19

# Resume nếu bị gián đoạn (bỏ qua thành phố đã tải)
python fetch_historical.py --start 2025-01-01 --end 2026-05-19 --resume
```

Dữ liệu được ghi vào `weather_hourly.csv`.

## Nguồn dữ liệu

- [Open-Meteo Forecast API](https://open-meteo.com/en/docs) — dữ liệu realtime
- [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api) — dữ liệu lịch sử (ERA5)
- Múi giờ: `Asia/Ho_Chi_Minh` (UTC+7)

## License

MIT
