from functions import * # type: ignore
import geopandas as gpd
import pandas as pd
import os
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from geoalchemy2 import Geometry
from geopy.geocoders import Nominatim
from time import sleep

# Set the working directory to ensure relative paths work correctly
os.chdir('/Users/amirdonyadide/Desktop/SE4G')

try:
    # Load shapefiles
    comune_df= load_shapefile('data/shape_files/Comune/Com01012024_g_WGS84.shp')
    # Notify successful loading of shapefiles
    print("Shapefiles loaded successfully.")
except FileNotFoundError as e:
    # Handle file not found error
    print(f"Error loading shapefiles: {e}")
    raise
except Exception as e:
    # Handle other exceptions
    print(f"An error occurred while loading shapefiles: {e}")
    raise

# Read Excel file into a DataFrame
try:
    olympic_events_df = pd.read_excel('data/olympic_events.xlsx', header=0)
    # Convert 'game_id' column to integer type
    olympic_events_df['fid'] = olympic_events_df['fid'].astype(int)
except FileNotFoundError as e:
    # Handle file not found error
    print(f"Error loading Excel file: {e}")
    raise
except Exception as e:
    # Handle other exceptions
    print(f"An error occurred while loading Excel file: {e}")
    raise

try:
    users_df = pd.read_excel('data/users.xlsx', header=0)
    # Convert all columns to string type
    users_df = users_df.astype(str)
except FileNotFoundError as e:
    # Handle file not found error
    print(f"Error loading Excel file: {e}")
    raise
except Exception as e:
    # Handle other exceptions
    print(f"An error occurred while loading Excel file: {e}")
    raise

# Read Csv file into a DataFrame
try:
    indicators_translation = pd.read_csv('data/selected_indicators.csv', header=None)
    indicators_translation.columns = ['Indicator', 'Translation']
except FileNotFoundError as e:
    # Handle file not found error
    print(f"Error loading Csv file: {e}")
    raise
except Exception as e:
    # Handle other exceptions
    print(f"An error occurred while loading Csv file: {e}")
    raise


# Assign new columns using the defined functions
indicators_translation['Risk_Type'] = indicators_translation['Translation'].apply(extract_risk_type)
indicators_translation['Parameter_Type'] = indicators_translation['Translation'].apply(extract_parameter_type)
# Specify indicators
indicators = indicators_translation['Indicator'].tolist()


try:
    # Read the CSV file as a single string
    with open('data/target_cities.csv', 'r') as file:
        cities_str = file.read()
except FileNotFoundError as e:
    # Handle file not found error
    print(f"Error loading CSV file: {e}")
    raise

# Split the string by commas to get a list of cities
target_cities = [city.strip() for city in cities_str.split(',')]

# Initialize geolocator
geolocator = Nominatim(user_agent="city_geocoder")

# List to store city coordinates
city_coordinates = []

# Loop through each city and get its coordinates
for city in target_cities:
    try:
        location = geolocator.geocode(city + ", Italy")
        if location:
            city_coordinates.append((city, location.latitude, location.longitude))
        else:
            city_coordinates.append((city, None, None))
    except Exception as e:
        city_coordinates.append((city, None, None))
        print(f"Error geocoding {city}: {e}")
    sleep(1)  # Sleep to avoid overwhelming the geocoding service

# Create a DataFrame
cities_latlon_df = pd.DataFrame(city_coordinates, columns=['name', 'lat', 'lon'])

# Specify primary data columns
primary_data = ['uid', 'nome']
try:
    # Filter the comune shapefile for the target cities
    target_cities_shapefile = comune_df[comune_df['COMUNE'].isin(target_cities)]
    target_cities_shapefile = target_cities_shapefile[['COD_RIP', 'COD_REG', 'COD_PROV', 'COMUNE', 'geometry']]
    target_cities_shapefile.columns = ['cod_rip', 'cod_reg', 'cod_prov', 'nome', 'geometry']
    target_cities_shapefile = target_cities_shapefile.set_geometry('geometry')
    print("Filtered shapefile created successfully.")
    
    # Fetch data from the API for each city and combine it
    api_data_collection = []
    for _, row in target_cities_shapefile.iterrows():
        # Fetch data from the API based on the current row's cod_rip, cod_reg, and cod_prov
        city_data_from_api = fetch_api_data(row['cod_rip'], row['cod_reg'], row['cod_prov'])
        if not city_data_from_api.empty:
            api_data_collection.append(city_data_from_api)

    # Combine all API data into a single DataFrame
    combined_api_data = pd.concat(api_data_collection, ignore_index=True) if api_data_collection else pd.DataFrame()
    print("API data fetched and combined successfully.")

    # Merge the shapefile with the API data
    city_data_with_api = target_cities_shapefile.merge(
        combined_api_data[['cod_rip', 'cod_reg', 'cod_prov', 'nome', 'uid']],
        on=['cod_rip', 'cod_reg', 'cod_prov', 'nome'],
        how='left'
    )
    city_data_with_api = city_data_with_api.drop_duplicates(subset=['uid', 'nome', 'cod_rip', 'cod_reg', 'cod_prov']).reset_index(drop=True)

    # Ensure dtype of columns
    city_data_with_api[['cod_rip', 'cod_reg', 'cod_prov']] = city_data_with_api[['cod_rip', 'cod_reg', 'cod_prov']].astype('int64')
    print("Data preprocessing completed successfully.")

    # Check if 'uid' column exists and if it's unique
    if 'uid' not in city_data_with_api.columns:
        raise ValueError("Error: 'uid' column is missing in the DataFrame.")

    if not city_data_with_api['uid'].is_unique:
        raise ValueError("Error: 'uid' column contains non-unique values.")
    
    # Extract uids and download data for each uid
    city_dataframes = []
    uids_list = extract_uids(city_data_with_api)

    for uid in uids_list:
        # Fetch additional data for each uid
        data_by_uid = get_data_by_uid(uid)
        city_dataframes.append(data_by_uid)

    # Merge all DataFrames into a single DataFrame
    final_city_data = merge_dataframes(city_dataframes)
    # Drop unnecessary columns
    final_city_data.drop(columns=['osmid', 'breadcrumb', 'extent', 'cod_rip', 'cod_reg', 'cod_prov', 'pro_com'], inplace=True)

    # Explicitly set dtype for each column
    column_dtype_mapping = {'nome': str, 'uid': int}

    # Find the geometry column dynamically
    geometry_column = final_city_data.select_dtypes(include=['geometry']).columns
    if len(geometry_column) > 0:
        column_dtype_mapping[geometry_column[0]] = 'geometry'

    # Set other columns to float
    for col in final_city_data.columns:
        if col not in column_dtype_mapping:
            column_dtype_mapping[col] = float

    final_city_data = final_city_data.astype(column_dtype_mapping)

    # Filter the merged DataFrame
    filtered_city_data = final_city_data[primary_data + indicators]

    # Final merge with the geographical data
    final_city_dataset = pd.merge(
        filtered_city_data,
        city_data_with_api,
        on=['uid', 'nome'],
        how='inner'  
    )
    # Reorder the DataFrame
    columns_list = final_city_dataset.columns.tolist()
    reordered_columns = columns_list[-4:] + columns_list[:-4]
    final_city_dataset = final_city_dataset[reordered_columns]
    # Convert to GeoDataFrame
    final_city_gdf = gpd.GeoDataFrame(final_city_dataset, geometry='geometry')
    # Rename the column 'nome' to 'name'
    final_city_gdf = final_city_gdf.rename(columns={'nome': 'name'})
    #add lat and lon columns
    final_city_gdf = final_city_gdf.merge(cities_latlon_df, on='name', how='inner')

    print("Data processing and integration completed successfully.")

except ValueError as ve:
    print("ValueError:", ve)

except Exception as e:
    print("An error occurred:", e)

# Database connection
try:
    # Establish a connection to the PostgreSQL database using the provided URL
    db_url = 'postgresql://postgres:Amir0440935784@localhost:5432/SE4G'
    engine = create_engine(db_url)
    con = engine.connect()
except SQLAlchemyError as e:
    # Notify if an error occurs during the database connection
    print(f"Error connecting to the database: {e}")
    # Exit the program or handle the error appropriately

# Removing existing tables

try:
    # Reflect all tables existing in the database
    metadata = MetaData()
    metadata.reflect(bind=engine)

    # Define a list of tables related to PostGIS that should not be dropped
    postgis_tables = ['spatial_ref_sys', 'geometry_columns']  # Add more if necessary

    # Drop each table except those related to PostGIS
    for table_name in metadata.tables.keys():
        if table_name not in postgis_tables:
            table = Table(table_name, metadata, autoload=True, autoload_with=engine)
            table.drop(engine)

    # Notify when all non-PostGIS tables are successfully dropped
    print("All non-PostGIS tables dropped from the database.")
except SQLAlchemyError as e:
    # Notify if an error occurs during table dropping
    print(f"An error occurred while dropping tables from the database: {e}")
    # Exit the program or handle the error appropriately

# Insert processed city data into the database

try:
    # Insert the processed city geographical data into the 'cities' table, replacing existing data if any
    final_city_gdf.to_postgis('CITY', engine, if_exists='replace', index=False, dtype={'geometry': Geometry('POLYGON', srid='4326')})
    print("Final City Data inserted into the database successfully.")
except SQLAlchemyError as e:
    # Notify if an error occurs during city data insertion
    print(f"An error occurred while inserting city data into the database: {e}")
    # Exit the program or handle the error appropriately

# Insert processed Olympic events data into the database

try:
    # Insert the processed Olympic events data into the 'olympic_events_df' table, replacing existing data if any
    olympic_events_df.to_sql('OLYMPIC_EVENTS', con, if_exists='replace', index=False)
    print("Olympic Events Data inserted into the database successfully.")
except SQLAlchemyError as e:
    # Notify if an error occurs during Olympic events data insertion
    print(f"An error occurred while inserting Olympic events data into the database: {e}")
    # Exit the program or handle the error appropriately

try:
    # Insert the processed Olympic events data into the 'olympic_events_df' table, replacing existing data if any
    users_df.to_sql('USER', con, if_exists='replace', index=False)
    print("USER Data inserted into the database successfully.")
except SQLAlchemyError as e:
    # Notify if an error occurs during Olympic events data insertion
    print(f"An error occurred while inserting Users data into the database: {e}")
    # Exit the program or handle the error appropriately

try:
    # Insert the processed Olympic events data into the 'olympic_events_df' table, replacing existing data if any
    indicators_translation.to_sql('INDICATOR', con, if_exists='replace', index=False)
    print("indicators Data inserted into the database successfully.")
except SQLAlchemyError as e:
    # Notify if an error occurs during Olympic events data insertion
    print(f"An error occurred while inserting Indicators data into the database: {e}")
    # Exit the program or handle the error appropriately

finally:
    # Close the database connection
    try:
        con.close()
        # Notify when the database connection is closed
        print("Database connection closed.")
    except NameError:
        pass  # con variable not defined, meaning the connection wasn't established, so no need to close it