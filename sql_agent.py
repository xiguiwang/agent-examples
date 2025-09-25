from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

user='root'
password='mysql-pwd'
host = "127.0.0.1"
port = 3306
database = "foodDB"

PREFIX="""You are an agent designed to interact with a SQL database.
  Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
  Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
  You can order the results by a relevant column to return the most interesting examples in the database.
  Never query for all the columns from a specific table, only ask for the relevant columns given the question.
  You have access to tools for interacting with the database.
  Only use the below tools. Only use the information returned by the below tools to construct your final answer.
  You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
  
  If the question does not seem related to the database, just return "I don't know" as the answer.
"""
# DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
  
# === 1. 建数据库连接 ===
db_uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
db = SQLDatabase.from_uri(db_uri)

print("Tables:", db.get_usable_table_names())

# === 2. 初始化 LLM ===
def create_llm_model():
    url = "http://localhost:8000/v1"
    model="Qwen/Qwen3-4B"
    api_key="EMPTY"
    llm = ChatOpenAI(
        model=model,
        openai_api_key=api_key,
        openai_api_base=url,
        max_tokens=2048,
        temperature=0.0,
    )

    return llm

llm = create_llm_model()
# === 3. 创建 SQL Agent ===
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    prefix=PREFIX,
    agent_type="zero-shot-react-description", # "openai-tools",  # 也可以用 "zero-shot-react-description"
    verbose=True,
)

# === 4. 用自然语言查询 ===
result = agent_executor.invoke({"input": "列出 food_InfoTb 里的数据"})
print(result["output"])

#result = agent_executor.invoke({"input": "查一下 food_InfoTb 里最近插入的 5 条数据"})
#print(result["output"])

# === 5. 让 LLM 生成更新操作 ===
#result = agent_executor.invoke({
#    "input": "往 food_InfoTb 表里插入一条记录：foodName=土豆, foodType=蔬菜, PicUrl=https://example.com/potato.jpg"
#})
insert_result = agent_executor.invoke({
    "input": "往 food_InfoTb 表里插入一条记录，foodName=黄瓜，foodType=蔬菜，PicUrl=https://example.com/cucumber.jpg"
})
print(insert_result["output"])
