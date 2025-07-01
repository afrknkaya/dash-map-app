# app.py
import dash
from dash import html, dcc, Output, Input, State, no_update, ClientsideFunction
import dash_bootstrap_components as dbc

# Sayfaları import et
from pages import main_dashboard, landing_page, global_overview, regional_analysis, comparison_page

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.VAPOR, dbc.icons.BOOTSTRAP],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ]
               )
app.title = "Enerji İstatistikleri Paneli"
server = app.server

# Yan Menü (Offcanvas) İçeriği
offcanvas_menu_content = dbc.Nav(
    [
        dbc.NavLink("Ana Sayfa", href="/", active="exact", className="offcanvas-nav-link"),
        dbc.NavLink("Detaylı Dashboard", href="/dashboard", active="exact", className="offcanvas-nav-link"),
        dbc.NavLink("Global Bakış", href="/global", active="exact", className="offcanvas-nav-link"),
        dbc.NavLink("Bölgesel Analiz", href="/regional", active="exact", className="offcanvas-nav-link"),
        dbc.NavLink("Ülke Karşılaştırma", href="/comparison", active="exact", className="offcanvas-nav-link"),
        
    ],
    vertical=True,
    pills=True,
)

# Navigasyon Çubuğu (Navbar) - Sizin paylaştığınız son haliyle aynı
navbar = dbc.Navbar(
    dbc.Container(
        [ 
            dbc.Row(
                [ 
                    dbc.Col( 
                        dbc.Button( 
                            html.I(className="bi bi-list fs-5"), 
                            id="open-offcanvas-button",
                            n_clicks=0,
                            color="light",
                            outline=True,
                            size="sm",
                            className="me-2 rounded-pill",
                            style={
                                "padding-top": "0.2rem", "padding-bottom": "0.2rem",
                                "padding-left": "0.6rem", "padding-right": "0.6rem",
                                "line-height": "1"
                            }
                        ),
                        width="auto",
                        align="center"
                    ), 
                    dbc.Col( 
                        html.A( 
                            html.Div([ 
                                html.I(className="bi bi-lightning-charge-fill me-2 fs-4 align-middle"),
                                html.Span(app.title, className="align-middle fs-5 fw-bold")
                            ], style={"display": "flex", "alignItems": "center"}),
                            href="/",
                            style={"textDecoration": "none", "color": "inherit"}
                        ),
                        width="auto",
                        align="center"
                    ), 
                    dbc.Col( 
                        html.Div( # Tema Switch için sarmalayıcı div (Sizin kodunuzda bu şekildeydi, düzeltilmiş hali)
                            [
                                html.Span(html.I(className="bi bi-moon-stars-fill"), id="theme-icon-moon", className="me-2 align-middle"),
                                dbc.Switch(
                                    id="theme-switch",
                                    value=False, 
                                    className="d-inline-block align-middle",
                                    persistence=True,
                                    persistence_type="local"
                                ),
                                html.Span(html.I(className="bi bi-sun-fill"), id="theme-icon-sun", className="ms-2 align-middle")
                            ],
                            className="d-flex align-items-center"
                        ),
                        width="auto",
                        align="center",
                        className="ms-auto" 
                    ) 
                ], 
                align="center",
                justify="between",
                className="w-100 g-0"
            ) 
        ], 
        fluid=True
    ), 
    color="primary",
    dark=True,
    sticky="top",
    className="shadow-sm mb-0"
)

# Ana Uygulama Layout'u
app.layout = html.Div([
    dcc.Store(id='theme-preference-store', storage_type='local', data='dark'), # data='dark' eklendi
    dcc.Location(id='url', refresh=False),
    navbar,
    dbc.Offcanvas(
        offcanvas_menu_content,
        id="offcanvas-menu",
        title="Navigasyon Menüsü",
        is_open=False,
        placement="start",
        backdrop=True,
        scrollable=True,
    ),
    html.Div(id='page-content', className="") 
])

# CLIENTSIDE CALLBACK (Tema class'ını body'ye eklemek için)
app.clientside_callback(
    ClientsideFunction(
        namespace='clientside',
        function_name='update_theme'
    ),
    Output('theme-preference-store', 'data'), 
    Input('theme-switch', 'value'),
    State('theme-preference-store', 'data') 
)

# Yan Menüyü (Offcanvas) Açıp Kapatma Callback'i (Butonla)
@app.callback(
    Output("offcanvas-menu", "is_open"),
    Input("open-offcanvas-button", "n_clicks"),
    State("offcanvas-menu", "is_open"),
    prevent_initial_call=True,
)
def toggle_offcanvas(n_clicks_button, is_open_state):
    if n_clicks_button:
        return not is_open_state
    return is_open_state

# URL Değiştiğinde Yan Menüyü Kapatma Callback'i
@app.callback(
    Output("offcanvas-menu", "is_open", allow_duplicate=True), 
    Input("url", "pathname"), 
    State("offcanvas-menu", "is_open"),
    prevent_initial_call=True 
)
def close_offcanvas_on_navigate(pathname, current_is_open):
    if current_is_open:
        return False
    return no_update

# URL'ye Göre Sayfa İçeriğini Güncelleme Callback'i
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/dashboard':
        return main_dashboard.layout
    elif pathname == '/global':
        return global_overview.layout
    elif pathname == '/regional':
        return regional_analysis.layout
    elif pathname == '/comparison':
        return comparison_page.layout
  
    elif pathname == '/':
        return landing_page.layout() 
    else:
        return dbc.Container(
            dbc.Alert(
                [
                    html.H1("404: Sayfa Bulunamadı", className="alert-heading"),
                    html.P(f"'{pathname}' adresinde bir sayfa bulunamadı."),
                    html.Hr(),
                    dbc.Button("Ana Sayfaya Dön", href="/", color="primary", className="ms-auto")
                ], color="danger", className="mt-5 text-center p-4 shadow rounded"
            ), className="py-5"
        )

if __name__ == '__main__':
    app.run(debug=True)
