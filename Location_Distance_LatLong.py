#!/usr/bin/env python
# coding: utf-8

# ============================================
# INSTALL REQUIRED LIBRARIES
# ============================================

get_ipython().system('pip install geopy')
get_ipython().system('pip install osmnx')
get_ipython().system('pip install haversine')


# ============================================
# LOAD INPUT DATA
# ============================================

import pandas as pd

# Specify encoding (if CSV contains non-UTF8 characters)
df = pd.read_csv("Locations_LatLong.csv", encoding='windows-1252')

print(df.head())


# ============================================
# DRIVING DISTANCE CALCULATION
# ============================================

import osmnx as ox
import networkx as nx
from geopy.distance import geodesic

# Load CSV file
df = pd.read_csv("Locations_LatLong.csv", encoding='windows-1252')

# Split into base and target groups
base_df = df[df['Company'] == 'Brand A'].reset_index(drop=True)
target_df = df[df['Company'].isin(['Brand B', 'Brand C'])].reset_index(drop=True)


# ----------------------------
# Function to check valid coordinates
# ----------------------------
def is_valid_coord(lat, lon):
    try:
        lat = float(lat)
        lon = float(lon)
        return (-90 <= lat <= 90) and (-180 <= lon <= 180)
    except:
        return False


# ----------------------------
# Function to calculate driving distance using OSM road network
# ----------------------------
def calculate_driving_distance(lat1, lon1, lat2, lon2, G):
    try:
        start_node = ox.distance.nearest_nodes(G, lon1, lat1)
        end_node = ox.distance.nearest_nodes(G, lon2, lat2)
        if start_node is None or end_node is None:
            return None
        # Convert meters to kilometers
        return nx.shortest_path_length(G, start_node, end_node, weight='length') / 1000
    except:
        return None


# ----------------------------
# Calculate distances for one base station (Brand A)
# ----------------------------
def calculate_distances_for_base(base_row, target_df, radius_km=15):
    results = []
    base_lat, base_lon = base_row['Lat'], base_row['Long']
    base_sor = base_row['SOR']

    if not is_valid_coord(base_lat, base_lon):
        print(f"Skipping Base {base_sor}: invalid coordinates ({base_lat}, {base_lon})")
        return results

    # Filter candidate targets within given radius (geodesic distance)
    candidate_df = target_df[
        target_df.apply(
            lambda r: is_valid_coord(r['Lat'], r['Long']) and 
                      geodesic((base_lat, base_lon), (r['Lat'], r['Long'])).km <= radius_km,
            axis=1
        )
    ]

    if candidate_df.empty:
        return results

    # Load OSM road network around the base point
    try:
        G = ox.graph_from_point((base_lat, base_lon), dist=25000, network_type="drive")
    except Exception as e:
        print(f"Skipping Base {base_sor}: cannot load graph ({e})")
        return results

    # Calculate road distance for each nearby target
    for _, t_row in candidate_df.iterrows():
        road_dist = calculate_driving_distance(base_lat, base_lon, t_row['Lat'], t_row['Long'], G)
        if road_dist is not None and road_dist <= radius_km:
            results.append({
                "From": base_sor,       # Base (Brand A)
                "To": t_row['SOR'],     # Target (Brand B/C)
                "Road_km": road_dist
            })

    return results


# ============================================
# MAIN LOOP
# ============================================

all_results = []
for _, base_row in base_df.iterrows():
    all_results.extend(calculate_distances_for_base(base_row, target_df, radius_km=15))

# Save results
if all_results:
    df_result = pd.DataFrame(all_results)
    df_result.to_csv("Road_Distance_Results.csv", index=False, encoding="utf-8-sig")
    print("CSV file saved successfully!")
    print(df_result.head())
else:
    print("No valid distances calculated.")
