#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install geopy')
get_ipython().system('pip install osmnx')
get_ipython().system('pip install haversine')


# In[2]:


import pandas as pd

# ระบุ encoding เป็น windows-1252 หรือ iso-8859-1
df = pd.read_csv("GasStations_LatLong_PNAT.csv", encoding='windows-1252')


print(df.head())



# ## Driving Distance

# In[ ]:


import pandas as pd
import osmnx as ox
import networkx as nx
from geopy.distance import geodesic

# Load CSV
df = pd.read_csv("GasStations_LatLong_PNAT.csv", encoding='windows-1252')

susco_df = df[df['Company'] == 'SUSCO'].reset_index(drop=True)
bcp_bsrc_df = df[df['Company'].isin(['BCP', 'BSRC'])].reset_index(drop=True)

# ฟังก์ชันตรวจสอบ latitude/longitude valid
def is_valid_coord(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    except:
        return False

# ฟังก์ชันคำนวณระยะทางบนถนน
def calculate_driving_distance(lat1, lon1, lat2, lon2, G):
    try:
        start_node = ox.distance.nearest_nodes(G, lon1, lat1)
        end_node = ox.distance.nearest_nodes(G, lon2, lat2)
        if start_node is None or end_node is None:
            return None
        return nx.shortest_path_length(G, start_node, end_node, weight='length') / 1000
    except:
        return None

# ฟังก์ชันคำนวณระยะทางสำหรับ SUSCO หนึ่งปั๊ม
def calculate_distances_for_susco(s_row, bcp_bsrc_df, radius_km=15):
    results = []
    susco_lat, susco_lon = s_row['Lat'], s_row['Long']
    susco_sor = s_row['SOR']

    if not is_valid_coord(susco_lat, susco_lon):
        print(f"Skipping SUSCO {susco_sor}: invalid coordinates ({susco_lat}, {susco_lon})")
        return results

    # Candidate BCP/BSRC filter
    candidate_df = bcp_bsrc_df[
        bcp_bsrc_df.apply(
            lambda r: is_valid_coord(r['Lat'], r['Long']) and geodesic((susco_lat, susco_lon), (r['Lat'], r['Long'])).km <= radius_km,
            axis=1
        )
    ]

    if candidate_df.empty:
        return results

    # โหลด OSM graph รอบ SUSCO
    try:
        G = ox.graph_from_point((susco_lat, susco_lon), dist=25000, network_type="drive")
    except Exception as e:
        print(f"Skipping SUSCO {susco_sor}: cannot load graph ({e})")
        return results

    for _, b_row in candidate_df.iterrows():
        road_dist = calculate_driving_distance(susco_lat, susco_lon, b_row['Lat'], b_row['Long'], G)
        if road_dist is not None and road_dist <= radius_km:
            results.append({
                "From": susco_sor,
                "To": b_row['SOR'],
                "Road_km": road_dist
            })

    return results

# MAIN LOOP
all_results = []
for _, s_row in susco_df.iterrows():
    all_results.extend(calculate_distances_for_susco(s_row, bcp_bsrc_df, radius_km=15))

# Save results
if all_results:
    df_result = pd.DataFrame(all_results)
    df_result.to_csv("BGN_bcp_distances.csv", index=False, encoding="utf-8-sig")
    print("✅ Saved CSV")
    print(df_result.head())
else:
    print("No valid distances calculated.")

