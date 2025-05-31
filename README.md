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
        "model": "Qwen/Qwen2.5-1.5B-Instruct",
        "prompt": "San Francisco is a",
        "max_tokens": 32,
        "temperature": 0
    }'
```
