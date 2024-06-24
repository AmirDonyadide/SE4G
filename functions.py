import geopandas as gpd
import pandas as pd
import requests
import pyproj

# Function to load shapefiles
def load_shapefile(file_path):
    try:
        # Read shapefiles into a list of GeoDataFrames
        return gpd.read_file(file_path)
    except FileNotFoundError as e:
        # Handle file not found error
        print(f"Error loading shapefiles: {e}")
        raise
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred while loading shapefiles: {e}")
        raise

# Download data for each uid
def get_data_by_uid(uid):
    try:
        # Construct the API request URL
        api_url = f'https://test.idrogeo.isprambiente.it/api/pir/comuni/{uid}'

        # Fetch data from the API
        response = requests.get(api_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Convert the response JSON data into a Python dictionary
            data = response.json()

            # Convert the dictionary into a Pandas DataFrame
            df = pd.json_normalize(data)

            # Return the DataFrame
            return df
        else:
            # Print an error message and return None
            print("Failed to fetch data from the API. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        # Handle request exceptions
        print(f"An error occurred while making the API request: {e}")
        return None
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred while processing the data: {e}")
        return None

def merge_dataframes(dataframes):
    try:
        # Check if the list of DataFrames is not empty
        if dataframes:
            # Merge DataFrames using pandas concat function
            merged_df = pd.concat(dataframes, ignore_index=True)
            return merged_df
        else:
            # If the list is empty, return an empty DataFrame
            return pd.DataFrame()
    except Exception as e:
        # Handle exceptions during merging
        print(f"An error occurred while merging dataframes: {e}")
        return pd.DataFrame()

def fetch_api_data(rip, reg, prov):
    try:
        # Construct the API request URL
        api_url = f'https://test.idrogeo.isprambiente.it/api/pir/comuni?cod_rip={rip}&cod_reg={reg}&cod_prov={prov}'

        # Fetch data from the API
        response = requests.get(api_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Convert the response JSON data into a Python dictionary
            data = response.json()

            # Convert the dictionary into a Pandas DataFrame
            df = pd.json_normalize(data)

            # Return the DataFrame
            return df
        else:
            # Print an error message and return None
            print("Failed to fetch data from the API. Status code:", response.status_code)
            return None
    except requests.RequestException as e:
        # Handle request exceptions
        print(f"An error occurred while making the API request: {e}")
        return None
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred while processing the data: {e}")
        return None

def extract_uids(df):
    try:
        # Extract 'uid' column from DataFrame and convert to list
        uids_list = df['uid'].tolist()
        return uids_list
    except KeyError as e:
        # Handle key error if 'uid' column is missing
        print(f"The DataFrame does not contain the 'uid' column: {e}")
        return []
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred while extracting UIDs: {e}")
        return []

def download_data_as_dataframe(endpoint_url, timeout=10):
    """
    Download data from an API endpoint and convert it to a pandas DataFrame.

    Args:
        endpoint_url (str): The URL of the API endpoint.
        timeout (int, optional): Timeout for the HTTP request in seconds (default: 10).

    Returns:
        pandas.DataFrame: DataFrame containing the downloaded data, or None if an error occurs.
    """
    try:
        # Send a GET request to the endpoint with a timeout
        response = requests.get(endpoint_url, timeout=timeout)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Convert JSON response to DataFrame
        data = response.json()
        df = pd.DataFrame(data)

        return df

    except requests.exceptions.RequestException as e:
        # Log the error
        print(f"Error downloading data from {endpoint_url}: {e}")
        return None

# Define function to extract risk type from description
def extract_risk_type(description):
    try:
        if 'landslide' in description.lower():
            return 'landslide'
        elif 'flood' in description.lower():
            return 'flood'
        else:
            raise ValueError("No valid risk type found in description.")
    except Exception as e:
        print(f"Error extracting risk type: {e}")
        return None

# Define function to extract parameter type from description
def extract_parameter_type(description):
    try:
        if 'surface area' in description.lower():
            return 'surface area'
        elif 'population' in description.lower():
            return 'population'
        elif 'building' in description.lower():
            return 'building'
        elif 'local business units' in description.lower():
            return 'local business units'
        elif 'cultural heritage' in description.lower():
            return 'cultural heritage'
        elif 'families' in description.lower():
            return 'families'
        else:
            raise ValueError("No valid parameter type found in description.")
    except Exception as e:
        print(f"Error extracting parameter type: {e}")
        return None

# Define function to extract units from description
def extract_units(description):
    try:
        if '(km2)' in description.lower():
            return 'km2'
        elif '(no. of inhabitants)' in description.lower():
            return 'no. of inhabitants'
        elif '(n.)' in description.lower():
            return 'n.'
        else:
            raise ValueError("No valid units found in description.")
    except Exception as e:
        print(f"Error extracting units: {e}")
        return None

def utm_to_latlon(easting, northing, zone_number=32, zone_letter='N'):
    proj = pyproj.Proj(proj='utm', zone=zone_number, ellps='WGS84', datum='WGS84')
    lon, lat = proj(easting, northing, inverse=True)
    return lat, lon
