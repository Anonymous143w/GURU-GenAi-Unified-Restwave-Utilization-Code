import sys
import os
from typing import List, Union
from pathlib import Path
import tempfile
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHUNK_SIZE, CHUNK_OVERLAP

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredImageLoader,
)

from PIL import Image
import pytesseract

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )
        
    def _save_upload_to_temp(self, uploaded_file) -> str:
        """Save uploaded file to temporary location and return path."""
        suffix = Path(uploaded_file.name).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            return tmp.name
            
    def _process_text(self, file) -> List[str]:
        """Process text files."""
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            content = file.read().decode('latin-1')
        return self.text_splitter.split_text(content)

    def _process_pdf(self, file) -> List[str]:
        """Process PDF files."""
        temp_path = self._save_upload_to_temp(file)
        loader = PyPDFLoader(temp_path)
        pages = loader.load()
        texts = [page.page_content for page in pages]
        os.unlink(temp_path)  # Clean up temp file
        return self.text_splitter.split_text('\n'.join(texts))

    def _process_image(self, file) -> List[str]:
        """Process image files using OCR."""
        temp_path = self._save_upload_to_temp(file)
        try:
            # Use UnstructuredImageLoader for better image handling
            loader = UnstructuredImageLoader(temp_path)
            image_document = loader.load()
            text = '\n'.join([doc.page_content for doc in image_document])
        except Exception as e:
            # Fallback to basic OCR if UnstructuredImageLoader fails
            image = Image.open(temp_path)
            text = pytesseract.image_to_string(image)
        finally:
            os.unlink(temp_path)  # Clean up temp file
        
        return self.text_splitter.split_text(text)

    def process_documents(self, files) -> List[str]:
        """Process multiple documents of different types."""
        all_chunks = []
        
        for file in files:
            file_extension = Path(file.name).suffix.lower()
            
            try:
                if file_extension == '.txt':
                    chunks = self._process_text(file)
                elif file_extension == '.pdf':
                    chunks = self._process_pdf(file)
                elif file_extension in ['.png', '.jpg', '.jpeg']:
                    chunks = self._process_image(file)
                else:
                    continue  # Skip unsupported file types
                    
                all_chunks.extend(chunks)
            except Exception as e:
                print(f"Error processing {file.name}: {str(e)}")
                continue
                
        return all_chunks