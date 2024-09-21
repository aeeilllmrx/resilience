from flask import Flask
from markupsafe import Markup
from shapely import wkt

import csv
import pandas as pd

import folium
import json
import random

app = Flask(__name__)


def load_locations_from_csv(file_path):
    """
    Load locations from a CSV file.

    Use the latitude and longitude columns to create a list of tuples.

    :param file_path: str, path to the CSV file
    :return: list, loaded locations data
    """
    with open("parking_lots.csv", "r") as file:
        reader = csv.DictReader(file)
        return [(float(row["latitude"]), float(row["longitude"])) for row in reader][
            :50
        ]


def generate_popup_html(name, features):
    """
    Generate HTML for a Folium popup based on the given features.

    :param name: str, name of the application (remedy)
    :param features: dict, features of the application
    :return: str, HTML content for the popup
    """
    description = features.get("Description", "")
    cost = features.get("Cost", 0)

    html_content = f"""
	<div style="font-family: Arial, sans-serif; width: 300px; font-size: 14px;">
		<h2 style="margin-bottom: 5px;">Opportunity Area: Parking Lot</h2>
		<p style="margin-top: 0; margin-bottom: 15px;"><strong>Proposed Remedy: {name}</strong></p>
		<p style="margin-top: 0; margin-bottom: 15px;">{description}</p>
		
		<div style="display: flex; align-items: center; margin-bottom: 10px;">
			<span><strong>⌂</strong> Aboveground</span>
		</div>
		
		<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 15px;">
			<span style="font-size: 1.2em; font-weight: bold;">Cost: ${cost:,}</span>
		</div>
		
		<div>
	"""

    for benefit, level in features.items():
        if benefit not in ["Description", "Cost"]:
            filled_stars = "★" * int(level)
            empty_stars = "☆" * (5 - int(level))
            html_content += f"""
			<div style="margin-bottom: 5px;">
				<span>{benefit}</span><br>
				<span style="color: #4CAF50;">{filled_stars}</span><span style="color: #D3D3D3;">{empty_stars}</span>
			</div>
			"""

    html_content += """
		</div>
	</div>
	"""

    return Markup(html_content)


def load_applications(file_path):
    """
    Load applications from a JSON file.

    :param file_path: str, path to the JSON file
    :return: dict, loaded applications data
    """
    with open(file_path, "r") as file:
        return json.load(file)


def get_name_from_location(location, remedies):
    # Return a random value from remedies
    return random.choice(remedies)


# Define a function that returns a hard-coded color based on the FSHRI value
def get_color(fshri_value):
    if fshri_value == 1:
        return "#cceeff"  # Light Blue
    elif fshri_value == 2:
        return "#99ddff"  # Slightly Darker Blue
    elif fshri_value == 3:
        return "#66ccff"  # Medium Blue
    elif fshri_value == 4:
        return "#3399ff"  # Darker Blue
    elif fshri_value == 5:
        return "#0066cc"  # Dark Blue
    else:
        return "#ffffff"  # Default to white if FSHRI is outside expected range


@app.route("/")
def index():
    df_flood_zone = pd.read_csv("flood.csv")

    start_coords = (40.6782, -73.9442)
    m = folium.Map(location=start_coords, zoom_start=13)

    applications = load_applications("remedies.json")
    remedies = list(applications.keys())

    locations = load_locations_from_csv("parking_lots.csv")
    color_options = ["green", "yellow", "orange", "red"]

    # Iterate through each row of the DataFrame and plot the polygon
    for index, row in df_flood_zone.iterrows():
        # Parse the MULTIPOLYGON from the 'the_geom' column using shapely
        multipolygon = wkt.loads(row["the_geom"])

        # Get the FSHRI value and corresponding color
        fshri_value = row["FSHRI"]
        polygon_color = get_color(fshri_value)

        # A MULTIPOLYGON consists of multiple POLYGONS, so we iterate through them
        for polygon in multipolygon.geoms:
            # Extract the exterior coordinates of the polygon
            exterior_coords = [(y, x) for x, y in polygon.exterior.coords]

            # Add the polygon to the folium map with the hard-coded color based on FSHRI
            folium.Polygon(
                locations=exterior_coords,
                color=polygon_color,
                fill=True,
                fill_color=polygon_color,
                fill_opacity=0.4,
                opacity=0.6,
            ).add_to(m)

    for location in locations:
        name = get_name_from_location(location, remedies)
        marker_color = random.choice(color_options)

        popup_html = generate_popup_html(name, applications[name])
        folium.Marker(
            location=location,  # Replace with actual coordinates
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=name,
            icon=folium.Icon(color=marker_color, icon="info-sign"),
        ).add_to(m)

    return m._repr_html_()


if __name__ == "__main__":
    app.run(debug=True)
