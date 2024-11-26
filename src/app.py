from flask import Flask, request, jsonify
from logging_config import setup_logging
import mysql.connector
from mysql.connector import Error
import json
import os

app = Flask(__name__)

# Set the environment: 'development', 'production'
#app.config['ENV'] = 'production'  # Change to 'production' in production mode

# Load configuration from config.json
def load_config():
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config

# Set up configuration
config = load_config()
app.config['DB_HOST'] = config['db']['host']
app.config['DB_DATABASE'] = config['db']['database']
app.config['DB_USER'] = config['db']['user']
app.config['DB_PASSWORD'] = config['db']['password']
#app.config['ENV'] = config['env']

# Load environment-specific settings
ENV = os.getenv("FLASK_ENV", "development")
app.config["ENV"] = ENV

# Setup logging
setup_logging(app)

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['DB_HOST'],
            database=app.config['DB_DATABASE'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASSWORD']
        )
        return connection
    except Error as e:
        app.logger.error(f"Error connecting to MySQL: {e}")
        return None

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    hkid = data.get('hkid')  # Accept the HKID field

    if not name or not email or not hkid:
        app.logger.warning("Missing required fields: name, email, or hkid")
        return jsonify({'error': 'Name, email, and HKID are required'}), 400

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "INSERT INTO users (name, email, hkid) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, hkid))
            connection.commit()
            app.logger.info(f"User {name} created successfully with email {email} and HKID {hkid}")
            return jsonify({'message': 'User created successfully'}), 201
        except mysql.connector.IntegrityError as e:
            # Handle duplicate HKID error
            if "Duplicate entry" in str(e):
                app.logger.error(f"Duplicate HKID error: {hkid} already exists")
                return jsonify({'error': 'HKID must be unique'}), 400
            app.logger.error(f"Database error: {e}")
            return jsonify({'error': str(e)}), 500
        except Error as e:
            app.logger.error(f"Database connection error: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            connection.close()

@app.route('/users', methods=['GET'])
def read_users():
    """Retrieve all users."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, name, email, hkid FROM users"
            cursor.execute(query)
            users = cursor.fetchall()
            app.logger.info(f"Retrieved {len(users)} users from the database")
            # Use jsonify and pretty print the JSON with indent=4
            response = jsonify(users)
            response.status_code = 200
            response.data = json.dumps(users, indent=4)  # Add pretty formatting
            return response
            #return jsonify(users), 200
        except Error as e:
            app.logger.error(f"Database read error: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            connection.close()

@app.route('/users/<int:user_id>', methods=['GET'])
def read_user(user_id):
    """Retrieve a single user by ID."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT id, name, email, hkid FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            user = cursor.fetchone()
            if user:
                app.logger.info(f"Retrieved user {user_id}: {user['name']}")
                return jsonify(user), 200
            else:
                app.logger.warning(f"User with ID {user_id} not found")
                return jsonify({'error': 'User not found'}), 404
        except Error as e:
            app.logger.error(f"Database read error: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            connection.close()

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user details."""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    hkid = data.get('hkid')  # Accept the HKID field

    if not name or not email or not hkid:
        app.logger.warning(f"Missing required fields for updating user {user_id}: name, email, or hkid")
        return jsonify({'error': 'Name, email, and HKID are required'}), 400

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "UPDATE users SET name = %s, email = %s, hkid = %s WHERE id = %s"
            cursor.execute(query, (name, email, hkid, user_id))
            connection.commit()
            if cursor.rowcount == 0:
                app.logger.warning(f"User with ID {user_id} not found for update")
                return jsonify({'error': 'User not found'}), 404
            app.logger.info(f"User {user_id} updated successfully: {name}")
            return jsonify({'message': 'User updated successfully'}), 200
        except mysql.connector.IntegrityError as e:
            if "Duplicate entry" in str(e):
                app.logger.error(f"Duplicate HKID error during update: {hkid} already exists")
                return jsonify({'error': 'HKID must be unique'}), 400
            app.logger.error(f"Database error during update: {e}")
            return jsonify({'error': str(e)}), 500
        except Error as e:
            app.logger.error(f"Database connection error during update: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            connection.close()

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user by ID."""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            connection.commit()
            if cursor.rowcount == 0:
                app.logger.warning(f"User with ID {user_id} not found for deletion")
                return jsonify({'error': 'User not found'}), 404
            app.logger.info(f"User with ID {user_id} deleted successfully")
            return jsonify({'message': 'User deleted successfully'}), 200
        except Error as e:
            app.logger.error(f"Database deletion error: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            connection.close()

if __name__ == '__main__':
    # Ensure app runs in debug mode for development, and in production mode otherwise
    app.run(debug=(app.config['ENV'] == 'development'))
