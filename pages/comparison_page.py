# pages/comparison_page.py
from dash import html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import plotly.io as pio

# pio.templates.default = "plotly_dark" # Artık callback içinde dinamik ayarlıyoruz

# data_loader'dan SADECE fonksiyonu ve SÜTUN adlarını import et
from components.data_loader import (
    load_and_prepare_country_data, # Fonksiyonu import ediyoruz
    SUTUN_ULKE, SUTUN_TEKNOLOJI, SUTUN_YIL, SUTUN_DEGER
)

# Veriyi yükle ve bu modüle özel global değişkenleri ayarla
# Bu işlem comparison_page.py dosyası import edildiğinde bir kere çalışacak
# print("comparison_page.py: Veri yükleme işlemi başlıyor...")
df_country_global_comp, filters_data_global_comp, metrics_info_global_comp = load_and_prepare_country_data()

# Metrik bilgilerini ve filtreleri bu sayfaya özel değişkenlere ata
if not df_country_global_comp.empty:
    # print(f"comparison_page.py: Veri başarıyla yüklendi. {len(df_country_global_comp)} satır.")
    CURRENT_METRIC_INFO_COMP = metrics_info_global_comp.get('ana_metrik', {})
    CURRENT_METRIC_NAME_COMP = CURRENT_METRIC_INFO_COMP.get('isim', 'Kurulu Kapasite')
    CURRENT_METRIC_UNIT_COMP = CURRENT_METRIC_INFO_COMP.get('birim', 'MW')
    all_technologies_comp = filters_data_global_comp.get('technologies', [])
    years_list_for_slider_comp = [int(y) for y in filters_data_global_comp.get('years', [])]
else:
    # print("comparison_page.py: UYARI! Veri yüklenemedi veya boş.")
    CURRENT_METRIC_NAME_COMP = "Veri Yok"
    CURRENT_METRIC_UNIT_COMP = ""
    filters_data_global_comp = {} # Boş sözlük ata
    all_technologies_comp = []
    years_list_for_slider_comp = []

# Ana layout tanımı (df_country_global_comp'in durumuna göre)
if df_country_global_comp.empty: # <-- DÜZELTME: df_country_global_comp KULLANILDI
    layout = dbc.Container([
        dbc.Alert(
            [html.H4("Veri Yükleme Hatası!", className="alert-heading"),
             html.P("Ana ülke verileri yüklenemedi. Lütfen uygulamayı kontrol edin.")],
            color="danger", className="mt-3 text-center"
        )])
else:
    min_slider_year_comp = min(years_list_for_slider_comp) if years_list_for_slider_comp else 2000
    max_slider_year_comp = max(years_list_for_slider_comp) if years_list_for_slider_comp else 2023
    default_start_year_comp = max(2010, min_slider_year_comp)
    default_end_year_comp = max_slider_year_comp
    slider_value_comp = [default_start_year_comp, default_end_year_comp]
    slider_marks_comp = {}
    if years_list_for_slider_comp:
        current_min_year_slider_comp = min(years_list_for_slider_comp)
        current_max_year_slider_comp = max(years_list_for_slider_comp)
        slider_marks_comp = {
            str(year): str(year) for year in years_list_for_slider_comp
            if year % 5 == 0 or year == current_min_year_slider_comp or year == current_max_year_slider_comp}
        if not slider_marks_comp:
            if current_min_year_slider_comp == current_max_year_slider_comp:
                 slider_marks_comp[str(current_min_year_slider_comp)] = str(current_min_year_slider_comp)
            else:
                 slider_marks_comp[str(current_min_year_slider_comp)] = str(current_min_year_slider_comp)
                 slider_marks_comp[str(current_max_year_slider_comp)] = str(current_max_year_slider_comp)
    else: slider_marks_comp = {str(2000): '2000', str(2023): '2023'}

    layout = dbc.Container(fluid=True, className="dbc dbc-row-selectable py-3", children=[
        html.H2(f"Ülkeler Arası {CURRENT_METRIC_NAME_COMP} Karşılaştırması", className="text-center mb-4"),
        dbc.Card([
            dbc.CardHeader(
                dbc.Stack(
                    [
                        html.H5(children=[html.I(className="bi bi-filter-square-fill me-2"), "Karşılaştırma Filtreleri"], className="mb-0"),
                        dbc.Button(
                            children=[html.I(className="bi bi-chevron-up")],
                            id="comp-filter-collapse-toggle-button",
                            color="link", className="ms-auto p-0 border-0", size="sm", n_clicks=0
                        ),
                    ], direction="horizontal",
                )
            ),
            dbc.Collapse(
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Teknoloji Seçin (Tek Seçim):", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id='comp-technology-dropdown',
                                options=[{'label': tech, 'value': tech} for tech in all_technologies_comp],
                                value=all_technologies_comp[0] if all_technologies_comp else None,
                                multi=False, clearable=False, className="mb-3"
                            )
                        ], width=12, md=4),
                        dbc.Col([
                            html.Label("Karşılaştırılacak Ülkeleri Seçin (En Fazla 4):", className="form-label fw-bold"),
                            dcc.Dropdown(
                                id='comp-country-dropdown',
                                options=[], value=[], multi=True,
                                placeholder="Önce teknoloji seçin, sonra ülkeleri...", className="mb-3"
                            )
                        ], width=12, md=4),
                        dbc.Col([
                            html.Label("Yıl Aralığı:", className="form-label fw-bold"),
                            dcc.RangeSlider(
                                id='comp-year-slider', min=min_slider_year_comp, max=max_slider_year_comp,
                                step=1, marks=slider_marks_comp, value=slider_value_comp,
                                tooltip={"placement": "bottom", "always_visible": False}, className="mb-3"
                            )
                        ], width=12, md=4),
                    ]),
                ]),
                id="comp-filter-collapse-area", is_open=True,
            )
        ], className="mb-4"),
        dbc.Row([
            dbc.Col(dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='comp-time-series-chart')))), width=12, className="mb-3")
        ]),
        dbc.Row([
            dbc.Col(dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='comp-latest-year-bar-chart')))), width=12, md=6, className="mb-3"),
            dbc.Col(dcc.Loading(dbc.Card(dbc.CardBody(dcc.Graph(id='comp-latest-year-pie-chart')))), width=12, md=6, className="mb-3"),
        ]),
    ])

    @callback(
        [Output("comp-filter-collapse-area", "is_open"), Output("comp-filter-collapse-toggle-button", "children")],
        [Input("comp-filter-collapse-toggle-button", "n_clicks")],
        [State("comp-filter-collapse-area", "is_open")],
        prevent_initial_call=True
    )
    def toggle_comp_filter_collapse(n_clicks, is_open):
        new_is_open_state = not is_open
        new_icon = html.I(className="bi bi-chevron-up") if new_is_open_state else html.I(className="bi bi-chevron-down")
        if n_clicks: return new_is_open_state, [new_icon]
        return no_update, no_update

    def create_comp_empty_figure(message="Karşılaştırma için veri yok veya yetersiz filtre."):
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16, color="grey"))
        fig.update_layout(xaxis_visible=False, yaxis_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig

    @callback(
        [Output('comp-country-dropdown', 'options'), Output('comp-country-dropdown', 'value')],
        [Input('comp-technology-dropdown', 'value')]
    )
    def update_country_options_for_comparison(selected_technology):
        if not selected_technology or df_country_global_comp.empty: # _comp KULLANILDI
            return [], []
        tech_specific_df = df_country_global_comp[df_country_global_comp[SUTUN_TEKNOLOJI] == selected_technology] # _comp KULLANILDI
        if tech_specific_df.empty:
            return [], []
        countries_with_selected_tech = sorted(tech_specific_df[SUTUN_ULKE].unique())
        country_options = [{'label': country, 'value': country} for country in countries_with_selected_tech]
        return country_options, []

    @callback(
        Output('comp-time-series-chart', 'figure'),
        [Input('comp-technology-dropdown', 'value'),
         Input('comp-country-dropdown', 'value'),
         Input('comp-year-slider', 'value'),
         Input('theme-preference-store', 'data')] # TEMA INPUT'U EKLENDİ
    )
    def update_comparison_time_series(selected_tech, selected_countries, selected_years, current_theme_preference):
        if not selected_tech or not selected_countries or len(selected_countries) == 0 or not selected_years:
            return create_comp_empty_figure("Lütfen teknoloji, en az bir ülke ve yıl aralığı seçin.")
        if len(selected_countries) > 4:
            return create_comp_empty_figure("En fazla 4 ülke seçebilirsiniz.")
        
        start_year, end_year = int(selected_years[0]), int(selected_years[1])
        filtered_df = df_country_global_comp[ # _comp KULLANILDI
            (df_country_global_comp[SUTUN_TEKNOLOJI] == selected_tech) &
            (df_country_global_comp[SUTUN_ULKE].isin(selected_countries)) &
            (df_country_global_comp[SUTUN_YIL].astype(int) >= start_year) &
            (df_country_global_comp[SUTUN_YIL].astype(int) <= end_year)
        ]
        if filtered_df.empty:
            return create_comp_empty_figure(f"'{selected_tech}' için seçili ülkelerde belirtilen yıllarda veri bulunamadı.")
        df_grouped = filtered_df.groupby([SUTUN_YIL, SUTUN_ULKE])[SUTUN_DEGER].sum().reset_index()

        active_theme = current_theme_preference if current_theme_preference else 'dark'
        current_plotly_template = "plotly_white" if active_theme == 'light' else "plotly_dark"
        font_color_for_graph = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_bg = "rgba(228, 228, 228, 0.95)" if active_theme == 'light' else "rgba(40, 38, 70, 0.9)"
        hover_font_color_in_label = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_border = "#7cc4fb" if active_theme == 'light' else "#a53c7d"
        
        fig = px.line(df_grouped, x=SUTUN_YIL, y=SUTUN_DEGER, color=SUTUN_ULKE, markers=True,
                      title=f"'{selected_tech}' Teknolojisi İçin {CURRENT_METRIC_NAME_COMP} Karşılaştırması",
                      labels={SUTUN_DEGER: f'{CURRENT_METRIC_NAME_COMP} ({CURRENT_METRIC_UNIT_COMP})', SUTUN_YIL: 'Yıl', SUTUN_ULKE: 'Ülke'})
        fig.update_layout(
            template=current_plotly_template,
            hovermode="x unified", legend_title_text='Ülkeler', 
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font_color=font_color_for_graph,
            hoverlabel=dict(bgcolor=hover_bg,font_size=11,font_color=hover_font_color_in_label,bordercolor=hover_border,align="left",namelength=-1))
        fig.update_traces(hovertemplate="<b>%{fullData.name}</b><br>" + f"{CURRENT_METRIC_NAME_COMP}: %{{y:,.0f}} {CURRENT_METRIC_UNIT_COMP}<extra></extra>")
        return fig

    @callback(
        Output('comp-latest-year-bar-chart', 'figure'),
        [Input('comp-technology-dropdown', 'value'),
         Input('comp-country-dropdown', 'value'),
         Input('comp-year-slider', 'value'),
         Input('theme-preference-store', 'data')] # TEMA INPUT'U EKLENDİ
    )
    def update_comparison_bar_chart(selected_tech, selected_countries, selected_years, current_theme_preference):
        if not selected_tech or not selected_countries or len(selected_countries) == 0 or not selected_years:
            return create_comp_empty_figure("Bar grafik için lütfen teknoloji, en az bir ülke ve yıl seçin.")
        if len(selected_countries) > 4:
             return create_comp_empty_figure("En fazla 4 ülke seçebilirsiniz.")
        
        target_year = int(selected_years[1])
        filtered_df = df_country_global_comp[ # _comp KULLANILDI
            (df_country_global_comp[SUTUN_TEKNOLOJI] == selected_tech) &
            (df_country_global_comp[SUTUN_ULKE].isin(selected_countries)) &
            (df_country_global_comp[SUTUN_YIL].astype(int) == target_year)
        ]
        if filtered_df.empty:
            return create_comp_empty_figure(f"'{selected_tech}' için {target_year} yılında seçili ülkelerde veri bulunamadı.")
        df_bar = filtered_df.groupby(SUTUN_ULKE)[SUTUN_DEGER].sum().reset_index().sort_values(by=SUTUN_DEGER, ascending=False)
        if df_bar.empty: return create_comp_empty_figure("Bar grafik için gruplanacak veri yok.")

        active_theme = current_theme_preference if current_theme_preference else 'dark'
        current_plotly_template = "plotly_white" if active_theme == 'light' else "plotly_dark"
        font_color_for_graph = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_bg = "rgba(228, 228, 228, 0.95)" if active_theme == 'light' else "rgba(40, 38, 70, 0.9)"
        hover_font_color_in_label = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_border = "#7cc4fb" if active_theme == 'light' else "#a53c7d"

        fig = px.bar(df_bar, x=SUTUN_ULKE, y=SUTUN_DEGER, color=SUTUN_ULKE,
                     title=f"{target_year} Yılı '{selected_tech}' {CURRENT_METRIC_NAME_COMP} Karşılaştırması",
                     labels={SUTUN_DEGER: f'{CURRENT_METRIC_NAME_COMP} ({CURRENT_METRIC_UNIT_COMP})', SUTUN_ULKE: 'Ülke'})
        fig.update_layout(
            template=current_plotly_template,
            showlegend=False, paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
            font_color=font_color_for_graph,
            hoverlabel=dict(bgcolor=hover_bg, font_size=12, font_color=hover_font_color_in_label, bordercolor=hover_border))
        fig.update_traces(hovertemplate="<b>%{x}</b><br>" + f"{CURRENT_METRIC_NAME_COMP}: %{{y:,.0f}} {CURRENT_METRIC_UNIT_COMP}<extra></extra>")
        return fig

    @callback(
        Output('comp-latest-year-pie-chart', 'figure'),
        [Input('comp-technology-dropdown', 'value'),
         Input('comp-country-dropdown', 'value'),
         Input('comp-year-slider', 'value'),
         Input('theme-preference-store', 'data')] # TEMA INPUT'U EKLENDİ
    )
    def update_comparison_pie_chart(selected_tech, selected_countries, selected_years, current_theme_preference):
        if not selected_tech or not selected_countries or len(selected_countries) < 1 :
            return create_comp_empty_figure("Pasta grafik için lütfen teknoloji, en az bir ülke ve yıl seçin.")
        if not selected_years:
             return create_comp_empty_figure("Lütfen yıl aralığı seçin.")
        if len(selected_countries) > 4:
            return create_comp_empty_figure("En fazla 4 ülke seçebilirsiniz.")
            
        target_year = int(selected_years[1])
        filtered_df = df_country_global_comp[ # _comp KULLANILDI
            (df_country_global_comp[SUTUN_TEKNOLOJI] == selected_tech) &
            (df_country_global_comp[SUTUN_ULKE].isin(selected_countries)) &
            (df_country_global_comp[SUTUN_YIL].astype(int) == target_year)
        ]
        if filtered_df.empty or filtered_df[SUTUN_DEGER].sum() <= 0:
            return create_comp_empty_figure(f"'{selected_tech}' için {target_year} yılında seçili ülkelerde pozitif veri bulunamadı.")
        df_pie = filtered_df.groupby(SUTUN_ULKE)[SUTUN_DEGER].sum().reset_index()
        df_pie = df_pie[df_pie[SUTUN_DEGER] > 0]
        if df_pie.empty : return create_comp_empty_figure("Pasta grafik için pozitif değerli veri yok.")
        
        active_theme = current_theme_preference if current_theme_preference else 'dark'
        current_plotly_template = "plotly_white" if active_theme == 'light' else "plotly_dark"
        font_color_for_graph = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_bg = "rgba(228, 228, 228, 0.95)" if active_theme == 'light' else "rgba(40, 38, 70, 0.9)"
        hover_font_color_in_label = "#001f36" if active_theme == 'light' else "#e8e8f0"
        hover_border = "#7cc4fb" if active_theme == 'light' else "#a53c7d"

        fig = px.pie(df_pie, names=SUTUN_ULKE, values=SUTUN_DEGER, hole=0.3,
                     title=f"{target_year} Yılı '{selected_tech}' {CURRENT_METRIC_NAME_COMP} Paylaşımı",
                     labels={SUTUN_DEGER: f'{CURRENT_METRIC_NAME_COMP} ({CURRENT_METRIC_UNIT_COMP})', SUTUN_ULKE: 'Ülke'})
        fig.update_traces(textposition='inside', textinfo='percent+label',
                          hovertemplate="<b>%{label}</b><br>" + f"{CURRENT_METRIC_NAME_COMP}: %{{value:,.0f}} {CURRENT_METRIC_UNIT_COMP}<br>Pay: %{{percent}}<extra></extra>")
        fig.update_layout(
            template=current_plotly_template,
            paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
            legend_title_text='Ülkeler',
            font_color=font_color_for_graph,
            hoverlabel=dict(bgcolor=hover_bg, font_size=12, font_color=hover_font_color_in_label, bordercolor=hover_border)
        )
        return fig