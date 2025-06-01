# This repo ceate AI-agent examples based on my Local LLM services

Set up vLLM service
[vLLM setupt](vLLM_setup.md)

## AI Agent Example

1. create Model
* reference this to creat a model `https://python.langchain.com/docs/integrations/chat/vllm/`

```
conda create -n lainchain python=3.12
conda activate lainchain 
pip install lainchain langchain_community
pip install lainchain langchain-openai
pip install openai
pip install ipython
```

2. create graph state with node

```
pip install langgraph 
python agent_1.py
```

## Reference
* https://langchain-ai.github.io/langgraph/
* https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot
