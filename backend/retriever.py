"""Retriever
Handles document retrieval from the vector store.
"""

import os
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils.helpers import setup_logging


class Retriever:
    """Handles document retrieval from the vector store."""
    def __init__(self, log_file='retriever.log') -> None:
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        
        self.embeddings = OpenAIEmbeddings()
        self.vector_store_path = os.path.join(self.data_dir, 'vector_store')
        print(self.vector_store_path)

        self.docsearch = self.load_vector_store()


    def load_vector_store(self):
        """Loads the vector store from the data directory.
        """
        try:
            if os.path.exists(self.vector_store_path):
                logging.info(f"Loading vector store from {self.vector_store_path}...")
                docsearch = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logging.info("Vector store loaded successfully.")
                return docsearch
            else:
                logging.error("Vector store not found.")
                return None
        except Exception as e:
            logging.error(f"Failed to load vector store: {e}", exc_info=True)
            return None

    def retrieve(self, query, k=5):
        """
        Retrieves relevant documents for a query.
        """
        if self.docsearch is None:
            logging.error("Vector store is not loaded.")
            return []
        try:
            docs = self.docsearch.similarity_search(query, k=k)
            return docs
        except Exception as e:
            logging.error(f"Error retrieving documents: {e}", exc_info=True)
            return []
