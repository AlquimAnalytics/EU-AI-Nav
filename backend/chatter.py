"""Chatter
Runs a chatbot that uses a vector store to retrieve and answer questions.
"""

import os
import logging
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import LLMChain
from langchain_core.runnables import RunnablePassthrough

from utils.helpers import setup_logging
from retriever import Retriever

load_dotenv()

class Chatter:
    """Advanced chatbot logic integrating retrieval and response generation with conversation memory."""
    
    def __init__(self, log_file='chatter.log') -> None:
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        
        # Initialize API key
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            logging.error("OpenAI API key is not set.")
            raise ValueError("OpenAI API key is required. Please set the OPENAI_API_KEY environment variable.")

        # Initialize components
        self.retriever = Retriever()
        self.llm = ChatOpenAI(
            model_name='gpt-4o-mini', 
            openai_api_key=self.openai_api_key,
            temperature=0.3,  # Lower temperature for more consistent responses
            max_tokens=1000
        )
        
        # Initialize conversation memory
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Keep last 10 exchanges
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Initialize chains
        self.qa_chain = self.create_qa_chain()
        self.query_analyzer = self.create_query_analyzer()
        self.response_formatter = self.create_response_formatter()
        
        # Conversation statistics
        self.conversation_stats = {
            "total_queries": 0,
            "successful_retrievals": 0,
            "failed_retrievals": 0,
            "start_time": datetime.now()
        }

    def create_query_analyzer(self):
        """Creates a chain to analyze and improve user queries."""
        query_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a query analysis expert. Analyze the user's query in the context of the conversation history and respond with a JSON object containing:

            1. is_relevant: true if the query is related to EU AI Act or legal documents, false otherwise
            2. reformulated_query: an improved version of the query for better retrieval
            3. key_concepts: list of important concepts from the query
            4. query_type: one of "factual", "procedural", "comparative", "clarification", "follow_up", or "example_request"
            5. confidence: a number between 0 and 1 indicating your confidence

            IMPORTANT: Consider the conversation history when analyzing follow-up questions like:
            - "Can you give me an example?" (likely asking for examples of the previous topic)
            - "What about that?" (referring to something mentioned earlier)
            - "How does that work?" (asking for clarification on previous content)
            - "Tell me more" (requesting additional details on the topic)
            - "Give me a more detailed explanation" (asking for expanded information)
            - "Explain further" (requesting more comprehensive coverage)
            - "What else?" (asking for additional information on the topic)

            For follow-up questions, reformulate them to include the context from the conversation.
            If the user asks for "more details" or "detailed explanation", expand the query to request comprehensive information about the previous topic.

            Example response format:
            {
                "is_relevant": true,
                "reformulated_query": "What are examples of high-risk AI systems under the EU AI Act?",
                "key_concepts": ["high-risk AI systems", "examples", "EU AI Act"],
                "query_type": "example_request",
                "confidence": 0.9
            }"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Analyze this query: {query}")
        ])
        
        return query_analysis_prompt | self.llm | StrOutputParser()

    def create_qa_chain(self):
        """Creates an advanced QA chain with better prompting."""
        
        # System message for the main QA chain
        system_message = """You are a helpful AI assistant specializing in explaining the EU AI Act in simple, clear terms. Your goal is to provide accurate but user-friendly responses.

CORE PRINCIPLES:
1. **Keep it Simple**: Use clear, everyday language - avoid legal jargon
2. **Be Concise**: Provide direct answers without overwhelming detail
3. **Be Helpful**: Focus on what the user actually needs to know
4. **Stay Accurate**: Only provide information from the context provided
5. **Be Conversational**: Keep the conversation flowing naturally, don't be too formal
6. **Use Context**: Consider the conversation history to understand follow-up questions

RESPONSE STYLE:
- Start with a simple, direct answer
- Use bullet points for key points (max 3-4 points)
- Keep responses under 150 words when possible
- Use examples when helpful
- End with a brief, practical takeaway

FOLLOW-UP QUESTIONS:
- If the user asks for examples, provide specific, relevant examples from the context
- If they ask "what about X?", connect it to the previous conversation
- If they ask for clarification, build on what was discussed before
- If they ask for "more details" or "detailed explanation", provide comprehensive coverage including background, implications, and practical aspects
- Always maintain conversation continuity
- For detailed requests, you can provide longer, more comprehensive responses (up to 250 words)

AVOID:
- Overly technical language
- Long lists of requirements
- Legal citations unless specifically asked
- Repetitive information
- Ignoring conversation context

If the context doesn't contain enough information, say so clearly and suggest what they might ask instead."""

        # Main QA prompt
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", """Context Information:
{context}

Current Question: {question}

Please provide a helpful and user-friendly response based on the context provided.""")
        ])
        
        return qa_prompt | self.llm | StrOutputParser()

    def create_response_formatter(self):
        """Creates a chain to format and polish responses."""
        format_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a response formatting expert. Your job is to make responses more user-friendly and readable.

Guidelines:
- Keep the response simple and conversational
- Use clear formatting (bold for key terms, bullet points for lists)
- Don't add unnecessary complexity or technical details
- Ensure the response flows naturally and is easy to read
- Keep the original meaning and accuracy intact
- If the response is already good, make minimal changes

AVOID:
- Adding extra technical explanations
- Making responses longer than necessary
- Over-formatting or excessive styling
- Changing the core message"""),
            ("human", "Format this response to be more user-friendly: {response}")
        ])
        
        return format_prompt | self.llm | StrOutputParser()

    def preprocess_query(self, query: str) -> Dict:
        """Preprocess and analyze the user query."""
        try:
            # Clean the query
            query = query.strip()
            if not query:
                return {"error": "Empty query provided"}
            
            # Get chat history for context
            chat_history = self.memory.chat_memory.messages
            
            # Temporarily disable query analyzer due to version compatibility issues
            # Use fallback analysis instead
            return self._create_default_analysis(query, chat_history)
            
        except Exception as e:
            logging.error(f"Error preprocessing query: {e}")
            return {"error": f"Query preprocessing failed: {str(e)}"}

    def _create_default_analysis(self, query: str, chat_history: List = None) -> Dict:
        """Create a default analysis when the query analyzer fails."""
        # Simple keyword-based relevance check
        eu_ai_keywords = [
            "eu ai act", "artificial intelligence", "ai regulation", "european union",
            "ai system", "risk", "compliance", "regulation", "legal", "law"
        ]
        
        # Follow-up question indicators
        follow_up_indicators = [
            "example", "examples", "instance", "instances", "case", "cases",
            "what about", "how about", "tell me more", "explain", "clarify",
            "that", "this", "it", "them", "those", "these",
            "more", "detailed", "detailed explanation", "more detailed",
            "expand", "elaborate", "further", "additional", "extra",
            "go on", "continue", "what else", "anything else",
            "specifically", "in detail", "at length", "comprehensive"
        ]
        
        query_lower = query.lower()
        
        # Check if it's a follow-up question
        is_follow_up = any(indicator in query_lower for indicator in follow_up_indicators)
        
        # If it's a follow-up question and we have chat history, assume it's relevant
        if is_follow_up and chat_history and len(chat_history) > 0:
            # Try to extract context from the last few messages
            recent_context = ""
            for msg in chat_history[-4:]:  # Last 4 messages
                if hasattr(msg, 'content'):
                    recent_context += msg.content + " "
            
            # Create a more specific reformulated query based on the type of follow-up
            if any(word in query_lower for word in ["example", "examples", "instance", "case"]):
                reformulated_query = f"examples of {recent_context.strip()}"
            elif any(word in query_lower for word in ["more", "detailed", "expand", "elaborate", "further"]):
                reformulated_query = f"detailed explanation of {recent_context.strip()}"
            elif any(word in query_lower for word in ["what about", "how about"]):
                reformulated_query = f"{query} in context of {recent_context.strip()}"
            else:
                reformulated_query = f"{query} in context of {recent_context.strip()}"
            
            return {
                "is_relevant": True,
                "reformulated_query": reformulated_query,
                "key_concepts": ["follow_up", "context"],
                "query_type": "follow_up",
                "confidence": 0.8
            }
        
        # Regular keyword-based check
        is_relevant = any(keyword in query_lower for keyword in eu_ai_keywords)
        
        return {
            "is_relevant": is_relevant,
            "reformulated_query": query,
            "key_concepts": [],
            "query_type": "factual",
            "confidence": 0.7
        }

    def retrieve_context(self, query: str, k: int = 5) -> Tuple[List, float]:
        """Retrieve relevant context with confidence scoring."""
        try:
            docs = self.retriever.retrieve(query=query, k=k)
            
            if not docs:
                # For follow-up questions, try a broader search
                if any(indicator in query.lower() for indicator in ["example", "examples", "instance", "case"]):
                    # Try searching for broader terms related to the query
                    broader_query = query.replace("example", "").replace("examples", "").strip()
                    if broader_query:
                        docs = self.retriever.retrieve(query=broader_query, k=k)
                elif any(indicator in query.lower() for indicator in ["detailed", "more", "expand", "elaborate", "further"]):
                    # For detailed explanation requests, try to get more comprehensive context
                    docs = self.retriever.retrieve(query=query, k=k*2)  # Get more documents for detailed explanations
                
                if not docs:
                    return [], 0.0
            
            # Calculate simple relevance score based on document count and content
            relevance_score = min(len(docs) / k, 1.0)
            
            # Combine document contents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            return docs, relevance_score
            
        except Exception as e:
            logging.error(f"Error retrieving context: {e}")
            return [], 0.0

    def generate_response(self, query: str, context: str, chat_history: List) -> str:
        """Generate a response using the QA chain."""
        try:
            response = self.qa_chain.invoke({
                "question": query,
                "context": context,
                "chat_history": chat_history
            })
            
            # Format the response
            formatted_response = self.response_formatter.invoke({"response": response})
            
            return formatted_response
            
        except Exception as e:
            logging.error(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while processing your request. Please try again."

    def handle_irrelevant_query(self, query: str) -> str:
        """Handle queries that are not relevant to the knowledge base."""
        return """I understand you're asking about "{query}", but I'm specifically designed to help with questions related to the documents in my knowledge base. 

        I can help you with:
        - Questions about the content in my knowledge base
        - Information retrieval from the available documents
        - Clarifications about specific topics covered in the documents

        Could you please rephrase your question to be more specific to the content I have access to, or ask me what topics I can help you with?""".format(query=query)

    def chat(self, query: str) -> Dict:
        """
        Main chat method that processes user queries and returns structured responses.
        """
        try:
            self.conversation_stats["total_queries"] += 1
            logging.info(f"Received query: {query}")
            
            # Preprocess the query
            query_analysis = self.preprocess_query(query)
            
            if "error" in query_analysis:
                return {
                    "response": f"I'm sorry, but I couldn't process your query: {query_analysis['error']}",
                    "success": False,
                    "query_analysis": query_analysis
                }
            
            # Check if query is relevant
            if not query_analysis.get("is_relevant", True):
                return {
                    "response": self.handle_irrelevant_query(query),
                    "success": True,
                    "query_analysis": query_analysis,
                    "context_used": False
                }
            
            # Retrieve context
            reformulated_query = query_analysis.get("reformulated_query", query)
            docs, relevance_score = self.retrieve_context(reformulated_query)
            
            if relevance_score > 0:
                self.conversation_stats["successful_retrievals"] += 1
                context = "\n\n".join([doc.page_content for doc in docs])
            else:
                self.conversation_stats["failed_retrievals"] += 1
                context = "No relevant information found in the knowledge base."
            
            # Get chat history
            chat_history = self.memory.chat_memory.messages
            
            # Generate response
            response = self.generate_response(query, context, chat_history)
            
            # Update memory
            self.memory.chat_memory.add_user_message(query)
            self.memory.chat_memory.add_ai_message(response)
            
            # Prepare response structure
            result = {
                "response": response,
                "success": True,
                "query_analysis": query_analysis,
                "context_used": relevance_score > 0,
                "relevance_score": relevance_score,
                "documents_retrieved": len(docs),
                "conversation_stats": self.conversation_stats
            }
            
            logging.info(f"Generated response successfully. Relevance score: {relevance_score}")
            return result
            
        except Exception as e:
            logging.error(f"Failed to generate response: {e}", exc_info=True)
            return {
                "response": "I'm sorry, but I encountered an unexpected error while processing your request. Please try again or rephrase your question.",
                "success": False,
                "error": str(e)
            }

    def get_conversation_stats(self) -> Dict:
        """Get conversation statistics."""
        return {
            **self.conversation_stats,
            "uptime": str(datetime.now() - self.conversation_stats["start_time"])
        }

    def reset_conversation(self) -> Dict:
        """Reset the conversation memory."""
        self.memory.clear()
        return {"message": "Conversation memory has been reset."}

if __name__ == "__main__":
    chatter = Chatter()
    print("Chatter initialized. Type 'exit' or 'quit' to end the conversation.")
    print("Type 'stats' to see conversation statistics.")
    print("Type 'reset' to reset conversation memory.")

    while True:
        query = input("\nUser: ")
        if query.lower() in ['exit', 'quit']:
            break
        elif query.lower() == 'stats':
            stats = chatter.get_conversation_stats()
            print(f"\nConversation Statistics:")
            print(f"Total queries: {stats['total_queries']}")
            print(f"Successful retrievals: {stats['successful_retrievals']}")
            print(f"Failed retrievals: {stats['failed_retrievals']}")
            print(f"Uptime: {stats['uptime']}")
            continue
        elif query.lower() == 'reset':
            result = chatter.reset_conversation()
            print(f"\n{result['message']}")
            continue
        
        result = chatter.chat(query)
        print(f"\nAssistant: {result['response']}")
        
        if result.get('success') and result.get('context_used'):
            print(f"\n[Retrieved {result['documents_retrieved']} documents, Relevance: {result['relevance_score']:.2f}]")
