# This repo ceate AI-agent examples based on my Local LLM services

## Overview agent

AI agent

[Agent implementation in Langchain & Langgraph](./doc/agent_and_langgraph.md)

## Prerqueist

Set up vLLM service
[vLLM setupt](./doc/vLLM_setup.md)

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
pip install langchain-mcp-adapters
pip install mcp
```

2. create graph state with node

```
pip install langgraph 
python agent_1.py
```

3. Agent integrated MCP tools to query database, list files in directory, simulate query weather, and memroy tools.

```
python agent_all.py
```
![Agent all](./tools/accessory/output_1080.gif)

## Reference
* https://langchain-ai.github.io/langgraph/
* https://langchain-ai.github.io/langgraph/tutorials/get-started/1-build-basic-chatbot
* https://github.com/modelcontextprotocol/python-sdk.git
* https://langchain-ai.github.io/langgraph/how-tos/tool-calling/#handle-large-numbers-of-tools
