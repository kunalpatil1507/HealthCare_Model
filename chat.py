import os
import google.generativeai as genai
from gtts import gTTS
import pygame
import time
from flask import Flask, request, jsonify, send_file
from dotenv import load_dotenv
from io import BytesIO
from function import text_to_speech, speech_to_text  # Import functions from your code
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Configure Google AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction=(
        "You are a compassionate and knowledgeable doctor dedicated to promoting health and well-being. "
        "Your task is to engage in conversations that reflect your medical expertise, offering clear, practical, "
        "and preventive guidance based on the symptoms or concerns shared by the user. Use relatable examples, "
        "scientific reasoning, and evidence-based practices to provide advice that focuses on prevention, lifestyle "
        "improvements, and early interventions. Speak with empathy, clarity, and encouragement, ensuring your "
        "responses are tailored to the user's needs. Emphasize the importance of maintaining a healthy lifestyle, "
        "early recognition of warning signs, and consulting a healthcare professional when necessary. Ask questions "
        "to understand the user's situation better and provide actionable steps to help them prevent potential health issues."
    ),
)
chat_session = model.start_chat(history=[])

# Initialize Flask app
app = Flask(__name__)

# Initial bot message
initial_message = "Hello, how can I help you?"
print(f"Bot: {initial_message}")
text_to_speech(initial_message)

CORS(app, origins=["http://localhost:5173"])

# Flask route to handle text and audio input
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        print(data)
        user_input = data.get('user_input', None)
        audio_data = data.get('audio_input', None)

        if user_input:  # Handle text input
            response = chat_session.send_message(user_input)
            model_response = response.text
        elif audio_data:  # Handle audio input
            user_input = speech_to_text(audio_data)
            response = chat_session.send_message(user_input)
            model_response = response.text
        else:
            return jsonify({"error": "No input provided"}), 400

        # Convert the text response to speech
        audio_output = text_to_speech(model_response)

        # Return both text and audio response
        return jsonify({"text_response": model_response, "audio_response": audio_output}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500

# Helper function to handle text to speech and return as byte stream
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_stream = BytesIO()
    tts.save(audio_stream)
    audio_stream.seek(0)
    return send_file(audio_stream, mimetype='audio/mp3', as_attachment=True, download_name="response.mp3")

# Run the Flask server
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
