from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class LocalLLMPipeline:
    def __init__(self, model_id="google/flan-t5-base"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id).to(self.device)
        
    def __call__(self, prompt, max_length=512, truncation=True, **kwargs):
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=truncation, max_length=512).to(self.device)
        min_tokens = kwargs.get('min_new_tokens', 10)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs, 
                max_new_tokens=max_length,
                min_new_tokens=min_tokens,
                num_return_sequences=1,
                repetition_penalty=1.2,
                no_repeat_ngram_size=3,
                do_sample=True,
                temperature=0.3,
                top_p=0.9,
                length_penalty=2.0
            )
        result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return [{"generated_text": result}]

# Singleton instance
_llm_pipeline = None

def load_llm():
    global _llm_pipeline
    if _llm_pipeline is None:
        _llm_pipeline = LocalLLMPipeline()
    return _llm_pipeline
