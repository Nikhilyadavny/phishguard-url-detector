from flask import Flask, render_template, request, jsonify
import pickle

app = Flask(__name__)

# Load model
with open("phishing.pkl", "rb") as file:
    model = pickle.load(file)

# Load CountVectorizer
with open("vectorizer.pkl", "rb") as file:
    cv = pickle.load(file)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():

    try:
        # Get data from frontend
        data = request.get_json()

        if not data or "url" not in data:
            return jsonify({
                "error": "No URL provided"
            }), 400

        url = data["url"].strip()

        if not url:
            return jsonify({
                "error": "Please enter a URL"
            }), 400

        # Convert URL using the SAME vectorizer
        url_vector = cv.transform([url])

        # Make prediction
        prediction = model.predict(url_vector)[0]

        # Display model output in terminal
        print("URL:", url)
        print("MODEL PREDICTION:", prediction)

        # Your model uses Bad / Good
        if str(prediction).lower() == "bad":
            result = "PHISHING"
            safe = False
        else:
            result = "SAFE"
            safe = True

        # Confidence
        confidence = None

        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(url_vector)[0]
            confidence = round(float(max(probabilities)) * 100, 2)

        return jsonify({
            "result": result,
            "safe": safe,
            "confidence": confidence,
            "url": url
        })

    except Exception as e:

        print("ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)