from .llm_loader import load_llm

def summarize_document(text_chunks):
    llm_pipeline = load_llm()
    total_chunks = len(text_chunks)
    if total_chunks == 0:
        return "Not enough text to summarize."
        
    # We want exactly 5 to 6 points. Let's aim for 5 if the doc is small, or 6.
    num_points = 5 if total_chunks <= 5 else 6
    
    # Select 'num_points' representative chunks evenly spread across the document
    if total_chunks <= num_points:
        selected_chunks = text_chunks
    else:
        step = total_chunks / num_points
        selected_chunks = [text_chunks[int(i * step)] for i in range(num_points)]
        
    summary_points = []
    
    for idx, chunk in enumerate(selected_chunks):
        # Truncate chunk if needed to keep LLM context small and focused
        words = chunk.split()
        if len(words) > 150:
            chunk = " ".join(words[:150])
            
        prompt = f"Extract the single most important, highly efficient key point from the following text in exactly one clear sentence.\n\nText:\n{chunk}\n\nKey Point:"
        
        try:
            response = llm_pipeline(prompt, max_length=100, min_new_tokens=15, truncation=True)
            point = response[0]['generated_text'].strip()
            
            # Clean up potential LLM weirdness
            point = point.replace("\n", " ").strip("-").strip("*").strip()
            if point and len(point) > 10:
                # Ensure it ends with a period and starts capitalized
                if not point.endswith('.'):
                    point += '.'
                point = point[0].upper() + point[1:]
                summary_points.append(f"- {point}")
        except Exception as e:
            print(f"Error generating point {idx}: {e}")
            
    if not summary_points:
        return "Failed to generate efficient summary."
        
    return "\n".join(summary_points)
