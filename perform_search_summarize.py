import numpy as np
import faiss

from sentence_transformers import SentenceTransformer
from transformers import T5Tokenizer, T5ForConditionalGeneration

from huggingface_hub import InferenceClient
HF_TOKEN='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'

client = InferenceClient(token=HF_TOKEN)


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

from transformers import T5Tokenizer, T5ForConditionalGeneration

def generate_with_chat_completion(
        chat_history,
        model_name="GeorgiaTech/t5-small-finetuned",
        callback=None,
        max_length=128
):
    """
    Simulate chat completion using a T5 model.
    - chat_history: list of (role, message) tuples, e.g. [("user", "Hi"), ("assistant", "Hello!")]
    - callback: function to call with the generated reply
    """
    # Load model and tokenizer
    tokenizer = T5Tokenizer.from_pretrained(model_name)
    model = T5ForConditionalGeneration.from_pretrained(model_name)

    # Format the chat history as a single prompt
    prompt = "summarize: "
    for role, message in chat_history:
        prompt += f"{role}: {message} "

    # Tokenize and generate
    inputs = tokenizer(prompt.strip(), return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(**inputs, max_length=max_length, num_beams=4, early_stopping=True)
    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Call the callback with the reply
    if callback:
        callback(reply)
    return reply

# Example callback function
def my_callback(response):
    print("Assistant:", response)

# Example chat history and usage
chat_history = [
    ("user", "list cancelled appointments")]



# Example usage:
def my_callback(response):
    print("Callback received response:", response)

# generate_with_chat_completion([1, 2, 3], "What is the capital of France?", hf_token="hf_xxx", callback=my_callback)


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
        chat_history = [("user", user_query)]
        # Optionally, you could append retrieved content here if available

        # 3. Pass chat history to T5 and print the output via callback
        generate_with_chat_completion(chat_history, callback=my_callback)

