"""Retriever
Handles document retrieval from the vector store.
"""

import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils.helpers import setup_logging
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, TextLoader

class Retriever:
    """Handles document retrieval from the vector store."""
    def __init__(self, log_file='indexer.log') -> None:
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings()
        
        # Load or create the vector store
        self.vector_store_path = os.path.join(self.data_dir, 'vector_store')
        try:
            self.vector_store = FAISS.load_local(
                self.vector_store_path,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
        except Exception as e:
            print(f"Error loading vector store: {e}")
            print("Recreating vector store...")
            self._create_vector_store()

    def _create_vector_store(self):
        """Creates a new vector store from the documents in the data directory."""
        try:
            # Load documents from the data directory
            loader = DirectoryLoader(
                os.path.join(self.data_dir, 'documents'),
                glob="**/*.txt",
                loader_cls=TextLoader
            )
            documents = loader.load()
            
            # Split documents into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Create and save the vector store
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
            self.vector_store.save_local(self.vector_store_path)
            print("Vector store created successfully!")
        except Exception as e:
            print(f"Error creating vector store: {e}")
            raise

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
