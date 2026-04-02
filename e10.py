import requests
from datetime import datetime

API_KEY = "eff258d2-d6a8-4db9-94b3-95e514b48511"  # <-- hier deinen Tankerkoenig API-Key eintragen

LAT = 49.352   # Wendelstein
LNG = 11.150
RADIUS_KM = 10
FUEL_TYPE = "e10"

def fetch_prices():
    url = "https://creativecommons.tankerkoenig.de/json/list.php"
    params = {
        "lat": LAT,
        "lng": LNG,
        "rad": RADIUS_KM,
        "sort": "price",
        "type": FUEL_TYPE,
        "apikey": API_KEY,
    }

    r = requests.get(url, params=params, timeout=10)
    data = r.json()

    if not data.get("ok"):
        print("API-Fehler:", data.get("message"))
        return []

    return data.get("stations", [])

def main():
    stations = fetch_prices()
    if not stations:
        print("Keine Daten erhalten.")
        return

    print("\n=== E10-Preise rund um 90530 (±10 km) ===")
    print("Stand:", datetime.now().strftime("%d.%m.%Y %H:%M:%S"))

    for s in stations:
        if s.get("price") is None:
            continue
        print(f"{s['price']:4.2f} € | {s['brand']} {s['name']} | {s['street']} {s['place']} | {s['dist']:.1f} km")

#if __name__ == "__main__":
    main()
