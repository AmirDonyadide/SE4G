from flask import Flask, jsonify, request
import psycopg2
import logging
from psycopg2 import sql  

app = Flask(__name__)
# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="SE4G",
            user="postgres",
            password="Amir0440935784"
        )
        return conn
    except psycopg2.Error as e:
        app.logger.error(f"Error connecting to the database: {e}")
        return None

# API endpoint to fetch details of cities and geometry
@app.route('/api/cities', methods=['GET'])
def get_all_cities():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM public."CITY"')
            cities = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(cities)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching cities: {e}")
        return jsonify({'error': f"Error fetching cities: {e}"}), 500
    finally:
        conn.close()

# API endpoint to fetch details of 1 city by name and specific column
@app.route('/api/cities/<string:parameter>/<string:name>', methods=['GET'])
def get_city_by_name_and_parameter(parameter,name):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            cur.execute(sql.SQL('SELECT {} FROM public."CITY" WHERE name = %s').format(sql.Identifier(parameter)), (name,))
            city = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(city)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching city: {e}")
        return jsonify({'error': f"Error fetching city: {e}"}), 500
    finally:
        conn.close()

# API endpoint to fetch details of indicators
@app.route('/api/indicators', methods=['GET'])
def get_all_indicators():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM public."INDICATOR"')
            indicators = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(indicators)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching indicators: {e}")
        return jsonify({'error': f"Error fetching indicators: {e}"}), 500
    finally:
        conn.close()

# API endpoint to fetch details of 1 indicator by name and specific column
@app.route('/api/indicators/<string:parameter>/<string:name>', methods=['GET'])
def get_indicator_by_name_and_parameter(parameter,name):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            query = sql.SQL('SELECT {field} FROM public."INDICATOR" WHERE "Indicator" = %s').format(field=sql.Identifier(parameter))
            cur.execute(query, (name,))
            indicator = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(indicator)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching indicator: {e}")
        return jsonify({'error': f"Error fetching indicator: {e}"}), 500
    finally:
        conn.close()

# API endpoint to fetch details of all users
@app.route('/api/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM public."USER"')
            users = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(users)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching users: {e}")
        return jsonify({'error': f"Error fetching users: {e}"}), 500
    finally:
        conn.close()

# API endpoint to fetch details of 1 user by name and specific column
@app.route('/api/users/<string:parameter>/<string:name>', methods=['GET'])
def get_user_by_name_and_parameter(parameter,name):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            query = sql.SQL('SELECT {field} FROM public."USER" WHERE "username" = %s').format(field=sql.Identifier(parameter))
            cur.execute(query, (name,))
            user = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(user)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching user: {e}")
        return jsonify({'error': f"Error fetching user: {e}"}), 500
    finally:
        conn.close()

# API endpoint to fetch details of all olympic events
@app.route('/api/olympic_events', methods=['GET'])
def get_all_olympic_events():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM public."OLYMPIC_EVENTS"')
            olympic_events = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(olympic_events)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching olympic events: {e}")
        return jsonify({'error': f"Error fetching olympic events: {e}"}), 500
    finally:
        conn.close()

# API endpoint to fetch details of olympic events by city_uid and specific column
@app.route('/api/olympic_events/<string:parameter>/<string:city_uid>', methods=['GET'])
def get_olympic_events_by_city_uid_and_parameter(parameter,city_uid):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        with conn.cursor() as cur:
            query = sql.SQL('SELECT {field} FROM public."OLYMPIC_EVENTS" WHERE "city_uid" = %s').format(field=sql.Identifier(parameter))
            cur.execute(query, (city_uid,))
            olympic_events = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
            return jsonify(olympic_events)
    except psycopg2.Error as e:
        app.logger.error(f"Error fetching olympic events: {e}")
        return jsonify({'error': f"Error fetching olympic events: {e}"}), 500
    finally:
        conn.close()

# API endpoint to send details of new user to the users table
@app.route('/api/user', methods=['POST'])
def add_user():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.json
        with conn.cursor() as cur:
            cur.execute('INSERT INTO public."USER" (username, name, last_name, email, password) VALUES (%s, %s, %s, %s, %s)',
                        (data['username'], data['name'], data['last_name'], data['email'], data['password']))
            conn.commit()
            return jsonify({'message': 'User added successfully'})
    except psycopg2.Error as e:
        app.logger.error(f"Error adding user: {e}")
        return jsonify({'error': f"Error adding user: {e}"}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    try:
        app.run(port=5005, debug=False)
    except Exception as e:
        print(f"An error occurred: {e}")