from flask import Flask, jsonify, request
import os
import math
import pymysql
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=5,
        read_timeout=5,
        write_timeout=5,
    )

def init_db():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS charging_stations (
                  id INT AUTO_INCREMENT PRIMARY KEY,
                  name VARCHAR(128) NOT NULL,
                  latitude DOUBLE NOT NULL,
                  longitude DOUBLE NOT NULL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS trip_logs (
                  id BIGINT AUTO_INCREMENT PRIMARY KEY,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  user_battery_percent INT,
                  start_lat DOUBLE,
                  start_lon DOUBLE,
                  dest_lat DOUBLE,
                  dest_lon DOUBLE,
                  est_distance_km DOUBLE
                )
            """)
    finally:
        if conn: conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat/2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon/2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))

@app.get("/health")
def health():
    try:
        conn = get_db_connection()
        conn.ping(reconnect=True)
        return jsonify(status="ok"), 200
    except Exception as e:
        return jsonify(status="db_error", error=str(e)), 500

@app.post("/api/plan")
def plan_trip():
    """
    Request JSON:
    {
      "start": {"lat": 12.9, "lon": 77.6},
      "dest":  {"lat": 13.0, "lon": 77.7},
      "battery": 72,                # %
      "efficiency": 6.0,            # km per % battery (example)
      "battery_health": 94,         # %
      "last_charge_km": 35
    }
    """
    data = request.get_json(force=True)
    start = data.get("start", {})
    dest  = data.get("dest", {})
    battery = float(data.get("battery", 100))
    efficiency = float(data.get("efficiency", 5.0))
    battery_health = float(data.get("battery_health", 100))
    last_charge_km = float(data.get("last_charge_km", 0))

    # Distance
    distance = haversine(
        float(start.get("lat")), float(start.get("lon")),
        float(dest.get("lat")), float(dest.get("lon"))
    )

    # Simple range estimate (battery health degrades usable range)
    usable_pct = battery * (battery_health / 100.0)
    est_range = usable_pct * efficiency

    # Find nearest station (very basic proximity query)
    nearest = None
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT id,name,latitude,longitude FROM charging_stations")
            stations = cur.fetchall()
            for s in stations:
                d = haversine(float(start.get("lat")), float(start.get("lon")),
                              s["latitude"], s["longitude"])
                if nearest is None or d < nearest["distance_km"]:
                    nearest = {"id": s["id"], "name": s["name"],
                               "lat": s["latitude"], "lon": s["longitude"],
                               "distance_km": round(d, 2)}
    finally:
        if conn: conn.close()

    result = {
        "distance_to_destination_km": round(distance, 2),
        "nearest_station": nearest,
        "battery_percentage": round(battery, 1),
        "estimated_range_km": round(est_range, 1),
        "battery_health_%": round(battery_health, 1),
        "distance_since_last_charge_km": round(last_charge_km, 1),
        "battery_used_since_last_charge_%": round((last_charge_km / efficiency), 1),
        "estimated_arrival_time_min": round(distance, 1)  # naive placeholder
    }

    # Log trip
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO trip_logs(user_battery_percent, start_lat, start_lon, dest_lat, dest_lon, est_distance_km)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (battery, float(start.get("lat")), float(start.get("lon")),
                  float(dest.get("lat")), float(dest.get("lon")), distance))
    finally:
        if conn: conn.close()

    return jsonify(result), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
