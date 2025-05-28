from flask import Flask, request, jsonify
from flask_cors import CORS
from chatter import Chatter 
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow all origins during debugging
CORS(app, resources={r"/api/*": {
    "origins": "*",  # Allow all origins temporarily
    "methods": ["POST", "OPTIONS", "GET"],
    "allow_headers": ["Content-Type", "Authorization"],
    "expose_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}})

# Initialize your Chatter instance
chatter = Chatter()

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        app.logger.info(f'Received request data: {data}')
        
        user_input = data.get('message')
        if not user_input:
            return jsonify({'response': 'No input provided.'}), 400
            
        response = chatter.chat(user_input)
        app.logger.info(f'Generated response: {response}')
        
        return jsonify({'response': response})
    except Exception as e:
        app.logger.error(f'Error in chat endpoint: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
