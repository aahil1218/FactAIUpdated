from flask import Flask, request, jsonify
import pickle
from flask_cors import CORS # Needed to allow the Chrome extension to connect
import os

app = Flask(__name__)
# Allow cross-origin requests from the Chrome extension
CORS(app) 

# --- Model Loading ---
try:
    with open('ai_detector_model.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('tfidf_vectorizer.pkl', 'rb') as f:
        vectorizer = pickle.load(f)
    print("Model and vectorizer loaded successfully.")
except FileNotFoundError:
    print("FATAL ERROR: Model files not found. Run ai_detector_trainer.py first.")
    exit()

@app.route('/api/detect-ai', methods=['POST'])
def detect_ai():
    data = request.json
    text = data.get('text', '')

    if not text or len(text) < 50:
        return jsonify({"error": "Text too short or missing"}), 400

    try:
        # 1. Vectorize the input text
        text_vectorized = vectorizer.transform([text])

        # 2. Predict the probability
        probabilities = model.predict_proba(text_vectorized)[0]
        ai_score = probabilities[1] * 100 
        human_score = probabilities[0] * 100

        # Mock suggestion logic (since our custom model doesn't generate them)
        let_suggestions = []
        if ai_score > 70:
            let_suggestions = ["Try rephrasing with personal anecdotes.", "Break up long sentences.", "Inject more emotional language."];
        elif ai_score > 40:
            let_suggestions = ["Check for formal vocabulary usage.", "Vary sentence structure."];
        else:
            let_suggestions = ["Looks great! Score is low AI risk."];


        return jsonify({
            "ai_score": ai_score,
            "human_score": human_score,
            "suggestions": let_suggestions
        })
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {e}"}), 500

if __name__ == '__main__':
    # Running on 127.0.0.1 (localhost) on port 5000
    app.run(debug=True, host='127.0.0.1', port=5000)