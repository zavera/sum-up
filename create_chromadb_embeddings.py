import logging
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

# Configuration
EMBEDDING_DIM = 384
CHROMA_DATA_PATH = "/tmp/chroma_db"
COLLECTION_NAME = "appointments"
ID_FIELDS = ["appointment_id", "visit_id", "resource_id"]  # <-- Modified to support multiple IDs
model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB persistent client and collection
client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
collection = client.get_or_create_collection(COLLECTION_NAME)

# Load or initialize id_to_record mapping
ID_TO_RECORD_PATH = "/tmp/id_to_record.pkl"
if os.path.exists(ID_TO_RECORD_PATH):
    with open(ID_TO_RECORD_PATH, "rb") as f:
        id_to_record = pickle.load(f)
else:
    id_to_record = {}

def save_id_to_record(mapping, path):
    with open(path, "wb") as f:
        pickle.dump(mapping, f)

def get_id_list(after):
    """
    Returns a list of string IDs from the after dict, for all ID_FIELDS.
    """
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

def embed_message(after):
    """
    after: dict, e.g. {"appointment_id": 123, "visit_id": 456, "resource_id": 789, ...}
    """
    try:
        # Exclude all ID fields from the embedding text
        text = " ".join(str(after.get(f, "")) for f in after if after.get(f) and f not in ID_FIELDS)
        logging.info(text)
        if not text.strip():
            return  # Nothing to embed

        # Use a composite ID by joining all present IDs with underscores
        id_list = get_id_list(after)
        if not id_list:
            raise ValueError("No valid ID fields found in record.")
        record_id = "_".join(id_list)  # Composite ID for uniqueness

        embedding = model.encode([text])[0].tolist()  # Chroma expects list[float]

        # Remove old vector if exists
        try:
            collection.delete(ids=[record_id])
        except Exception:
            pass  # Ignore if not present

        # Add new embedding with metadata and text
        collection.add(
            embeddings=[embedding],
            ids=[record_id],
            metadatas=[after],
            documents=[text]
        )

        # Update and persist id_to_record mapping
        id_to_record[record_id] = after
        save_id_to_record(id_to_record, ID_TO_RECORD_PATH)

    except Exception as e:
        logging.error(f"Error embedding message {after}: {e}")

def main():
    print("this is a test.")
    # Example usage:
    # after = {"appointment_id": 123, "visit_id": 456, "resource_id": 789, "appointment_status": "Checked-Out"}
    # embed_message(after)

if __name__ == "__main__":
    main()
