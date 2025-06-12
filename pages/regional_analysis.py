# pages/regional_analysis.py
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.io as pio

# Treemap için yumuşak renk paletleri
TREEMAP_COLORS_DARK = px.colors.qualitative.Set3
TREEMAP_COLORS_LIGHT = px.colors.qualitative.Pastel

from components.data_loader import (
    load_and_prepare_country_data, 
    SUTUN_ULKE, SUTUN_TEKNOLOJI, SUTUN_YIL, SUTUN_DEGER, SUTUN_ISO_CODE
)

df_regional_data, filters_regional, metrics_regional = load_and_prepare_country_data()

SUTUN_BOLGE_REG_PAGE = 'Region'
SUTUN_GROUP_TECH_REG_PAGE = 'Group Technology'
SUTUN_RE_NON_RE_REG_PAGE = 'RE or Non-RE'

if not df_regional_data.empty:
    PAGE_METRIC_INFO_REG = metrics_regional.get('ana_metrik', {})
    PAGE_METRIC_NAME_REG = PAGE_METRIC_INFO_REG.get('isim', 'Kurulu Kapasite')
    PAGE_METRIC_UNIT_REG = PAGE_METRIC_INFO_REG.get('birim', 'MW')
    
    all_regions = sorted(df_regional_data[SUTUN_BOLGE_REG_PAGE].unique().tolist()) if SUTUN_BOLGE_REG_PAGE in df_regional_data.columns else []
    all_group_techs = sorted(df_regional_data[SUTUN_GROUP_TECH_REG_PAGE].unique().tolist()) if SUTUN_GROUP_TECH_REG_PAGE in df_regional_data.columns else []
    all_re_non_re = sorted(df_regional_data[SUTUN_RE_NON_RE_REG_PAGE].unique().tolist()) if SUTUN_RE_NON_RE_REG_PAGE in df_regional_data.columns else []
    years_list_regional = [int(y) for y in filters_regional.get('years', [])]
    min_year_regional = min(years_list_regional) if years_list_regional else 2000
    max_year_regional = max(years_list_regional) if years_list_regional else 2023
    initial_start_year_regional = max(2010, min_year_regional)
    initial_end_year_regional = max_year_regional
else:
    PAGE_METRIC_NAME_REG, PAGE_METRIC_UNIT_REG = "Veri Yok", ""
    all_regions, all_group_techs, all_re_non_re, years_list_regional = [], [], [], []
    min_year_regional, max_year_regional, initial_start_year_regional, initial_end_year_regional = 2000, 2023, 2010, 2023

if df_regional_data.empty:
    layout = dbc.Container([
        dbc.Alert([
            html.H4("Veri Yükleme Hatası!", className="alert-heading"),
            html.P("Bölgesel analiz sayfası için veriler yüklenemedi.")
        ], color="danger", className="mt-3 text-center")])
else:
    layout = dbc.Container(fluid=True, className="dbc dbc-row-selectable py-3", children=[
        html.H2("Bölgesel Enerji Kapasitesi Analizi", className="text-center mb-4"),
        dbc.Card([
            dbc.CardHeader(
                dbc.Stack([
                    html.H5(children=[html.I(className="bi bi-bar-chart-line-fill me-2"), "Analiz Filtreleri"], className="mb-0"),
                    dbc.Button(children=[html.I(className="bi bi-chevron-up")], id="regional-filter-collapse-toggle-button", color="link", className="ms-auto p-0 border-0", size="sm", n_clicks=0)
                ], direction="horizontal")
            ),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Analiz Edilecek Bölgeler:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id='reg-region-dropdown', options=[{'label': region, 'value': region} for region in all_regions],
                                value=['Asia', 'Europe', 'North America', 'Africa'] if all(r in all_regions for r in ['Asia', 'Europe', 'North America', 'Africa']) else all_regions[:4],
                                multi=True, className="mb-3")
                        ], width=12, md=3),
                        dbc.Col([
                            html.Label("Teknoloji Grubu:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id='reg-group-tech-dropdown', options=[{'label': tech, 'value': tech} for tech in all_group_techs],
                                multi=True, placeholder="Tüm teknoloji grupları...", className="mb-3")
                        ], width=12, md=3),
                        dbc.Col([
                            html.Label("Enerji Tipi:", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id='reg-re-non-re-dropdown', options=[{'label': item, 'value': item} for item in all_re_non_re],
                                placeholder="Tüm enerji tipleri...", multi=True, className="mb-3")
                        ], width=12, md=3),
                        dbc.Col([
                            html.Label("Yıl Aralığı:", className="form-label fw-bold"),
                            dcc.RangeSlider(
                                id='reg-year-slider', min=min_year_regional, max=max_year_regional, step=1,
                                marks={y: str(y) for y in years_list_regional if y % 5 == 0 or y in (min_year_regional, max_year_regional)},
                                value=[initial_start_year_regional, initial_end_year_regional],
                                tooltip={"placement": "bottom", "always_visible": False}, className="mb-3")
                        ], width=12, md=3),
                    ])
                ]),
                id="regional-filter-collapse-area", is_open=True,
            )
        ], className="mb-4"),
        
        # === LAYOUT SIRALAMASI DÜZELTİLDİ ===

        # 1. SATIR: TREEMAP (Artık Üstte)
        dbc.Row([
            dbc.Col(dcc.Loading(dbc.Card(
                [
                    dbc.CardHeader(html.H5("Kapasite Hiyerarşisi (Treemap)", className="mb-0")),
                    dbc.CardBody(dcc.Graph(id='reg-treemap-chart', style={'height': '60vh'}))
                ]
            )), width=12, className="mb-3")
        ]),

        # 2. SATIR: ZAMAN SERİSİ ve BAR GRAFİK (Artık Altta)
        dbc.Row([
            dbc.Col(dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='reg-time-series-chart')))), width=12, lg=7, className="mb-3"),
            dbc.Col(dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='reg-stacked-bar-chart')))), width=12, lg=5, className="mb-3"),
        ]),
        
    ])

    @callback(
        [Output("regional-filter-collapse-area", "is_open"),
         Output("regional-filter-collapse-toggle-button", "children")],
        [Input("regional-filter-collapse-toggle-button", "n_clicks")],
        [State("regional-filter-collapse-area", "is_open")],
        prevent_initial_call=True
    )
    def toggle_regional_filter_collapse(n_clicks, is_open):
        new_is_open_state = not is_open
        new_icon = html.I(className="bi bi-chevron-up") if new_is_open_state else html.I(className="bi bi-chevron-down")
        if n_clicks: return new_is_open_state, [new_icon]
        return no_update, no_update
        
    def create_regional_empty_figure(message="Grafik için veri yok veya yetersiz filtre."):
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="grey"))
        fig.update_layout(xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

    # pages/regional_analysis.py -> Sadece bu fonksiyon güncellenecek

    @callback(
        [Output('reg-time-series-chart', 'figure'),
         Output('reg-stacked-bar-chart', 'figure'),
         Output('reg-treemap-chart', 'figure')],
        [Input('reg-region-dropdown', 'value'),
         Input('reg-group-tech-dropdown', 'value'),
         Input('reg-re-non-re-dropdown', 'value'),
         Input('reg-year-slider', 'value'),
         Input('theme-preference-store', 'data')]
    )
    def update_regional_graphs(selected_regions, selected_group_techs, selected_re_non_re, selected_years, current_theme_preference):
        if not selected_regions or not selected_years:
            empty_fig = create_regional_empty_figure("Lütfen en az bir bölge ve yıl aralığı seçin.")
            return empty_fig, empty_fig, empty_fig

        start_year, end_year = selected_years[0], selected_years[1]
        
        filtered_df = df_regional_data[
            (df_regional_data[SUTUN_BOLGE_REG_PAGE].isin(selected_regions)) &
            (df_regional_data[SUTUN_YIL].between(start_year, end_year))
        ]
        
        if selected_group_techs:
            filtered_df = filtered_df[filtered_df[SUTUN_GROUP_TECH_REG_PAGE].isin(selected_group_techs)]
        if selected_re_non_re:
            filtered_df = filtered_df[filtered_df[SUTUN_RE_NON_RE_REG_PAGE].isin(selected_re_non_re)]
        
        if filtered_df.empty:
            empty_fig = create_regional_empty_figure("Seçilen filtrelere uygun veri bulunamadı.")
            return empty_fig, empty_fig, empty_fig

        # === Tema ve Hover Renk Ayarları ===
        active_theme = current_theme_preference if current_theme_preference else 'dark'
        plotly_template = "plotly_white" if active_theme == 'light' else "plotly_dark"
        font_color = "#212529" if active_theme == 'light' else "#e8e8f0"

        # Hoverlabel için özel renkler (Sizin belirttiğiniz gibi)
        hover_bg = "rgba(230, 230, 230, 0.95)" if active_theme == 'light' else "rgba(40, 38, 70, 0.95)"
        hover_border = "#7cc4fb" if active_theme == 'light' else "#a53c7d"
        hover_font_color = font_color # Ana font rengini kullanalım
        # === Ayarlar Sonu ===
        
        # --- 1. ZAMAN SERİSİ GRAFİĞİ ---
        df_time_series = filtered_df.groupby(['Year', 'Region'])[SUTUN_DEGER].sum().reset_index()
        fig_time_series = px.line(
            df_time_series, x='Year', y=SUTUN_DEGER, color='Region',
            title="Bölgelerin Yıllara Göre Toplam Kurulu Kapasite Trendi",
            labels={SUTUN_DEGER: f"{PAGE_METRIC_NAME_REG} ({PAGE_METRIC_UNIT_REG})", 'Year': "Yıl", 'Region': "Bölge"})
        fig_time_series.update_layout(
            template=plotly_template, 
            hovermode="x unified", 
            legend_title_text='Bölgeler',
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color=font_color,
            # === HOVERLABEL STİLİ EKLENDİ/GÜNCELLENDİ ===
            hoverlabel=dict(
                bgcolor=hover_bg,
                font_size=11, 
                font_color=hover_font_color,
                bordercolor=hover_border,
                align="left",
                namelength=-1 
            )
        )

        # --- 2. YIĞILMALI BAR GRAFİK ---
        df_last_year = filtered_df[filtered_df[SUTUN_YIL] == end_year]
        df_stacked_bar = df_last_year.groupby(['Region', 'Group Technology'])[SUTUN_DEGER].sum().reset_index()
        
        common_bar_pie_layout_updates = dict(
            template=plotly_template, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)', 
            font_color=font_color,
            hoverlabel=dict(bgcolor=hover_bg, font_size=12, font_color=hover_font_color, bordercolor=hover_border)
        )
        
        fig_stacked_bar = px.bar(
            df_stacked_bar, x='Region', y=SUTUN_DEGER, color='Group Technology',
            title=f"{end_year} Yılında Bölgelere Göre Teknoloji Dağılımı",
            labels={SUTUN_DEGER: f"{PAGE_METRIC_NAME_REG} ({PAGE_METRIC_UNIT_REG})", 'Region': "Bölge", 'Group Technology': "Teknoloji Grubu"})
        fig_stacked_bar.update_layout(barmode='stack', xaxis={'categoryorder':'total descending'}, **common_bar_pie_layout_updates)

        # --- 3. TREEMAP GRAFİĞİ ---
        df_treemap = df_last_year.copy()
        if df_treemap.empty:
            fig_treemap = create_regional_empty_figure(f"{end_year} yılı için Treemap verisi yok.")
        else:
            active_treemap_colors = TREEMAP_COLORS_LIGHT if active_theme == 'light' else TREEMAP_COLORS_DARK

            fig_treemap = px.treemap(
                df_treemap,
                path=[px.Constant("Tüm Bölgeler"), SUTUN_BOLGE_REG_PAGE, SUTUN_ULKE, SUTUN_GROUP_TECH_REG_PAGE, SUTUN_TEKNOLOJI],
                values=SUTUN_DEGER,
                color_discrete_sequence=active_treemap_colors, 
                title=f"{end_year} Yılı Kapasite Dağılımı Hiyerarşisi",
                hover_data={'Region': False, SUTUN_ULKE: True, 'Group Technology': False, SUTUN_TEKNOLOJI: True, SUTUN_DEGER: ':.0f'}
            )
            fig_treemap.update_traces(textinfo="label+percent root")
            fig_treemap.update_layout(
                template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', font_color=font_color,
                margin = dict(t=50, l=10, r=10, b=10)
            )

        return fig_time_series, fig_stacked_bar, fig_treemap