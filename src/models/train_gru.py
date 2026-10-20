from pathlib import Path
import random

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
)


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODEL_DIR = PROJECT_ROOT / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

SEED = 42

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# ============================================================
# CONFIGURATION
# ============================================================

BATCH_SIZE = 256

HIDDEN_SIZE = 32

NUM_LAYERS = 1

DROPOUT = 0.0

LEARNING_RATE = 1e-3

EPOCHS = 8

PATIENCE = 3


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print(
    "GLYCOTWIN GRU TRAINING"
)

print("=" * 60)

print(
    f"Device: {DEVICE}"
)

print(
    f"PyTorch: {torch.__version__}"
)


# ============================================================
# LOAD DATA
# ============================================================

X_sequence = np.load(
    PROCESSED_DIR
    / "X_sequence_processed.npy"
).astype(np.float32)

X_static = np.load(
    PROCESSED_DIR
    / "X_static_processed.npy"
).astype(np.float32)

y = np.load(
    PROCESSED_DIR
    / "y.npy"
).astype(np.float32)

train_mask = np.load(
    PROCESSED_DIR
    / "train_mask.npy"
)

val_mask = np.load(
    PROCESSED_DIR
    / "val_mask.npy"
)

test_mask = np.load(
    PROCESSED_DIR
    / "test_mask.npy"
)


# ============================================================
# BASIC VALIDATION
# ============================================================

print("\nData")
print("-" * 60)

print(
    f"Sequence shape: {X_sequence.shape}"
)

print(
    f"Static shape:   {X_static.shape}"
)

print(
    f"Target shape:   {y.shape}"
)

assert X_sequence.shape[0] == len(y)
assert X_static.shape[0] == len(y)

assert X_sequence.shape[1] == 12
assert X_sequence.shape[2] == 4

assert X_static.shape[1] == 6

assert np.isfinite(
    X_sequence
).all()

assert np.isfinite(
    X_static
).all()

assert np.isfinite(
    y
).all()


# ============================================================
# SPLIT DATA
# ============================================================

X_seq_train = X_sequence[
    train_mask
]

X_seq_val = X_sequence[
    val_mask
]

X_seq_test = X_sequence[
    test_mask
]


X_static_train = X_static[
    train_mask
]

X_static_val = X_static[
    val_mask
]

X_static_test = X_static[
    test_mask
]


y_train = y[
    train_mask
]

y_val = y[
    val_mask
]

y_test = y[
    test_mask
]


print("\nSplits")
print("-" * 60)

print(
    f"Train: {len(y_train):,}"
)

print(
    f"Validation: {len(y_val):,}"
)

print(
    f"Test: {len(y_test):,}"
)

print(
    f"Train positive rate: "
    f"{y_train.mean():.3f}"
)

print(
    f"Validation positive rate: "
    f"{y_val.mean():.3f}"
)

print(
    f"Test positive rate: "
    f"{y_test.mean():.3f}"
)


# ============================================================
# TORCH DATASETS
# ============================================================

train_dataset = TensorDataset(
    torch.tensor(
        X_seq_train,
        dtype=torch.float32,
    ),
    torch.tensor(
        X_static_train,
        dtype=torch.float32,
    ),
    torch.tensor(
        y_train,
        dtype=torch.float32,
    ),
)

val_dataset = TensorDataset(
    torch.tensor(
        X_seq_val,
        dtype=torch.float32,
    ),
    torch.tensor(
        X_static_val,
        dtype=torch.float32,
    ),
    torch.tensor(
        y_val,
        dtype=torch.float32,
    ),
)

test_dataset = TensorDataset(
    torch.tensor(
        X_seq_test,
        dtype=torch.float32,
    ),
    torch.tensor(
        X_static_test,
        dtype=torch.float32,
    ),
    torch.tensor(
        y_test,
        dtype=torch.float32,
    ),
)


train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
)

val_loader = DataLoader(
    val_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
)


# ============================================================
# MODEL
# ============================================================

class GlycoTwinGRU(nn.Module):

    def __init__(
        self,
        sequence_features,
        static_features,
        hidden_size=32,
        num_layers=1,
        dropout=0.0,
    ):

        super().__init__()

        self.gru = nn.GRU(
            input_size=sequence_features,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=(
                dropout
                if num_layers > 1
                else 0.0
            ),
        )

        self.classifier = nn.Sequential(

            nn.Linear(
                hidden_size
                + static_features,
                32,
            ),

            nn.ReLU(),

            nn.Dropout(
                dropout
            ),

            nn.Linear(
                32,
                1,
            ),
        )

    def forward(
        self,
        sequence,
        static,
    ):

        _, hidden = self.gru(
            sequence
        )

        # Final GRU hidden state
        temporal_state = hidden[-1]

        combined = torch.cat(
            [
                temporal_state,
                static,
            ],
            dim=1,
        )

        return self.classifier(
            combined
        ).squeeze(1)


model = GlycoTwinGRU(
    sequence_features=4,
    static_features=6,
    hidden_size=HIDDEN_SIZE,
    num_layers=NUM_LAYERS,
    dropout=DROPOUT,
).to(DEVICE)


print("\nModel")
print("-" * 60)

print(model)


# ============================================================
# CLASS WEIGHT
# ============================================================

positive_count = y_train.sum()

negative_count = (
    len(y_train)
    - positive_count
)

pos_weight_value = (
    negative_count
    / positive_count
)

pos_weight = torch.tensor(
    [pos_weight_value],
    dtype=torch.float32,
    device=DEVICE,
)

print(
    f"\nPositive weight: "
    f"{pos_weight_value:.3f}"
)


# ============================================================
# LOSS + OPTIMIZER
# ============================================================

criterion = nn.BCEWithLogitsLoss(
    pos_weight=pos_weight
)

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE,
)


# ============================================================
# EVALUATION
# ============================================================

def evaluate(
    model,
    loader,
):

    model.eval()

    probabilities = []
    targets = []

    total_loss = 0.0
    total_examples = 0

    with torch.no_grad():

        for (
            sequence,
            static,
            target,
        ) in loader:

            sequence = sequence.to(
                DEVICE
            )

            static = static.to(
                DEVICE
            )

            target = target.to(
                DEVICE
            )

            logits = model(
                sequence,
                static,
            )

            loss = criterion(
                logits,
                target,
            )

            batch_size = (
                target.size(0)
            )

            total_loss += (
                loss.item()
                * batch_size
            )

            total_examples += (
                batch_size
            )

            probability = torch.sigmoid(
                logits
            )

            probabilities.extend(
                probability.cpu().numpy()
            )

            targets.extend(
                target.cpu().numpy()
            )

    probabilities = np.asarray(
        probabilities
    )

    targets = np.asarray(
        targets
    )

    predictions = (
        probabilities >= 0.5
    ).astype(int)

    auroc = roc_auc_score(
        targets,
        probabilities,
    )

    average_precision = (
        average_precision_score(
            targets,
            probabilities,
        )
    )

    precision = precision_score(
        targets,
        predictions,
        zero_division=0,
    )

    recall = recall_score(
        targets,
        predictions,
        zero_division=0,
    )

    f1 = f1_score(
        targets,
        predictions,
        zero_division=0,
    )

    cm = confusion_matrix(
        targets,
        predictions,
    )

    return {
        "loss": total_loss / total_examples,
        "auroc": auroc,
        "ap": average_precision,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "confusion_matrix": cm,
        "probabilities": probabilities,
        "targets": targets,
    }


# ============================================================
# TRAINING
# ============================================================

best_val_auc = -np.inf

best_epoch = 0

epochs_without_improvement = 0

best_state = None


for epoch in range(
    1,
    EPOCHS + 1,
):

    model.train()

    running_loss = 0.0

    total_examples = 0

    for (
        sequence,
        static,
        target,
    ) in train_loader:

        sequence = sequence.to(
            DEVICE
        )

        static = static.to(
            DEVICE
        )

        target = target.to(
            DEVICE
        )

        optimizer.zero_grad()

        logits = model(
            sequence,
            static,
        )

        loss = criterion(
            logits,
            target,
        )

        loss.backward()

        optimizer.step()

        batch_size = (
            target.size(0)
        )

        running_loss += (
            loss.item()
            * batch_size
        )

        total_examples += (
            batch_size
        )

    train_loss = (
        running_loss
        / total_examples
    )

    val_metrics = evaluate(
        model,
        val_loader,
    )

    print(
        f"\nEpoch {epoch}/{EPOCHS}"
    )

    print(
        f"Train loss: "
        f"{train_loss:.4f}"
    )

    print(
        f"Val loss: "
        f"{val_metrics['loss']:.4f}"
    )

    print(
        f"Val AUROC: "
        f"{val_metrics['auroc']:.4f}"
    )

    print(
        f"Val AP: "
        f"{val_metrics['ap']:.4f}"
    )

    print(
        f"Val Precision: "
        f"{val_metrics['precision']:.4f}"
    )

    print(
        f"Val Recall: "
        f"{val_metrics['recall']:.4f}"
    )

    print(
        f"Val F1: "
        f"{val_metrics['f1']:.4f}"
    )

    if (
        val_metrics["auroc"]
        > best_val_auc
    ):

        best_val_auc = (
            val_metrics["auroc"]
        )

        best_epoch = epoch

        epochs_without_improvement = 0

        best_state = {
            key: value.detach().cpu().clone()
            for key, value
            in model.state_dict().items()
        }

        print(
            "  New best validation model."
        )

    else:

        epochs_without_improvement += 1

        print(
            f"  No improvement "
            f"({epochs_without_improvement}/"
            f"{PATIENCE})"
        )

        if (
            epochs_without_improvement
            >= PATIENCE
        ):

            print(
                "\nEarly stopping."
            )

            break


# ============================================================
# RESTORE BEST MODEL
# ============================================================

if best_state is None:

    raise RuntimeError(
        "No best model state was saved."
    )

model.load_state_dict(
    best_state
)

model.to(DEVICE)


# ============================================================
# FINAL VALIDATION
# ============================================================

val_metrics = evaluate(
    model,
    val_loader,
)


# ============================================================
# FINAL TEST
#
# Test set is evaluated ONCE after model selection.
# ============================================================

test_metrics = evaluate(
    model,
    test_loader,
)


# ============================================================
# PRINT RESULTS
# ============================================================

print("\n")
print("=" * 60)
print("BEST MODEL")
print("=" * 60)

print(
    f"Best epoch: {best_epoch}"
)

print(
    f"Best validation AUROC: "
    f"{val_metrics['auroc']:.4f}"
)

print(
    f"Validation AP: "
    f"{val_metrics['ap']:.4f}"
)

print("\n")
print("=" * 60)
print("FINAL TEST RESULTS")
print("=" * 60)

print(
    f"Test AUROC:    "
    f"{test_metrics['auroc']:.4f}"
)

print(
    f"Test AP:       "
    f"{test_metrics['ap']:.4f}"
)

print(
    f"Test Precision: "
    f"{test_metrics['precision']:.4f}"
)

print(
    f"Test Recall:    "
    f"{test_metrics['recall']:.4f}"
)

print(
    f"Test F1:         "
    f"{test_metrics['f1']:.4f}"
)

print(
    "\nTest confusion matrix:"
)

print(
    test_metrics["confusion_matrix"]
)


# ============================================================
# SAVE MODEL
# ============================================================

model_path = (
    MODEL_DIR
    / "glycotwin_gru_corrected.pt"
)

torch.save(
    {
        "model_state_dict":
            model.state_dict(),

        "sequence_features": 4,

        "static_features": 6,

        "hidden_size":
            HIDDEN_SIZE,

        "num_layers":
            NUM_LAYERS,

        "dropout":
            DROPOUT,

        "best_epoch":
            best_epoch,

        "validation_auroc":
            val_metrics["auroc"],

        "test_auroc":
            test_metrics["auroc"],

        "test_average_precision":
            test_metrics["ap"],

        "threshold":
            0.5,

        "seed":
            SEED,
    },
    model_path,
)


print(
    f"\nModel saved to:"
)

print(
    model_path
)