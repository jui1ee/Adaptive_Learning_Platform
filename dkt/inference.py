import torch

def encode(seq):
    return [s * 2 + r for s, r in seq]

def predict_mastery(model, seq, num_skills):
    if not seq:
        return {i: 0.5 for i in range(num_skills)}

    x = torch.tensor([encode(seq)])

    with torch.no_grad():
        output = model(x)

    # 🔥 Use mean over all time steps (NOT just last)
    mean_output = output.mean(dim=1)[0]

    return {i: round(float(mean_output[i]), 2) for i in range(num_skills)}

def classify(mastery):
    values = list(mastery.values())

    if not values:
        return [], [], []

    low = min(values)
    high = max(values)

    # handle edge case: all values same
    if low == high:
        return list(mastery.keys()), [], []

    weak, medium, strong = [], [], []

    for k, v in mastery.items():
        if v < low + (high - low) / 3:
            weak.append(k)
        elif v < low + 2 * (high - low) / 3:
            medium.append(k)
        else:
            strong.append(k)

    return weak, medium, strong