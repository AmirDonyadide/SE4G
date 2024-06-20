from flask import Flask, jsonify,request
import psycopg2

app = Flask(__name__)

try:
    # Connect to PostgreSQL database
    conn = psycopg2.connect(
        host="localhost",
        database="SE4G",
        user="postgres",
        password="Amir0440935784"
    )
    cur = conn.cursor()
except psycopg2.Error as e:
    print(f"Error connecting to the database: {e}")
    exit(1)

# API endpoint to fetch details of  cities and geomerty
@app.route('/api/cities', methods=['GET'])
def get_all_cities():
    try:
        cur.execute("SELECT * FROM cities")
        cities = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return jsonify(cities)
    except psycopg2.Error as e:
        return jsonify({'error': f"Error fetching cities: {e}"}), 500

# API endpoint to fetch details of  indicators
@app.route('/api/indicators', methods=['GET'])
def get_all_indicators():
    try:
        cur.execute("SELECT * FROM indicators")
        indicators = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return jsonify(indicators)
    except psycopg2.Error as e:
        return jsonify({'error': f"Error fetching indicators: {e}"}), 500


# API endpoint to fetch details of a specific city
@app.route('/api/city/<uid>', methods=['GET'])
def get_city(uid):
    try:
        cur.execute("SELECT * FROM cities WHERE uid = %s", (uid,))
        city_data = cur.fetchone()
        if city_data:
            # Get column names dynamically
            colnames = [desc[0] for desc in cur.description]
            # Create dictionary using column names and data
            city = dict(zip(colnames, city_data))
            return jsonify(city)
        else:
            return jsonify({'error': 'City not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': f"Error fetching city details: {e}"}), 500

#API endpoint to fetch details of a user by userid
@app.route('/api/user/<uid>', methods=['GET'])
def get_user(uid):
    try:
        cur.execute("SELECT * FROM users WHERE uid = %s", (uid,))
        user_data = cur.fetchone()
        if user_data:
            # Get column names dynamically
            colnames = [desc[0] for desc in cur.description]
            # Create dictionary using column names and data
            user = dict(zip(colnames, user_data))
            return jsonify(user)
        else:
            return jsonify({'error': 'User not found'}), 404
    except psycopg2.Error as e:
        return jsonify({'error': f"Error fetching user details: {e}"}), 500

#API endpoint to fetch details of all users
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        cur.execute("SELECT * FROM users")
        users = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return jsonify(users)
    except psycopg2.Error as e:
        return jsonify({'error': f"Error fetching users: {e}"}), 500
    
#API endpoint to fetch details of all olympic_events by game_id
@app.route('/api/olympic_events/<game_id>', methods=['GET'])
def get_olympic_events(game_id):
    try:
        cur.execute("SELECT * FROM olympic_events WHERE game_id = %s", (game_id,))
        olympic_events = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return jsonify(olympic_events)
    except psycopg2.Error as e:
        return jsonify({'error': f"Error fetching olympic_events: {e}"}), 500

#API endpoint to fetch details of all olympic_events
@app.route('/api/olympic_events', methods=['GET'])
def get_all_olympic_events():
    try:
        cur.execute("SELECT * FROM olympic_events")
        olympic_events = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        return jsonify(olympic_events)
    except psycopg2.Error as e:
        return jsonify({'error': f"Error fetching olympic_events: {e}"}), 500

#API endpoint to send details of new user to the users table
@app.route('/api/user', methods=['POST'])
def add_user():
    try:
        data = request.json
        cur.execute("INSERT INTO users (userid,name,last_name,email,password) VALUES (%s, %s, %s, %s, %s)",
                    (data['userid'], data['name'], data['last_name'], data['email'], data['password']))
        conn.commit()
        return jsonify({'message': 'User added successfully'})
    except psycopg2.Error as e:
        return jsonify({'error': f"Error adding user: {e}"}), 500
    

if __name__ == '__main__':
    try:
        app.run(port=5005,debug=True)
    except Exception as e:
        print(f"An error occurred: {e}")
