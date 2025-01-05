import streamlit as st
from .document_processor import DocumentProcessor
from .rag_system import RAGSystem
import time

class GURUInterface:
    def __init__(self):
        self.processor = DocumentProcessor()
        self.rag_system = RAGSystem()
        
    def setup_interface(self):
        # Page configuration
        st.set_page_config(
            page_title="GURU Educational Platform",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Main title with styling
        st.markdown("""
        <h1 style='text-align: center;'>🎓 GURU - Educational Chatbot Creator</h1>
        """, unsafe_allow_html=True)
        
        # Sidebar configuration
        with st.sidebar:
            st.header("📚 Document Upload")
            
            # File uploader with multiple file types
            uploaded_files = st.file_uploader(
                "Upload your educational materials",
                accept_multiple_files=True,
                type=['txt', 'pdf', 'png', 'jpg', 'jpeg'],
                help="Supported formats: TXT, PDF, PNG, JPG"
            )
            
            # Process uploaded files
            if uploaded_files:
                with st.spinner("Processing documents... Please wait."):
                    try:
                        # Progress bar for document processing
                        progress_bar = st.progress(0)
                        for i, file in enumerate(uploaded_files):
                            progress = (i + 1) / len(uploaded_files)
                            progress_bar.progress(progress)
                            
                        documents = self.processor.process_documents(uploaded_files)
                        st.session_state.qa_chain = self.rag_system.create_knowledge_base(documents)
                        
                        # Success message with file count
                        st.success(f"✅ Successfully processed {len(uploaded_files)} document(s)!")
                        
                        # Display processed files
                        with st.expander("Processed Files"):
                            for file in uploaded_files:
                                st.text(f"📄 {file.name}")
                                
                    except Exception as e:
                        st.error(f"❌ Error processing documents: {str(e)}")
                        st.info("Please try uploading again or contact support if the error persists.")
            
            # Add system information
            with st.expander("ℹ️ System Information"):
                st.markdown("""
                - **Supported File Types**: PDF, TXT, Images (PNG, JPG)
                - **Max File Size**: 200MB
                - **Processing**: Text extraction & OCR for images
                """)
        
        # Main chat interface
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header("💬 Chat Interface")
            
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Chat history container
            chat_container = st.container()
            
            with chat_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask your question about the uploaded documents..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                with st.chat_message("user"):
                    st.write(prompt)
                
                with st.chat_message("assistant"):
                    if "qa_chain" in st.session_state:
                        with st.spinner("Thinking..."):
                            response = st.session_state.qa_chain({
                                "question": prompt,
                                "chat_history": [(m["content"], "") for m in st.session_state.messages[:-1]]
                            })
                            st.write(response["answer"])
                            st.session_state.messages.append(
                                {"role": "assistant", "content": response["answer"]}
                            )
                            
                            # Show sources if available
                            if response.get("source_documents"):
                                with st.expander("View Sources"):
                                    for i, doc in enumerate(response["source_documents"]):
                                        st.markdown(f"**Source {i+1}:**")
                                        st.text(doc.page_content[:200] + "...")
                    else:
                        st.warning("🚨 Please upload some documents first!")
        
        with col2:
            st.header("📊 Session Info")
            if "messages" in st.session_state:
                st.metric("Messages Count", len(st.session_state.messages))
            
            if "qa_chain" in st.session_state:
                st.success("System Ready")
                if st.button("Clear Chat History"):
                    st.session_state.messages = []
                    st.experimental_rerun()
            else:
                st.error("Waiting for Documents")
            
            # Tips section
            with st.expander("💡 Tips"):
                st.markdown("""
                - Upload multiple documents to enhance the knowledge base
                - Ask specific questions for better responses
                - Use clear and concise language
                - Check sources for answer verification
                """)

def custom_css():
    st.markdown("""
        <style>
        .stButton button {
            width: 100%;
        }
        .stProgress .st-bo {
            background-color: #00ff00;
        }
        </style>
    """, unsafe_allow_html=True)