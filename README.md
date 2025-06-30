# 🤖 Advanced RAG Assistant

A sophisticated Retrieval-Augmented Generation (RAG) system with advanced prompting strategies, conversation memory, and a modern user interface. This system provides accurate, context-aware responses based on your document knowledge base.

## ✨ Features

### 🧠 Advanced Prompting Strategies
- **Query Analysis**: Intelligent query preprocessing and reformulation
- **Context-Aware Responses**: Multi-stage prompting with conversation memory
- **Response Formatting**: Professional, well-structured output with markdown formatting
- **Relevance Scoring**: Smart document retrieval with confidence metrics
- **Error Handling**: Robust fallback strategies and graceful error recovery

### 💬 Conversation Management
- **Memory System**: Maintains conversation context across multiple exchanges
- **Query Classification**: Automatically categorizes queries by type and relevance
- **Context Validation**: Ensures responses are based on available knowledge
- **Conversation Statistics**: Track usage patterns and system performance

### 🔍 Enhanced Retrieval
- **Smart Document Selection**: Advanced relevance scoring and ranking
- **Metadata Handling**: Comprehensive document information tracking
- **Flexible Search**: Configurable retrieval parameters and thresholds
- **Health Monitoring**: Real-time system status and performance metrics

### 🎨 Modern User Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Real-time Updates**: Live conversation flow with typing indicators
- **System Status**: Visual health indicators and performance metrics
- **Conversation Controls**: Reset, statistics, and system management tools

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Vector Store  │
│   (React)       │◄──►│   (Flask)       │◄──►│   (FAISS)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   OpenAI API    │
                       │   (GPT-4)       │
                       └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key

### Backend Setup

1. **Clone and navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Prepare your documents:**
   - Place your documents in `data/documents/`
   - Run the indexing process (if not already done)

5. **Start the backend server:**
   ```bash
   python app.py
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start the development server:**
   ```bash
   npm start
   ```

4. **Open your browser:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

## 📚 API Endpoints

### Core Endpoints

- `POST /api/chat` - Main chat endpoint
- `GET /api/stats` - Get conversation statistics
- `POST /api/reset` - Reset conversation memory
- `GET /api/health` - System health check
- `GET /api/capabilities` - System capabilities information

### Example Usage

```bash
# Send a chat message
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are the key provisions of the EU AI Act?"}'

# Get system statistics
curl http://localhost:5001/api/stats

# Reset conversation
curl -X POST http://localhost:5001/api/reset
```

## 🧪 Advanced Features

### Query Analysis
The system automatically analyzes incoming queries to:
- Determine relevance to the knowledge base
- Reformulate queries for better retrieval
- Classify query types (factual, procedural, comparative, clarification)
- Calculate confidence scores

### Response Generation Pipeline
1. **Query Preprocessing**: Clean and analyze the input
2. **Context Retrieval**: Find relevant documents with scoring
3. **Response Generation**: Generate context-aware responses
4. **Response Formatting**: Apply professional formatting
5. **Memory Update**: Store conversation context

### Conversation Memory
- Maintains context across multiple exchanges
- Configurable memory window (default: 10 exchanges)
- Automatic memory management and cleanup

### Relevance Scoring
- Document content analysis
- Query-document overlap calculation
- Length and coverage metrics
- Confidence-based filtering

## 🔧 Configuration

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key
PORT=5001
LOG_LEVEL=INFO
```

### System Parameters
- **Temperature**: 0.3 (for consistent responses)
- **Max Tokens**: 1000 (response length limit)
- **Memory Window**: 10 exchanges
- **Default Retrieval**: 5 documents
- **Max Retrieval**: 10 documents

## 📊 Monitoring and Analytics

### Conversation Statistics
- Total queries processed
- Successful vs failed retrievals
- System uptime
- Performance metrics

### Health Monitoring
- API connectivity status
- Vector store health
- Embedding model status
- Overall system health

## 🛠️ Development

### Project Structure
```
rag-flask-app/
├── backend/
│   ├── app.py              # Flask API server
│   ├── chatter.py          # Core RAG logic
│   ├── retriever.py        # Document retrieval
│   ├── indexer.py          # Document indexing
│   ├── utils/
│   │   └── helpers.py      # Utility functions
│   └── data/
│       ├── documents/      # Source documents
│       └── vector_store/   # FAISS index
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   └── App.css         # Styling
│   └── package.json
└── README.md
```

### Adding New Documents
1. Place documents in `backend/data/documents/`
2. Run the indexing process
3. Restart the backend server

### Customizing Prompts
Edit the prompt templates in `chatter.py`:
- `create_query_analyzer()` - Query analysis prompts
- `create_qa_chain()` - Main response generation
- `create_response_formatter()` - Response formatting

## 🚀 Deployment

### Production Setup
1. **Backend**: Use Gunicorn for production
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5001 app:app
   ```

2. **Frontend**: Build for production
   ```bash
   npm run build
   ```

3. **Environment**: Set production environment variables
4. **Monitoring**: Enable logging and health checks

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with LangChain and OpenAI
- Vector storage powered by FAISS
- Modern UI with React
- Robust API with Flask

## 📞 Support

For questions or issues:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

---

**Happy chatting with your RAG assistant! 🤖✨** 