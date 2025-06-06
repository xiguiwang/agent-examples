# Some conception in Langchain, MCP etc. 

## Tool call
The result would be an AIMessage containing the model's response in natural language (e.g., "Hello!"). However, if we pass an input relevant to the tool, the model should choose to call it:

```
result = llm_with_tools.invoke("What is 2 multiplied by 3?")
```

But, if the tool was called, result will have a tool_calls attribute. This attribute includes everything needed to execute the tool, including the tool name and input arguments:

```
result.tool_calls
{'name': 'multiply', 'args': {'a': 2, 'b': 3}, 'id': 'xxx', 'type': 'tool_call'}
```

## Langchain Tools 

### Overview
The **tool** abstraction in LangChain associates a Python **function** with a **schema** that defines the function's **name, description** and **expected arguments**.

**Tools** can be passed to **chat models** that support **tool calling** allowing the model to request the execution of a specific function with specific inputs.

### Tool interface

The tool interface is defined in the BaseTool class which is a subclass of the Runnable Interface.

The key attributes that correspond to the tool's schema:

* name: The name of the tool.
* description: A description of what the tool does.
* args: Property that returns the JSON schema for the tool's arguments.
* 
The key methods to execute the function associated with the tool:

* invoke: Invokes the tool with the given arguments.
* ainvoke: Invokes the tool with the given arguments, asynchronously. Used for async programming with Langchain.

### Tool artifacts
Tools are utilities that can be called by a model, and whose outputs are designed to be fed back to a model. Sometimes, however, there are artifacts of a tool's execution that we want to make accessible to downstream components in our chain or agent, but that we don't want to expose to the model itself. For example if a tool returns a custom object, a dataframe or an image, we may want to pass some metadata about this output to the model without passing the actual output to the model. At the same time, we may want to be able to access this full output elsewhere, for example in downstream tools.


```
@tool(response_format="content_and_artifact")
def some_tool(...) -> Tuple[str, Any]:
    """Tool that does something."""
    ...
    return 'Message for chat model', some_artifact 
```
See [how to return artifacts](https://python.langchain.com/docs/how_to/tool_artifacts/) from tools for more details.


### DeepSpeed explaination 
在 LangChain 框架中，`@tool`是一个非常重要的装饰器（decorator），它的作用是将普通 Python 函数转换为 LangChain 的工具（Tool）对象。让我详细解释一下：

1. `@tool` 是什么？
* **装饰器（Decorator）** ：Python 的特殊语法，用于修改或增强函数的行为

* **工具转换器**：将普通函数转换为 LangChain 的 Tool 类实例

* **元数据提取器**：自动从函数中提取名称、描述和参数信息

2. 装饰后的变化
你的代码：

```python
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
```
实际上等价于：

```python
from langchain_core.tools import Tool

def multiply(a: int, b: int) -> int:
    return a * b

# 手动创建 Tool 实例
multiply_tool = Tool(
    name="multiply",
    description="Multiply two numbers.",
    func=multiply,
    args_schema={
        "a": {"type": "int", "description": ""},
        "b": {"type": "int", "description": ""}
    }
)
```

3. 关键作用

| 功能 |  说明 |  示例中的表现|
|----|-----|--------|
|工具封装   | 将函数包装成 LangChain 可识别的工具对象 |	multiply 函数变成 Tool 实例|
|元数据提取	|自动获取函数名、文档字符串和参数类型	|使用函数名 "multiply" 和 docstring 作为描述|
|类型验证	|基于函数注解自动验证输入参数类型	|确保 a 和 b 都是整数|
|代理集成	|使函数能被 LangChain 代理（Agent）调用	|代理可以识别并使用此工具|

4. 实际使用场景
当你在 LangChain 代理中这样使用时：

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent


# 创建包含多个工具的代理
tools = [multiply]  # 注意：这里使用装饰后的工具对象

agent = create_tool_calling_agent(llm, tools, prompt)
```
代理可以:

 1. 自动识别工具名称和描述（"multiply" 和 "Multiply two numbers."）

 1. 理解参数要求（需要两个整数）

 1. 在需要计算时调用此工具

 1. 将结果整合到后续处理中

5. 查看工具信息
你可以检查装饰后的对象：

```python
print(multiply.name)       # 输出: "multiply"
print(multiply.description) # 输出: "Multiply two numbers."
print(multiply.args)       # 输出: {'a': {'type': 'int'}, 'b': {'type': 'int'}}
```
6. 为什么需要这样设计？
LangChain 的代理系统需要：

 * 标准化工具接口

 * 自动化的工具发现机制

 * 统一的参数验证

 * 无缝的与语言模型协作

`@tool` 装饰器正是为了解决这些问题而设计的，它让普通函数可以无缝集成到 LangChain 的代理工作流中，而不需要手动创建复杂的封装对象。


## MCP tools

在 MCP (Model Control Protocol) 框架中，`@mcp.tool()` 是一个用于注册工具函数到MCP服务器的**装饰器**。它的作用与 LangChain 中的`@tool`类似，但服务于不同的框架和目的。让我详细解释：

1. MCP 框架背景
MCP 是一个用于模型控制和通信的协议框架。在你提供的示例中：

```python
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Math")  # 创建名为 "Math" 的 MCP 服务器
```
2. @mcp.tool() 的作用
这是一个**装饰器工厂函数**，它的核心功能是：

|  功能 |  说明 |
|-----|-----|
|工具注册   |	将普通 Python 函数注册为 MCP 服务器可调用的远程工具|
|接口暴露   |	使函数可通过 MCP 协议从外部调用（如通过 stdio 传输）|
|元数据提取 |	自动提取函数签名和文档字符串作为工具描述|
|类型处理	|   基于类型注解处理参数验证和序列化|

3. 装饰器的工作原理
当你这样使用时：

```python
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
```
实际上等价于：

```python
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

# 注册到 MCP 服务器
mcp.register_tool(
    name="add",
    description="Add two numbers",
    function=add,
    parameter_types={"a": int, "b": int},
    return_type=int
)
```
4. 关键特性

a) 自动名称和描述提取
 * 使用函数名作为工具名（`add`, `multiply`）

 * 使用 docstring 作为工具描述

b) 类型注解处理
 * 自动识别参数类型（`a: int, b: int`）

 * 自动识别返回类型（`-> int`）

 * 提供类型安全的远程调用

c) 传输协议集成
```python
mcp.run(transport="stdio")  # 使用标准输入输出作为通信通道
```
这意味着函数可以通过：

* 命令行调用

* 其他进程通信

* 网络请求（如果使用其他传输方式）

5. 实际使用场景示例

假设你启动了这个服务，可以通过以下方式调用：

```json
// 输入（通过 stdin 发送）
{
  "tool": "add",
  "args": {"a": 5, "b": 3}
}

// 输出（通过 stdout 返回）
{
  "result": 8
}
```
6. 与 LangChain 的 `@tool` 比较

|特性   |  MCP 的 @mcp.tool()| LangChain 的 @tool|
|-----|-------------------|------------------|
| 框架 |	MCP 服务框架|	LangChain 代理框架 |
|主要用途	|创建可远程调用的服务	|创建 AI 代理可使用的工具|
|通信方式	|通过传输层（stdio/HTTP等）|	进程内直接调用|
|类型系统	|强类型，基于注解	|强类型，基于 Pydantic|
|部署场景	|独立服务/微服务	|AI 应用内部组件|

7. 为什么需要这样设计？

 * **解耦**：将功能作为独立服务运行

 * **跨语言支持**：任何能处理 stdio/HTTP 的语言都可调用

 * **模型隔离**：避免将模型直接加载到主应用

 * **可扩展性**：轻松添加新工具而不影响主程序

总之，`@mcp.tool()` 是 MCP 框架中用于声明和暴露远程可调用服务的核心机制，它让普通 Python 函数成为可通过标准协议访问的微服务。

## Reference
* https://python.langchain.com/docs/concepts/tools
* https://langchain-ai.github.io/langgraph/agents/tools
* https://github.com/langchain-ai/langchain/blob/9a78246d29d07fa7806e9426efd0ef8e82b07394/libs/core/langchain_core/tools/simple.py#L33
