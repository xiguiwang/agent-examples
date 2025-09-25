from langchain.agents import AgentExecutor, create_self_ask_with_search_agent
from langchain_core.prompts import PromptTemplate
from langchain.agents.self_ask_with_search.prompt import PROMPT
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# 1. 定义 Prompt（Self-Ask 模板）
template = """Question: Who lived longer, Muhammad Ali or Alan Turing?
Are follow up questions needed here: Yes.
Follow up: How old was Muhammad Ali when he died?
Intermediate answer: Muhammad Ali was 74 years old when he died.
Follow up: How old was Alan Turing when he died?
Intermediate answer: Alan Turing was 41 years old when he died.
So the final answer is: Muhammad Ali

Question: {input}
Are follow up questions needed here:{agent_scratchpad}"""
prompt = PromptTemplate.from_template(template)

# 2. 定义一个 mock 搜索工具
def mock_search(query: str) -> str:
    """模拟搜索引擎，只返回固定答案"""
    if "founder of craigslist" in query:
        return "Craigslist was founded by Craig Newmark."
    if "Craig Newmark born" in query:
        return "Craig Newmark was born on December 6, 1952."
    return "I don't know."

search_tool = Tool(
    name="Intermediate Answer",
    func=mock_search,
    description="Mock search tool for demo"
)

# 3. 定义 LLM（这里用 OpenAI，你可以换成本地模型或别的）
inference_server_url = "http://localhost:8000/v1"
llm = ChatOpenAI(
    model="Qwen/Qwen3-4B",
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=32,
    temperature=0,
)

# 4. 创建 Self-Ask agent (Runnable)
agent = create_self_ask_with_search_agent(llm, [search_tool], prompt)

# 5. 包装进 AgentExecutor
agent_executor = AgentExecutor(agent=agent, tools=[search_tool], verbose=True)

# 6. 运行
result = agent_executor.invoke({"input": "When was the founder of craigslist born?"})
print("\nFinal Answer:", result)
