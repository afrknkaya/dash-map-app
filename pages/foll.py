# pages/foll.py
from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import folium
import numpy as np
import requests
import json
import branca.colormap as cm
from components.data_loader import (
    load_and_prepare_country_data,
    SUTUN_ULKE, SUTUN_TEKNOLOJI, SUTUN_YIL, SUTUN_DEGER, SUTUN_ISO_CODE
)

GEOJSON_URL = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
geojson_data_global = None
try:
    response = requests.get(GEOJSON_URL)
    response.raise_for_status()
    geojson_data_global = response.json()
except requests.exceptions.RequestException as e:
    print(f"GeoJSON load error: {e}")
except json.JSONDecodeError as e:
    print(f"GeoJSON parse error: {e}")

DARK_THEME_COLORS_FOLL = {
    "map_tile": "CartoDB dark_matter",
    "tooltip_bg": "#18131f",
    "tooltip_text": "#e8e8f0",
    "tooltip_border": "#6a2f66",
    "country_stroke_color": "#707080",
    "nan_fill": "#2a2a2e",
    "choropleth_palette_name": "inferno",
    "text_main": "#ffffff"
}
LIGHT_THEME_COLORS_FOLL = {
    "map_tile": "CartoDB positron",
    "tooltip_bg": "#f8f9fa",
    "tooltip_text": "#001f36",
    "tooltip_border": "#ced4da",
    "country_stroke_color": "#ababab",
    "nan_fill": "#d3d3d3",
    "choropleth_palette_name": "PuBuGn",
    "text_main": "#000000"
}

df_folium_page_data, filters_folium_page_data, metrics_folium_page_info = load_and_prepare_country_data()
if not df_folium_page_data.empty:
    PAGE_METRIC_INFO_FOLL = metrics_folium_page_info.get('ana_metrik', {})
    PAGE_METRIC_NAME_FOLL = PAGE_METRIC_INFO_FOLL.get('isim', 'Kurulu Kapasite')
    PAGE_METRIC_UNIT_FOLL = PAGE_METRIC_INFO_FOLL.get('birim', 'MW')
    all_technologies_foll_page = filters_folium_page_data.get('technologies', [])
    years_list_foll_page = [int(y) for y in filters_folium_page_data.get('years', [])]
    min_year_foll_page = min(years_list_foll_page)
    max_year_foll_page = max(years_list_foll_page)
    initial_year_foll_page = max_year_foll_page
else:
    PAGE_METRIC_NAME_FOLL, PAGE_METRIC_UNIT_FOLL = "Veri Yok", ""
    all_technologies_foll_page, years_list_foll_page = [], []
    min_year_foll_page, max_year_foll_page, initial_year_foll_page = 2000, 2023, 2023

layout = dbc.Container(fluid=True, className="dbc dbc-row-selectable py-3", children=[
    html.H2(f"Global Enerji Atlası (Folium) - {PAGE_METRIC_NAME_FOLL}", className="text-center mb-4"),
    dbc.Card([
        dbc.CardHeader(html.H5([html.I(className="bi bi-map-fill me-2"), "Harita Filtreleri"], className="mb-0")),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Yıl Seçin:", className="form-label fw-bold"),
                    dcc.Slider(
                        id='foll-map-year-slider',
                        min=min_year_foll_page, max=max_year_foll_page, step=1,
                        marks={y: str(y) for y in years_list_foll_page if y % 5 == 0 or y in (min_year_foll_page, max_year_foll_page)},
                        value=initial_year_foll_page,
                        tooltip={"placement": "bottom", "always_visible": True},
                        className="mb-3"
                    )
                ], width=12, md=6),
                dbc.Col([
                    html.Label("Teknoloji Seçin (Opsiyonel):", className="form-label fw-bold"),
                    dcc.Dropdown(
                        id='foll-map-technology-dropdown',
                        options=[{'label': 'Tüm Teknolojiler', 'value': 'all'}] + [{'label': tech, 'value': tech} for tech in all_technologies_foll_page],
                        value='all', multi=False, clearable=True,
                        placeholder="Bir teknoloji seçin veya tümü...", className="mb-3"
                    )
                ], width=12, md=6),
            ])
        ])
    ], className="mb-4"),
    dbc.Row([
        dbc.Col(
            dcc.Loading(
                html.Iframe(
                    id='folium-map-iframe',
                    style={'width': '100%', 'height': '70vh', 'border': '1px solid var(--active-border-color)'}
                )
            ), width=12
        )
    ])
])

def generate_folium_map_html(year_param, technology_param, theme_param, geojson_data_param):
    active_theme_colors = DARK_THEME_COLORS_FOLL if theme_param == 'dark' else LIGHT_THEME_COLORS_FOLL

    filtered_df = df_folium_page_data[df_folium_page_data[SUTUN_YIL] == year_param]
    if technology_param != 'all':
        filtered_df = filtered_df[filtered_df[SUTUN_TEKNOLOJI] == technology_param]
    summary = filtered_df.groupby([SUTUN_ISO_CODE, SUTUN_ULKE], as_index=False)[SUTUN_DEGER].sum()
    summary = summary[summary[SUTUN_DEGER] > 0].copy()

    # ✅ Adaptif logaritmik dönüşüm (küçük değerler için duyarlı)
    values = summary[SUTUN_DEGER]
    min_val = values.min()
    max_val = values.max()

    # Küçük farkları hissedilir kılmak için logaritmik + lineer karışımı (softlog)
    def soft_log_transform(x):
        return np.log1p(x) / np.log1p(max_val)

    summary["log_deger"] = values.apply(soft_log_transform)

    m = folium.Map(location=[30, 10], zoom_start=2, tiles=active_theme_colors["map_tile"])
    summary_dict = summary.set_index(SUTUN_ISO_CODE)[SUTUN_DEGER].to_dict()
    summary_log_dict = summary.set_index(SUTUN_ISO_CODE)["log_deger"].to_dict()

    for feature in geojson_data_param['features']:
        iso = feature['id']
        feature['properties'][SUTUN_ULKE] = feature['properties'].get('name')
        feature['properties'][SUTUN_DEGER] = summary_dict.get(iso, 0)
        feature['properties']['log_deger'] = summary_log_dict.get(iso, 0)

    folium.Choropleth(
        geo_data=geojson_data_param,
        name='choropleth',
        data=summary,
        columns=[SUTUN_ISO_CODE, "log_deger"],
        key_on='feature.id',
        fill_color=active_theme_colors["choropleth_palette_name"],
        fill_opacity=0.7,
        line_opacity=0.3,
        line_color=active_theme_colors['country_stroke_color'],
        nan_fill_color=active_theme_colors['nan_fill'],
        highlight=True,
        legend_name=f'{PAGE_METRIC_NAME_FOLL} (Oranlanmış)'
    ).add_to(m)

    folium.GeoJson(
        geojson_data_param,
        name="Tooltip",
        style_function=lambda x: {
            'fillOpacity': 0,
            'color': active_theme_colors['country_stroke_color'],
            'weight': 0.5
        },
        tooltip=folium.GeoJsonTooltip(
            fields=[SUTUN_ULKE, SUTUN_DEGER],
            aliases=["Ülke:", f"{PAGE_METRIC_NAME_FOLL} ({PAGE_METRIC_UNIT_FOLL}):"],
            localize=True,
            labels=True,
            sticky=False,
            style=(
                f"background-color:{active_theme_colors['tooltip_bg']};"
                f"color:{active_theme_colors['tooltip_text']};"
                f"border:1px solid {active_theme_colors['tooltip_border']};"
                f"border-radius:6px; padding:8px; font-size:0.9em;"
            )
        )
    ).add_to(m)

    folium.LayerControl().add_to(m)
    return m._repr_html_()


@callback(
    Output('folium-map-iframe', 'srcDoc'),
    [Input('foll-map-year-slider', 'value'),
     Input('foll-map-technology-dropdown', 'value'),
     Input('theme-preference-store', 'data')]
)
def update_folium_map(selected_year, selected_technology, current_theme_preference):
    if selected_year is None:
        return "<div>Lütfen bir yıl seçin.</div>"
    theme = current_theme_preference if current_theme_preference else 'dark'
    return generate_folium_map_html(selected_year, selected_technology, theme, geojson_data_global)
