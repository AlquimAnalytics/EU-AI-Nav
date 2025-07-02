"""Retriever
Handles document retrieval from the vector store with enhanced relevance scoring.
"""

import os
import logging
from typing import List, Dict, Tuple, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from utils.helpers import setup_logging


class Retriever:
    """Enhanced document retrieval with relevance scoring and metadata handling."""
    
    def __init__(self, log_file='retriever.log') -> None:
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        
        # Initialize embeddings
        try:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small",  # Using the latest embedding model
                dimensions=1536  # Specify dimensions for consistency
            )
        except Exception as e:
            logging.error(f"Failed to initialize embeddings: {e}")
            raise
        
        self.vector_store_path = os.path.join(self.data_dir, 'vector_store')
        logging.info(f"Vector store path: {self.vector_store_path}")

        self.docsearch = self.load_vector_store()
        
        # Retrieval configuration
        self.default_k = 5
        self.max_k = 10
        self.min_relevance_score = 0.3

    def load_vector_store(self) -> Optional[FAISS]:
        """Loads the vector store from the data directory with enhanced error handling."""
        try:
            if os.path.exists(self.vector_store_path):
                logging.info(f"Loading vector store from {self.vector_store_path}...")
                
                # Check if required files exist
                index_file = os.path.join(self.vector_store_path, 'index.faiss')
                pkl_file = os.path.join(self.vector_store_path, 'index.pkl')
                
                if not (os.path.exists(index_file) and os.path.exists(pkl_file)):
                    logging.error("Vector store files are incomplete.")
                    return None
                
                docsearch = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings
                )
                
                # Get basic stats about the vector store
                if hasattr(docsearch, 'index') and docsearch.index is not None:
                    num_vectors = docsearch.index.ntotal
                    logging.info(f"Vector store loaded successfully with {num_vectors} vectors.")
                else:
                    logging.warning("Vector store loaded but index information unavailable.")
                
                return docsearch
            else:
                logging.error(f"Vector store directory not found at {self.vector_store_path}")
                return None
                
        except Exception as e:
            logging.error(f"Failed to load vector store: {e}", exc_info=True)
            return None

    def calculate_relevance_score(self, docs: List[Document], query: str) -> float:
        """
        Calculate a relevance score based on document characteristics.
        
        Args:
            docs: Retrieved documents
            query: Original query
            
        Returns:
            Relevance score between 0 and 1
        """
        if not docs:
            return 0.0
        
        try:
            # Simple relevance scoring based on document count and content length
            total_content_length = sum(len(doc.page_content) for doc in docs)
            avg_content_length = total_content_length / len(docs)
            
            # Normalize based on expected content length (adjust as needed)
            content_score = min(avg_content_length / 500, 1.0)  # Assuming 500 chars is good
            
            # Document count score (more documents = potentially better coverage)
            count_score = min(len(docs) / self.default_k, 1.0)
            
            # Query-document overlap score (simple keyword matching)
            query_words = set(query.lower().split())
            overlap_scores = []
            
            for doc in docs:
                doc_words = set(doc.page_content.lower().split())
                if doc_words:
                    overlap = len(query_words.intersection(doc_words)) / len(query_words)
                    overlap_scores.append(overlap)
            
            overlap_score = sum(overlap_scores) / len(overlap_scores) if overlap_scores else 0.0
            
            # Weighted combination of scores
            final_score = (content_score * 0.3 + count_score * 0.3 + overlap_score * 0.4)
            
            return min(final_score, 1.0)
            
        except Exception as e:
            logging.error(f"Error calculating relevance score: {e}")
            return 0.5  # Default fallback score

    def retrieve(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Retrieves relevant documents for a query with enhanced error handling.
        
        Args:
            query: The search query
            k: Number of documents to retrieve (defaults to self.default_k)
            
        Returns:
            List of relevant documents
        """
        if self.docsearch is None:
            logging.error("Vector store is not loaded.")
            return []
        
        if not query or not query.strip():
            logging.warning("Empty query provided.")
            return []
        
        # Validate and set k
        if k is None:
            k = self.default_k
        k = min(max(1, k), self.max_k)  # Ensure k is between 1 and max_k
        
        try:
            logging.info(f"Retrieving {k} documents for query: '{query}'")
            
            # Perform similarity search
            docs = self.docsearch.similarity_search(
                query, 
                k=k,
                fetch_k=min(k * 2, self.max_k)  # Fetch more for better selection
            )
            
            if docs:
                relevance_score = self.calculate_relevance_score(docs, query)
                logging.info(f"Retrieved {len(docs)} documents with relevance score: {relevance_score:.3f}")
                
                # Log document metadata if available
                for i, doc in enumerate(docs):
                    metadata = getattr(doc, 'metadata', {})
                    logging.debug(f"Document {i+1}: {metadata.get('source', 'Unknown source')}")
            else:
                logging.warning("No documents retrieved for the query.")
            
            return docs
            
        except Exception as e:
            logging.error(f"Error retrieving documents: {e}", exc_info=True)
            return []

    def retrieve_with_scores(self, query: str, k: Optional[int] = None) -> Tuple[List[Document], List[float]]:
        """
        Retrieves documents with similarity scores.
        
        Args:
            query: The search query
            k: Number of documents to retrieve
            
        Returns:
            Tuple of (documents, similarity_scores)
        """
        if self.docsearch is None:
            logging.error("Vector store is not loaded.")
            return [], []
        
        if not query or not query.strip():
            logging.warning("Empty query provided.")
            return [], []
        
        if k is None:
            k = self.default_k
        k = min(max(1, k), self.max_k)
        
        try:
            logging.info(f"Retrieving {k} documents with scores for query: '{query}'")
            
            # Perform similarity search with scores
            docs_and_scores = self.docsearch.similarity_search_with_score(
                query, 
                k=k
            )
            
            if docs_and_scores:
                docs, scores = zip(*docs_and_scores)
                docs = list(docs)
                scores = list(scores)
                
                logging.info(f"Retrieved {len(docs)} documents with scores ranging from {min(scores):.3f} to {max(scores):.3f}")
                return docs, scores
            else:
                logging.warning("No documents retrieved for the query.")
                return [], []
                
        except Exception as e:
            logging.error(f"Error retrieving documents with scores: {e}", exc_info=True)
            return [], []

    def get_vector_store_info(self) -> Dict:
        """
        Get information about the vector store.
        
        Returns:
            Dictionary with vector store statistics
        """
        info = {
            "loaded": self.docsearch is not None,
            "path": self.vector_store_path,
            "exists": os.path.exists(self.vector_store_path)
        }
        
        if self.docsearch is not None and hasattr(self.docsearch, 'index'):
            try:
                info["num_vectors"] = self.docsearch.index.ntotal
                info["dimensions"] = self.docsearch.index.d
            except Exception as e:
                logging.error(f"Error getting vector store info: {e}")
                info["error"] = str(e)
        
        return info

    def health_check(self) -> Dict:
        """
        Perform a health check on the retriever.
        
        Returns:
            Health status dictionary
        """
        try:
            # Test embeddings
            test_embedding = self.embeddings.embed_query("test")
            embeddings_ok = len(test_embedding) > 0
            
            # Test vector store
            vector_store_ok = self.docsearch is not None
            
            # Test retrieval with a simple query
            retrieval_ok = False
            if vector_store_ok:
                test_docs = self.retrieve("test", k=1)
                retrieval_ok = True  # If no exception, retrieval is working
            
            return {
                "status": "healthy" if all([embeddings_ok, vector_store_ok, retrieval_ok]) else "unhealthy",
                "embeddings": "ok" if embeddings_ok else "error",
                "vector_store": "ok" if vector_store_ok else "error",
                "retrieval": "ok" if retrieval_ok else "error",
                "vector_store_info": self.get_vector_store_info()
            }
            
        except Exception as e:
            logging.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
