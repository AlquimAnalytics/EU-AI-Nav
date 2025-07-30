import React, { useState, useEffect, useRef } from 'react';
import './App.css';

function App() {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [stats, setStats] = useState(null);
    const messagesEndRef = useRef(null);

    const API_BASE_URL = process.env.REACT_APP_API_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:5001/api';

    console.log('Environment variables check:');
    console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
    console.log('REACT_APP_BACKEND_URL:', process.env.REACT_APP_BACKEND_URL);
    console.log('NODE_ENV:', process.env.NODE_ENV);
    console.log('Final API_BASE_URL:', API_BASE_URL);

    const exampleQuestions = [
        "What is the EU AI Act?",
        "What are the risk categories in the EU AI Act?",
        "How do I know whether an AI system is high-risk?",
        "What are the compliance requirements for businesses?",
    ];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Test backend connectivity on startup
        testBackendConnection();
        getStats();
    }, []);

    const testBackendConnection = async () => {
        try {
            console.log(`Testing backend connection to: ${API_BASE_URL}/health`);
            const response = await fetch(`${API_BASE_URL}/health`);
            if (response.ok) {
                const data = await response.json();
                console.log('Backend connection successful:', data);
            } else {
                console.error('Backend health check failed:', response.status);
            }
        } catch (error) {
            console.error('Backend connection test failed:', error);
            console.error('This might explain fetch failures in the app');
        }
    };

    const getStats = async () => {
        try {
            console.log(`Fetching stats from: ${API_BASE_URL}/stats`);
            const response = await fetch(`${API_BASE_URL}/stats`);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                setStats(data.stats);
            }
        } catch (error) {
            console.error('Failed to get stats:', error);
            console.error('API_BASE_URL:', API_BASE_URL);
        }
    };

    const sendMessage = async (messageText = null) => {
        const textToSend = messageText || inputMessage;
        if (!textToSend.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            text: textToSend,
            sender: 'user',
            timestamp: new Date().toLocaleTimeString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            console.log(`Sending message to: ${API_BASE_URL}/chat`);
            const response = await fetch(`${API_BASE_URL}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: textToSend }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            const assistantMessage = {
                id: Date.now() + 1,
                text: data.response,
                sender: 'assistant',
                timestamp: new Date().toLocaleTimeString(),
                metadata: {
                    success: data.success,
                    contextUsed: data.context_used,
                    relevanceScore: data.relevance_score,
                    documentsRetrieved: data.documents_retrieved,
                    queryAnalysis: data.query_analysis
                }
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Update stats
            if (data.conversation_stats) {
                setStats(data.conversation_stats);
            }

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: Date.now() + 1,
                text: 'Sorry, I encountered an error while processing your request. Please try again.',
                sender: 'assistant',
                timestamp: new Date().toLocaleTimeString(),
                isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleExampleClick = (question) => {
        sendMessage(question);
    };

    const resetConversation = async () => {
        try {
            console.log(`Resetting conversation at: ${API_BASE_URL}/reset`);
            const response = await fetch(`${API_BASE_URL}/reset`, { method: 'POST' });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            setMessages([]);
            getStats();
        } catch (error) {
            console.error('Failed to reset conversation:', error);
            console.error('API_BASE_URL:', API_BASE_URL);
            console.error('Full error:', error);
        }
    };

    const formatMessage = (text) => {
        // Simple markdown-like formatting
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/- (.*)/g, '• $1')
            .split('\n').map((line, i) => <div key={i} dangerouslySetInnerHTML={{ __html: line }} />);
    };

    return (
        <div className="App">
            <header className="App-header">
                <h1>🤖 EU AI Act Assistant</h1>
                <p>Your AI companion for understanding the EU AI Act and its implications</p>
            </header>

            <div className="chat-container">
                <div className="messages-container">
                    {messages.length === 0 && (
                        <div className="welcome-message">
                            <h3>Welcome to the EU AI Act Assistant!</h3>
                            <p>I'm here to help you understand the European Union Artificial Intelligence Act and its implications.</p>

                            <div className="example-questions">
                                <h4>Try asking me about:</h4>
                                <div className="question-chips">
                                    {exampleQuestions.map((question, index) => (
                                        <button
                                            key={index}
                                            className="question-chip"
                                            onClick={() => handleExampleClick(question)}
                                        >
                                            {question}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {messages.map((message) => (
                        <div
                            key={message.id}
                            className={`message ${message.sender} ${message.isError ? 'error' : ''}`}
                        >
                            <div className="message-content">
                                <div className="message-text">
                                    {formatMessage(message.text)}
                                </div>
                                <div className="message-timestamp">
                                    {message.timestamp}
                                </div>
                                {message.metadata && message.sender === 'assistant' && (
                                    <div className="message-metadata">
                                        {message.metadata.contextUsed && (
                                            <span className="metadata-item">
                                                📄 {message.metadata.documentsRetrieved} docs
                                            </span>
                                        )}
                                        {message.metadata.relevanceScore && (
                                            <span className="metadata-item">
                                                🎯 {Math.round(message.metadata.relevanceScore * 100)}% relevant
                                            </span>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="message assistant">
                            <div className="message-content">
                                <div className="loading-indicator">
                                    <div className="typing-dots">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <div className="input-container">
                    <div className="input-wrapper">
                        <input
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                            placeholder="Ask me anything about the EU AI Act..."
                            disabled={isLoading}
                            className="message-input"
                        />
                        <button
                            onClick={() => sendMessage()}
                            disabled={isLoading || !inputMessage.trim()}
                            className="send-button"
                        >
                            {isLoading ? '⏳' : '📤'}
                        </button>
                    </div>
                </div>
            </div>

            <div className="sidebar">
                <div className="sidebar-section">
                    <h3>📊 Statistics</h3>
                    {stats ? (
                        <div className="stats">
                            <div className="stat-item">
                                <span className="stat-label">Total Queries:</span>
                                <span className="stat-value">{stats.total_queries}</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-label">Successful Retrievals:</span>
                                <span className="stat-value">{stats.successful_retrievals}</span>
                            </div>
                            <div className="stat-item">
                                <span className="stat-label">Failed Retrievals:</span>
                                <span className="stat-value">{stats.failed_retrievals}</span>
                            </div>
                            {stats.uptime && (
                                <div className="stat-item">
                                    <span className="stat-label">Uptime:</span>
                                    <span className="stat-value">{stats.uptime}</span>
                                </div>
                            )}
                        </div>
                    ) : (
                        <p>Loading statistics...</p>
                    )}
                </div>

                <div className="sidebar-section">
                    <h3>🛠️ Actions</h3>
                    <button onClick={resetConversation} className="action-button">
                        🔄 Reset Conversation
                    </button>
                </div>

                <div className="sidebar-section">
                    <h3>ℹ️ About</h3>
                    <p>This assistant uses advanced prompting strategies and conversation memory to provide accurate, context-aware responses about the EU AI Act.</p>
                </div>
            </div>
        </div>
    );
}

export default App;
