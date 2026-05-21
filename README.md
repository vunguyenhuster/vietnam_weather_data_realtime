# Vietnam Weather Data Collector

Thu thập dữ liệu thời tiết **84 thành phố Việt Nam** từ [Open-Meteo API](https://open-meteo.com/) (miễn phí, không cần API key).

## Dữ liệu

`weather_hourly.csv` — dữ liệu thời tiết hàng giờ cho 84 thành phố, từ 1/1/2025 đến 19/5/2026. Định dạng thời gian: `YYYY-MM-DD HH:MM:SS`.

### 37 cột (3 key + 34 biến thời tiết)

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

## Quick Start

```bash
# Lần đầu — tải toàn bộ dữ liệu
python fetch_historical.py --start 2025-01-01 --end 2026-05-20

# Hàng ngày — thêm dữ liệu mới
python fetch_historical.py --end 2026-05-21 --append
```

## Sử dụng

### Tải dữ liệu lịch sử hàng giờ

```bash
# Tải toàn bộ dữ liệu lịch sử (lần đầu)
python fetch_historical.py --start 2025-01-01 --end 2026-05-19

# Resume nếu bị gián đoạn (bỏ qua thành phố đã tải)
python fetch_historical.py --start 2025-01-01 --end 2026-05-19 --resume

# Thêm dữ liệu ngày mới (tự động chỉ lấy phần chưa có)
python fetch_historical.py --end 2026-05-25 --append
```

| Chế độ | Cách dùng | Mô tả |
|---|---|---|
| Lần đầu | `--start DATE --end DATE` | Ghi đè file, fetch toàn bộ từ đầu |
| Resume | `--start DATE --end DATE --resume` | Bỏ qua thành phố đã có, tiếp tục thành phố còn thiếu |
| **Append** | `--end DATE --append` | Tự tìm ngày mới nhất của từng thành phố, chỉ fetch từ sau ngày đó. Không đụng data cũ |

Dữ liệu được ghi vào `weather_hourly.csv`. Định dạng thời gian: `YYYY-MM-DD HH:MM:SS`.

## Nguồn dữ liệu

- [Open-Meteo Historical API](https://open-meteo.com/en/docs/historical-weather-api) — dữ liệu lịch sử (ERA5)
- Múi giờ: `Asia/Ho_Chi_Minh` (UTC+7)

## License

MIT
