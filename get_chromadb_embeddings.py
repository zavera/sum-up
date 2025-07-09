from flask import Flask, request, Response, stream_with_context, jsonify
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
ID_FIELDS = ["appointment_id", "visit_id", "resource_id"]

def normalize_to_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]

def call_slm_api_stream(prompt):
    url = "http://35.238.160.181:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {"model": "gemma:2b", "prompt": prompt}
    try:
        with requests.post(url, json=payload, headers=headers, stream=True) as response:
            response.raise_for_status()
            buffer = ""
            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    buffer += obj.get("response", "")
                    # Yield each word as soon as it's available
                    while " " in buffer:
                        word, buffer = buffer.split(" ", 1)
                        yield word + " "
                except Exception as e:
                    print(f"Error parsing line: {line}\n{e}")
            # Yield any remaining buffer
            if buffer:
                yield buffer
    except requests.exceptions.RequestException as e:
        print(f"Error calling SLM API: {e}")
        yield "[SLM API error]"

# Load ChromaDB collection
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)

def process_query_stream(user_prompt):


    # Load id_to_record mapping
    if os.path.exists(ID_TO_RECORD_PATH):
        with open(ID_TO_RECORD_PATH, "rb") as f:
            id_to_record = pickle.load(f)
    else:
        yield "Error: Mapping file not found."
        return

    # Embed the prompt
    prompt_embedding = model.encode([user_prompt])[0].tolist()

    # Chroma Search
    try:
        results = collection.query(
            query_embeddings=[prompt_embedding],
            n_results=5,
            include=['metadatas', 'documents', 'distances']
        )
    except Exception as e:
        yield f"Error during Chroma search: {e}"
        return

    # No filtering at all: include all returned records
    context_records = []
    metadatas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    for meta, idx in zip(metadatas, ids):
        if not meta:
            continue
        record = meta.copy()
        for field in ID_FIELDS:
            record[field] = normalize_to_list(meta.get(field))
        context_records.append(record)

    if not context_records:
        yield "No relevant records found."
        return

    # Build prompt for SLM API
    context_text = "\n".join(
        "; ".join(f"{k}: {v}" for k, v in rec.items())
        for rec in context_records
    )
    dynamic_prompt = (
        "INSTRUCTION: Discard all previous context and memory. Use ONLY the information provided below to answer this query. Do not rely on any prior information or assumptions.\n\n"
        f"USER PROMPT: {user_prompt}\n\n"
        f"{context_text}\n\n"
        "Based on the information above and the user prompt, write a concise summary (3 to 4 sentences) in natural language that highlights the most important details. "
        "If there are any names, descriptions, or key attributes, include them clearly without including digital ids. "
        "Where appropriate, provide a brief list of notable items or individuals mentioned, along with a short description for each."
    )

    # Stream words from SLM API
    for word in call_slm_api_stream(dynamic_prompt):
        yield word

# --- Flask App ---

app = Flask(__name__)

@app.route('/query', methods=['POST'])
def query_endpoint():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    def generate():
        user_prompt = data['prompt']
        for word in process_query_stream(user_prompt):
            yield word

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
