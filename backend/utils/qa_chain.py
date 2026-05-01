import numpy as np
from .llm_loader import load_llm

def ask_question(query, vectorstore, history=None):
    llm_pipeline = load_llm()
    index = vectorstore["index"]
    mapping = vectorstore["mapping"]
    embedder = vectorstore["embedder"]
    
    query_emb = embedder.encode([query], show_progress_bar=False).astype('float32')
    
    k = 3
    distances, indices = index.search(query_emb, k)
    
    context_texts = []
    for i in indices[0]:
        if i != -1 and i in mapping:
            context_texts.append(mapping[i])
            
    context_str = "\n".join(context_texts)
    
    prompt = f"""You are INFOMINE, an offline document intelligence assistant. You help users understand, summarize, and quiz themselves on their uploaded PDF documents. You are precise, concise, and grounded only in the document content provided to you.

Core Principles:
1. GROUNDED ANSWERS ONLY: Never generate information not found in the provided document context. If the answer is not in the context, say: "I could not find this in your documents."
2. CITE YOUR SOURCE: Always mention the section, page, or chunk where you found the answer.
3. CONCISE BY DEFAULT: Answer in 2-4 sentences unless the user asks for detail. Avoid padding.
4. PLAIN LANGUAGE: Explain clearly. Avoid jargon unless the document uses it.
5. ONE THING AT A TIME: Don't mix Q&A, summary, and quiz in one response unless explicitly asked.
6. HONEST UNCERTAINTY: If the context is ambiguous or incomplete, say so clearly instead of guessing.

Context:
{context_str}

Question: {query}

Answer:"""

    try:
        response = llm_pipeline(prompt, max_length=200, truncation=True)
        bot_response = response[0]['generated_text'].strip()
        return bot_response
    except Exception as e:
        return f"Error generating answer: {str(e)}"
