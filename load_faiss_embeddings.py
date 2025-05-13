
import faiss
from sentence_transformers import SentenceTransformer
import logging

# Example: initialize or load these globally in your script
EMBEDDING_DIM = 384  # or your model's dimension
INDEX_PATH = "/tmp/faiss_index"



logging.basicConfig(
    level=logging.INFO,
    filename='/tmp/load_faiss_embeddings.log',  # Log file path
    filemode='a',                 # Append mode
    format='%(asctime)s %(levelname)s:%(message)s'
)

# Load or create FAISS index (should be done outside this function for efficiency)
def load_faiss_index(index_path, dimension):
    import os
    logging.info("inside load")
    if os.path.exists(index_path):
        return faiss.read_index(index_path)
    else:
        base_index = faiss.IndexFlatL2(dimension)
        return faiss.IndexIDMap(base_index)

faiss_index = load_faiss_index(INDEX_PATH, EMBEDDING_DIM)
logging.info(f"works")

def main():
    # faiss_index is already initialized and available here
    #print("FAISS index is ready with", faiss_index.ntotal, "vectors.")
    logging.info(f"FAISS index is ready with: {faiss_index.ntotal} vectors")
if __name__ == "__main__":
    main()
