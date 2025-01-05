import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import OPENAI_API_KEY, TEMPERATURE, DB_PATH

from langchain_community.embeddings import OpenAIEmbeddings  # Updated import
from langchain_community.chat_models import ChatOpenAI  # Updated import
from langchain.chains import ConversationalRetrievalChain  # Updated import
from langchain_community.vectorstores import FAISS  # Updated import
from langchain_community.docstore.document import Document  # Updated import

class RAGSystem:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.llm = ChatOpenAI(temperature=TEMPERATURE)
        
    def create_knowledge_base(self, texts):
        # Convert text chunks to Documents
        documents = [Document(page_content=text) for text in texts]
        
        # Create FAISS vector store
        vectorstore = FAISS.from_documents(documents, self.embeddings)
        
        # Create conversational chain
        chain = ConversationalRetrievalChain.from_llm(
            self.llm,
            vectorstore.as_retriever(search_kwargs={"k": 3}),  # Retrieve top 3 most relevant chunks
            return_source_documents=True
        )