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

### Build vLLM for Nvidia GPU docker images

build vLLM for NVidia GPU docker image
```
DOCKER_BUILDKIT=1 docker build . \
    --target vllm-openai \
    --tag vllm/vllm-openai \
    --file docker/Dockerfile

or

DOCKER_BUILDKIT=1 docker build  \
    --build-arg max_jobs=64 --build-arg nvcc_threads=32
    --build-arg https_proxy=$https_proxy \
    --build-arg http_proxy=$http_proxy \
    --build-arg torch_cuda_arch_list="" \
    --target vllm-openai  \
    --tag vllm/vllm-openai \
    --file docker/Dockerfile .
```
By default vLLM will build for all GPU types for widest distribution. If you are just building for the current GPU type the machine is running on, you can add the argument --build-arg torch_cuda_arch_list="" for vLLM to find the current GPU type and build for that.

* https://docs.vllm.ai/en/stable/deployment/docker.html

## Pit fall of NV Tesla V100
```
1.
* packages/torch/cuda/__init__.py:262: UserWarning:
vllm-openai  |     Found GPU1 Tesla V100-PCIE-32GB which is of cuda capability 7.0.
vllm-openai  |     PyTorch no longer supports this GPU because it is too old.
vllm-openai  |     The minimum cuda capability supported by this library is 7.5.
vllm-openai  |
vllm-openai  |   warnings.warn(
vllm-openai  | INFO 06-02 23:13:06 [worker.py:109] Profiling enabled. Traces will be saved to: /mnt
vllm-openai  | INFO 06-02 23:13:07 [parallel_state.py:1064] rank 0 in world size 1 is assigned as DP rank 0, PP rank 0, TP rank 0, EP rank 0
vllm-openai  | INFO 06-02 23:13:07 [model_runner.py:1170] Starting to load model Qwen/Qwen3-8B...
vllm-openai  | Process SpawnProcess-1:
vllm-openai  | ERROR 06-02 23:13:07 [engine.py:457] CUDA error: no kernel image is available for execution on the device 


2 * bfloat16 is not supported
packages/vllm/worker/worker.py", line 140, in init_device
vllm-openai  |     _check_if_gpu_supports_dtype(self.model_config.dtype)
vllm-openai  |   File "/usr/local/lib/python3.12/dist-packages/vllm/worker/worker.py", line 479, in _check_if_gpu_supports_dtype
vllm-openai  |     raise ValueError(
vllm-openai  | ValueError: Bfloat16 is only supported on GPUs with compute capability of at least 8.0. Your Tesla V100-PCIE-32GB GPU has compute capability 7.0. You can use float16 instead by explicitly setting thedtype flag in CLI, for example: --dtype=half.
Gracefully stopping... (press Ctrl+C again to force)
```

### Start vLLM for Agent

Follow the instructions provided in the README of Qwen2 for deploying an OpenAI-compatible API service. Specifically, consult the vLLM section for high-throughput GPU deployment or the Ollama section for local CPU (+GPU) deployment. For the QwQ and Qwen3 model, it is recommended to add the --enable-reasoning and --reasoning-parser deepseek_r1 parameters when starting the service. Do not add the --enable-auto-tool-choice and --tool-call-parser hermes parameters, as Qwen-Agent will parse the tool outputs from vLLM on its own.

Reference
* https://github.com/xiguiwang/Qwen-Agent

### Access the vLLM services
After docker container started

Access through OPEA API
```
cd ~/agent-examples/examples
python client.py
```
The output are:
```
Chat response: ChatCompletion(id='chatcmpl-88e00a46d2f340628a88770dda3084e0', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='<think>\nOkay, the user asked for a joke. Let me think of something that\'s both funny and not too cheesy. Maybe a classic one that\'s widely appreciated. The one about the chicken and the egg? Wait, that\'s a bit old. Maybe something with a twist. Oh, the "Why don\'t scientists trust atoms?" joke. That\'s a good one. It\'s a play on words with "atoms" and "atom" as a unit. Let me check if that\'s the right setup. Yeah, the punchline is that they make up everything, so they\'re not trustworthy. That works. I should make sure to present it clearly and maybe add a light-hearted comment to keep the conversation friendly. Alright, that should do it.\n</think>\n\nSure! Here\'s a classic one for you:\n\n**Why don\'t scientists trust atoms?**  \n*Because they make up everything!*\n\n😄 Let me know if you want another!', refusal=None, role='assistant', audio=None, function_call=None, tool_calls=[], reasoning_content=None), stop_reason=None)], created=1748737191, model='Qwen/Qwen3-4B', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=193, prompt_tokens=24, total_tokens=217, completion_tokens_details=None, prompt_tokens_details=None), prompt_logprobs=None, kv_transfer_params=None)
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

## Lainchain chatbot
```
conda create -n lainchain python=3.12
conda activate lainchain 
pip install lainchain langchain_community
pip install lainchain langchain-openai
pip install openai
```

reference this to creat a model `https://python.langchain.com/docs/integrations/chat/vllm/`
