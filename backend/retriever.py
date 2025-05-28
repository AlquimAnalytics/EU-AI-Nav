"""Retriever
Handles document retrieval from the vector store.
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils.helpers import setup_logging

class Retriever:
    """Handles document retrieval from the vector store."""
    def __init__(self, log_file='indexer.log') -> None:
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Load the vector store
        self.vector_store_path = os.path.join(self.data_dir, 'vector_store')
        self.vector_store = FAISS.load_local(
            self.vector_store_path,
            self.embeddings
        )

    def retrieve(self, query, k=5):
        """
        Retrieves relevant documents for a query.
        
        Args:
            query (str): The query to retrieve documents for
            k (int): Number of documents to retrieve
            
        Returns:
            list: List of retrieved documents
        """
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            print(f"Error retrieving documents: {e}")
            return []
