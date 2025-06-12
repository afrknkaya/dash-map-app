# pages/landing_page.py
import dash_bootstrap_components as dbc
from dash import html, dcc
# get_asset_url ve Lottie ile ilgili importlar kaldırıldı

# LOKAL_LOTTIE_DOSYA_ADI değişkeni de kaldırıldı

def layout(): # layout bir fonksiyon olarak kalmaya devam ediyor
    return dbc.Container(
        [
            dbc.Row(
                dbc.Col(
                    html.Div( # Bu ana içerik kutusu .landing-jumbo-content class'ına sahip
                        [
                            # Lottie animasyonunu içeren html.Div kaldırıldı.
                            # İçeriğin ortalanması ve boşluklar için padding/margin ayarları eklendi.
                            html.H1(
                                "Enerji Verileri Görselleştirme Platformu", 
                                className="display-3 text-center",
                                style={"paddingTop": "2rem"} # Üstten biraz boşluk
                            ),
                            html.P(
                                "Dünya genelindeki enerji kurulu kapasite verilerini interaktif grafiklerle keşfedin.",
                                className="lead mt-3 text-center",
                            ),
                            html.Hr(className="my-4 border-light", style={"width": "60%", "margin": "2rem auto"}),
                            html.P(
                                "Bu platform, çeşitli ülkelerin ve teknolojilerin yıllara göre enerji trendlerini analiz etmenize olanak tanır.",
                                className="text-center"
                            ),
                            html.P(
                                dbc.Button("Dashboard'u Keşfet", color="primary", href="/dashboard", size="lg", className="mt-4"),
                                className="lead text-center",
                                style={"paddingBottom": "2rem"} # Alttan biraz boşluk
                            ),
                        ],
                        className="h-100 p-4 p-md-5 rounded-3 text-center landing-jumbo-content",
                        # style={"position": "relative"} # Bu satır bir önceki denemeden kalmış olabilir, kaldırıldı.
                    ),
                    md=10,
                    lg=8,
                ),
                justify="center",
                align="center", # Bu Row'un içeriğini dikeyde ortalar
            )
        ],
        id="landing-page-container",
        fluid=True,
        style={"padding": "0", "display": "flex", "minHeight": "calc(100vh - 56px)"} # Flex ile dikey ortalamayı destekler
                                                                                    # ve navbar hariç tüm yüksekliği kaplar
    )