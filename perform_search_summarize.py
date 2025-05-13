import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Load FAISS index
faiss_index = faiss.read_index("/tmp/faiss_index")  # Adjust path as needed

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load T5 model and tokenizer
t5_model = T5ForConditionalGeneration.from_pretrained("t5-small")
t5_tokenizer = T5Tokenizer.from_pretrained("t5-small")

def similarity_search_ids(query, faiss_index, embedding_model, k=3):
    query_vec = embedding_model.encode([query])[0].astype(np.float32)
    query_vec = np.expand_dims(query_vec, axis=0)
    distances, indices = faiss_index.search(query_vec, k)
    return indices[0], distances[0]

def generate_with_t5(top_ids, user_query, t5_model, t5_tokenizer):
    # Convert IDs to string for context
    context = " ".join(str(i) for i in top_ids if i != -1)
    prompt = f"question: {user_query} context: {context}"
    input_ids = t5_tokenizer(prompt, return_tensors="pt").input_ids
    output_ids = t5_model.generate(input_ids, max_length=128, num_beams=4, early_stopping=True)
    output_text = t5_tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return output_text

if __name__ == "__main__":
    user_query = input("Enter your query: ").strip()
    if not user_query:
        print("No input provided. Exiting.")
    else:
        # 1. Similarity search (get top vector IDs)
        top_ids, top_distances = similarity_search_ids(user_query, faiss_index, embedding_model, k=3)
        print("\nTop retrieved vector IDs and distances:")
        for idx, dist in zip(top_ids, top_distances):
            if idx != -1:
                print(f"ID: {idx}, Distance: {dist:.4f}")
        # 2. Pass IDs to T5
        t5_output = generate_with_t5(top_ids, user_query, t5_model, t5_tokenizer)
        print("\nT5 Output:\n", t5_output)
