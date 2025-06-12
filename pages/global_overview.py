# pages/global_overview.py
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np # Logaritma ve sayısal işlemler için
import plotly.io as pio

from components.data_loader import (
    load_and_prepare_country_data, 
    SUTUN_ULKE, SUTUN_TEKNOLOJI, SUTUN_YIL, SUTUN_DEGER, SUTUN_ISO_CODE
)

df_map_data, filters_map_data, metrics_map_info = load_and_prepare_country_data()

if not df_map_data.empty:
    PAGE_METRIC_INFO_GLOBAL = metrics_map_info.get('ana_metrik', {})
    PAGE_METRIC_NAME_GLOBAL = PAGE_METRIC_INFO_GLOBAL.get('isim', 'Kurulu Kapasite')
    PAGE_METRIC_UNIT_GLOBAL = PAGE_METRIC_INFO_GLOBAL.get('birim', 'MW')
    all_technologies_global_page = filters_map_data.get('technologies', [])
    years_list_for_slider_global_page = [int(y) for y in filters_map_data.get('years', [])]
    min_slider_year_global_page = min(years_list_for_slider_global_page) if years_list_for_slider_global_page else 2000
    max_slider_year_global_page = max(years_list_for_slider_global_page) if years_list_for_slider_global_page else 2023
    initial_year_global_page = max_slider_year_global_page
else:
    PAGE_METRIC_NAME_GLOBAL = "Veri Yok"
    PAGE_METRIC_UNIT_GLOBAL = ""
    all_technologies_global_page = []
    years_list_for_slider_global_page = []
    min_slider_year_global_page, max_slider_year_global_page, initial_year_global_page = 2000, 2023, 2023

if df_map_data.empty:
    layout = dbc.Container(#... (Hata layout'u aynı) ...
        [dbc.Alert([html.H4("Veri Yükleme Hatası!", className="alert-heading"), html.P("Global sayfa için ülke verileri yüklenemedi.")], color="danger", className="mt-3 text-center")]
    )
else:
    layout = dbc.Container(fluid=True, className="dbc dbc-row-selectable py-3", children=[
        html.H2(f"Global Enerji Atlası - {PAGE_METRIC_NAME_GLOBAL}", className="text-center mb-4"),
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader(dbc.Stack([
                    html.H5(children=[html.I(className="bi bi-funnel-fill me-2"), "Harita Filtreleri"], className="mb-0"),
                    dbc.Button(children=[html.I(className="bi bi-chevron-up")],id="global-filter-collapse-toggle-button", color="link", className="ms-auto p-0 border-0", size="sm", n_clicks=0)
                ], direction="horizontal")),
                dbc.Collapse(dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Yıl Seçin:", className="form-label fw-bold"),
                            dcc.Slider(id='global-map-year-slider', min=min_slider_year_global_page, max=max_slider_year_global_page, step=1,
                                       marks={year: str(year) for year in years_list_for_slider_global_page if year % 5 == 0 or year == min_slider_year_global_page or year == max_slider_year_global_page} if years_list_for_slider_global_page else {},
                                       value=initial_year_global_page, tooltip={"placement": "bottom", "always_visible": True}, className="mb-3")
                        ], width=12, md=6),
                        dbc.Col([
                            html.Label("Teknoloji Seçin (Opsiyonel):", className="form-label fw-bold"),
                            dcc.Dropdown(id='global-map-technology-dropdown',
                                         options=[{'label': 'Tüm Teknolojiler', 'value': 'all'}] + [{'label': tech, 'value': tech} for tech in all_technologies_global_page],
                                         value='all', multi=False, clearable=True, placeholder="Bir teknoloji seçin veya tümü...", className="mb-3")
                        ], width=12, md=6),
                    ])]),
                    id="global-filter-collapse-area", is_open=True)
            ]), className="mb-4")
        ]),
        dbc.Row([dbc.Col(dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='global-choropleth-map', style={'height': '65vh'})))), width=12)]),
        # ... layout tanımı içinde, en sondaki dbc.Row'dan sonra:
        dbc.Row([dbc.Col(html.Div(id="global-kpi-area"), width=12, className="mt-3")]),
        
        # === YENİ SANKEY DİYAGRAMI ALANI ===
        dbc.Row([
            dbc.Col(dcc.Loading(dbc.Card(
                [
                    dbc.CardHeader(html.H5("Global Kapasite Akışı (Sankey Diagramı)", className="mb-0")),
                    dbc.CardBody(dcc.Graph(id='global-sankey-diagram', style={'height': '60vh'}))
                ]
            )), width=12, className="mt-4") # Üstteki KPI'lardan biraz boşluklu
        ])
    ])

    @callback(
        [Output("global-filter-collapse-area", "is_open"), Output("global-filter-collapse-toggle-button", "children")],
        [Input("global-filter-collapse-toggle-button", "n_clicks")],
        [State("global-filter-collapse-area", "is_open")],
        prevent_initial_call=True
    )
    def toggle_global_filter_collapse(n_clicks, is_open):
        # ... (Bu callback aynı) ...
        new_is_open_state = not is_open
        new_icon = html.I(className="bi bi-chevron-up") if new_is_open_state else html.I(className="bi bi-chevron-down")
        if n_clicks: return new_is_open_state, [new_icon]
        return no_update, no_update

    def create_global_empty_map_figure(message="Harita için veri yok veya yetersiz filtre."):
        # ... (Bu fonksiyon aynı) ...
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="grey"))
        fig.update_layout(xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', geo=dict(bgcolor='rgba(0,0,0,0)'))
        return fig

    # pages/global_overview.py -> SADECE update_global_choropleth_map fonksiyonu güncellenecek

    # ... (dosyanın başındaki importlar, veri yükleme, layout ve diğer callback'ler aynı kalacak) ...
    # ... (toggle_global_filter_collapse ve create_global_empty_map_figure fonksiyonları aynı kalacak) ...

    @callback(
        Output('global-choropleth-map', 'figure'),
        [Input('global-map-year-slider', 'value'),
         Input('global-map-technology-dropdown', 'value'),
         Input('theme-preference-store', 'data')] 
    )
    def update_global_choropleth_map(selected_year, selected_technology, current_theme_preference):
        if selected_year is None or df_map_data.empty:
            return create_global_empty_map_figure("Lütfen bir yıl seçin.")

        map_df_filtered_year = df_map_data[df_map_data[SUTUN_YIL].astype(int) == int(selected_year)]
        chart_title_tech_part = "Tüm Teknolojiler"
        if selected_technology and selected_technology != 'all':
            map_df_filtered_tech = map_df_filtered_year[map_df_filtered_year[SUTUN_TEKNOLOJI] == selected_technology]
            chart_title_tech_part = f"'{selected_technology}' Teknolojisi"
        else:
            map_df_filtered_tech = map_df_filtered_year

        if map_df_filtered_tech.empty:
            return create_global_empty_map_figure(f"{selected_year} yılı {chart_title_tech_part.lower()} için {PAGE_METRIC_NAME_GLOBAL.lower()} verisi bulunamadı.")

        country_summary = map_df_filtered_tech.groupby([SUTUN_ULKE, SUTUN_ISO_CODE])[SUTUN_DEGER].sum().reset_index()
        country_summary_positive = country_summary[country_summary[SUTUN_DEGER] > 0].copy()
        
        if country_summary_positive.empty:
             return create_global_empty_map_figure(f"{selected_year} {chart_title_tech_part.lower()} için haritada gösterilecek pozitif {PAGE_METRIC_NAME_GLOBAL.lower()} verisi yok.")
        
        country_summary_positive['log_deger'] = np.log10(country_summary_positive[SUTUN_DEGER])

        active_theme = current_theme_preference if current_theme_preference else 'dark'
        plotly_template = "plotly_white" if active_theme == 'light' else "plotly_dark"
        font_color_for_map = "#001f36" if active_theme == 'light' else "#e8e8f0"
        map_color_scale = px.colors.sequential.PuBuGn if active_theme == 'light' else px.colors.sequential.Inferno
        land_color_map = 'rgba(217, 217, 217, 0.7)' if active_theme == 'light' else 'rgba(100, 100, 100, 0.4)'
        ocean_color_map = 'rgba(235, 245, 255, 0.5)' if active_theme == 'light' else 'rgba(10,10,20,0.8)'
        subunitcolor_map = 'rgba(150,150,150,0.7)' if active_theme == 'light' else 'rgba(80,80,80,0.5)'

        fig = px.choropleth(
            country_summary_positive,
            locations=SUTUN_ISO_CODE,
            color='log_deger', # Renklendirme için logaritmik değerler
            hover_name=SUTUN_ULKE,
            custom_data=[SUTUN_ULKE, SUTUN_DEGER], # Orijinal ülke adı ve DEĞERİ hover'a taşı
            projection="natural earth",
            color_continuous_scale=map_color_scale, # Bu, log_deger'e uygulanacak
            labels={'log_deger': f'{PAGE_METRIC_UNIT_GLOBAL}'} 
        )
        
        fig.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" + # Ülke Adı
                f"{PAGE_METRIC_NAME_GLOBAL}: %{{customdata[1]:,.0f}} {PAGE_METRIC_UNIT_GLOBAL}" + # Orijinal Değer
                "<extra></extra>"
            )
        )

        # === RENK SKALASI ÇUBUĞU İÇİN ÖZEL TIK DEĞERLERİ VE ETİKETLERİ ===
        min_val_orig = country_summary_positive[SUTUN_DEGER].min()
        max_val_orig = country_summary_positive[SUTUN_DEGER].max()
        
        tick_values_log = []
        tick_texts_orig = []

        if min_val_orig > 0 and max_val_orig > 0 and max_val_orig > min_val_orig:
            # Başlangıç ve bitiş üslerini bulalım (10 tabanında)
            start_power = np.floor(np.log10(min_val_orig))
            end_power = np.ceil(np.log10(max_val_orig))
            
            # Çok fazla tick olmaması için adım belirleyelim
            num_desired_ticks = 5 
            power_range = end_power - start_power
            step = 1
            if power_range > num_desired_ticks:
                step = int(np.ceil(power_range / num_desired_ticks))
                step = max(1, step) # Adım en az 1 olmalı

            current_power = start_power
            while current_power <= end_power + step: # end_power'ı da dahil etmek ve biraz ötesine geçebilmek için
                orig_val = 10**current_power
                # Eğer orijinal değer, maksimum verinin çok ötesindeyse ve zaten birkaç tick eklediysek dur.
                if orig_val > max_val_orig * 1.5 and len(tick_values_log) >=2 :
                    if tick_values_log[-1] < np.log10(max_val_orig) : # Son tick max değerden küçükse max değeri de ekle
                         tick_values_log.append(np.log10(max_val_orig))
                         tick_texts_orig.append(f"{max_val_orig:,.0f}")
                    break
                
                # Eğer tick min_val_orig'den çok küçükse ve ilk tick değilse atla,
                # ama bir sonraki tick min_val_orig'e yakınsa bunu da ekle.
                if orig_val < min_val_orig / 1.5 and len(tick_values_log) == 0 and 10**(current_power+step) > min_val_orig :
                     tick_values_log.append(np.log10(min_val_orig)) # İlk tick olarak min değeri ekle
                     tick_texts_orig.append(f"{min_val_orig:,.0f}")


                if orig_val >= min_val_orig / 1.5 and orig_val <= max_val_orig * 1.5 :
                    log_val = np.log10(orig_val)
                    if not tick_values_log or abs(log_val - tick_values_log[-1]) > 0.1 : # Çok yakın tickleri engelle
                        tick_values_log.append(log_val)
                        if orig_val >= 1000000: tick_texts_orig.append(f"{orig_val/1000000:,.1f}M")
                        elif orig_val >= 1000: tick_texts_orig.append(f"{orig_val/1000:,.0f}K")
                        else: tick_texts_orig.append(f"{orig_val:,.0f}")
                
                if current_power == end_power and max_val_orig > orig_val : # Son tick max değerden küçükse max değeri de ekle
                    if not tick_values_log or abs(np.log10(max_val_orig) - tick_values_log[-1]) > 0.1 :
                         tick_values_log.append(np.log10(max_val_orig))
                         tick_texts_orig.append(f"{max_val_orig:,.0f}")

                if current_power > end_power + step : # Güvenlik için döngüden çık
                    break
                current_power += step


            # Eğer hiç tick oluşmadıysa veya sadece 1 tane varsa, min ve max'ı ekleyelim
            if len(tick_values_log) < 2:
                tick_values_log = []
                tick_texts_orig = []
                if min_val_orig > 0:
                    tick_values_log.append(np.log10(min_val_orig))
                    tick_texts_orig.append(f"{min_val_orig:,.0f}")
                if max_val_orig > 0 and (min_val_orig != max_val_orig or not tick_values_log) :
                    # Eğer son eklenen tick max değer değilse veya hiç tick yoksa max'ı ekle
                    if not tick_values_log or abs(np.log10(max_val_orig) - tick_values_log[-1]) > 0.01:
                        tick_values_log.append(np.log10(max_val_orig))
                        tick_texts_orig.append(f"{max_val_orig:,.0f}")
            
            # Tick değerlerini sırala ve benzersiz yap (nadiren gerekebilir ama garanti)
            if tick_values_log:
                sorted_ticks_with_text = sorted(zip(tick_values_log, tick_texts_orig))
                final_tick_values_log = []
                final_tick_texts_orig = []
                for i, (log_val, text_val) in enumerate(sorted_ticks_with_text):
                    if i == 0 or abs(log_val - final_tick_values_log[-1]) > 0.01: # Çok yakınları atla
                        final_tick_values_log.append(log_val)
                        final_tick_texts_orig.append(text_val)
                tick_values_log = final_tick_values_log
                tick_texts_orig = final_tick_texts_orig


        fig.update_layout(
            template=plotly_template,
            title_text=f"{selected_year} Yılı - {chart_title_tech_part} - Global {PAGE_METRIC_NAME_GLOBAL} Dağılımı",
            title_x=0.5,
            font_color=font_color_for_map,
            geo=dict(
                showframe=False, showcoastlines=False, projection_type='natural earth',
                bgcolor='rgba(0,0,0,0)', landcolor=land_color_map, oceancolor=ocean_color_map,
                subunitcolor=subunitcolor_map
            ),
            margin={"r":0,"t":40,"l":0,"b":0},
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            
            coloraxis_colorbar=dict( # type='log' burada olmayacak çünkü veriyi zaten logaritmik yaptık
                title=dict(
                    text=f"{PAGE_METRIC_UNIT_GLOBAL}", # "(Log Ölçek)" ifadesini kaldırdık, çünkü tikler orijinal değerler
                    font=dict(color=font_color_for_map, size=10)
                ),
                thicknessmode="pixels", thickness=15,
                lenmode="fraction", len=0.75,
                yanchor="middle", y=0.5,
                xanchor="left", x=0.01,
                ticks="outside",
                tickvals=tick_values_log if tick_values_log else None, # Hesaplanmış logaritmik pozisyonlar
                ticktext=tick_texts_orig if tick_texts_orig else None, # Orijinal değer etiketleri
                tickfont=dict(color=font_color_for_map, size=9)
            )
        )
        return fig
    
    # ... (update_global_kpis fonksiyonu aynı kalacak) ...
    
    @callback(
        Output('global-kpi-area', 'children'),
        [Input('global-map-year-slider', 'value'),
         Input('global-map-technology-dropdown', 'value')]
    )
    def update_global_kpis(selected_year, selected_technology):
        # ... (Bu fonksiyon aynı kalacak) ...
        if selected_year is None or df_map_data.empty: return ""
        # ... (geri kalan KPI mantığı aynı)
        kpi_df = df_map_data[df_map_data[SUTUN_YIL].astype(int) == int(selected_year)]
        tech_filter_text = "Tüm Teknolojiler"
        if selected_technology and selected_technology != 'all':
            kpi_df = kpi_df[kpi_df[SUTUN_TEKNOLOJI] == selected_technology]
            tech_filter_text = f"'{selected_technology}' Teknolojisi"
        if kpi_df.empty:
            return dbc.Alert(f"{selected_year} {tech_filter_text.lower()} için KPI verisi bulunamadı.", color="warning", className="text-center")
        total_global_capacity = kpi_df[SUTUN_DEGER].sum()
        num_countries_with_data = kpi_df[SUTUN_ULKE].nunique()
        top_country_data = None
        if not kpi_df.empty and kpi_df[SUTUN_DEGER].sum() > 0 :
            top_country_series = kpi_df.groupby(SUTUN_ULKE)[SUTUN_DEGER].sum().nlargest(1)
            if not top_country_series.empty:
                top_country_data = {'name': top_country_series.index[0], 'value': top_country_series.iloc[0]}
        kpi_cards = [
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(f"{total_global_capacity:,.0f} {PAGE_METRIC_UNIT_GLOBAL}", className="card-title text-primary mb-0"),
                html.P(f"Toplam Global {PAGE_METRIC_NAME_GLOBAL} ({selected_year}, {tech_filter_text})", className="card-text small text-muted")
            ])], className="h-100"), md=4, className="mb-2"),
            dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(f"{num_countries_with_data}", className="card-title text-info mb-0"),
                html.P(f"Veri Bulunan Ülke Sayısı ({selected_year}, {tech_filter_text})", className="card-text small text-muted")
            ])], className="h-100"), md=4, className="mb-2"),]
        if top_country_data:
            kpi_cards.append(dbc.Col(dbc.Card([dbc.CardBody([
                html.H4(f"{top_country_data['name']}", className="card-title text-success mb-0", style={'fontSize': '1.1rem', 'whiteSpace': 'nowrap', 'overflow': 'hidden', 'textOverflow': 'ellipsis'}),
                html.P(f"En Yüksek Kapasiteli Ülke ({top_country_data['value']:,.0f} {PAGE_METRIC_UNIT_GLOBAL})", className="card-text small text-muted")
            ])], className="h-100"), md=4, className="mb-2"))
        return dbc.Row(kpi_cards, className="justify-content-center")
    # pages/global_overview.py dosyasının en sonuna eklenecek

    # pages/global_overview.py -> SADECE bu callback fonksiyonunu güncelleyin

    @callback(
        Output('global-sankey-diagram', 'figure'),
        [Input('global-map-year-slider', 'value'),
         Input('global-map-technology-dropdown', 'value'), # Input'u geri ekledim
         Input('theme-preference-store', 'data')]
    )
    def update_global_sankey_diagram(selected_year, selected_technology, current_theme_preference):
        # Sankey için tüm teknolojileri göstermek genellikle daha anlamlıdır,
        # bu yüzden 'selected_technology' filtresini şimdilik kullanmıyoruz ama
        # isterseniz aşağıdaki veri filtreleme adımında aktive edebilirsiniz.
        
        if selected_year is None or df_map_data.empty:
            return create_global_empty_figure("Sankey diagramı için lütfen bir yıl seçin.")

        # Bu değişkenlerin dosyanın başında tanımlanması daha iyi olur ama fonksiyon içinde de çalışır.
        SUTUN_BOLGE_GLOBAL_PAGE = 'Region'
        SUTUN_RE_NON_RE_GLOBAL_PAGE = 'RE or Non-RE'
        SUTUN_GROUP_TECH_GLOBAL_PAGE = 'Group Technology'

        required_sankey_cols = [SUTUN_BOLGE_GLOBAL_PAGE, SUTUN_RE_NON_RE_GLOBAL_PAGE, SUTUN_GROUP_TECH_GLOBAL_PAGE]
        if not all(col in df_map_data.columns for col in required_sankey_cols):
            return create_global_empty_figure("Sankey için gerekli sütunlar (Region, vb.) veride bulunamadı.")

        sankey_df = df_map_data[
            (df_map_data[SUTUN_YIL] == int(selected_year)) &
            (df_map_data[SUTUN_DEGER] > 0)
        ]
        
        # Eğer teknoloji filtresi uygulanmak istenirse, bu satır aktive edilebilir:
        # if selected_technology and selected_technology != 'all':
        #     sankey_df = sankey_df[sankey_df[SUTUN_TEKNOLOJI] == selected_technology]

        if sankey_df.empty:
            return create_global_empty_figure(f"{selected_year} yılı için Sankey verisi bulunamadı.")
            
        # Tema için renk paletleri (Yeni hiyerarşideki düğümleri içerecek şekilde güncellendi)
        active_theme = current_theme_preference if current_theme_preference else 'dark'
        if active_theme == 'light':
            palette = {
                'Total Renewable': '#27ae60', 'Total Non-Renewable': '#e67e22',
                'Asia': '#3498db', 'Europe': '#9b59b6', 'Africa': '#f1c40f',
                'Americas': '#e74c3c', 'Oceania': '#1abc9c',
                'Fossil fuels': '#c0392b', 'Nuclear': '#8e44ad', 'Solar': '#f39c12', 
                'Wind': '#2980b9', 'Hydro': '#2c3e50', 'Bioenergy': '#27ae60',
                'Other renewable energy': '#aed581', 'Other non-renewable energy': '#ffb74d',
                'font_color': '#2c3e50', 'link_default': 'rgba(200, 200, 200, 0.4)',
                'node_default': '#ced4da', 'Total Global': '#0984e3'
            }
        else: # Karanlık tema
            palette = {
                'Total Renewable': '#2ecc71', 'Total Non-Renewable': '#e74c3c',
                'Asia': '#f1c40f', 'Europe': '#9b59b6', 'Africa': '#e67e22',
                'Americas': '#3498db', 'Oceania': '#1abc9c',
                'Fossil fuels': '#c0392b', 'Nuclear': '#8e44ad', 'Solar': '#f39c12', 
                'Wind': '#3498db', 'Hydro': '#2980b9', 'Bioenergy': '#27ae60',
                'Other renewable energy': '#dce775', 'Other non-renewable energy': '#ffb74d',
                'font_color': '#ecf0f1', 'link_default': 'rgba(127, 140, 141, 0.5)',
                'node_default': '#34495e', 'Total Global': '#3498db'
            }

        # === YENİ HİYERARŞİYE GÖRE VERİ HAZIRLIĞI ===
        # Hiyerarşi: Global Toplam -> RE/Non-RE -> Bölge -> Teknoloji Grubu
        
        # Akışları hesaplamak için groupby kullanalım
        flow1 = sankey_df.groupby(SUTUN_RE_NON_RE_GLOBAL_PAGE)[SUTUN_DEGER].sum().reset_index()
        flow1.rename(columns={SUTUN_RE_NON_RE_GLOBAL_PAGE: 'target', SUTUN_DEGER: 'value'}, inplace=True)
        flow1['source'] = 'Total Global'

        flow2 = sankey_df.groupby([SUTUN_RE_NON_RE_GLOBAL_PAGE, SUTUN_BOLGE_GLOBAL_PAGE])[SUTUN_DEGER].sum().reset_index()
        flow2.rename(columns={SUTUN_RE_NON_RE_GLOBAL_PAGE: 'source', SUTUN_BOLGE_GLOBAL_PAGE: 'target', SUTUN_DEGER: 'value'}, inplace=True)
            
        flow3 = sankey_df.groupby([SUTUN_BOLGE_GLOBAL_PAGE, SUTUN_GROUP_TECH_GLOBAL_PAGE])[SUTUN_DEGER].sum().reset_index()
        flow3.rename(columns={SUTUN_BOLGE_GLOBAL_PAGE: 'source', SUTUN_GROUP_TECH_GLOBAL_PAGE: 'target', SUTUN_DEGER: 'value'}, inplace=True)

        # Tüm akışları birleştir
        sankey_links_df = pd.concat([flow1, flow2, flow3], ignore_index=True)
        sankey_links_df.dropna(inplace=True) # NaN içeren satırları kaldır

        if sankey_links_df.empty:
            return create_global_empty_figure("Sankey akışı için veri bulunamadı.")

        # Düğümleri ve index haritasını oluştur
        all_labels = pd.unique(sankey_links_df[['source', 'target']].values.ravel('K')).tolist()
        node_map = {label: i for i, label in enumerate(all_labels)}
        
        # Source, target, value ve renk listelerini oluştur
        source_indices = sankey_links_df['source'].map(node_map)
        target_indices = sankey_links_df['target'].map(node_map)
        value_list = sankey_links_df['value']
        
        node_colors = [palette.get(label, palette['node_default']) for label in all_labels]
        
        link_colors = []
        for src_label in sankey_links_df['source']:
            color = palette.get(src_label, palette['link_default'])
            if color.startswith("#"):
                color = f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.4)"
            elif color.startswith("rgb("):
                color = color.replace(')', ', 0.4)').replace('rgb', 'rgba')
            elif color.startswith("rgba("):
                parts = color.split(',')
                if len(parts) == 4:
                     color = f"{parts[0]},{parts[1]},{parts[2]}, 0.4)"
            link_colors.append(color)

        # === GRAFİK OLUŞTURMA ===
        fig = go.Figure(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=all_labels,
                color=node_colors
            ),
            link=dict(
                source=source_indices,
                target=target_indices,
                value=value_list,
                color=link_colors
            )
        ))

        fig.update_layout(
            title_text=f"{selected_year} Yılı Global Kapasite Akışı (Enerji Tipi > Bölge > Teknoloji Grubu)", 
            title_x=0.5,
            template="plotly_white" if active_theme == 'light' else "plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=palette['font_color']
        )
        return fig