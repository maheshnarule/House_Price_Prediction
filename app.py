from flask import Flask, request, render_template, redirect, url_for, session, flash
import mysql.connector
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Config
db_config = {
    "host": "sql103.infinityfree.com",
    "user": "if0_39578571",
    "password": "8i6iiQDXcRAfktw",
    "database": "if0_39578571_mycompany"
}

def get_connection():
    return mysql.connector.connect(**db_config)

# Load Model & Data
model = pickle.load(open("model.pkl", "rb"))
data = pd.read_csv("house_clean (1).csv")
X_columns = list(model.feature_names_in_)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            flash("User already exists. Please login.", "error")
            return redirect(url_for('login'))

        cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Account created! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user:
            session['logged_in'] = True
            session['email'] = email
            return redirect(url_for('predict_form'))
        else:
            flash("Invalid email or password", "error")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/predict_form')
def predict_form():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    location_list = sorted(data['location'].unique())
    return render_template('predict.html', locations=location_list)

@app.route('/predict', methods=['POST'])
def predict():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    try:
        sqft = float(request.form['sqft'])
        bath = int(request.form['bath'])
        bhk = int(request.form['bhk'])
        location = request.form['location']

        x = np.zeros(len(X_columns))
        x[X_columns.index('total_sqft')] = sqft
        x[X_columns.index('bath')] = bath
        x[X_columns.index('bhk')] = bhk
        if location in X_columns:
            x[X_columns.index(location)] = 1

        price = model.predict([x])[0]
        price = round(price, 2)
        return render_template('predict.html',
                               prediction_text=f"💰 Predicted Price: ₹ {price} Lakhs",
                               locations=sorted(data['location'].unique()))
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
