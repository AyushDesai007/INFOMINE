from .llm_loader import load_llm

def generate_quiz(text_chunks):
    llm_pipeline = load_llm()
    questions = []
    
    for chunk in text_chunks[:5]:
        q_prompt = f"Ask a specific question based on this text:\n\n{chunk}\n\nQuestion:"
        try:
            q_response = llm_pipeline(q_prompt, max_length=150, truncation=True)
            generated_question = q_response[0]['generated_text'].strip()
            
            if len(generated_question) < 5:
                continue
                
            a_prompt = f"Answer the following question explicitly using the text below.\n\nText:\n{chunk}\n\nQuestion:\n{generated_question}\n\nAnswer:"
            a_response = llm_pipeline(a_prompt, max_length=150, truncation=True)
            generated_answer = a_response[0]['generated_text'].strip()
            
            questions.append({
                "question": generated_question,
                "options": [], 
                "answer": generated_answer,
                "explanation": "Generated from the document chunk locally."
            })
            
        except Exception as e:
            print(f"Error generating Q&A: {str(e)}")
            continue
            
    if not questions:
        return [{"question": "Error", "answer": "The local LLM failed to generate valid text."}]
        
    return questions
