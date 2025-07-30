from flask import Flask, request, jsonify
from flask_cors import CORS
from chatter import Chatter 
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure CORS for production
CORS(app, resources={r"/api/*": {
    "origins": [
        "https://rag-flask-frontend.onrender.com",
        "http://localhost:3000",  # For local development
        "*"  # Allow all origins for debugging
    ],
    "methods": ["POST", "OPTIONS", "GET", "HEAD"],
    "allow_headers": ["Content-Type", "Authorization", "Accept"],
    "expose_headers": ["Content-Type", "Authorization"],
    "supports_credentials": False
}})

# Additional CORS for debugging
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Initialize your Chatter instance
chatter = Chatter()

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint that handles user queries."""
    try:
        data = request.get_json()
        logger.info(f'Received request data: {data}')
        
        user_input = data.get('message')
        if not user_input:
            return jsonify({
                'response': 'No input provided.',
                'success': False,
                'error': 'Missing message field'
            }), 400
            
        # Get the structured response from chatter
        result = chatter.chat(user_input)
        logger.info(f'Generated response: {result.get("response", "No response")}')
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'Error in chat endpoint: {str(e)}')
        return jsonify({
            'response': 'An error occurred while processing your request.',
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get conversation statistics."""
    try:
        stats = chatter.get_conversation_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        logger.error(f'Error getting stats: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation memory."""
    try:
        result = chatter.reset_conversation()
        return jsonify({
            'success': True,
            'message': result['message']
        })
    except Exception as e:
        logger.error(f'Error resetting conversation: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        return jsonify({
            'status': 'healthy',
            'service': 'RAG Chat API',
            'version': '1.0.0',
            'timestamp': os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost'),
            'environment': os.getenv('FLASK_ENV', 'development')
        })
    except Exception as e:
        logger.error(f'Health check failed: {str(e)}')
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/capabilities', methods=['GET'])
def get_capabilities():
    """Get information about what the assistant can help with."""
    return jsonify({
        'success': True,
        'capabilities': {
            'description': 'I am an AI assistant specialized in answering questions based on the documents in my knowledge base.',
            'features': [
                'Document-based question answering',
                'Context-aware responses',
                'Conversation memory',
                'Query analysis and improvement',
                'Structured and formatted responses'
            ],
            'supported_query_types': [
                'Factual questions about document content',
                'Procedural questions',
                'Comparative analysis',
                'Clarification requests'
            ],
            'limitations': [
                'Can only answer questions related to the available documents',
                'Cannot access external information beyond the knowledge base',
                'May not have complete information on all topics'
            ]
        }
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested API endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f'Internal server error: {str(error)}')
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.getenv('FLASK_ENV', 'development') == 'development'
    logger.info(f'Starting RAG Chat API on port {port} (debug={debug_mode})')
    logger.info(f'Environment: {os.getenv("FLASK_ENV", "development")}')
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
