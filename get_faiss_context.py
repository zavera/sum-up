import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import requests
import logging
import os
import pickle

# --- CONFIGURATION ---
EMBEDDING_DIM = 384
INDEX_PATH = "/tmp/faiss_index"
CONTEXTS_PATH = "/tmp/faiss_contexts.pkl"  # List of texts in same order as index IDs
MODEL_NAME = "all-MiniLM-L6-v2"
SLM_API_URL = "http://35.238.160.181:11434/api/generate"  # Replace with your SLM API endpoint
TOP_K = 5

logging.basicConfig(level=logging.INFO)

def load_faiss_index(index_path, dimension):
    if os.path.exists(index_path):
        return faiss.read_index(index_path)
    else:
        raise FileNotFoundError(f"FAISS index not found at {index_path}")

def load_contexts(contexts_path):
    if os.path.exists(contexts_path):
        with open(contexts_path, "rb") as f:
            return pickle.load(f)  # Should be a list of strings
    else:
        raise FileNotFoundError(f"Contexts file not found at {contexts_path}")

def get_top_k_contexts(query, model, faiss_index, contexts, k=5):
    query_embedding = model.encode([query], convert_to_numpy=True)
    D, I = faiss_index.search(query_embedding, k)
    retrieved_contexts = [contexts[idx] for idx in I[0] if idx != -1]
    return retrieved_contexts

def build_prompt(user_input, contexts):
    context_str = "\n\n".join(contexts)
    prompt = (
        f"Context:\n{context_str}\n\n"
        f"Question: {user_input}\n\n"
        "Please summarize the context and answer the question above as clearly and concisely as possible."
    )
    return prompt

def call_slm_api(prompt):
    payload = {"prompt": prompt, "max_tokens": 256}
    response = requests.post(SLM_API_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("completion", response.text)
    else:
        raise Exception(f"SLM API error: {response.status_code} {response.text}")

def main():
    # Load resources
    model = SentenceTransformer(MODEL_NAME)
    faiss_index = load_faiss_index(INDEX_PATH, EMBEDDING_DIM)
    contexts = load_contexts(CONTEXTS_PATH)

    # Get user input
    user_input = input("Please enter your question or topic: ").strip()
    if not user_input:
        print("No input provided.")
        return

    # Retrieve relevant contexts
    top_contexts = get_top_k_contexts(user_input, model, faiss_index, contexts, TOP_K)
    if not top_contexts:
        print("No relevant context found.")
        return

    # Build prompt for SLM
    prompt = build_prompt(user_input, top_contexts)
    print("\n--- Prompt sent to SLM ---\n")
    print(prompt)
    print("\n--- Generating summary/answer... ---\n")

    # Call SLM API
    try:
        result = call_slm_api(prompt)
        print("SLM Response:\n", result)
    except Exception as e:
        print("Error calling SLM API:", e)

if __name__ == "__main__":
    main()
