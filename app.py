# app.py

from flask import Flask, request, jsonify
import pandas as pd
import joblib
from feature_extraction import extract_features

app = Flask(__name__)
model = joblib.load("model.pkl")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    if not data or 'url' not in data:
        return jsonify({"error": "Missing URL in request"}), 400

    url = data['url']
    try:
        features = extract_features(url)
        df = pd.DataFrame([features])
        prediction = model.predict(df)[0]
        result = "phishing" if prediction == 1 else "legitimate"
        return jsonify({"url": url, "prediction": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
