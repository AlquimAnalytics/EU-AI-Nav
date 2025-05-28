"""Retriever
Contains the Retriever class to load the vector store and make similarity searches.
"""

import os
import logging
from utils.helpers import setup_logging
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document


class Retriever:
    """Retriever class to load the vector store and make similarity searches."""
    def __init__(self, log_file='retriever.log'):
        self.data_dir = "data"
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        self.embeddings = OllamaEmbeddings(model="mxbai-embed-large")
        self.vector_store_path = os.path.join(self.data_dir, 'vector_store')

        self.docsearch = self.load_vector_store()

    def load_vector_store(self) -> FAISS:
        """
        Loads the vector store from the data directory.
        """
        try:
            if os.path.exists(self.vector_store_path):
                logging.info(f"Loading vector store from {self.vector_store_path}...")
                docsearch = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    index_name='index',
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

    def retrieve(self, query, k):
        """
        Retrieves relevant documents for a given query.
        """
        if self.docsearch is None:
            logging.error("Vector store is not loaded.")
            return []

        try:
            results = self.docsearch.similarity_search(query, k=k)
            return results
        except Exception as e:
            logging.error(f"Failed to retrieve documents: {e}", exc_info=True)
            return []
