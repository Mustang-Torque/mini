from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rapidfuzz import process
import os

app = FastAPI()

# -----------------------------
# Enable CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Load dataset (ROBUST)
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.txt")

pairs = []

try:
    with open(DATA_PATH, encoding="utf-8") as f:
        for line in f:
            if "=>" not in line:
                continue

            parts = line.strip().split("=>")
            if len(parts) != 2:
                continue

            inp = parts[0].strip().lower()
            out = parts[1].strip()

            if inp and out:
                pairs.append((inp, out))

    print(f"Loaded {len(pairs)} pairs")

except Exception as e:
    print("Error loading dataset:", e)

inputs = [p[0] for p in pairs]


# -----------------------------
# Response logic (MODE 1)
# -----------------------------
def get_response(text: str):
    text_clean = text.strip().lower()

    if not text_clean:
        return "please enter a message"

    # Exact match
    for inp, out in pairs:
        if text_clean == inp:
            return out

    # Fuzzy match
    if inputs:
        result = process.extractOne(text_clean, inputs)

        if result:
            match, score, idx = result
            if score > 75:
                return pairs[idx][1]

    return "i do not understand that yet"


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def home():
    return {
        "status": "running",
        "dataset_size": len(pairs)
    }


@app.post("/chat")
def chat(data: dict):
    user_input = data.get("message", "")

    response = get_response(user_input)

    return {
        "input": user_input,
        "response": response
    }