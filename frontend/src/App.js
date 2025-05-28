import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// Get API URL from environment variable, fallback to localhost for development
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function App() {
    const [input, setInput] = useState('');
    const [chatHistory, setChatHistory] = useState([]);
    const [loading, setLoading] = useState(false);

    const exampleQuestions = [
        "What is the EU AI Act?",
        // "What are the risk categories?",
        "How do I know whether an AI system is high-risk?",
        "Why do we need to regulate the use of Artificial Intelligence?",
        "What is the purpose of the EU AI Act?",
        "What are the key provisions of the EU AI Act?",
        "How does the EU AI Act protect individuals' rights?",
        "What are the penalties for non-compliance with the EU AI Act?",
        "What is the timeline for the EU AI Act to be implemented?",

    ];

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = input.trim();
        setLoading(true);

        // Add user message to chat history
        setChatHistory(prev => [...prev, { type: 'user', content: userMessage }]);

        try {
            const res = await axios.post(`${API_URL}/api/chat`, { message: userMessage });
            // Add assistant response to chat history
            setChatHistory(prev => [...prev, { type: 'assistant', content: res.data.response }]);
        } catch (error) {
            console.error(error);
            setChatHistory(prev => [...prev, {
                type: 'assistant',
                content: 'An error occurred while processing your request.'
            }]);
        } finally {
            setLoading(false);
            setInput('');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleExampleClick = (question) => {
        setInput(question);
    };

    return (
        <div className="app-container">
            <div className="chat-container">
                <h1 className="title">RAG Assistant</h1>
                <p className="subtitle">Your AI companion for RAG pipeline development</p>

                <div className="example-questions">
                    <h3>Try asking about:</h3>
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

                <div className="chat-messages">
                    {chatHistory.map((message, index) => (
                        <div key={index} className="message-container">
                            <div className={`message ${message.type}`}>
                                <div className="message-content">
                                    <h3>{message.type === 'assistant' ? 'Assistant' : 'You'}</h3>
                                    <p>{message.content}</p>
                                </div>
                            </div>
                        </div>
                    ))}
                    {loading && (
                        <div className="message-container">
                            <div className="message assistant">
                                <div className="message-content">
                                    <h3>Assistant</h3>
                                    <div className="loading-indicator">
                                        <span className="loading-dot"></span>
                                        <span className="loading-dot"></span>
                                        <span className="loading-dot"></span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                <form onSubmit={handleSubmit} className="input-form">
                    <div className="input-wrapper">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Ask me anything about RAG pipelines... (Press Enter to send, Shift+Enter for new line)"
                            required
                            className="chat-input"
                        />
                        <button
                            type="submit"
                            className={`submit-button ${loading ? 'loading' : ''}`}
                            disabled={loading || !input.trim()}
                        >
                            {loading ? (
                                <span className="loading-spinner"></span>
                            ) : (
                                <svg viewBox="0 0 24 24" fill="none" className="send-icon">
                                    <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                    <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                            )}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default App;
