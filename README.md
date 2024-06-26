# Geoinformatics Data Visualization Dash App

## Introduction

This project is a Dash application designed to visualize geoinformatics data interactively. The application leverages various datasets to provide insights through maps and plots. It is built using Python's Dash framework, Plotly for visualizations, and Folium for interactive maps.

## Features

- Interactive maps with additional plugins such as MiniMap, Fullscreen, Draw, and MeasureControl.
- Various types of plots (pie charts, bar plots) for data visualization.
- Dynamic data retrieval from API endpoints.
- Customizable user inputs for selecting cities and parameter types.

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/geoinformatics-dash-app.git
   cd geoinformatics-dash-app
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Ensure that your API server is running and accessible at the specified endpoints in the `Dash_app.py` file.
2. Run the Dash application:

   ```bash
   python Dash_app.py
   ```

3. Open your web browser and navigate to `http://127.0.0.1:8050` to access the application.

## File Structure

- `Dash_app.py`: Main application file.
- `assets/`: Directory containing custom stylesheets and other assets.
- `functions.py`: Contains helper functions for data retrieval and processing.

## Dependencies

- Dash
- Geopandas
- Plotly
- Folium
- Requests

Ensure all dependencies are installed by running `pip install -r requirements.txt`.

## Data Sources

The application retrieves data from the following API endpoints:

- Cities data: `http://localhost:5005/api/cities`
- Indicators data: `http://localhost:5005/api/indicators`
- Olympic events data: `http://localhost:5005/api/olympic_events`
- Users data: `http://localhost:5005/api/users`

## Customization

You can customize the application by modifying the layout and callbacks in the `Dash_app.py` file to suit your specific data and visualization needs.

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

Special thanks to the contributors of the libraries and tools used in this project.

---

Copy and paste this content into your `README.md` file in your GitHub repository. Let me know if you need any more adjustments or additional information.
