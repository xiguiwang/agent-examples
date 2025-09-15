# Setup vllm Reranker on CPU

## build vLLM-CPU docker image

The released vllm-cpu enable avx-512 and avx-bfloat. It cannot run on Client CPU.
We build a vllm docker image for client CPU.

Check the cpu feature by `lscpu` and enable/disable each feature.

Clone the vllm repo and set the feature according to the flag of CPU.

```
git clone https://github.com/vllm-project/vllm.git
cd vllm

docker build -f docker/Dockerfile.cpu \
        --platform=linux/amd64 \
        --build-arg VLLM_CPU_AVX512BF16=false \
        --build-arg VLLM_CPU_AVX512VNNI=true \
        --build-arg VLLM_CPU_DISABLE_AVX512=false \
        -t vllm-openai:vllm-cpu .
```

## Start Docker Container

```
dockere compose -f ./compose-reranker.yaml up -d
```

After docker container stared,
check the reranker access:

```
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
```

The expected output are:

```
{"id":"rerank-46396c6c394b4d1bb810855365ad488e","model":"Qwen3-Reranker-4B","usage":{"total_tokens":9},"results":[{"index":1,"document":{"text":"banana","multi_modal":null},"relevance_score":0.9121023416519165},{"index":0,"document":{"text":"apple","multi_modal":null},"relevance_score":0.6095536351203918},{"index":2,"document":{"text":"fruit","multi_modal":null},"relevance_score":0.5293400883674622},{"index":3,"document":{"text":"vegetable","multi_modal":null},"relevance_score":0.13090011477470398}]}```
```

