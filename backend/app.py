import os
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret")

@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200

# Optional demo endpoints used by your frontend
STATIONS = [
    {"id": 1, "name": "Alpha Charger", "lat": 12.9716, "lon": 77.5946,
     "img": "https://picsum.photos/seed/alpha/800/400"},
    {"id": 2, "name": "Beta Supercharge", "lat": 13.0827, "lon": 80.2707,
     "img": "https://picsum.photos/seed/beta/800/400"},
]

@app.get("/stations")
def stations():
    return jsonify({"stations": STATIONS})

@app.post("/select-station")
def select_station():
    body = request.get_json(force=True) or {}
    st_id = int(body.get("station_id", 0))
    lat = float(body.get("lat", 0))
    lon = float(body.get("lon", 0))
    battery = float(body.get("battery", 80))
    last_km = float(body.get("last_charge_km", 0))
    st = next((s for s in STATIONS if s["id"] == st_id), None)
    if not st:
        return jsonify({"error": "station_not_found"}), 404
    dist = round(((st["lat"]-lat)**2 + (st["lon"]-lon)**2) ** 0.5 * 111, 2)
    health_pct = 95.0
    km_per_pct = 6.0 * (health_pct/100.0)
    return jsonify({
        "station": st,
        "distance_to_station_km": dist,
        "battery_percentage": battery,
        "battery_health_%": health_pct,
        "estimated_range_km": round(battery*km_per_pct,1),
        "distance_since_last_charge_km": last_km,
        "battery_used_since_last_charge_%": round(last_km/max(km_per_pct,1e-6),1)
    })
