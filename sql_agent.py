from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI

user='root'
password='mysql-pwd'
host = "127.0.0.1"
port = 3306
database = "foodDB"
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
