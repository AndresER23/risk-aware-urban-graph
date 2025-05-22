# 🛣️ risk-aware-urban-graph

Enhances an urban street network graph with safety context by assigning each edge a predicted risk level (based on UPZ zones) and distance to the nearest CAI (police post). Combines spatial analysis with time series forecasting (ARIMA) to enable dynamic, risk-aware routing and urban security planning.

---

## 📌 Features

- Annotates each street segment (edge) with:
  - 🔸 **Predicted risk level** using ARIMA models on historical data per UPZ.
  - 🔹 **Distance to the nearest CAI** (local police facility).
- Integrates spatial and temporal analysis using GeoPandas, NetworkX, and statsmodels.
- Supports secure routing, dynamic risk mapping, and mobility planning.

---

## 📈 Predictive Risk Modeling (ARIMA)

- Time series models (ARIMA) are fitted using historical incident data for each UPZ.
- Forecasts are generated for short-term risk levels and assigned to the graph.
- Enables time-aware analysis of urban safety (e.g., planning for future scenarios or peak hours of crime).

---

## 🗂️ Project Structure

├── data/
│ ├── incidents_by_upz.csv # Historical incidents per UPZ
│ ├── gdf_upz.geojson # UPZ boundaries
│ ├── gdf_cais.geojson # CAI locations
├── src/
│ ├── assign_risk.py # Graph annotation
│ ├── forecast_risk.py # ARIMA modeling for UPZ risk
├── notebooks/
│ └── arima_modeling.ipynb # Risk forecasting example
├── README.md
