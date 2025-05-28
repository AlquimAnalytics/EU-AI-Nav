"""Chatter
Runs a chatbot that uses a vector store to retrieve and answer questions.
"""

import os, logging, json

from utils.helpers import setup_logging
# from vectorStoreRetriever import VectorStoreRetriever
from retriever import Retriever
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class Chatter:
    """Core chatbot logic integrating retrieval and response generation."""
    def __init__(self, log_file='chatter.log') -> None:
        self.data_dir = 'ject/data'
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')

        if not self.openai_api_key:
            logging.error("OpenAI API key is not set.")
            raise ValueError("OpenAI API key is required.")

        self.retriever = Retriever()
        self.llm = ChatOpenAI(model_name='gpt-4', openai_api_key=self.openai_api_key)
        self.qa_chain = self.create_qa_chain()

    def create_qa_chain(self):
        """
        Creates a RetrievalQA chain integrating the retriever and the language model.
        """
        if self.retriever.docsearch is None:
            logging.error("Vector store is not loaded in the retriever.")
            raise ValueError("Vector store is not available.")

        retriever = self.retriever.docsearch.as_retriever(search_kwargs={"k": 5})

        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are an AI assistant specialized in legal documents.\n"
                "Use the following context to answer the question.\n\n"
                "Context:\n{context}\n\n"
                "Question:\n{question}\n\n"
                "Answer in a clear and concise manner."
            )
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt_template}
        )

        return qa_chain

    def chat(self, query):
        """
        Processes a user query and returns a response.
        """
        try:
            logging.info(f"Received query: {query}")
            response = self.qa_chain.invoke({"query": query})
            logging.info(f"Generated response: {response}")
            return response['result']
        except Exception as e:
            logging.error(f"Failed to generate response: {e}", exc_info=True)
            return "I'm sorry, but I couldn't process your request at this time."

if __name__ == "__main__":
    chatter = Chatter()

    while True:
        query = input("User: ")
        if query.lower() in ['exit', 'quit']:
            break
        response = chatter.chat(query)
        print(f"Assistant: {response}")
