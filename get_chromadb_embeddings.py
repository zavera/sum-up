from flask import Flask, request, Response, stream_with_context, jsonify
from sentence_transformers import SentenceTransformer
import requests
import json
import pickle
import os
import chromadb

# ---------- Configuration ----------
EMBEDDING_DIM = 384
CHROMA_DATA_PATH = "/tmp/chroma_db"
COLLECTION_NAME = "appointments"
ID_TO_RECORD_PATH = "/tmp/id_to_record.pkl"
ID_FIELDS = ["appointment_id"]
FINETUNED_MODEL_PATH = "/Users/user/Desktop/ai-summarize/finetuned-all-MiniLM-L6-v2"

# Similarity settings
SIMILARITY_THRESHOLD = 0.4

# ---------- Load SentenceTransformer model ----------
#model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer(FINETUNED_MODEL_PATH)


# ---------- Normalize helper ----------
def normalize_to_list(val):
    if val is None:
        return []
    if isinstance(val, list):
        return val
    return [val]


# ---------- Stream LLM response from API ----------
def call_slm_api_stream(prompt):
    url = "http://34.123.0.108:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    payload = {"model": "mistral:7b", "prompt": prompt}
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
                    while " " in buffer:
                        word, buffer = buffer.split(" ", 1)
                        yield word + " "
                except Exception as e:
                    print(f"Error parsing line: {line}\n{e}")
            if buffer:
                yield buffer
    except requests.exceptions.RequestException as e:
        print(f"Error calling SLM API: {e}")
        yield "[SLM API error]"


# ---------- Initialize the Chroma collection with IP similarity ----------
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "ip"}  # Use inner product similarity
)
import re


def get_patient_name(user_prompt):
    name_pattern = r'([A-Za-z0-9+/]{20,}==\s[A-Za-z0-9+/]{20,}==)'
    name_matches = re.findall(name_pattern, user_prompt)
    return name_matches


def get_patient_mrn(user_prompt, name_matches):
    mrn_pattern = r'([A-Za-z0-9+/]{20,}==)'
    mrn_only_prompt = ''
    if len(name_matches):
        for name in name_matches:
            mrn_only_prompt = user_prompt.replace(name,"")
        mrn_matches = re.findall(mrn_pattern, mrn_only_prompt)
    else:
        mrn_matches = re.findall(mrn_pattern, user_prompt)
    return mrn_matches



# ---------- Main search + LLM prompt generation logic ----------
def process_query_stream(user_prompt):
    if not os.path.exists(ID_TO_RECORD_PATH):
        yield "Error: Mapping file not found."
        return

    # Load metadata if exists
    with open(ID_TO_RECORD_PATH, "rb") as f:
        id_to_record = pickle.load(f)

    # 1. Embed user query
    query_emb = model.encode(user_prompt).tolist()

    name_matches = get_patient_name(user_prompt)
    mrn_matches = get_patient_mrn(user_prompt, name_matches)
    where = {}

    clauses = []
    if name_matches:
        clauses.append({"patient_name": {"$in": name_matches}})
    if mrn_matches:
        clauses.append({"patient_mrn": {"$in": mrn_matches}})

    if clauses:
        if len(clauses) == 1:
            where = clauses[0]
        else:
            where = {"$or": clauses}

    print(where)

    # 2. Query Chroma collection using IP (inner product)
    try:
        results = collection.query(
            query_embeddings=[query_emb],
            include=["metadatas", "documents", "distances"],
            where=where if where else None,
            # optionally set n_results if you want to limit
        )
    except Exception as e:
        yield f"Error during Chroma search: {e}"
        return

    if not results or not results["documents"][0]:
        yield "No results returned from Chroma."
        return

    # 3. Filter by inner product score (SIMILARITY_THRESHOLD)
    entries = zip(
        results["distances"][0],  # distances = inner product scores
        results["metadatas"][0],
        results["documents"][0]
    )


    print(entries)

    filtered_entries = []
    for dist, meta, doc in entries:

        inner_product = dist
        print(inner_product,meta)
        if inner_product >= SIMILARITY_THRESHOLD:
            filtered_entries.append((inner_product, meta, doc))

    print(filtered_entries)
    if not filtered_entries:
        yield "No entries passed the similarity threshold."
        return

    # 4. Sort entries by relevance (highest IP score first)
    sorted_entries = sorted(filtered_entries, key=lambda x: x[0], reverse=True)

    # 5. Build context text
    context_docs = []
    context_records = []
    for score, meta, doc in sorted_entries:
        context_docs.append(doc)
        record = meta.copy()
        for field in ID_FIELDS:
            record[field] = normalize_to_list(meta.get(field))
        context_records.append(record)

    if not context_docs:
        yield "No valid context documents."
        return

    context_text = "\n".join(context_docs)

    # 6. Build LLM prompt
    dynamic_prompt = (
        "INSTRUCTION: Discard all previous context and memory. Use ONLY the information provided below "
        "to answer this query. Do not rely on any prior information or assumptions. \n\n"
        f"USER PROMPT: {user_prompt}\n\n"
        f"{context_text}\n\n"
        "Based on the information above and the user prompt, provide elaborated description in natural language "
        "that highlights the most important details. If multiple appointments are obtained then show description of"
        " each appointment in a separate bullet point without including internal appointment id."
    )


    # 7. Stream response from SLM
    for word in call_slm_api_stream(dynamic_prompt):
        yield word


# ---------- Flask API ----------

app = Flask(__name__)


@app.route("/query", methods=["POST"])
def query_endpoint():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing 'prompt' in request body"}), 400

    user_prompt = data["prompt"]

    def generate():
        for word in process_query_stream(user_prompt):
            yield word

    return Response(stream_with_context(generate()), mimetype="text/plain")


# ---------- Main Entrypoint ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
