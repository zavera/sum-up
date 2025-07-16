import logging
import os
import pickle
from datetime import datetime
from sentence_transformers import SentenceTransformer
import chromadb

# Configuration
EMBEDDING_DIM = 384
CHROMA_DATA_PATH = "/tmp/chroma_db"
COLLECTION_NAME = "appointments"
ID_TO_RECORD_PATH = "/tmp/id_to_record.pkl"
ID_FIELDS = ["appointment_id", "visit_id", "resource_id"]

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# Initialize ChromaDB persistent client and collection
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
collection = client.get_or_create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:space": "ip"}
)

# Save the ID-to-record mapping
def save_id_to_record(mapping, path):
    with open(path, "wb") as f:
        pickle.dump(mapping, f)

def get_id_list(after):
    ids = []
    for field in ID_FIELDS:
        value = after.get(field)
        if value is None:
            continue
        if isinstance(value, list):
            ids.extend([str(v) for v in value])
        else:
            ids.append(str(value))
    return ids

# Convert UNIX timestamp (ms) to human-readable text
def format_timestamp(ts):
    try:
        dt = datetime.fromtimestamp(ts / 1000)
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:
        return str(ts)

# Convert structured metadata to natural language for embedding
def structured_to_text(data):
    parts = []

    appointment_id = data.get("appointment_id")
    patient_id = data.get("patient_id")
    patient_mrn = data.get("patient_mrn", "")
    patient_name = data.get("patient_name", "").strip()
    study_name = data.get("study_name", "").strip()
    visit_type = data.get("visit_type", "").strip()
    visit_template = data.get("visit_template", "").strip()
    appointment_status = data.get("appointment_status", "").strip()
    appointment_status_reason = data.get("appointment_status_reason", "").strip()
    comment = data.get("comment", "").strip()
    start_time = format_timestamp(data.get("scheduled_start_time"))
    end_time = format_timestamp(data.get("scheduled_end_time"))

    if study_name:
        parts.append(f"This appointment is part of the clinical study titled '{study_name}'.")

    if patient_name:
        parts.append(f"It was scheduled for patient '{patient_name}'.")
    elif patient_id:
        parts.append(f"It was scheduled for patient with ID {patient_id}.")

    if visit_type:
        parts.append(f"The type of visit is categorized as '{visit_type}'.")

    if visit_template:
        parts.append(f"The visit follows the template '{visit_template}'.")

    if start_time and end_time:
        parts.append(f"The appointment was originally scheduled from {start_time} to {end_time}.")

    if appointment_status:
        if appointment_status_reason:
            parts.append(f"The current status is '{appointment_status}' due to '{appointment_status_reason}'.")
        else:
            parts.append(f"The appointment has a status of '{appointment_status}'.")

    if comment:
        parts.append(f"Additional comment noted: '{comment}'.")

    # Optional: include internal IDs and MRNs for completeness (not used in LLM prompt)
    if appointment_id:
        parts.append(f"Internal appointment ID is {appointment_id}.")
    if patient_mrn:
        parts.append(f"Patient medical record number (MRN): {patient_mrn}.")

    return " ".join(parts)

# Main embedding entry point
def embed_message(after):
    try:
        # Load or initialize ID-to-record mapping
        if os.path.exists(ID_TO_RECORD_PATH):
            with open(ID_TO_RECORD_PATH, "rb") as f:
                id_to_record = pickle.load(f)
        else:
            logging.info(f"Mapping file not found — creating new at {ID_TO_RECORD_PATH}")
            id_to_record = {}

        # Convert to descriptive text for embedding
        text = structured_to_text(after)
        if not text.strip():
            logging.warning("No valid text to embed from record")
            return

        logging.info(f"Embedding text: {text}")

        # Get unique record ID
        id_list = get_id_list(after)
        if not id_list:
            raise ValueError("No valid ID fields found in record.")
        record_id = "_".join(id_list)

        # Generate embedding
        embedding = model.encode([text])[0].tolist()

        # Delete existing entry if present
        try:
            collection.delete(ids=[record_id])
        except Exception:
            pass

        # Add new embedding entry to ChromaDB
        collection.add(
            embeddings=[embedding],
            ids=[record_id],
            metadatas=[after],
            documents=[text]
        )

        # Save updated mapping
        id_to_record[record_id] = after
        with open(ID_TO_RECORD_PATH, "wb") as f:
            pickle.dump(id_to_record, f)

        logging.info(f"Stored record '{record_id}' in ChromaDB and updated mapping.")

    except Exception as e:
        logging.error(f"Error embedding record: {e}")

# Optional main test entry
def main():
    print("This module is designed to be imported and used by a CDC listener or batch processor.")

if __name__ == "__main__":
    main()
