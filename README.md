⚡ Energy Data Visualization Platform
This project is an interactive web application developed to analyze and visualize installed energy capacity data from around the world. It is built with Python using Dash and Plotly libraries. Users can explore energy trends by country, region, and technology over the years through interactive charts.

✨ Features
Home Page: A modern welcome page introducing the project and its purpose.

Detailed Country Panel: Allows in-depth analysis of a selected country’s energy data:

Capacity trends by technology over the years (Line Chart).

Technology distribution in a selected year (Pie/Bar Chart).

An interactive Sankey diagram showing the flow of the energy portfolio.

Global Overview: Summarizes the global situation:

An interactive Choropleth map displaying global capacity distribution for a selected year and technology.

Key performance indicators such as total capacity and the number of countries with available data.

Regional Analysis: Compares different geographical regions:

Capacity trends over time for each region.

Stacked capacity charts grouped by technology for each region.

A Treemap showing capacity hierarchy.

Country Comparison: Allows comparison of up to 4 countries for a specific technology.

Dynamic Theme: Toggle between light and dark mode.

📂 Project Structure
The project is organized in a modular and readable manner:


.
├── app.py                  # Main Dash application with layout and routing logic
├── Procfile                # For deployment on platforms like Heroku
├── requirements.txt        # Required Python libraries
│
├── assets/                 # Static files like CSS and JavaScript
│   ├── style.css           # Global stylesheet
│   ├── clientside.js       # Client-side logic (e.g., theme toggle)
│   └── Animation...json    # Lottie animation file (deprecated)
│
├── components/             # Reusable modules
│   ├── data_loader.py      # Loads and processes country-level data (Country.csv)
│   └── region_data_loader.py # Loads and processes region-level data (Region.csv)
│
├── data/                   # Raw data files
│   ├── Country.csv         # Detailed capacity data by country
│   ├── Global.csv          # (Not currently in use)
│   └── Region.csv          # Aggregated capacity data by region
│
└── pages/                  # Different pages of the application
    ├── landing_page.py     # Main landing page
    ├── main_dashboard.py   # Detailed country analysis panel
    ├── global_overview.py  # Global map and KPIs
    ├── regional_analysis.py# Regional comparison page
    └── comparison_page.py  # Country comparison page
🚀 Installation and Running
Follow these steps to run the project locally:

1. Clone the Repository:
git clone https://github.com/afrknkaya/dash-map-app.git
cd dash-map-app
2. Create a Virtual Environment (Recommended):
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
3. Install Required Packages:
All required packages are listed in the requirements.txt file.
pip install -r requirements.txt
4. Run the Application:
python app.py
The app will start at http://127.0.0.1:8050/ by default.

🛠️ Technologies Used
Backend & Frontend: Dash

Data Visualization: Plotly Express

Data Manipulation: Pandas

UI Components: Dash Bootstrap Components

Deployment: Gunicorn (as defined in the Procfile)

