import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from load_faiss_embeddings import faiss_index


# Example: initialize or load these globally in your script
EMBEDDING_DIM = 384  # or your model's dimension
INDEX_PATH = "/tmp/faiss_index"
EMBEDDING_FIELDS = ["field1", "field2"]  # list of fields to concatenate for embedding
ID_FIELD = "id"
model = SentenceTransformer("all-MiniLM-L6-v2")


def save_faiss_index(index, index_path):
    faiss.write_index(index, index_path)


def embed_message(after):
    """
    after: dict, e.g. {"id": 123, "field1": "text", "field2": "more text", ...}
    """
    try:
        # Compose the text to embed from specified fields
        text = " ".join(str(after.get(f, "")) for f in EMBEDDING_FIELDS if after.get(f))
        if not text.strip():
            return  # Nothing to embed

        record_id = int(after[ID_FIELD])
        embedding = model.encode([text])[0].astype(np.float32)
        embedding = np.expand_dims(embedding, axis=0)
        id_array = np.array([record_id], dtype=np.int64)

        # Remove old vector if exists, then add new
        faiss_index.remove_ids(id_array)
        faiss_index.add_with_ids(embedding, id_array)

        # Persist index after update
        save_faiss_index(faiss_index, INDEX_PATH)

    except Exception as e:
        print(f"Error embedding message {after}: {e}")
