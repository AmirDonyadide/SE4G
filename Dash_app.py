from dash import Dash, html, dcc, Output, Input
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from functions import download_data_as_dataframe
import folium
from folium.plugins import MiniMap, Fullscreen, Draw, MeasureControl
import requests
import pandas as pd

# Download cities data from the API endpoints
cities = download_data_as_dataframe("http://localhost:5005/api/cities")
#making geodataframe from lat lon columns
cities = gpd.GeoDataFrame(cities, geometry=gpd.points_from_xy(cities.lon, cities.lat))

# Download indicators data from the API endpoints
indicators = download_data_as_dataframe("http://localhost:5005/api/indicators")

# Download olympic_events data from the API endpoints
olympic_events = download_data_as_dataframe("http://localhost:5005/api/olympic_events")

# Download reports data from the API endpoints
reports = download_data_as_dataframe("http://localhost:5005/api/reports")

# Download users data from the API endpoints
users = download_data_as_dataframe("http://localhost:5005/api/users")


# Options for dropdowns
city_options = [{'label': city, 'value': city} for city in cities['name']]
parameter_type_options = [{'label': parameter_type[0], 'value': parameter_type[1]} for parameter_type in [('Surface Area', 'surface area'), ('Population', 'population'), ('Building', 'building'), ('Local Business Units', 'local business units'), ('Families', 'families')]]
plot_type_options = [{'label': plot_type[0], 'value': plot_type[1]} for plot_type in [('Pie Chart', 'pie'), ('Bar Plot', 'bar')]]


# Initialize the Dash app
external_stylesheets = ['assets/styles.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "IDK"

app.layout = html.Div([
    # Header Section
    html.Div([
        html.H1("Geoinformatics Data Visualization"),
        html.P("Explore geographic data with interactive maps")
    ], className='header'),
    
    # Two main sections: Map and Selection
    html.Div([
        # Left Section - Selection Tools
        html.Div([
            html.Label("Username:"),
            dcc.Input(
                id='username-input',
                type='text'
            ),
            html.Label("Password:"),
            dcc.Input(
                id='password-input',
                type='password'
            ),
            html.Br(),  # Add space between dropdowns
            html.Label("City:"),
            html.Br(),  # Add space between dropdowns
            dcc.Dropdown(
                id='city-dropdown',
                options=city_options,
                value=[],
                multi=False
            ),
            html.Label("Parameter:"),
            html.Br(),  # Add space between dropdowns
            dcc.Dropdown(
                id='parameter-type-dropdown',
                options=parameter_type_options,
                value=[]
            ),
            html.Label("Plot Type:"),
            html.Br(),  # Add space between dropdowns
            dcc.Dropdown(
                id='plot-type-dropdown',
                options=plot_type_options,
                value=[]
            ),
        ], className='selection-section'),
        
        # Right Section - Map
        html.Div([
            html.Iframe(id='folium-map', srcDoc=open('/Users/alela/OneDrive - Politecnico di Milano/UNI/SOFTWARE ENGINEERING FOR GEOINF/SE4G-main/SE4G-main/map.html', 'r').read(), width='100%', height='500')
        ], className='map-section')
    ], className='main-section'),

    # Bottom Section - divided into 2 parts: the right is the plot section and the left is the table section
    html.Div([
        # Left Section - Table
        html.Div([
            html.Div(id='table1-section'),
            html.Br(),  # Add space between tables
            # Add download button for the table 1
            html.A(html.Button('Download Table as CSV', className='download-button'), id='download1-link', download="table.csv", href="", target="_blank"),
            html.Br(),  # Add space between tables
            html.Br(),  # Add space between tables
            html.Div(id='table2-section'),
            html.Br(),  # Add space between tables
            # Add download button for the table 2
            html.A(html.Button('Download Table as CSV', className='download-button'), id='download2-link', download="table.csv", href="", target="_blank"),
        ], className='table-section'),

        # Right Section - Plot
        html.Div([
            html.Div(id='plot-section')
        ], className='plot-section')
    ], className='bottom-section'),

    # Registration and Report sections side-by-side
    html.Div([
        # Original Registration Form
        html.Div([
            html.H3("Register New User"),
            html.Label("Username:"),
            dcc.Input(
                id='new-username-input',
                type='text',
                className='dash-input'
            ),
            html.Label("Name:"),
            dcc.Input(
                id='name-input',
                type='text',
                className='dash-input'
            ),
            html.Label("Last Name:"),
            dcc.Input(
                id='last-name-input',
                type='text',
                className='dash-input'
            ),
            html.Label("Email:"),
            dcc.Input(
                id='email-input',
                type='email',
                className='dash-input'
            ),
            html.Label("Password:"),
            dcc.Input(
                id='new-password-input',
                type='password',
                className='dash-password'
            ),
            html.Br(),  # Add space between inputs
            html.Button('Register', id='register-button', n_clicks=0, className='dash-button'),
            html.Div(id='register-message')
        ], className='register-section', style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'}),

        # Report Section
        html.Div([
            html.H3("Submit Report"),
            html.Label("Name:"),
            dcc.Input(
                id='report-name-input',
                type='text',
                className='dash-input'
            ),
            html.Label("Report:"),
            dcc.Textarea(
                id='report-input',
                className='dash-input',
                style={'width': '100%', 'height': 100}
            ),
            html.Br(),  # Add space between inputs
            html.Button('Submit Report', id='report-button', n_clicks=0, className='dash-button'),
            html.Div(id='report-message')
        ], className='register-section', style={'width': '48%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ], className='form-sections', style={'width': '100%', 'display': 'flex', 'justify-content': 'space-between'}),

    # Break 5 lines
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),

    # Add copyright
    html.Div([
        html.P("© 2024 IDK. All rights reserved.")
    ], className='footer')
])



# Callback to update the plot section based on the selected city, parameter type and plot type
@app.callback(
    Output('plot-section', 'children'),
    [Input('city-dropdown', 'value'),
     Input('parameter-type-dropdown', 'value'),
     Input('plot-type-dropdown', 'value'),
     Input('username-input', 'value'),
     Input('password-input', 'value')]
)
def update_plot_section(selected_city, selected_parameter_type, selected_plot_type, user, password):
    if user and password:
        if user in users['username'].values:
            if password == users[users['username'] == user]['password'].values[0]:
                if selected_city and selected_parameter_type and selected_plot_type:
                    # Get the data for the selected city
                    city_data = cities[cities['name'] == selected_city]
                    # Get the data for the selected parameter type
                    parameter_data = indicators[indicators['Parameter_Type'] == selected_parameter_type]
                    # Merge the city and parameter data
                    data=city_data[parameter_data['Indicator'].tolist()]
                    #merge the data and parameter data
                    data = data.T.reset_index()
                    data.columns = ['Indicator', 'Value']
                    df=data.merge(parameter_data, on='Indicator')
                    # Create the plot based on the selected plot type
                    if selected_plot_type == 'pie':
                        #legend base on df['Translation']
                        #title base on df['Risk Type']
                        fig = px.pie(df, values='Value', names='Indicator', title=selected_parameter_type,color_discrete_sequence=px.colors.sequential.RdBu, hole=.3)
                        fig.update_traces(textposition='inside', textinfo='percent')
                    elif selected_plot_type == 'bar':
                        #legend base on df['Translation']
                        #title base on df['Risk Type']
                        fig = px.bar(df, x='Indicator', y='Value', title=selected_parameter_type, color='Indicator', barmode='group')
                    else:
                        fig = go.Figure()
                    return dcc.Graph(figure=fig)
                else:
                    return html.P("Please select a city, parameter type, and plot type to view the plot.")
            else:
                return html.P("Invalid password")
        else:
            return html.P("Invalid username")
    else:
        return html.P("Please enter username and password")


# Callback to update the table1 section based on the selected city and olympic_events
@app.callback(
    Output('table1-section', 'children'),
    [Input('city-dropdown', 'value'),
        Input('username-input', 'value'),
        Input('password-input', 'value')]
)
def update_table1_section(selected_city, user, password):
    if user and password:
        if user in users['username'].values:
            if password == users[users['username'] == user]['password'].values[0]:
                # Check if the input is available
                if selected_city:
                    if selected_city in olympic_events['CITY'].values:
                        # Get the olympic events data for the selected city
                        olympic_events_data = olympic_events[olympic_events['CITY'] == selected_city]
                        # Create the table based on the selected olympic events data(only SPORT and VENUE columns
                        table = html.Table(
                            className='table',  # Apply the 'table' class for styling
                            children=[
                                html.Thead(
                                    html.Tr([html.Th(col) for col in olympic_events_data[['SPORT', 'VENUE']]])
                                ),
                                html.Tbody([
                                    html.Tr([
                                        html.Td(olympic_events_data.iloc[i]['SPORT']),
                                        html.Td(olympic_events_data.iloc[i]['VENUE'])
                                    ]) for i in range(len(olympic_events_data))
                                ])
                            ]
                        )
                        return table
                    else:
                        return html.P("No Olympic events found for the selected city.")
                else:
                    return html.P("Please select a city to view the table.")
            else:
                return html.P("Invalid password")
        else:
            return html.P("Invalid username")
    else:
        return html.P("Please enter username and password")

# Callback to update the table2 section based on the selected city and indicators
@app.callback(
    Output('table2-section', 'children'),
    [Input('city-dropdown', 'value'),
        Input('parameter-type-dropdown', 'value'),
        Input('username-input', 'value'),
        Input('password-input', 'value')]
)
def update_table2_section(selected_city, selected_parameter_type, user, password):
    if user and password:
        if user in users['username'].values:
            if password == users[users['username'] == user]['password'].values[0]:
                # Check if the input is available
                if selected_city and selected_parameter_type:
                    # Get the data for the selected city
                    city_data = cities[cities['name'] == selected_city]
                    # Get the data for the selected parameter type
                    parameter_data = indicators[indicators['Parameter_Type'] == selected_parameter_type]
                    # Merge the city and parameter data
                    data = city_data[parameter_data['Indicator'].tolist()]
                    # Merge the data and parameter data
                    data = data.T.reset_index()
                    data.columns = ['Indicator', 'Value']
                    df = data.merge(parameter_data, on='Indicator')
                    df=df.drop(columns=['Parameter_Type', 'Risk_Type'])
                    # Create the table based on the df
                    table = html.Table(
                        className='table',  # Apply the 'table' class for styling
                        children=[
                            html.Thead(
                                html.Tr([html.Th(col) for col in df.columns])
                            ),
                            html.Tbody([
                                html.Tr([
                                    html.Td(df.iloc[i]['Indicator']),
                                    html.Td(df.iloc[i]['Value']),
                                    html.Td(df.iloc[i]['Translation'])
                                ]) for i in range(len(df))
                            ])
                        ]
                    )
                    return table
                else:
                    return html.P("Please select a city and parameter type to view the table.")
            else:
                return html.P("Invalid password")
        else:
            return html.P("Invalid username")
    else:
        return html.P("Please enter username and password")

# Callback to update the folium map based on the selected city
@app.callback(
    Output('folium-map', 'srcDoc'),
    [Input('city-dropdown', 'value'),
    Input('parameter-type-dropdown', 'value')]
)
def update_folium_map(selected_city, selected_parameter_type):
    # Check if the input is available
    if selected_city:
        lat=download_data_as_dataframe("http://localhost:5005/api/cities/lat/"+selected_city).iloc[0][0]
        lon=download_data_as_dataframe("http://localhost:5005/api/cities/lon/"+selected_city).iloc[0][0]
        # Get the data for the selected city
        city_data = cities[cities['name'] == selected_city]
        # Create a folium map centered at the selected city
        folium_map = folium.Map(location=[lat, lon], zoom_start=11)
        # Add a marker for the selected city and selected parameter type
        parameter_data = indicators[indicators['Parameter_Type'] == selected_parameter_type]
        sum=int(city_data[parameter_data['Indicator']].iloc[0].sum())
        folium.Marker([lat, lon], popup=f"{selected_city}  {selected_parameter_type}: {sum}").add_to(folium_map)
        # Add different base layers with attributions
        folium.TileLayer('OpenStreetMap').add_to(folium_map)
        folium.TileLayer('CartoDB Positron', attr='Map tiles by CartoDB, under CartoDB Attribution.').add_to(folium_map)
        folium.TileLayer('CartoDB DarkMatter', attr='Map tiles by CartoDB, under CartoDB Attribution.').add_to(folium_map)
        # Add Google Earth base layer
        folium.TileLayer(tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Earth', name='Google Earth').add_to(folium_map)
        # Add a mini map
        minimap = MiniMap(width=100, height=100)
        folium_map.add_child(minimap)
        # Add fullscreen button
        Fullscreen().add_to(folium_map)
        # Add measure control to the map
        MeasureControl(primary_length_unit='kilometers', primary_area_unit='hectares').add_to(folium_map)
        # Add draw tools
        Draw().add_to(folium_map)
        # Add layer control to the map
        folium.LayerControl().add_to(folium_map)
        
        # Save the map to an HTML file
        folium_map.save("map.html")
        return open('map.html', 'r').read()
    else:
        # Create a folium map centered at Italy
        folium_map = folium.Map(location=[41.8719, 12.5674], zoom_start=4)
        # Add markers for all cities
        # popups should be the city names and population values
        for i in range(len(cities)):
            folium.Marker([cities.iloc[i]['lat'], cities.iloc[i]['lon']], popup=f"{cities.iloc[i]['name']}  Population: {cities.iloc[i]['population']}").add_to(folium_map)
        # Add different base layers with attributions
        folium.TileLayer('OpenStreetMap').add_to(folium_map)
        folium.TileLayer('CartoDB Positron', attr='Map tiles by CartoDB, under CartoDB Attribution.').add_to(folium_map)
        folium.TileLayer('CartoDB DarkMatter', attr='Map tiles by CartoDB, under CartoDB Attribution.').add_to(folium_map)
        # Add Google Earth base layer
        folium.TileLayer(tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}', attr='Google Earth', name='Google Earth').add_to(folium_map)
        # Add a mini map
        minimap = MiniMap(width=100, height=100)
        folium_map.add_child(minimap)
        # Add fullscreen button
        Fullscreen().add_to(folium_map)
        # Add measure control to the map
        MeasureControl(primary_length_unit='kilometers', primary_area_unit='hectares').add_to(folium_map)
        # Add draw tools
        Draw().add_to(folium_map)
        # Add layer control to the map
        folium.LayerControl().add_to(folium_map)
        
        # Save the map to an HTML file
        folium_map.save("map.html")
        return open('map.html', 'r').read()

# Callback to update the download link based on the selected city and olympic_events
@app.callback(
    Output('download1-link', 'href'),
    [Input('city-dropdown', 'value')]
)
def update_download_link(selected_city):
    if selected_city:
        # Get the olympic events data for the selected city
        olympic_events_data = olympic_events[olympic_events['CITY'] == selected_city]
        # Create a CSV file with the selected data
        csv_string = olympic_events_data.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + csv_string
        return csv_string
    else:
        return ""

# Callback to update the download link based on the selected city and parameter type
@app.callback(
    Output('download2-link', 'href'),
    [Input('city-dropdown', 'value'),
     Input('parameter-type-dropdown', 'value')]
)
def update_download_link(selected_city, selected_parameter_type):
    if selected_city and selected_parameter_type:
        # Get the data for the selected city
        city_data = cities[cities['name'] == selected_city]
        # Get the data for the selected parameter type
        parameter_data = indicators[indicators['Parameter_Type'] == selected_parameter_type]
        # Merge the city and parameter data
        data = city_data[parameter_data['Indicator'].tolist()]
        # Merge the data and parameter data
        data = data.T.reset_index()
        data.columns = ['Indicator', 'Value']
        df = data.merge(parameter_data, on='Indicator')
        # Create a CSV file with the selected data
        csv_string = df.to_csv(index=False, encoding='utf-8')
        csv_string = "data:text/csv;charset=utf-8," + csv_string
        return csv_string
    else:
        return ""

# Callback to register new user
@app.callback(
    Output('register-message', 'children'),
    [Input('register-button', 'n_clicks')],
    [Input('new-username-input', 'value'),
     Input('name-input', 'value'),
     Input('last-name-input', 'value'),
     Input('email-input', 'value'),
     Input('new-password-input', 'value')]
)
def register_new_user(n_clicks, new_username, name, last_name, email, new_password):
    if n_clicks:
        if new_username and name and last_name and email and new_password:
            if new_username not in users['username'].values:
                # Send the data to the API endpoint
                response = requests.post("http://localhost:5005/api/user", json={'username': new_username, 'name': name, 'last_name': last_name, 'email': email, 'password': new_password})
                if response.status_code == 200:
                    return html.P("User registered successfully")
                else:
                    return html.P("Error registering user")
            else:
                return html.P("User already exists")
        else:
            return html.P("Please enter all the details to register")
    else:
        return ""
    

# Callback to submit a new report
@app.callback(
    Output('report-message', 'children'),
    [Input('report-button', 'n_clicks')],
    [Input('report-name-input', 'value'),
     Input('report-input', 'value')]
)
def submit_report(n_clicks, report_name, reports):
    if n_clicks:
        if report_name and reports:
            # Send the data to the API endpoint
                response2 = requests.post("http://localhost:5005/api/reports", json={'name': report_name, 'report': reports})
                if response2.status_code == 200:
                    return html.P("Report sent successfully")
                else:
                    return html.P("Error sending the report")            
        else:
            return html.P("Please enter fill all the sections to send a report")
    else:
        return ""
# Run the app
if __name__ == '__main__':
    app.run_server(debug=False, host='127.0.0.1', port=8054)
