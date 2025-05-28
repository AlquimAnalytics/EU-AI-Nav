from flask import Flask, request, jsonify
from flask_cors import CORS
from chatter import Chatter 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get frontend URL from environment variable or use default
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:3000')

# Configure CORS with specific origin
CORS(app, resources={r"/api/*": {"origins": [FRONTEND_URL, "http://localhost:3000"]}})

# Initialize your Chatter instance
chatter = Chatter()

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('message')
    if not user_input:
        return jsonify({'response': 'No input provided.'}), 400
    response = chatter.chat(user_input)
    app.logger.info(f'API URL: {request.url}')
    app.logger.info(f'Request: {data}')
    app.logger.info(f'Response: {response}')
    return jsonify({'response': response})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
