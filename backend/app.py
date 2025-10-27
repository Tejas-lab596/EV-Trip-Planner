from flask import Flask, jsonify, request
import math

app = Flask(__name__)

# Sample charging station data
STATIONS = [
    {
        "id": 1,
        "name": "EV FastCharge - Pune",
        "lat": 18.5204,
        "lon": 73.8567,
        "img": "https://via.placeholder.com/400x200?text=FastCharge+Pune"
    },
    {
        "id": 2,
        "name": "GreenPlug Station - Mumbai",
        "lat": 19.0760,
        "lon": 72.8777,
        "img": "https://via.placeholder.com/400x200?text=GreenPlug+Mumbai"
    },
]

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two points (in km)."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    return R * 2 * math.asin(math.sqrt(a))

@app.route('/')
def home():
    return jsonify({"message": "EV Trip Planner API running!"})

@app.route('/stations')
def get_stations():
    return jsonify({"stations": STATIONS})

@app.route('/select-station', methods=['POST'])
def select_station():
    data = request.json
    station_id = data.get("station_id")
    user_lat = data.get("lat")
    user_lon = data.get("lon")
    battery = data.get("battery", 80)  # default %
    last_charge_km = data.get("last_charge_km", 40)
    efficiency = 6.0  # km per 1% battery

    station = next((s for s in STATIONS if s["id"] == station_id), None)
    if not station:
        return jsonify({"error": "Station not found"}), 404

    distance = haversine(user_lat, user_lon, station["lat"], station["lon"])
    est_range = battery * efficiency
    total_capacity_km = 100 * efficiency
    battery_health = round((est_range / total_capacity_km) * 100, 1)

    result = {
        "station": station,
        "distance_to_station_km": round(distance, 2),
        "battery_percentage": battery,
        "estimated_range_km": round(est_range, 1),
        "battery_health_%": battery_health,
        "distance_since_last_charge_km": last_charge_km,
        "battery_used_since_last_charge_%": round((last_charge_km / efficiency), 1),
        "estimated_arrival_time_min": round(distance, 1)
    }

    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
