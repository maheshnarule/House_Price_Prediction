from flask import Flask, request, render_template
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# Load model and data
model = pickle.load(open("model.pkl", "rb"))
#data = pd.read_csv("C:/House/house_clean (1).csv")  # raw string for Windows paths

# Extract feature columns
X_columns = list(model.feature_names_in_)
locations = [col for col in X_columns if col not in ['total_sqft', 'bath', 'bhk']]

# # Landing page with carousel
# @app.route('/')
# def home():
#     return render_template('index.html')

# Prediction form page
@app.route('/predict_form')
def predict_form():
    location_list = sorted(data['location'].unique())
    return render_template('predict.html', locations=location_list)

# Prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        sqft = float(request.form['sqft'])
        bath = int(request.form['bath'])
        bhk = int(request.form['bhk'])
        location = request.form['location']

        # Create feature array
        x = np.zeros(len(X_columns))
        x[X_columns.index('total_sqft')] = sqft
        x[X_columns.index('bath')] = bath
        x[X_columns.index('bhk')] = bhk
        if location in X_columns:
            x[X_columns.index(location)] = 1

        # Predict
        price = model.predict([x])[0]
        price = round(price, 2)

        # Render prediction page with result
        return render_template('predict.html',
                               prediction_text=f"💰 Predicted Price: ₹ {price} Lakhs",
                               locations=sorted(data['location'].unique()))
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    app.run(debug=True)
