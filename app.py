import os
import google.generativeai as genai
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- DEBUG: CHECK IF KEY IS LOADED ---
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("CRITICAL ERROR: GEMINI_API_KEY not found in environment variables!")
else:
    print("SUCCESS: Gemini API Key loaded.")

genai.configure(api_key=api_key)

# Configure the model with safety settings set to 'BLOCK_NONE' 
# so wellness advice isn't accidentally censored
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    generation_config={
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1000,
    }
)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"reply": "I didn't receive a message."}), 400

        # Create a more structured prompt for Gemini
        prompt = (
            "You are CareNest AI, a helpful Health and Wellness assistant. "
            "Provide supportive and friendly wellness advice. "
            "If the user asks something dangerous, tell them to see a doctor. "
            f"User Question: {user_message}"
        )
        
        response = model.generate_content(prompt)
        
        # Check if response has text (Gemini can return empty if blocked)
        if response.text:
            return jsonify({"reply": response.text})
        else:
            return jsonify({"reply": "I'm sorry, I cannot answer that specifically. How else can I help?"})

    except Exception as e:
        # This will show the real error in your Render Logs tab
        print(f"DETAILED ERROR: {e}")
        return jsonify({"reply": f"Connection Error: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
