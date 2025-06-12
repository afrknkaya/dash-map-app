# pages/main_dashboard.py
from dash import html, dcc, callback, Output, Input, State, no_update, callback_context
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import plotly.io as pio

# Gerekli Sütun Adları (Country.csv dosyanızdan)
# data_loader'da zaten tanımlı ama burada da emin olmak için listeyelim
# SUTUN_RE_NON_RE = 'RE or Non-RE'
# SUTUN_GROUP_TECHNOLOGY = 'Group Technology'

from components.data_loader import (
    load_and_prepare_country_data, SUTUN_ULKE, SUTUN_TEKNOLOJI,
    SUTUN_YIL, SUTUN_DEGER
)

df_country_global, filters_data_global, metrics_info_global = load_and_prepare_country_data()

# Eğer 'RE or Non-RE' veya 'Group Technology' sütunları farklı isimlerdeyse,
# bu değişkenleri data_loader.py'de tanımlayıp buradan import etmek en doğrusu olur.
# Şimdilik bu isimlerde olduklarını varsayıyorum.
SUTUN_RE_NON_RE = 'RE or Non-RE'
SUTUN_GROUP_TECHNOLOGY = 'Group Technology'


if not df_country_global.empty:
    ANA_METRIK_INFO = metrics_info_global.get('ana_metrik', {})
    ANA_METRIK_ISIM = ANA_METRIK_INFO.get('isim', 'Değer')
    ANA_METRIK_BIRIM = ANA_METRIK_INFO.get('birim', '')
else:
    ANA_METRIK_ISIM = "Veri Yok"
    ANA_METRIK_BIRIM = ""
    filters_data_global = filters_data_global if isinstance(filters_data_global, dict) else {}

if df_country_global.empty:
    layout = dbc.Container([
        dbc.Alert(
            [html.H4("Veri Yükleme Hatası!", className="alert-heading"),
             html.P("Ana ülke verileri yüklenemedi veya filtrelendikten sonra boş kaldı."),
             html.P("Lütfen terminaldeki `components/data_loader.py` çıktılarını ve CSV dosya yollarını kontrol edin.")],
            color="danger", className="mt-3 text-center"
        )])
else:
    
    years_list_for_slider = [int(y) for y in filters_data_global.get('years', [])]
    min_slider_year = min(years_list_for_slider) if years_list_for_slider else 2000
    max_slider_year = max(years_list_for_slider) if years_list_for_slider else 2023
    default_start_year = max(2010, min_slider_year)
    default_end_year = max_slider_year
    slider_value = [default_start_year, default_end_year]
    slider_marks = {}
    if years_list_for_slider:
        current_min_year_slider = min(years_list_for_slider)
        current_max_year_slider = max(years_list_for_slider)
        slider_marks = {
            str(year): str(year) for year in years_list_for_slider
            if year % 5 == 0 or year == current_min_year_slider or year == current_max_year_slider}
        if not slider_marks:
            if current_min_year_slider == current_max_year_slider:
                slider_marks[str(current_min_year_slider)] = str(current_min_year_slider)
            else:
                slider_marks[str(current_min_year_slider)] = str(current_min_year_slider)
                slider_marks[str(current_max_year_slider)] = str(current_max_year_slider)
    else: slider_marks = {str(2000): '2000', str(2023): '2023'}

    initial_country_value = str('Turkey') if 'Turkey' in filters_data_global.get('countries', []) else (str(filters_data_global.get('countries', [None])[0]) if filters_data_global.get('countries') else None)


    layout = dbc.Container(fluid=True, className="dbc dbc-row-selectable py-3", children=[
        html.H2("Ülke Enerji Kapasitesi Analizi", className="text-center mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(
                    dbc.Stack(
                        [
                            html.H5(children=[html.I(className="bi bi-sliders me-2"), "Filtreler"], className="mb-0"),
                            dbc.Button(
                                children=[html.I(className="bi bi-chevron-up")],
                                id="filter-collapse-toggle-button",
                                color="link", className="ms-auto p-0 border-0", size="sm", n_clicks=0
                            ),
                        ], direction="horizontal",)
                ),
                dbc.Collapse(
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Yıl Aralığı:", className="form-label fw-bold"),
                                dcc.RangeSlider(id='year-slider', min=min_slider_year, max=max_slider_year, step=1,
                                                marks=slider_marks, value=slider_value,
                                                tooltip={"placement": "bottom", "always_visible": False}, className="mb-3")
                            ], width=12, md=4),
                            dbc.Col([
                                html.Label("Ülke Seçin:", className="form-label fw-bold"),
                                dcc.Dropdown(id='country-dropdown',
                                             options=[{'label': str(c), 'value': str(c)} for c in filters_data_global.get('countries', [])],
                                             value=initial_country_value,
                                             multi=False, searchable=True, placeholder="Bir ülke seçin...", className="mb-3", clearable=False)
                            ], width=12, md=4),
                            dbc.Col([
                                html.Label("Teknoloji Seçin:", className="form-label fw-bold"),
                                dcc.Dropdown(id='technology-dropdown',
                                             options=[], value=[], multi=True, searchable=True, 
                                             placeholder="Önce ülke seçin...", className="mb-3")
                            ], width=12, md=4),
                        ])
                    ]),
                    id="filter-collapse-area", is_open=True,
                )])
            , width=12)], className="mb-3"),
        dbc.Row(id='kpi-cards-row', className="mb-3 justify-content-center"),
        dbc.Row([
            dbc.Col(
                dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='time-series-chart', config={'displayModeBar': False}))))
            , width=12, lg=7, className="mb-3"),
            dbc.Col(
                dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='technology-distribution-chart', config={'displayModeBar': False}))))
            , width=12, lg=5, className="mb-3"),
        ]),
        # Veri tablosu kaldırılmıştı, o yüzden burada yok.

        # === YENİ SANKEY DİYAGRAMI ALANI ===
        dbc.Row([
            dbc.Col(dcc.Loading(dbc.Card(
                [
                    dbc.CardHeader(html.H5("Enerji Portföyü Akışı (Sankey Diagramı)", className="mb-0")),
                    dbc.CardBody(dcc.Graph(id='sankey-diagram', style={'height': '60vh'}))
                ]
            )), width=12, className="mb-3")
        ])
    ]) 

    # ... (Diğer callback'leriniz aynı kalacak: toggle_filter_collapse, create_empty_figure, update_technology_options, update_kpi_cards, update_time_series_chart, update_technology_distribution_chart)
    # Sadece en sona yeni Sankey callback'ini ekleyeceğiz.
    # Önceki callback'leri buraya tekrar ekliyorum ki dosya tam olsun.

    @callback(
        [Output("filter-collapse-area", "is_open"), Output("filter-collapse-toggle-button", "children")],
        [Input("filter-collapse-toggle-button", "n_clicks")],
        [State("filter-collapse-area", "is_open")],
        prevent_initial_call=True
    )
    def toggle_filter_collapse(n_clicks, is_open):
        new_is_open_state = not is_open
        new_icon = html.I(className="bi bi-chevron-up") if new_is_open_state else html.I(className="bi bi-chevron-down")
        if n_clicks: return new_is_open_state, [new_icon]
        return no_update, no_update

    def create_empty_figure(message="Veri yok veya filtre sonucu boş."):
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="grey"))
        fig.update_layout(xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

    @callback(
        [Output('technology-dropdown', 'options'), Output('technology-dropdown', 'value')],
        [Input('country-dropdown', 'value')]
    )
    def update_technology_options(selected_country):
        if not selected_country or df_country_global.empty: return [], []
        country_specific_df = df_country_global[df_country_global[SUTUN_ULKE] == selected_country]
        if country_specific_df.empty: return [], []
        available_technologies_all = sorted(country_specific_df[SUTUN_TEKNOLOJI].unique())
        new_options = [{'label': str(tech), 'value': str(tech)} for tech in available_technologies_all]
        new_value = []
        if available_technologies_all:
            MAX_TECHS_TO_SHOW_ALL = 7 
            NUM_TOP_TECHS_TO_SHOW = 5
            if len(available_technologies_all) > MAX_TECHS_TO_SHOW_ALL:
                latest_year_for_country = country_specific_df[SUTUN_YIL].max()
                top_techs_df = country_specific_df[(country_specific_df[SUTUN_YIL] == latest_year_for_country)]
                if not top_techs_df.empty:
                    top_techs_series = top_techs_df.groupby(SUTUN_TEKNOLOJI)[SUTUN_DEGER].sum().nlargest(NUM_TOP_TECHS_TO_SHOW)
                    new_value = [str(tech) for tech in top_techs_series.index.tolist()]
                if not new_value and available_technologies_all:
                    new_value = [str(tech) for tech in available_technologies_all[:NUM_TOP_TECHS_TO_SHOW]]
            else:
                new_value = [str(tech) for tech in available_technologies_all]
        return new_options, new_value

    @callback(Output('kpi-cards-row', 'children'),
              [Input('year-slider', 'value'), Input('country-dropdown', 'value'), Input('technology-dropdown', 'value')])
    def update_kpi_cards(selected_years_tuple, selected_country, selected_technologies):
        # ... (Bu fonksiyonun içeriği aynı kalacak) ...
        if not selected_country or not selected_technologies or not selected_years_tuple or df_country_global.empty:
            return dbc.Col(dbc.Alert(f"{ANA_METRIK_ISIM} KPI'ları için lütfen tüm filtreleri seçin.",id="kpi-alert", color="info", dismissable=True, className="text-center"), width=12)
        if not selected_technologies:
             return dbc.Col(dbc.Alert("Lütfen en az bir teknoloji seçin.",id="kpi-tech-alert", color="warning", dismissable=True, className="text-center"), width=12)
        start_year, end_year = int(selected_years_tuple[0]), int(selected_years_tuple[1])
        df_kpi_year = df_country_global[
            (df_country_global[SUTUN_YIL].astype(int) == end_year) &
            (df_country_global[SUTUN_ULKE] == selected_country) &
            (df_country_global[SUTUN_TEKNOLOJI].isin(selected_technologies))]
        if df_kpi_year.empty:
            return dbc.Col(dbc.Alert(f"{selected_country}, {end_year} yılı için seçili teknolojilerle {ANA_METRIK_ISIM} verisi bulunamadı.",id="kpi-alert-no-data", color="warning", dismissable=True, className="text-center"), width=12)
        kpi_cards_list = []
        total_value_for_metric = df_kpi_year[SUTUN_DEGER].sum()
        kpi_cards_list.append(dbc.Col(dbc.Card([dbc.CardBody([
            html.H4(f"{total_value_for_metric:,.0f}", className="card-title text-primary mb-0"), 
            html.P(f"Toplam {ANA_METRIK_ISIM} ({end_year}, {ANA_METRIK_BIRIM})", className="card-text small text-muted")])],
            color="dark", outline=True, className="shadow-sm"), xs=12, sm=6, md=4, lg=3, className="mb-2"))
        if not df_kpi_year.empty and not df_kpi_year[SUTUN_DEGER].dropna().empty:
            top_tech_series = df_kpi_year.loc[df_kpi_year[SUTUN_DEGER].idxmax()]
            if isinstance(top_tech_series, pd.Series):
                kpi_cards_list.append(dbc.Col(dbc.Card([dbc.CardBody([
                    html.H4(f"{top_tech_series[SUTUN_TEKNOLOJI]}", className="card-title text-info mb-0", style={'fontSize': '1.1rem', 'whiteSpace': 'nowrap', 'overflow': 'hidden', 'textOverflow': 'ellipsis'}),
                    html.P(f"En Yüksek {ANA_METRIK_ISIM} ({top_tech_series[SUTUN_DEGER]:,.0f} {ANA_METRIK_BIRIM})", className="card-text small text-muted")])],
                    color="dark", outline=True, className="shadow-sm"), xs=12, sm=6, md=4, lg=3, className="mb-2"))
        return kpi_cards_list if kpi_cards_list else dbc.Col(dbc.Alert("Hesaplanacak KPI bulunamadı.",id="kpi-alert-calc-fail", color="secondary", className="text-center"), width=12)


    @callback(Output('time-series-chart', 'figure'),
              [Input('year-slider', 'value'), 
               Input('country-dropdown', 'value'), 
               Input('technology-dropdown', 'value'),
               Input('theme-preference-store', 'data')])
    def update_time_series_chart(selected_years_tuple, selected_country, selected_technologies, current_theme_preference):
        # ... (Bu fonksiyonun içeriği aynı kalacak) ...
        if not selected_country or not selected_technologies or not selected_years_tuple or df_country_global.empty:
            return create_empty_figure(f"{ANA_METRIK_ISIM} trendi için filtreleri seçin.")
        if not selected_technologies: return create_empty_figure("Lütfen en az bir teknoloji seçin.")
        start_year, end_year = int(selected_years_tuple[0]), int(selected_years_tuple[1])
        df_trend = df_country_global[(df_country_global[SUTUN_YIL].between(start_year, end_year)) & (df_country_global[SUTUN_ULKE] == selected_country) & (df_country_global[SUTUN_TEKNOLOJI].isin(selected_technologies))]
        if df_trend.empty: return create_empty_figure(f"{ANA_METRIK_ISIM} trendi için veri bulunamadı.")
        df_grouped = df_trend.groupby([SUTUN_YIL, SUTUN_TEKNOLOJI])[SUTUN_DEGER].sum().reset_index()
        active_theme = current_theme_preference if current_theme_preference else 'dark'
        plotly_template = "plotly_white" if active_theme == 'light' else "plotly_dark"
        font_color = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_bg = "rgba(230, 230, 230, 0.9)" if active_theme == 'light' else "rgba(40, 38, 70, 0.9)"
        hover_border = "#7cc4fb" if active_theme == 'light' else "#a53c7d"
        fig = px.line(df_grouped, x=SUTUN_YIL, y=SUTUN_DEGER, color=SUTUN_TEKNOLOJI, markers=True,
                      title=f'{selected_country} - {ANA_METRIK_ISIM} Trendi',
                      labels={SUTUN_DEGER: f'{ANA_METRIK_ISIM} ({ANA_METRIK_BIRIM})', SUTUN_YIL: 'Yıl', SUTUN_TEKNOLOJI: 'Teknoloji'})
        fig.update_traces(hovertemplate=("<b>%{fullData.name}</b><br>" + f"{ANA_METRIK_ISIM}: %{{y:,.0f}} {ANA_METRIK_BIRIM}" + "<extra></extra>"))
        fig.update_layout(template=plotly_template, hovermode="x unified", legend_title_text='Teknoloji', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color, 
                          hoverlabel=dict(bgcolor=hover_bg, font_size=11, font_color=font_color if active_theme == 'dark' else "#001f36", bordercolor=hover_border, align="left", namelength=-1 ))
        return fig

    @callback(Output('technology-distribution-chart', 'figure'),
              [Input('year-slider', 'value'), 
               Input('country-dropdown', 'value'), 
               Input('technology-dropdown', 'value'),
               Input('theme-preference-store', 'data')])
    def update_technology_distribution_chart(selected_years_tuple, selected_country, selected_technologies, current_theme_preference):
        # ... (Bu fonksiyonun içeriği aynı kalacak) ...
        if not selected_country or not selected_technologies or not selected_years_tuple or df_country_global.empty:
            return create_empty_figure(f"{ANA_METRIK_ISIM} dağılımı için filtreleri seçin.")
        if not selected_technologies: return create_empty_figure("Lütfen en az bir teknoloji seçin.")
        target_year = int(selected_years_tuple[1])
        df_dist = df_country_global[(df_country_global[SUTUN_YIL] == target_year) & (df_country_global[SUTUN_ULKE] == selected_country) & (df_country_global[SUTUN_TEKNOLOJI].isin(selected_technologies))]
        if df_dist.empty: return create_empty_figure(f"{selected_country}, {target_year} yılı için {ANA_METRIK_ISIM} dağılım verisi yok.")
        df_grouped = df_dist.groupby(SUTUN_TEKNOLOJI)[SUTUN_DEGER].sum().reset_index()
        df_grouped = df_grouped[df_grouped[SUTUN_DEGER] > 0].sort_values(by=SUTUN_DEGER, ascending=False)
        if df_grouped.empty: return create_empty_figure(f"{target_year} için pozitif {ANA_METRIK_ISIM} olan teknoloji yok.")
        active_theme = current_theme_preference if current_theme_preference else 'dark'
        plotly_template = "plotly_white" if active_theme == 'light' else "plotly_dark"
        font_color = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_bg = "rgba(230, 230, 230, 0.9)" if active_theme == 'light' else "rgba(40, 38, 70, 0.9)"
        hover_border = "#7cc4fb" if active_theme == 'light' else "#a53c7d"
        chart_type = "bar" if len(df_grouped) > 7 else "pie"
        common_layout_updates = dict(template=plotly_template, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color=font_color,
                                     hoverlabel=dict(bgcolor=hover_bg, font_size=12, font_color=font_color if active_theme == 'dark' else "#001f36", bordercolor=hover_border))
        if chart_type == "bar":
            fig = px.bar(df_grouped, x=SUTUN_TEKNOLOJI, y=SUTUN_DEGER, color=SUTUN_TEKNOLOJI,
                         title=f'{selected_country} - {target_year} {ANA_METRIK_ISIM} Dağılımı',
                         labels={SUTUN_DEGER: f'{ANA_METRIK_ISIM} ({ANA_METRIK_BIRIM})', SUTUN_TEKNOLOJI: 'Teknoloji'})
            fig.update_layout(showlegend=False, xaxis_tickangle=-30, **common_layout_updates)
            fig.update_traces(hovertemplate="<b>%{x}</b><br>" + f"{ANA_METRIK_ISIM}: %{{y:,.0f}} {ANA_METRIK_BIRIM}<extra></extra>")
        else: # pie
            fig = px.pie(df_grouped, names=SUTUN_TEKNOLOJI, values=SUTUN_DEGER, hole=0.3,
                         title=f'{selected_country} - {target_year} {ANA_METRIK_ISIM} Dağılımı')
            fig.update_traces(
                textposition='inside', 
                textinfo='percent+label', 
                hoverinfo='label+percent+value',
                # === HOVERTEMPLATE DÜZELTMESİ ===
                hovertemplate=(
                    "<b>%{label}</b><br>" +
                    f"{ANA_METRIK_ISIM}: %{{value:,.0f}} {ANA_METRIK_BIRIM}" + # <-- Hatalı PAGE_METRIC_UNIT_FOLL yerine ANA_METRIK_BIRIM kullanıldı
                    "<br>Pay: %{percent}<extra></extra>"
                )
            )
            fig.update_layout(legend_title_text='Teknoloji',**common_layout_updates)
        
        return fig


    # === YENİ SANKEY DIAGRAM CALLBACK'İ ===
    # pages/main_dashboard.py -> Sadece bu fonksiyon güncellenecek

    # pages/main_dashboard.py -> Sadece bu fonksiyon güncellenecek

    # pages/main_dashboard.py -> Sadece bu fonksiyon güncellenecek

    @callback(
        Output('sankey-diagram', 'figure'),
        [Input('country-dropdown', 'value'),
         Input('year-slider', 'value'),
         Input('theme-preference-store', 'data')]
    )
    def update_sankey_diagram(selected_country, selected_years, current_theme_preference):
        if not selected_country or not selected_years:
            return create_empty_figure("Sankey diagramı için lütfen bir ülke ve yıl aralığı seçin.")

        target_year = selected_years[1]

        required_sankey_cols = [SUTUN_RE_NON_RE, SUTUN_GROUP_TECHNOLOGY, SUTUN_TEKNOLOJI]
        if not all(col in df_country_global.columns for col in required_sankey_cols):
            return create_empty_figure("Sankey için gerekli sütunlar (RE or Non-RE, Group Technology) veride bulunamadı.")

        df_sankey = df_country_global[
            (df_country_global[SUTUN_ULKE] == selected_country) & 
            (df_country_global[SUTUN_YIL] == target_year) &
            (df_country_global[SUTUN_DEGER] > 0)
        ]

        if df_sankey.empty:
            return create_empty_figure(f"{selected_country}, {target_year} yılı için Sankey verisi bulunamadı.")
            
        # === YENİ RENK PALETİ SÖZLÜKLERİ ===
        active_theme = current_theme_preference if current_theme_preference else 'dark'
        
        if active_theme == 'light':
            # --- AYDINLIK TEMA İÇİN YUMUŞAK RENK PALETİ ---
            palette = {
                # Ana Kategoriler
                'Total Renewable': 'rgba(46, 139, 87, 0.7)',  # Deniz Yeşili (yumuşak)
                'Total Non-Renewable': 'rgba(210, 105, 30, 0.7)', # Çikolata/Kiremit (yumuşak)
                
                # Teknoloji Grupları - Her biri farklı ve yumuşak renklerde
                'Solar energy': '#f8cbad',          # Yumuşak Şeftali
                'Wind energy': '#95d1e6',           # Yumuşak Bebek Mavisi
                'Hydropower (excl. Pumped Storage)': '#6fa5d8',          # Yumuşak Kot Mavisi
                'Bioenergy': '#b2d2a4',      # Yumuşak Adaçayı Yeşili
                'Fossil fuels': "#000000",   # Yumuşak Somon
                'Nuclear': '#c6aedc',         # Yumuşak Lavanta
                'Other renewable energy': '#d4e157', # Yumuşak Limon Yeşili
                'Other non-renewable energy': '#ffcc80', # Yumuşak Kayısı
                
                # Genel
                'font_color': '#212529', # Koyu yazı
                'link_default': 'rgba(189, 195, 199, 0.5)', # Çok hafif gri link
                'accent1': '#0d6efd',    # Ülke düğümü için
                'accent2': '#0a58ca'
            }
        else: # Karanlık tema
            # --- KARANLIK TEMA İÇİN YUMUŞAK RENK PALETİ ---
            palette = {
                # Ana Kategoriler
                'Total Renewable': 'rgba(67, 160, 71, 0.8)',      # Koyu temada belirgin ama yumuşak yeşil
                'Total Non-Renewable': 'rgba(239, 83, 80, 0.8)',   # Koyu temada belirgin ama yumuşak kırmızı/mercan
                
                # Teknoloji Grupları - Her biri farklı ve yumuşak renklerde
                'Solar energy': '#fdd835',          # Yumuşak Altın Sarısı
                'Wind energy': "#a9e4ff",           # Yumuşak Gökyüzü Mavisi
                'Hydropower (excl. Pumped Storage)': '#42a5f5',          # Yumuşak Mavi
                'Bioenergy': "#798d63",      # Yumuşak Kahve
                'Fossil fuels': "#2b2928",   # Daha açık kahve/gri
                'Nuclear': '#7e57c2',         # Yumuşak Ametist
                'Other renewable energy': '#dce775', # Canlı Limon Yeşili
                'Other non-renewable energy': '#ffb74d', # Canlı Kayısı
                
                # Genel
                'font_color': '#e8e8f0',
                'link_default': 'rgba(110, 110, 110, 0.5)', # Nötr gri link
                'accent1': '#a53c7d',
                'accent2': '#f35294'
            }

        # === VERİ HAZIRLIĞI (Değişiklik yok) ===
        all_nodes = [selected_country] + \
                    list(df_sankey[SUTUN_RE_NON_RE].unique()) + \
                    list(df_sankey[SUTUN_GROUP_TECHNOLOGY].unique()) + \
                    list(df_sankey[SUTUN_TEKNOLOJI].unique())
        
        unique_labels = sorted(list(set(all_nodes)))
        node_map = {label: i for i, label in enumerate(unique_labels)}

        source, target, value, link_colors, node_colors = [], [], [], [], ["gray"] * len(unique_labels)
        
        # === DÜĞÜM RENKLENDİRME (Yeni Palette ile) ===
        for label, i in node_map.items():
            node_color = palette.get(label) 
            if node_color:
                node_colors[i] = node_color
            elif label == selected_country:
                node_colors[i] = palette['accent2'] if active_theme == 'dark' else palette['accent1']
            else: # Palettede özel rengi olmayan detay teknolojiler için
                # Kaynağının rengini bulmaya çalışalım
                try:
                    source_group = df_sankey[df_sankey[SUTUN_TEKNOLOJI] == label][SUTUN_GROUP_TECHNOLOGY].iloc[0]
                    node_colors[i] = palette.get(source_group, palette['link_default'])
                except:
                    node_colors[i] = palette['link_default']

        # === AKIŞ RENKLENDİRME (Yeni Palette ile) ===
        def add_flow(source_cat, target_cat, val):
            source.append(node_map[source_cat])
            target.append(node_map[target_cat])
            value.append(val)
            # Akışın rengini kaynağının rengiyle aynı yapalım
            link_colors.append(palette.get(source_cat, palette['link_default']).replace('0.8', '0.4').replace('0.7', '0.35'))

        flow1 = df_sankey.groupby(SUTUN_RE_NON_RE)[SUTUN_DEGER].sum()
        for cat, val in flow1.items():
            add_flow(selected_country, cat, val)

        flow2 = df_sankey.groupby([SUTUN_RE_NON_RE, SUTUN_GROUP_TECHNOLOGY])[SUTUN_DEGER].sum()
        for (cat, group_tech), val in flow2.items():
            add_flow(cat, group_tech, val)

        flow3 = df_sankey.groupby([SUTUN_GROUP_TECHNOLOGY, SUTUN_TEKNOLOJI])[SUTUN_DEGER].sum()
        for (group_tech, tech), val in flow3.items():
            add_flow(group_tech, tech, val)
        
        # === GRAFİK OLUŞTURMA ===
        fig = go.Figure(go.Sankey(
            node = dict(
              pad = 20,
              thickness = 15,
              line = dict(color = "black", width = 0.5),
              label = unique_labels,
              color = node_colors # Her düğüm için ayrı renk listesi
            ),
            link = dict(
              source = source,
              target = target,
              value = value,
              color = link_colors # Her akış için ayrı renk listesi
          )))

        fig.update_layout(
            title_text=f"{selected_country} - {target_year} Yılı Enerji Portföyü Akışı", 
            title_x=0.5,
            template="plotly_white" if active_theme == 'light' else "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=palette['font_color']
        )
        return fig