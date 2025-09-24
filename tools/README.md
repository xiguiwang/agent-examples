# LLM and Database Access

## Software Architecture of DB Libraries Layer
Here is the Software Architecture of DB libraries

```
+---------------------------------------------------+
|                 LangChain 的 SQLDatabase          |  (最高层抽象)
|              (为 LLM 交互设计，包含工具和链)        |
+---------------------------------------------------+
                            |
                            | 内部使用
                            v
+---------------------------------------------------+
|                  SQLAlchemy Core / ORM            |  (中间层抽象)
|        (Python 版的 SQL 工具包，数据库无关)          |
+---------------------------------------------------+
                            |
                            | 作为底层驱动之一
                            v
+---------------------------------------------------+
|                mysql.connector / pymysql          |  (最底层驱动)
|        (MySQL 官方/Python 社区的纯 Python 驱动)      |
+---------------------------------------------------+

```

### **详细区别对比**

|特性  |	LangChain 的 SQLDatabase|	SQLAlchemy|	mysql.connector |
|------|------|------|------|
|设计目的|	专门为 LLM 设计，让 LLM 能够理解和操作数据库。|	通用的 Python 数据库工具包和 ORM，用于构建稳健的数据库应用。|	纯粹的 MySQL 数据库驱动，提供最基础的连接和 SQL 执行功能。|
|抽象层级|	高级抽象。它封装了数据库连接、 schema 获取、查询执行和结果格式化。|	中层抽象。提供了 Core（SQL 表达式语言）和 ORM（对象关系映射）两种使用方式。|	底层驱动。直接与 MySQL 服务器进行 TCP 通信，执行原始 SQL 字符串。|
|核心功能 |	- 自动获取数据库 schema（表名、列名、样例数据）。 <br> - 提供 SQLDatabaseToolkit 等工具，让 LLM 能“选择工具”来查询数据库。 <br> - 安全控制（例如，禁止某些危险操作）。 <br> - 结果格式化，便于 LLM 理解。|	- 引擎（Engine）：管理数据库连接池。 <br> - SQL 表达式语言：用 Python 方式构建 SQL，避免 SQL 注入。 <br> - ORM：将数据库表映射为 Python 类，实现面向对象操作。 <br> - 连接池、事务管理。|	- 建立到 MySQL 服务器的连接。 <br> - 创建游标（Cursor）执行 SQL 语句。 <br> - 获取查询结果。|
| 与 LLM 的集成	| 深度集成。可以直接用在 Agent 中，作为其一个可用的“工具”。|	无集成。需要开发者自己编写代码，将数据库查询结果处理成 LLM 能理解的格式。|	无集成。比 SQLAlchemy 更底层，需要更多手动编码。|
|易用性（对于 LLM 应用）|	非常高。几行代码就能让 LLM Agent 具备数据库查询能力。|	中等。需要开发者熟悉 SQLAlchemy 并手动处理与 LLM 的交互逻辑。|	低。需要处理连接、游标、异常等底层细节，SQL 注入风险高。|
|灵活性	| 较低。主要围绕“让 LLM 安全查询”这个场景，定制复杂业务逻辑比较困难。|	非常高。可以构建从简单查询到复杂企业级应用的所有数据库操作。|	最高。你可以执行任何 SQL 语句，完全控制，但责任也最大。|
|数据库支持	| 通过 SQLAlchemy 支持所有主流数据库（MySQL, PostgreSQL, SQLite, Oracle 等）。|	支持所有主流数据库，通过不同的方言（Dialect）。|	仅支持 MySQL。|

### **代码示例对比**
假设我们有一个 users 表，现在想让 LLM 回答“有多少个用户？”这个问题。

#### 1. 使用 mysql.connector（最底层）

``` python
import mysql.connector

# 1. 建立连接
conn = mysql.connector.connect(
    host="localhost",
    user="your_user",
    password="your_password",
    database="your_db"
)
cursor = conn.cursor()

# 2. 手动编写并执行 SQL
query = "SELECT COUNT(*) FROM users;"
cursor.execute(query)

# 3. 获取结果
result = cursor.fetchone()
count = result[0]
print(f"用户数量是：{count}")

# 4. 手动关闭连接
cursor.close()
conn.close()

# 5. 现在你需要再将 `count` 组织成自然语言回答给 LLM 或用户。
```

#### 2. 使用 SQLAlchemy（中层抽象）

``` python
from sqlalchemy import create_engine, text

# 1. 创建引擎（连接池）
engine = create_engine("mysql+mysqlconnector://user:password@localhost/your_db")

# 2. 连接并执行（使用 text() 避免 SQL 注入）
with engine.connect() as conn:
    result = conn.execute(text("SELECT COUNT(*) FROM users"))
    count = result.scalar() # 直接获取标量值

print(f"用户数量是：{count}")

# 3. 同样，需要自己处理与 LLM 的交互。
```

#### 3. 使用 LangChain 的 SQLDatabase（高级抽象）

``` python
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms import OpenAI

# 1. 创建 SQLDatabase 实例（它内部使用 SQLAlchemy）
db = SQLDatabase.from_uri("mysql+mysqlconnector://user:password@localhost/your_db")

# 2. 创建 LLM 和 Toolkit
llm = OpenAI(temperature=0)
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 3. 创建 Agent
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True
)

# 4. 直接问自然语言问题！Agent 会自己决定如何查询数据库并组织答案。
agent_executor.run("我们有多少个用户？")

```

输出会类似于：

```
text
> 进入链...
行动： sql_db_list_tables
行动输入： ""
观察： users, products, orders...
...
思想： 我需要查询 users 表的总数。
行动： sql_db_query
行动输入： "SELECT COUNT(*) FROM users"
观察： [(15,)]
思想： 现在我知道答案了。
最终答案： 我们有15个用户。
```

## Set Up MySql

### Install Mysql Client 
```
sudo apt install mysql-client
```
#### GUI Client MySQl Workbench

GUI tools please refer to [Workbench](https://www.mysql.com/products/workbench)

[Download Workbench](https://dev.mysql.com/downloads/workbench) and install it

**Install WorkBench**

`sudo dpkg -i mysql-workbench-community_8.0.42-1ubuntu24.04_amd64.deb `

* Fix install dependency if there is error
```
sudo apt-get install -f
sudo dpkg -i mysql-workbench-community_8.0.42-1ubuntu24.04_amd64.deb 
```
**Note Remove package by the command**: `sudo dpkg -r mysql-workbench-community-dbgsym`

### Start Database Server

```
cd agent-examples/docker_compose/
docker compose -f compose_db.yaml up -d
```

### Connect to MySql Server 

```
mysql --host=127.0.0.1 --port=3306 -u root -p
```

![Client access MySql](./accessory/sql_client.png)
or

Workbench: 
Start `MySql Workbench`
![Start MySql Workbench](./accessory/workbench_start.png)


## Sql Command

![Sql access in Workbench](./accessory/workbench_sql.png)

```
CREATE DATABASE testDB;
show databases;
use testDB;
CREATE TABLE Persons_InfoTb (
         ID int NOT NULL,
         LastName varchar(255) NOT NULL,
         FirstName varchar(255),
         Age int,
         PRIMARY KEY (ID)
     );

INSERT INTO Persons_InfoTb VALUES (1, 'Zhang', 'San', 45);
INSERT INTO Persons_InfoTb VALUES (2, 'Li', 'Si', 35);
show tables;
select * from Persons;
```

