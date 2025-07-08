#!/usr/bin/env python3

import numpy as np
from sentence_transformers import SentenceTransformer
import requests
import json
import pickle
import os
import chromadb

EMBEDDING_DIM = 384
CHROMA_DATA_PATH = "/tmp/chroma_db"
COLLECTION_NAME = "appointments"
ID_TO_RECORD_PATH = "/tmp/id_to_record.pkl"

model = SentenceTransformer("all-MiniLM-L6-v2")

def call_slm_api(prompt):
    url = "http://35.238.160.181:11434/api/generate"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemma:2b",
        "prompt": prompt
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("Raw SLM API response text:", response.text)
        data = response.json()
        print("Raw SLM API response:", data)
        return data.get("response") or data.get("result") or data
    except requests.exceptions.RequestException as e:
        print(f"Error calling SLM API: {e}")
        return None

def main():
    # Load ChromaDB collection
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    collection = client.get_or_create_collection(COLLECTION_NAME)
    print("Loaded ChromaDB collection.")

    # Load id_to_record mapping
    if os.path.exists(ID_TO_RECORD_PATH):
        with open(ID_TO_RECORD_PATH, "rb") as f:
            id_to_record = pickle.load(f)
            print("Loaded id_to_record mapping.")
    else:
        print(f"Mapping file {ID_TO_RECORD_PATH} not found.")
        return

    # --- PROMPT: Use keywords matching your concatenation approach ---
    user_prompt = "appointment_status:Checked-Out"

    # Embed the prompt
    prompt_embedding = model.encode([user_prompt])[0].tolist()  # Chroma expects list[float]
    print("prompt_embedding length:", len(prompt_embedding))
    print("prompt_embedding type:", type(prompt_embedding[0]))

    # --- Chroma Search ---
    try:
        results = collection.query(
            query_embeddings=[prompt_embedding],
            n_results=5,
            include=['metadatas', 'documents', 'distances']
        )
        print("Chroma search successful.")
    except Exception as e:
        print(f"Error during Chroma search: {e}")
        return

    # --- Retrieve records by metadata and filter for 'Checked-Out' ---
    context_records = []
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    for meta, idx in zip(metadatas, ids):
        print("Retrieved index:", idx)
        if not meta:
            continue
        if meta.get('appointment_status') == 'Checked-Out':
            context_records.append(meta)

    if not context_records:
        print("No relevant records found.")
        return

    # --- Build prompt for SLM API ---
    context_text = "\n".join(
        f"Patient: {rec.get('patient_name', '[unknown]')}, Visit Type: {rec.get('visit_type', '[unknown]')}"
        for rec in context_records
    )
    dynamic_prompt = (
        f"{context_text}\n\n"
        f"List all patient names that were checked out and their visit type."
    )

    # --- Call SLM API ---
    response = call_slm_api(dynamic_prompt)
    print("SLM API Response:", response)

if __name__ == "__main__":
    main()
