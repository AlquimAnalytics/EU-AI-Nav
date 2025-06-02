"""Indexer
Contains a class to process PDF files and embed data into a single, incrementally updatable vector store.
After processing, files are moved to an archive.
"""

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from utils.helpers import setup_logging, archive_file
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

class Indexer:
    def __init__(self, log_file='indexer.log'):
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, log_file)
        self.embeddings = OpenAIEmbeddings()
        self.vector_store_path = os.path.join(self.data_dir, 'vector_store')
        print(f"Vector store path: {self.vector_store_path}")
        setup_logging(self.log_file)

    def run(self):
        """
        Main function to process all PDF files in the data directory.
        """
        try:
            files = [f for f in os.listdir(self.data_dir) if f.lower().endswith('.pdf')]
        except FileNotFoundError:
            logging.error(f"Data directory not found: {self.data_dir}")
            return
        except Exception as e:
            logging.error(f"Error accessing data directory {self.data_dir}: {e}", exc_info=True)
            return

        if not files:
            logging.warning(f"No PDF files found in {self.data_dir}")
            return
        
        for filename in files:
            self.append_vector_store(filename)
            # archive_file(self.data_dir, filename)

    def append_vector_store(self, filename):
        """
        Loads data from a PDF file, creates embeddings, and appends it to the vector store.
        """ 
        file_path = os.path.join(self.data_dir, filename)
        try:
            logging.info(f"Processing {file_path}...")
            loader = PyPDFLoader(file_path=file_path)
            docs = loader.load()

            if not docs:
                logging.warning(f"No content found in {file_path}")
                return  
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(docs)

            if os.path.exists(self.vector_store_path):
                logging.info("Loading existing vector store...")
                vector_store = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    index_name='index',
                    allow_dangerous_deserialization=True
                )
                logging.info("Adding new documents to the vector store...")
                vector_store.add_documents(chunks)
            else:
                logging.info("Creating new vector store...")
                vector_store = FAISS.from_documents(chunks, self.embeddings)

            # Save the updated vector store
            vector_store.save_local(self.vector_store_path)
            logging.info(f"Vector store saved to {self.vector_store_path}")
        except Exception as e:
            logging.error(f"Error processing file {filename}: {e}", exc_info=True)
        
        return

if __name__ == "__main__":
    print("Starting indexing...")
    indexer = Indexer()
    indexer.run()
    print("Indexing completed.")