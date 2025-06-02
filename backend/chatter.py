"""Chatter
Runs a chatbot that uses a vector store to retrieve and answer questions.
"""

import os, logging

from dotenv import load_dotenv

from utils.helpers import setup_logging
from langchain_core.output_parsers import StrOutputParser
from retriever import Retriever
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

load_dotenv()
class Chatter:
    """Core chatbot logic integrating retrieval and response generation."""
    def __init__(self, log_file='chatter.log') -> None:
        self.data_dir = 'data'
        self.log_file = os.path.join(self.data_dir, log_file)
        setup_logging(self.log_file)
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            logging.error("OpenAI API key is not set.")
            raise ValueError("OpenAI API key is required. Please set the OPENAI_API_KEY environment variable.")

        self.retriever = Retriever()
        self.llm = ChatOpenAI(model_name='gpt-4o-mini', openai_api_key=self.openai_api_key)
        self.qa_chain = self.create_qa_chain()

    def create_qa_chain(self):
        """
        Creates a QA chain using a prompt template and a language model.
        """
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are an AI assistant specialized in legal documents, especially in EU AI Act.\n"
                "Use the following context to answer the question.\n\n"
                "Context:\n{context}\n\n"
                "Question:\n{question}\n\n"
                "Answer in a clear and concise manner."
                "Don't answer questions that are not related to the context."
                "If you don't know the answer, say 'I don't know'."
            )
        )

        qa_chain = prompt_template | self.llm | StrOutputParser()
        return qa_chain

    def chat(self, query):
        """
        Processes a user query and returns a response.
        """
        try:
            logging.info(f"Received query: {query}")
            docs = self.retriever.retrieve(query=query,k=5)
            response = self.qa_chain.invoke({
                "question": query,
                "context": docs  
                # "contexts": "\n---\n".join([d.page_content for d in docs])
            })
            logging.info(f"Generated response: {response}")
            return response
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
