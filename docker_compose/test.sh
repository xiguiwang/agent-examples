curl http://localhost:8000/v1/chat/completions     -X POST     -d '{"model": "Qwen/Qwen3-4B", "messages": [{"role": "user", "content": "What is Deep Learning?"}], "max_tokens":17}'     -H 'Content-Type: application/json'

curl http://localhost:8080/v1/text2sql\
        -X POST \
        -d '{"input_text": "Find the total number of Albums.","conn_str": {"user": "'${POSTGRES_USER}'","password": "'${POSTGRES_PASSWORD}'","host": "'${ip_address}'", "port": "5442", "database": "'${POSTGRES_DB}'"}}' \
        -H 'Content-Type: application/json'
