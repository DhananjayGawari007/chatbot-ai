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
genai.configure(api_key=api_key)

# --- DEBUG: LIST MODELS ---
# This will print every model your key can see into the Render logs
try:
    print("Listing available models for this key:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"AVAILABLE MODEL: {m.name}")
except Exception as e:
    print(f"COULD NOT LIST MODELS: {e}")

# 2. Use the FULL PATH for the model name
# 'models/gemini-1.5-flash' is the most compatible path
model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"reply": "Empty message."}), 400

        # Simple prompt
        response = model.generate_content(user_message)
        
        if response.text:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "I'm sorry, I couldn't process that wellness query."})

    except Exception as e:
        print(f"DETAILED ERROR: {e}")
        return jsonify({"reply": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
