# RAG Flask App

A Flask-based RAG (Retrieval-Augmented Generation) application with a React frontend.

## Prerequisites

- Python 3.8+
- Node.js 16+
- Ollama running locally
- OpenAI API key

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   FLASK_ENV=development
   FLASK_APP=app.py
   ```

5. Start the backend server:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend: http://localhost:5001

## Running the Demo

1. Ensure Ollama is running locally
2. Start the backend server
3. Start the frontend server
4. Open http://localhost:3000 in your browser

## Troubleshooting

- If you encounter CORS issues, ensure both frontend and backend are running on their respective ports
- Make sure Ollama is running and accessible
- Verify your OpenAI API key is correctly set in the .env file 