import osmnx as ox
import networkx as nx
import numpy as np
from shapely.geometry import LineString
from matplotlib import colors
import pandas as pd 
# def calcular_rutas_coords(G, start_point, end_point, alpha=0.7, beta=0.3):
#     # Agregar geometría si no existe
#     for u, v, k, data in G.edges(keys=True, data=True):
#         if 'geometry' not in data:
#             point_u = (G.nodes[u]['x'], G.nodes[u]['y'])
#             point_v = (G.nodes[v]['x'], G.nodes[v]['y'])
#             data['geometry'] = LineString([point_u, point_v])

#     # Calcular pesos de riesgo
#     for u, v, k, data in G.edges(keys=True, data=True):
#         length = data.get('length', 1)
#         risk = data.get('incident_count_normalized', 0.5)
#         custom_weight = alpha * length + beta * (risk * 1000) + gamma * distance_to_cai
#         data['custom_weight'] = alpha * length + beta * (risk * 1000)

#     orig_node = ox.distance.nearest_nodes(G, X=start_point[0], Y=start_point[1])
#     dest_node = ox.distance.nearest_nodes(G, X=end_point[0], Y=end_point[1])

#     # Calcular rutas
#     route_shortest = nx.shortest_path(G, orig_node, dest_node, weight='length')
#     route_safest = nx.shortest_path(G, orig_node, dest_node, weight='custom_weight')

#     for path_name, path in [('ruta_corta', route_shortest), ('ruta_segura', route_safest)]:
#         upz_riesgos = set()
#         for u, v in zip(path[:-1], path[1:]):
#             data = G.get_edge_data(u, v, 0)
#             print(data)
#             riesgo = data.get('RIESGO', 0)
#             upz_riesgos.add(riesgo)
#         print(f"{path_name} tiene {len(upz_riesgos)} riesgos únicos: {upz_riesgos}")


#     # Función para extraer coordenadas y riesgos
#     def route_to_coords(route):
#         segments, risks = [], []
#         for u, v in zip(route[:-1], route[1:]):
#             edge_data = G.get_edge_data(u, v)
#             best = min(edge_data.values(), key=lambda d: d.get('length', 1))
#             geom = best.get('geometry', LineString([
#                 (G.nodes[u]['x'], G.nodes[u]['y']),
#                 (G.nodes[v]['x'], G.nodes[v]['y']),
#             ]))
#             segments.append([(lat, lon) for lon, lat in geom.coords])
#             risks.append(best.get('incident_count_normalized', 0.5))
#         return segments, risks

#     coords_safest, route_risks = route_to_coords(route_safest)
#     coords_shortest, _ = route_to_coords(route_shortest)

#     return coords_shortest, coords_safest, route_risks

def calcular_rutas_coords(G, start_point, end_point, alpha=0.7, beta=0.2, gamma=0.1):
    from shapely.geometry import LineString
    import networkx as nx
    import osmnx as ox

    # Agregar geometría si no existe
    for u, v, k, data in G.edges(keys=True, data=True):
        if 'geometry' not in data:
            point_u = (G.nodes[u]['x'], G.nodes[u]['y'])
            point_v = (G.nodes[v]['x'], G.nodes[v]['y'])
            data['geometry'] = LineString([point_u, point_v])

    # Calcular pesos personalizados
    for u, v, k, data in G.edges(keys=True, data=True):
        length = data.get('length', 1)
        risk = data.get('riesgo', 0.5)
        distance_to_cai = data.get('distancia_cai', 0)

        # Fórmula de peso personalizada
        custom_weight = alpha * length + beta * (risk * 1000) + gamma * distance_to_cai
        data['custom_weight'] = custom_weight

    # Encontrar nodos más cercanos
    orig_node = ox.distance.nearest_nodes(G, X=start_point[0], Y=start_point[1])
    dest_node = ox.distance.nearest_nodes(G, X=end_point[0], Y=end_point[1])

    # Calcular rutas
    route_shortest = nx.shortest_path(G, orig_node, dest_node, weight='length')
    route_safest = nx.shortest_path(G, orig_node, dest_node, weight='custom_weight')

    print(f"Ruta más corta: {sum(G[u][v][0]['length'] for u, v in zip(route_shortest[:-1], route_shortest[1:])):.4f}")
    print(f"Ruta más segura: {sum(G[u][v][0]['custom_weight'] for u, v in zip(route_safest[:-1], route_safest[1:])):.4f}")

    # Extraer coordenadas y riesgos
    def route_to_coords(route):
        segments, risks = [], []
        for u, v in zip(route[:-1], route[1:]):
            edge_data = G.get_edge_data(u, v)
            best = min(edge_data.values(), key=lambda d: d.get('length', 1))
            geom = best.get('geometry', LineString([
                (G.nodes[u]['x'], G.nodes[u]['y']),
                (G.nodes[v]['x'], G.nodes[v]['y']),
            ]))
            segments.append([(lat, lon) for lon, lat in geom.coords])
            risks.append(best.get('riesgo', 0.5))
        return segments, risks
    def calcular_riesgo_total(route):
        total_risk = 0.0
        for u, v in zip(route[:-1], route[1:]):
            data = G.get_edge_data(u, v, 0)
            total_risk += data.get('riesgo', 0.0)
        return total_risk
    
    riesgo_total_shortest = calcular_riesgo_total(route_shortest)
    riesgo_total_safest = calcular_riesgo_total(route_safest)

    coords_safest, route_risks = route_to_coords(route_safest)
    coords_shortest, _ = route_to_coords(route_shortest)

    return coords_shortest, coords_safest, [riesgo_total_shortest, riesgo_total_safest]

