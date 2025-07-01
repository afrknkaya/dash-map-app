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


🚀 Installation and Running

Follow these steps to run the project locally:

1. Clone the Repository:

git clone https://github.com/afrknkaya/dash-map-app.git

cd dash-map-app

2. Create a Virtual Environment (Recommended):
Windows
python -m venv venv
venv\Scripts\activate

macOS / Linux
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

