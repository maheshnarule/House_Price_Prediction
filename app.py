from flask import Flask, request, render_template, redirect, url_for, session
import mysql.connector
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for sessions

# =======================
# MySQL Database Connection
# =======================
conn = mysql.connector.connect(
    host="mysql-maheshproject.alwaysdata.net",
    user="425294",         # your MySQL username
    password="Mahesh@123",  # your MySQL password
    database="maheshproject_qst"
)
cursor = conn.cursor(dictionary=True)

# =======================
# Load ML Model & Data
# =======================
model = pickle.load(open("model.pkl", "rb"))
data = pd.read_csv("house_clean (1).csv")
X_columns = list(model.feature_names_in_)
locations = [col for col in X_columns if col not in ['total_sqft', 'bath', 'bhk']]

# =======================
# Routes
# =======================

# Landing Page
@app.route('/')
def home():
    return render_template('index.html')

#sign up
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Check if email already exists
        cursor.execute("SELECT * FROM users1 WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            flash("User already exists. Please login.")
            cursor.close()
            conn.close()
            return redirect(url_for('login'))

        # Insert new user
        cursor.execute("INSERT INTO users1 (name, email, password) VALUES (%s, %s, %s)",
                       (name, email, password))
        conn.commit()

        cursor.close()
        conn.close()

        flash("Registration successful! Please login.")
        return redirect(url_for('login'))

    return render_template('signup.html')


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor.execute("SELECT * FROM users1 WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()

        if user:
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('predict_form'))
        else:
            return render_template('login.html', error="Invalid email or password")

    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Prediction Form Page (Protected)
@app.route('/predict_form')
def predict_form():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    location_list = sorted(data['location'].unique())
    return render_template('predict.html', locations=location_list)

# Prediction Endpoint (Protected)
@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        sqft = float(request.form['sqft'])
        bath = int(request.form['bath'])
        bhk = int(request.form['bhk'])
        location = request.form['location']

        # Prepare input
        x = np.zeros(len(X_columns))
        x[X_columns.index('total_sqft')] = sqft
        x[X_columns.index('bath')] = bath
        x[X_columns.index('bhk')] = bhk
        if location in X_columns:
            x[X_columns.index(location)] = 1

        # Predict
        price = model.predict([x])[0]
        price = round(price, 2)
        return render_template('predict.html',
                               prediction_text=f"💰 Predicted Price: ₹ {price} Lakhs",
                               locations=sorted(data['location'].unique()))
    except Exception as e:
        return str(e)

# =======================
# Main
# =======================
if __name__ == "__main__":
    app.run(debug=True)
