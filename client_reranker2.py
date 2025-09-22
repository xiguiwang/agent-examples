import json

import requests

url = "http://127.0.0.1:8012/rerank"

headers = {"accept": "application/json", "Content-Type": "application/json"}

data = {
    "model": "Qwen/Qwen3-Reranker-4B", #"BAAI/bge-reranker-base",
    "query": "What is the capital of France?",
    "documents": [
        "The capital of Brazil is Brasilia.",
        "The capital of France is Paris.",
        "Horses and cows are both animals",
    ],
}


def main():
    response = requests.post(url, headers=headers, json=data)

    # Check the response
    if response.status_code == 200:
        print("Request successful!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    main()
