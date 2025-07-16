import pickle
from sentence_transformers import SentenceTransformer, losses, evaluation
from torch.utils.data import DataLoader, random_split

# Load your InputExamples
with open("input_examples.pkl", "rb") as f:
    all_examples = pickle.load(f)

# Set desired split ratio for validation
val_ratio = 0.15  # 15% for validation
val_size = int(len(all_examples) * val_ratio)
train_size = len(all_examples) - val_size

# Split data for training and validation
train_examples, val_examples = random_split(all_examples, [train_size, val_size])

# Create DataLoaders
batch_size = 32  # larger batch sizes for more stable updates if memory allows
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=batch_size)
val_dataloader = DataLoader(val_examples, shuffle=False, batch_size=batch_size)

# Load model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Set up loss function
train_loss = losses.CosineSimilarityLoss(model)

# Optional: Setup validation evaluator (Semantic textual similarity evaluator)
val_evaluator = evaluation.EmbeddingSimilarityEvaluator.from_input_examples(list(val_examples), name='val')

# Set learning rate and epochs
num_epochs = 3       # recommended: 3+, monitor val loss
warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)  # 10% of training steps

# Fine-tune model with validation evaluator and checkpointing
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=num_epochs,
    warmup_steps=warmup_steps,
    evaluator=val_evaluator,
    evaluation_steps=max(1, len(train_dataloader)//2),
    output_path="finetuned-all-MiniLM-L6-v2",
    show_progress_bar=True,
    optimizer_params={'lr': 2e-5}   # conservative LR for finetuning
)

print("Training finished. Best model saved in: finetuned-all-MiniLM-L6-v2")
