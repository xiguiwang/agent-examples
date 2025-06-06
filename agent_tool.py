#agent tools example
from langchain_core.tools import tool

import getpass
import os

from langchain_openai import ChatOpenAI

@tool
def multiply(a: int, b: int) -> int:
   """Multiply two numbers."""
   return a * b

@tool
def add(a: int, b: int) -> int:
   """Add two numbers."""
   return a * b

tools = [add, multiply]

inference_server_url = "http://localhost:8000/v1"

llm = ChatOpenAI(
    model="Qwen/Qwen2.5-7B-Instruct",
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=256,
    temperature=0,
)

llm_with_tools = llm.bind_tools(tools)

query = "What is 3 * 12?"

response = llm_with_tools.invoke(query)
print("response:\n", response)
print("content:\n", response.content)


query = "What is 3 * 12? Also, what is 11 + 49?"

print(f"\n\n{query} \n ==== \n ")
ret = llm_with_tools.invoke(query)
print(f"\n invoke query\n ==== \n ", ret)

ret = llm_with_tools.invoke(query).tool_calls
print(" \n*** invoke.tool_calls ret ***:", ret)
