from flask import Flask, request, jsonify
from flask_cors import CORS
from chatter import Chatter 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Update CORS to allow requests from both local and deployed frontend
CORS(app, resources={r"/api/*": {
    "origins": [
        "http://localhost:3000",
        "https://rag-flask-frontend.onrender.com"
    ]
}})

# Initialize your Chatter instance
chatter = Chatter()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')
    if not user_input:
        return jsonify({'response': 'No input provided.'}), 400
    response = chatter.chat(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
