## 🧭 Objective
This project calculates **driving distances** between locations using **OpenStreetMap road network data** via the `osmnx` and `networkx` libraries.

The program identifies pairs of nearby locations within a defined radius (default 15 km) and computes the estimated driving distance along actual roads, not just straight-line distance.
The results are exported as a CSV file showing the distance in kilometers between each pair.


---

## ⚙️ How It Works
1. Reads location data (latitude and longitude) from a CSV file.  
2. Filters valid coordinates and candidate pairs within a 15 km radius.  
3. Uses OpenStreetMap road data (via OSMnx) to calculate **real road distances** instead of straight-line (geodesic) distances.  
4. Saves results in a new CSV file (`BGN_bcp_distances.csv`) containing:
   - From (Origin_SOR) — the base or primary station
   - To (Target_SOR) — the nearby station within the search radius
   - Road_km — driving distance in kilometers

---

## 📥 Expected CSV Input Format (not included in repo)
The code expects an input file named `GasStations_LatLong.csv` with the following columns:

| Column | Description |
|:--------|:-------------|
| **Company** | Company name |
| **SOR** | Station identifier or code |
| **Lat** | Latitude (decimal degrees) |
| **Long** | Longitude (decimal degrees) |

*Note:* The actual dataset is not included
---

## 🧩 Requirements
Install the following Python packages before running:
```bash
pip install pandas osmnx networkx geopy
