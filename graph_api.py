from langgraph.graph import StateGraph, MessagesState  
from langchain_core.messages import AIMessage
from langgraph.graph import START, END

from langchain_openai import ChatOpenAI

from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from langgraph.checkpoint.memory import MemorySaver  

# 记忆检查点初始化
memory = MemorySaver()

inference_server_url = "http://localhost:8000/v1"
llm_model = ChatOpenAI(
    model="Qwen/Qwen3-4B",
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=2048,
    temperature=0,
)

@tool
def mock_search(query: str) -> str:
    """搜索引擎，搜索问题的答案"""
    if "founder of craigslist" in query:
        return "Craigslist was founded by Craig Newmark."
    if "Craig Newmark" in query and ("born" or "birth" in query):
        return "Craig Newmark was born on December 6, 1952."
    return "I don't know."

tools = [mock_search]
llm_with_tool = llm_model.bind_tools(tools) 

# 定义模型调用函数
def model_with_search_tools(state: MessagesState):  
    question = state["messages"]
    response = llm_with_tool.invoke(question)
    return {"messages": [response]}  

def route_function(state:MessagesState):
    messages = state["messages"][-1]
    if messages.tool_calls:
        return "tools"
    return END

tool_node = ToolNode(tools)

# 构建单节点图结构
workflow = StateGraph(MessagesState)  
workflow.add_node("mybot", model_with_search_tools)  
workflow.add_node("tools", tool_node)  
workflow.set_entry_point("mybot")
workflow.add_edge("tools", "mybot")
workflow.add_conditional_edges("mybot",
                route_function,
                {"tools":"tools", END:END})  

# 编译并执行工作流
app = workflow.compile(checkpointer=memory )  

# 测试执行
#result = app.invoke({"messages": ["When was the founder of craigslist born?"]})
#print(result)
config = {"configurable" : {"thread_id" : 1}}
for output in app.stream({"messages": ["When was the founder of craigslist born?"]},
            config=config):
    for key, value in output.items():
        print(f"here is the output from {key}")
        print("-----------")
        print(f"{value}\n")
#print(result)
