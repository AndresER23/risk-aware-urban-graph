import geopandas as gpd
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from shapely.geometry import Point
from shapely.geometry import LineString
from scipy.spatial import cKDTree

def asignar_riesgo_a_grafo(G, gdf_upz, df_riesgo, gdf_cais):
    """
    Asigna el riesgo por UPZ y la distancia al CAI más cercano a cada arista del grafo G.
    
    Parámetros:
    - G: MultiDiGraph de NetworkX.
    - gdf_upz: GeoDataFrame de UPZs con geometría.
    - df_riesgo: DataFrame con columnas ['CODIGO_UPZ', 'RIESGO'].
    - gdf_cais: GeoDataFrame con geometría de CAIs.
    
    A cada arista se le asigna:
        - data['riesgo']: riesgo asociado por UPZ.
        - data['distancia_cai']: distancia al CAI más cercano.
    """

    print("Iniciando asignación de riesgo y distancia a CAIs...")

    # Asegurar CRS consistente
    gdf_upz = gdf_upz.to_crs(G.graph['crs'])
    gdf_cais = gdf_cais.to_crs(G.graph['crs'])

    # Asegurar que las geometrías de los CAIs sean puntos
    if not all(gdf_cais.geometry.geom_type == 'Point'):
        print("Convirtiendo geometrías de CAIs a centroides...")
        gdf_cais['geometry'] = gdf_cais.geometry.centroid

    # Unir riesgo al GeoDataFrame de UPZ
    gdf_upz = gdf_upz.merge(df_riesgo[['CODIGO_UPZ', 'RIESGO']], on='CODIGO_UPZ', how='left')

    # Crear índice espacial para UPZs
    spatial_index = gdf_upz.sindex

    # Crear KDTree con coordenadas de los CAIs
    cai_coords = np.array([(geom.x, geom.y) for geom in gdf_cais.geometry])
    cai_tree = cKDTree(cai_coords)

    # Iterar sobre aristas del grafo
    for u, v, k, data in G.edges(keys=True, data=True):
        x1, y1 = G.nodes[u]['x'], G.nodes[u]['y']
        x2, y2 = G.nodes[v]['x'], G.nodes[v]['y']
        line = LineString([(x1, y1), (x2, y2)])
        midpoint = line.interpolate(0.5, normalized=True)

        # RIESGO por UPZ
        possible_matches_index = list(spatial_index.intersection(midpoint.bounds))
        possible_matches = gdf_upz.iloc[possible_matches_index]

        riesgo_asignado = 0.0  # por defecto
        for _, row in possible_matches.iterrows():
            if row['geometry'].contains(midpoint):
                riesgo_asignado = row['RIESGO'] if pd.notnull(row['RIESGO']) else 0.0
                break
        data['riesgo'] = riesgo_asignado

        # DISTANCIA al CAI más cercano
        dist, _ = cai_tree.query([midpoint.x, midpoint.y])
        data['distancia_cai'] = dist

    print("Asignación completa.")