import requests

# API endpoint
url = "http://localhost:8012/v1/rerank"

# Request headers
headers = {
    "Authorization": "Bearer Empty",  # your API key if needed
    "Content-Type": "application/json"
}

# Request payload
payload = {
    "model": "Qwen/Qwen3-Reranker-4B",
    "query": "Apple",
    "documents": ["apple", "banana", "fruit", "vegetable"],
    "top_n": 4,
    "return_documents": False,
    "max_chunks_per_doc": 1024,
    "overlap_tokens": 80
}

# Send request
response = requests.post(url, headers=headers, json=payload)

# Raise exception if HTTP error
response.raise_for_status()

# Parse JSON
data = response.json()

# Print the raw response
print("Raw response:", data)

# Example: extract rankings
if "results" in data:
    for rank, item in enumerate(data["results"], start=1):
        doc_idx = item.get("index")
        score = item.get("relevance_score")
        print(f"Rank {rank}: doc={payload['documents'][doc_idx]!r}, score={score}")
