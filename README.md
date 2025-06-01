# This repor ceate AI-agent examples based on my Local LLM services


## Set up vLLM service
### Build vLLM XPU docker images
```
git clone https://github.com/vllm-project/vllm.git
cd vllm 
docker build -f Dockerfile.xpu -t vllm-xpu-env --shm-size=4g .
```

### Start docker container

```
cd ~
git clone https://github.com/xiguiwang/agent-examples.git
cd agent-examples
docker compose up -d
```
or
```
docker run -it \
             --rm \
             --network=host \
             --device /dev/dri \
             -v /dev/dri/by-path:/dev/dri/by-path \
             vllm-xpu-env
```

### Access the vLLM services
After docker container started

Access through OPEA API
```
cd ~/agent-examples/examples
python client.py
```
Access by curl command
```
curl http://localhost:8000/v1/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "Qwen/Qwen3-4B",
        "prompt": "San Francisco is a",
        "max_tokens": 32,
        "temperature": 0
    }'
```
Non-stream output:
```
{"id":"cmpl-e0847e6bb50749c3926633dacae2273c","object":"text_completion","created":1748736946,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":" city in the state of California, USA. It is a major city in the San Francisco Bay Area, which is a major economic center in the United States.","logprobs":null,"finish_reason":"length","stop_reason":null,"prompt_logprobs":null}],"usage":{"prompt_tokens":4,"total_tokens":36,"completion_tokens":32,"prompt_tokens_details":null},"kv_transfer_params":null}(base)
```

Stream output format:
data: {"id":"cmpl-9d0ab69d6c9a4321857d6e0b9acaba7e","object":"text_completion","created":1748737044,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":" city","logprobs":null,"finish_reason":null,"stop_reason":null}],"usage":null}

data: {"id":"cmpl-9d0ab69d6c9a4321857d6e0b9acaba7e","object":"text_completion","created":1748737044,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":" in","logprobs":null,"finish_reason":null,"stop_reason":null}],"usage":null}

data: {"id":"cmpl-9d0ab69d6c9a4321857d6e0b9acaba7e","object":"text_completion","created":1748737044,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":" the","logprobs":null,"finish_reason":null,"stop_reason":null}],"usage":null}

data: {"id":"cmpl-9d0ab69d6c9a4321857d6e0b9acaba7e","object":"text_completion","created":1748737044,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":" state","logprobs":null,"finish_reason":null,"stop_reason":null}],"usage":null}

data: {"id":"cmpl-9d0ab69d6c9a4321857d6e0b9acaba7e","object":"text_completion","created":1748737044,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":" of","logprobs":null,"finish_reason":null,"stop_reason":null}],"usage":null}

data: {"id":"cmpl-9d0ab69d6c9a4321857d6e0b9acaba7e","object":"text_completion","created":1748737044,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":" California","logprobs":null,"finish_reason":null,"stop_reason":null}],"usage":null}

data: {"id":"cmpl-9d0ab69d6c9a4321857d6e0b9acaba7e","object":"text_completion","created":1748737044,"model":"Qwen/Qwen3-4B","choices":[{"index":0,"text":",","logprobs":null,"finish_reason":"length","stop_reason":null}],"usage":null}

data: [DONE]```
```
