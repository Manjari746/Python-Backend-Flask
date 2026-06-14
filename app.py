from flask import Flask,jsonify, request
import sqlite3
import hashlib
import os
import dotenv
import functools import wraps

API_TOKEN =os.getenv("API_TOKEN")
app = Flask(__name__)

def require_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if token != f"Bearer{API_TOKEN}":
            return jsonify ({"error":"Unauthorized"}),401
        return f(*args, **kwargs)
    return decorated_function

#updated function to establish connection to database 
def get_db_connection():
    import os
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path= os.path.join(BASE_DIR, "products.db")
    conn= sqlite3.connect(db_path, timeout=60)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/init', methods= ["GET"])
def init_db():
    conn = get_db_connection()
    conn.execute("""
                CREATE TABLE IF NOT EXISTS products(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL
                )
                """)
    # Intialising table users in which users info is stored
    conn.execute("""
                CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE, 
                password TEXT NOT NULL )
                """)
    conn.commit()
    conn.close()
    return jsonify({"message":"database init complete"})

@app.route('/')
def home():
    return jsonify({"message":"Hello, from flask server!"})

# retrieving information from server 
@app.route('/products', methods=["GET"])
def get_products():
    conn = get_db_connection()
    rows = conn.execute("SELECT * FROM products").fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

# sending data back to server 
@app.route('/products', methods = ["POST"])
@require_token
def add_products():
    data = request.get_json() #firstly parsing incoming json 
    name = data.get("name")
    price = data.get("price")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO products (name, price) VALUES(?,?)",(name, price))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    new_product = {
        "id" : new_id,
        "name": name,
        "price": price
    }

    return jsonify({"message": "product has been added!", "product": new_product}) , 201

#  register method - to register the user for the first time
@app.route("/register", methods = ["POST"])
def register():
    data = request.get_json()
    username= data.get("username")
    password= data.get("password")

    if not username or not password:
        return jsonify({"message":"Missing username or password"}),400
    
    # converting normal text password into encrypted password 
    # sha256 is the hashing algo 
    # with the help of this, if someone tries to access the database, they can't see our password
    hashed_password= hashlib.sha256(password.encode()).hexdigest()

    # Inserting the username and hashed_password into database
    try:
        conn = get_db_connection()
        conn.execute("INSERT INTO users(username, password) VALUES(?,?)",(username, hashed_password))
        conn.commit()
        conn.close()
        return jsonify({"message":"User registeration is successful!"})
    
    except sqlite3.IntegrityError:
        return jsonify({"error":"username is already exists"}),409
    
# login method - to login the user if it already exists
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password= data.get("password")

    if not username or not password:
        return jsonify({"error":"Missing username or password"})
    
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users where username = ? and password = ?",(username, hashed_password)).fetchone()
    conn.close()

    if user: 
        return jsonify({"message":f"Welcome, {username}!"})
    else :
        return jsonify({"error": "Invalid credentials"}),401
    
if __name__ == "__main__":
    # Automatically initialize the database whenever run the flask app
    with app.app_context(): 
        init_db()
    app.run(debug=True)