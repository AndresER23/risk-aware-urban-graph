import dash
from dash import html, dcc, Input, Output, State, ctx
import dash_leaflet as dl
import dash_bootstrap_components as dbc
import osmnx as ox
from routing_utils import calcular_rutas_coords
from grafo_utils import asignar_riesgo_a_grafo
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

place = "Bogotá, Colombia"
G = ox.graph_from_place(place, network_type="drive")
upz_gdf = gpd.read_file("upz_bogota.geojson")
df_pred = pd.read_csv("df_predicciones_riesgo.csv")
df_cai = gpd.read_file("cuadrantepolicia.geojson")

# Normalizar riesgo
df_pred['RIESGO'] = (df_pred['PREDICCION'] - df_pred['PREDICCION'].min()) / (
    df_pred['PREDICCION'].max() - df_pred['PREDICCION'].min())

# Asignar riesgos al grafo
asignar_riesgo_a_grafo(G, upz_gdf, df_pred, df_cai)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout de la app
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2("Ruta más segura vs más corta", className="text-center mb-4 text-primary"),
            dbc.Form([
                dbc.Label("Coordenadas de inicio (lat, lon):", className="fw-bold"),
                dbc.Input(id="start-coords", placeholder="4.604468689535771, -74.07062174311426", type="text", className="mb-3"),
                dbc.Label("Coordenadas de destino (lat, lon):", className="fw-bold"),
                dbc.Input(id="end-coords", placeholder="4.609002005163948, -74.07823610364643", type="text", className="mb-3"),
                dbc.Button("Calcular rutas", id="calculate-button", color="primary", className="mt-2 w-100 shadow-sm"),
            ])
        ], md=4),
        dbc.Col([
            dl.Map(center=[4.60971, -74.08175], zoom=13, children=[
                dl.TileLayer(),
                dl.LayerGroup(id="route-layer"),
                html.Div(
                    children=[
                        html.Div([html.Span("■ ", style={"color": "blue"}), "Ruta más corta"], style={"margin-bottom": "8px"}),
                        html.Div([html.Span("■ ", style={"color": "red"}), "Ruta más segura"])
                    ],
                    style={
                        "position": "absolute", "bottom": "20px", "left": "20px",
                        "background": "white", "padding": "12px 18px", "border-radius": "8px",
                        "box-shadow": "2px 2px 12px rgba(0,0,0,0.15)", "zIndex": "1000",
                        "font-weight": "600", "font-size": "15px", "font-family": "Arial, sans-serif"
                    }
                )
            ], style={'width': '100%', 'height': '80vh', 'borderRadius': '10px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'}, id="map")
        ], md=8)
    ]),
    html.Div(id="risk-info", className="mt-3"),
    html.Footer(
        "© 2025 Andrés Escobar",
        className="text-center text-muted mt-4 mb-2",
        style={"fontSize": "13px"}
    )
], fluid=True, style={"backgroundColor": "#f8f9fa", "padding": "20px 40px"})


@app.callback(
    Output("route-layer", "children"),
    Output("risk-info", "children"),
    Input("calculate-button", "n_clicks"),
    State("start-coords", "value"),
    State("end-coords", "value"),
    prevent_initial_call=True
)
def update_map(n_clicks, start_val, end_val):
    try:
        start_lat, start_lon = map(float, start_val.split(","))
        end_lat, end_lon = map(float, end_val.split(","))

        coords_shortest, coords_safest, route_risks = calcular_rutas_coords(
            G,
            (start_lon, start_lat),
            (end_lon, end_lat)
        )

        # Crear polyline y marcadores de la ruta más corta
        polyline_shortest = dl.Polyline(
            positions=coords_shortest, color="blue", weight=5,
            children=[dl.Tooltip("Ruta más corta")]
        )

        markers = [
            dl.Marker(position=(start_lat, start_lon), children=dl.Tooltip("Inicio")),
            dl.Marker(position=(end_lat, end_lon), children=dl.Tooltip("Destino"))
        ]

        # Evaluar si se muestra la ruta más segura
        elements = [polyline_shortest] + markers
        if route_risks[1] < route_risks[0]:
            polyline_safest = dl.Polyline(
                positions=coords_safest, color="red", weight=6,
                children=[dl.Tooltip("Ruta más segura")]
            )
            elements.append(polyline_safest)

            risk_comparison = html.Div([
                html.H5("Comparación de riesgo total:", className="mt-3"),
                html.Ul([
                    html.Li(f"Ruta más corta: {route_risks[0]:.4f}", style={"color": "blue"}),
                    html.Li(f"Ruta más segura: {route_risks[1]:.4f}", style={"color": "red"})
                ])
            ])
        else:
            risk_comparison = html.Div([
                html.H5("Comparación de riesgo total:", className="mt-3"),
                html.Ul([
                    html.Li(f"Ruta más corta: {route_risks[0]:.4f}", style={"color": "blue"}),
                    html.Li(f"Ruta más segura: {route_risks[1]:.4f}", style={"color": "red"})
                ]),
                html.P("Nota: La ruta más segura no fue mostrada ya que tiene un riesgo mayor o igual al de la ruta más corta.", className="text-muted fst-italic")
            ])

        return elements, risk_comparison

    except Exception as e:
        return [dl.Popup(position=[4.60971, -74.08175], children=str(e))], html.Div()


if __name__ == "__main__":
    app.run(debug=True)
