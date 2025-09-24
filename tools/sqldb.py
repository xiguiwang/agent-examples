# 安装驱动: pip install pymysql
from langchain_community.utilities import SQLDatabase

user='root'
password='mysql-pwd'
host = "127.0.0.1"
port = 3306
database = "foodDB"

url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
db = SQLDatabase.from_uri(url)

print("Tables:", db.get_usable_table_names())

# 查询示例
print(db.run("SELECT * FROM food_InfoTb LIMIT 10;"))
