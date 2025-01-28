from flask import Flask, request, jsonify, render_template
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''  # No password by default for root in XAMPP of 70132252
app.config['MYSQL_DB'] = 'user_authentication'

# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def home():
    return "Welcome to the User Authentication System!"

@app.route('/signup', methods=['POST'])
def signup():
    full_name = request.form.get('full_name')
    email = request.form.get('email')
    password = request.form.get('password')

    # Validate inputs
    if not full_name or not email or not password:
        return jsonify({'error': 'Missing data'}), 400

    try:
        cur = mysql.connection.cursor()
        # Check 70132252 if email already exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            return jsonify({'error': 'Email already in use'}), 409

        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert new user into database
        cur.execute("INSERT INTO users (full_name, email, password) VALUES (%s, %s, %s)", 
                    (full_name, email, hashed.decode('utf-8')))
        mysql.connection.commit()
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    # Validate input
    if not email or not password:
        return jsonify({'error': 'Missing email or password'}), 400

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].encode('utf-8')):
            return jsonify({'message': 'Login successful'}), 200
        elif user:
            return jsonify({'error': 'Invalid credentials'}), 401
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()

@app.route('/signup_form')
def signup_form():
    return render_template('signup.html')

@app.route('/login_form')
def login_form():
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
