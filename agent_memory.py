#from typing import Annotated
#from typing_extensions import TypedDict
#from langgraph.graph import StateGraph, START
#from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

#model="Qwen/Qwen2.5-7B-Instruct"
model = "Qwen/Qwen3-4B"

inference_server_url = "http://localhost:8000/v1"
llm = ChatOpenAI(
    model=model,
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=32,
    temperature=0,
)

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

checkpointer = InMemorySaver()

agent = create_react_agent(
    model=llm,
    tools=[get_weather],  
    prompt="You are a helpful assistant",
    checkpointer=checkpointer
)

# Run the agent
config = {"configurable": {"thread_id": "1"}}

# Run the agent
bj_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in Beijing?"}]},
    config
)

sh_response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in Shanghai?"}]},
    config
)
print(bj_response, '*'*20)
print(sh_response)
