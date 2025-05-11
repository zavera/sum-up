from kafka import KafkaConsumer
import json
import logging
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import os

# Load embedding model once (e.g., all-MiniLM-L6-v2)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Path to persist FAISS index
FAISS_INDEX_PATH = 'faiss_appointments.index'

# Initialize or load FAISS index
def load_faiss_index(dim):
    if os.path.exists(FAISS_INDEX_PATH):
        return faiss.read_index(FAISS_INDEX_PATH)
    else:
        return faiss.IndexFlatL2(dim)

def message_to_text(row):
    # Concatenate relevant fields as a single string for embedding
    return ' '.join(str(row[k]) for k in sorted(row.keys()))

def embed_row(row):
    text = message_to_text(row)
    embedding = model.encode([text])[0]  # Returns a numpy array
    return embedding.astype('float32')

def process_msg(msg:str):

    # Get embedding dimension from the model
    sample_embedding = embed_row({
        'appointment_id': 0, 'patient_id': 0, 'patient_name': '', 'patient_mrn': '',
        'scheduled_start_time': 0, 'scheduled_end_time': 0, 'visit_type': '',
        'visit_template': '', 'study_name': '', 'appointment_status': '',
        'appointment_status_reason': '', 'comment': ''
    })
    dim = sample_embedding.shape[0]
    index = load_faiss_index(dim)

    embedding = embed_row(msg)
    # Add to FAISS index (reshape to 2D array for FAISS)
    index.add(np.array([embedding]))
    logging.info(f"Processed row: {msg}")
    logging.info(f"Vector embedding: {embedding.tolist()}")
    # Persist the index after each addition (or batch for efficiency)
    faiss.write_index(index, FAISS_INDEX_PATH)
    print("Row embedded and persisted.")
