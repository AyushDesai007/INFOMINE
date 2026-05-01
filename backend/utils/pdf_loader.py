import io
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

def get_pdf_text(pdf_files_bytes):
    """
    Extracts text from a list of PDF file bytes.
    """
    text = ""
    for pdf_bytes in pdf_files_bytes:
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_bytes))
            for page in pdf_reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
        except Exception as e:
            print(f"Error reading PDF: {e}")
    return text

def get_text_chunks(text, chunk_size=120, chunk_overlap=20):
    if not text:
        return []
        
    words = text.split()
    chunks = []
    
    word_chunk_size = max(1, chunk_size // 5)
    word_overlap = max(1, chunk_overlap // 5)
    
    i = 0
    while i < len(words):
        chunk_words = words[i:i + word_chunk_size]
        chunk_text = " ".join(chunk_words)
        chunks.append(chunk_text)
        
        i += (word_chunk_size - word_overlap)
        
        if word_chunk_size <= word_overlap:
            i += 1
            
    return chunks

def build_vector_store(text_chunks):
    if not text_chunks:
        raise ValueError("No text provided to build the vector store.")
        
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    embeddings = model.encode(text_chunks, show_progress_bar=False)
    embeddings = np.array(embeddings).astype('float32')
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    index_to_chunk = {i: chunk for i, chunk in enumerate(text_chunks)}
    
    return {
        "index": index,
        "mapping": index_to_chunk,
        "embedder": model
    }
