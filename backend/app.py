from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from chatter import Chatter 
from dotenv import load_dotenv
import os
import logging
import json
from datetime import datetime, date

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

# Daily message counter (in-memory)
DAILY_LIMIT = 20
daily_counter = 0
current_date = None

def get_daily_counter():
    """Get the current daily counter."""
    global daily_counter, current_date
    today = date.today()
    
    # Check if it's a new day
    if current_date != today:
        # Reset counter for new day
        daily_counter = 0
        current_date = today
        logger.info(f'New day detected, counter reset to 0')
    
    return daily_counter

def increment_daily_counter():
    """Increment the daily counter."""
    global daily_counter, current_date
    today = date.today()
    
    # Check if it's a new day
    if current_date != today:
        daily_counter = 0
        current_date = today
        logger.info(f'New day detected, counter reset to 0')
    
    daily_counter += 1
    logger.info(f'Daily counter incremented to {daily_counter}')
    return daily_counter

def check_daily_limit():
    """Check if daily limit has been reached."""
    current_count = get_daily_counter()
    return current_count < DAILY_LIMIT

@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
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
        
        # Check daily limit
        if not check_daily_limit():
            current_count = get_daily_counter()
            return jsonify({
                'response': f'Daily message limit reached ({DAILY_LIMIT} messages per day). Please try again tomorrow.',
                'success': False,
                'error': 'Daily limit exceeded',
                'daily_count': current_count,
                'daily_limit': DAILY_LIMIT
            }), 429  # Too Many Requests
            
        # Increment counter before processing
        new_count = increment_daily_counter()
        logger.info(f'Processing message {new_count}/{DAILY_LIMIT}')
            
        # Get the structured response from chatter
        result = chatter.chat(user_input)
        logger.info(f'Generated response: {result.get("response", "No response")}')
        
        # Add counter info to response
        result['daily_count'] = new_count
        result['daily_limit'] = DAILY_LIMIT
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f'Error in chat endpoint: {str(e)}')
        return jsonify({
            'response': 'An error occurred while processing your request.',
            'success': False,
            'error': str(e)
        }), 500

@app.route('/stats', methods=['GET'])
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

@app.route('/counter', methods=['GET'])
def get_counter():
    """Get daily message counter status."""
    try:
        current_count = get_daily_counter()
        return jsonify({
            'success': True,
            'daily_count': current_count,
            'daily_limit': DAILY_LIMIT,
            'remaining': DAILY_LIMIT - current_count,
            'date': date.today().isoformat()
        })
    except Exception as e:
        logger.error(f'Error getting counter: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/reset', methods=['POST'])
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

@app.route('/health', methods=['GET'])
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

@app.route('/store-email', methods=['POST'])
def store_email():
    """Store user email address in a file."""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            return jsonify({
                'success': False,
                'error': 'Invalid email format'
            }), 400
        
        # Create data directory if it doesn't exist
        data_dir = 'data'
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # File path for storing emails
        emails_file = os.path.join(data_dir, 'user_emails.json')
        
        # Load existing emails
        emails = []
        if os.path.exists(emails_file):
            try:
                with open(emails_file, 'r') as f:
                    emails = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                emails = []
        
        # Check if email already exists
        email_exists = any(entry.get('email') == email for entry in emails)
        
        if not email_exists:
            # Add new email entry
            email_entry = {
                'email': email,
                'timestamp': datetime.now().isoformat()
            }
            emails.append(email_entry)
            
            # Save to file
            with open(emails_file, 'w') as f:
                json.dump(emails, f, indent=2)
            
            logger.info(f'New email stored: {email}')
        else:
            logger.info(f'Email already exists: {email}')
        
        # Always return success - allow access whether email is new or existing
        return jsonify({
            'success': True,
            'message': 'Access granted',
            'email_exists': email_exists
        })
        
    except Exception as e:
        logger.error(f'Error storing email: {str(e)}')
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/capabilities', methods=['GET'])
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
