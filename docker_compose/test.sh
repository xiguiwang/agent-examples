# OpenAI API access

curl http://localhost:8000/v1/chat/completions     -X POST     -d '{"model": "Qwen/Qwen3-4B", "messages": [{"role": "user", "content": "What is Deep Learning?"}], "max_tokens":17}'     -H 'Content-Type: application/json'


# Csustomed interface
curl http://localhost:8080/v1/text2sql\
        -X POST \
        -d '{"input_text": "Find the total number of Albums.","conn_str": {"user": "'${POSTGRES_USER}'","password": "'${POSTGRES_PASSWORD}'","host": "'${ip_address}'", "port": "5442", "database": "'${POSTGRES_DB}'"}}' \
        -H 'Content-Type: application/json'

# Embedding API
curl http://localhost:11434/api/embeddings -d '{
  "model": "nomic-embed-text",
  "prompt": "The sky is blue because of Rayleigh scattering"
}'

# Reranker API
curl -X POST \
  --url http://localhost:8012/v1/rerank \
  --header 'Authorization: Bearer Empty' \
  --header 'Content-Type: application/json' \
  --data '{
  "model": "Qwen/Qwen3-Reranker-4B",
  "query": "Apple",
  "documents": [ "apple", "banana", "fruit", "vegetable" ],
  "top_n": 4,
  "return_documents": false,
  "max_chunks_per_doc": 1024,
  "overlap_tokens": 80
}'

#Output
{"id":"rerank-46396c6c394b4d1bb810855365ad488e","model":"Qwen3-Reranker-4B","usage":{"total_tokens":9},"results":[{"index":1,"document":{"text":"banana","multi_modal":null},"relevance_score":0.9121023416519165},{"index":0,"document":{"text":"apple","multi_modal":null},"relevance_score":0.6095536351203918},{"index":2,"document":{"text":"fruit","multi_modal":null},"relevance_score":0.5293400883674622},{"index":3,"document":{"text":"vegetable","multi_modal":null},"relevance_score":0.13090011477470398}]}
