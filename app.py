import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# 1. Setup API Key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("CRITICAL: No API Key found! Check Render Environment Variables.")
else:
    genai.configure(api_key=api_key)

# 2. SELF-HEALING MODEL SELECTION
# This function finds the best available model for your specific key
def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        print(f"DEBUG: Your key has access to: {available_models}")
        
        # Priority list: Try 1.5 Flash, then 1.5 Pro, then old Pro
        for preference in ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']:
            if preference in available_models:
                print(f"DEBUG: Selecting {preference}")
                return genai.GenerativeModel(model_name=preference)
        
        # If none of the above, pick the first one available
        if available_models:
            print(f"DEBUG: Falling back to {available_models[0]}")
            return genai.GenerativeModel(model_name=available_models[0])
    except Exception as e:
        print(f"DEBUG: Error listing models: {e}")
    return None

model = get_working_model()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global model
    try:
        # Re-try model initialization if it failed at startup
        if model is None:
            model = get_working_model()
            if model is None:
                return jsonify({"reply": "API Key Error: No models available."}), 500

        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"reply": "No message received."}), 400

        # Simple prompt
        response = model.generate_content(user_message)
        
        return jsonify({"reply": response.text})

    except Exception as e:
        print(f"DETAILED ERROR: {e}")
        return jsonify({"reply": f"Sorry, I'm having trouble: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
