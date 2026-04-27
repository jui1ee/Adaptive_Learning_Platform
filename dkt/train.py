import torch
import torch.nn as nn

def encode(seq):
    return [s * 2 + r for s, r in seq]

def train_on_attempts(model, attempts, num_skills, epochs=3):
    if len(attempts) < 2:
        return model  # not enough data

    X = []
    y_skills = []
    y_correct = []

    enc = encode(attempts)

    X.append(enc[:-1])
    next_seq = attempts[1:]

    skills = []
    corrects = []

    for s, r in next_seq:
        skills.append(s)
        corrects.append(r)

    X = torch.tensor(X)
    y_skills = torch.tensor([skills])
    y_correct = torch.tensor([corrects], dtype=torch.float32)

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = nn.BCELoss()

    for epoch in range(epochs):
        model.train()
        output = model(X)

        preds = []
        targets = []

        for t in range(X.shape[1]):
            skill = y_skills[0][t]
            preds.append(output[0][t][skill])
            targets.append(y_correct[0][t])

        preds = torch.stack(preds)
        targets = torch.stack(targets)

        loss = loss_fn(preds, targets)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        # ✅ FIXED PRINT
        print(f"Epoch {epoch+1}/{epochs} - Loss: {loss.item():.4f}")

    return model