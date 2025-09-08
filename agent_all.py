from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage, AIMessage

import json

from langgraph.checkpoint.memory import MemorySaver

from langchain_mcp_adapters.client import MultiServerMCPClient
#from langgraph.prebuilt import create_react_agent

from langchain_core.runnables import Runnable
import asyncio

import inspect
global llm_with_tools

def dump_func_line():
    #print(inspect.stack()[1].function) #, inspect.currentframe().f_lineno)
    return

client = MultiServerMCPClient(
    {
        "pyfile_count": {
            "command": "python",
            # Replace with absolute path to your math_server.py file
            "args": ["/disk/agent-examples/py_count.py"],
            #"args": ["/ws1/xiguiwang/agent-examples/py_count.py"],
            "transport": "stdio",
        },
        "Sql-Database": {
            "command": "python",
            "args": ["/disk/agent-examples/tools/sql_mcp.py"],
            "transport": "stdio",
        }
    }
)
"""
"weather": {
    # Ensure your start your weather server on port 8000
    "url": "http://localhost:8000/mcp",
    "transport": "streamable_http",
}
"""

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


MODEL="Qwen/Qwen3-4B"
#MODEL="Qwen/Qwen2.5-7B-Instruct"

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        dump_func_line()
        self.tools_by_name = {tool.name: tool for tool in tools}

    async def __call__(self, inputs: dict):
        dump_func_line()
        #import pdb
        #pdb.set_trace()
        if messages := inputs.get("messages", []):
            message = messages[-1]
            #print("messages:", messages)
        else:
            raise ValueError("No message found in input")
        outputs = []

        for tool_call in message.tool_calls:
            tool_result = await self.tools_by_name[tool_call["name"]].ainvoke(
                tool_call["args"]
                )
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                )
            )
        #print("output messages:", outputs)
        return {"messages": outputs}

class AsyncToolNode(Runnable):
    """Wraps an async BasicToolNode so LangGraph can call it via ainvoke."""
    def __init__(self, tools):
        self.node = BasicToolNode(tools)

    async def ainvoke(self, input, config=None):
        #print("✅ Running async ainvoke on AsyncToolNode")
        return await self.node(input)

    def invoke(self, input, config=None):
        # Optional: fallback for sync contexts (not always safe)
        #print("⚠️ Warning: Sync invoke on async node - prefer ainvoke")
        return asyncio.run(self.node(input))

@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    user_input = input("User: ")
    return human_response["data"]

@tool
def get_weather(city: str) -> str:  
    """Get weather for a given city."""
    dump_func_line()
    return f"It's always sunny in {city}!"

def chatbot(state: State):
    global llm_with_tools
    dump_func_line()
    #return {"messages": [llm.invoke(state["messages"])]}
    output_messages = {"messages": [llm_with_tools.invoke(state["messages"])]}
    #print("output_messages", output_messages)
    return output_messages

def route_tools(
    state: State,
):
    """
    Use in the conditional_edge to route to the ToolNode if the last message
    has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")

    dump_func_line()
    #print("AI message:", ai_message, "*******")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    #print("*** route to END ***")
    return END

'''
from IPython.display import Image, display

try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    # This requires some extra dependencies and is optional
    pass
'''

async def get_mcp_tools():
    mcp_tools = await client.get_tools()
    return mcp_tools

def create_graph_agent():
    global llm_with_tools
    memory = MemorySaver()
    graph_builder = StateGraph(State)

    inference_server_url = "http://localhost:8000/v1"
    llm = ChatOpenAI(
        model=MODEL,
        openai_api_key="EMPTY",
        openai_api_base=inference_server_url,
        max_tokens=2048,
        temperature=0,
    )

    mcp_tools = asyncio.run(get_mcp_tools())

    #tools=[get_weather, mcp_tools] # human_assistance] #, mcp_tools]
    tools = [get_weather] + (mcp_tools or [])

    #tool_node = BasicToolNode(tools=tools)
    tool_node = AsyncToolNode(tools)
    graph_builder.add_node("tools", tool_node)

    llm_with_tools = llm.bind_tools(tools)

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("chatbot", chatbot)

    # The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
    # it is fine directly responding. This conditional routing defines the main agent loop.
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
        # It defaults to the identity function, but if you
        # want to use a node named something else apart from "tools",
        # You can update the value of the dictionary to something else
        # e.g., "tools": "my_tools"
        {"tools": "tools", END: END},
    )
    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.add_edge(START, "chatbot")

    graph = graph_builder.compile(checkpointer=memory)

    return graph


def stream_graph_updates(graph, user_input: str):
    dump_func_line()
    config = {"configurable": {"thread_id": "1"}}
    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )

    for event in events:
        event_message = event["messages"][-1]
        if isinstance(event_message, AIMessage):
            print(event_message.content)

def main():
    graph = create_graph_agent()
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(graph, user_input)
        except Exception:
            # This requires some extra dependencies and is optional
            print("Error")
            pass
    '''
    except:
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
     '''

if __name__ == "__main__":
    main()
