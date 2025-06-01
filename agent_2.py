#from typing import Annotated

#from typing_extensions import TypedDict

#from langgraph.graph import StateGraph, START
#from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI


inference_server_url = "http://localhost:8000/v1"
llm = ChatOpenAI(
    model="Qwen/Qwen3-4B",
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=32,
    temperature=0,
)

from langgraph.prebuilt import create_react_agent

def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"

agent = create_react_agent(
    model=llm,
    tools=[get_weather],  
    prompt="You are a helpful assistant"  
)

# Run the agent
response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)

print(response)
