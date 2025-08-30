## What is an Agent
Agents are systems that use LLMs as reasoning engines to determine which actions to take and the inputs necessary to perform the action. After executing actions, the results can be fed back into the LLM to determine whether more actions are needed, or whether it is okay to finish. This is often achieved via tool-calling.

 [Anthropic's Building Effective Agents blog post](https://www.anthropic.com/engineering/building-effective-agents) define the Agent as:

"Agent" can be defined in several ways. Some customers define agents as fully autonomous systems that operate independently over extended periods, using various tools to accomplish complex tasks. Others use the term to describe more prescriptive implementations that follow predefined workflows. At Anthropic, we categorize all these variations as agentic systems, but draw an important architectural distinction between workflows and agents:

Workflows are systems where LLMs and tools are orchestrated through predefined code paths.
Agents, on the other hand, are systems where LLMs dynamically direct their own processes and tool usage, maintaining control over how they accomplish tasks.

## How Langgraph Implementation of Agent

At its core, LangGraph models agent workflows as graphs.

The grap is composed of nodes and edges. Simply speaking: Nodes do the work, edges tell what to do next.

* To get an idea of the graph and agent, here is code snap of langgraph agent:

There is a `START` edge (entry point) and a `chatbot` node in the graph.

```Python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START

from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

inference_server_url = "http://localhost:8000/v1"
llm = ChatOpenAI(
    model="Qwen/Qwen3-4B",
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=32,
    temperature=0,
)

def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()
```

### Components of Agent/Graph
 You define the behavior of your agents using three key components:

1. **State**: A shared data structure that represents the current snapshot of your application. It can be any Python type, but is typically a `TypedDict` or `Pydantic BaseModel`.

2. **Nodes**: Python functions that encode the logic of your agents. They receive the current `State` as input, perform some computation or side-effect, and return an updated `State`.

3. **Edges**: Python functions that determine which `Node` to execute next based on the current `State`. They can be conditional branches or fixed transitions.

### Map Workflow to the Graph

By composing `Nodes` and `Edges`, you can create complex, looping workflows that evolve the State over time. The real power, though, comes from how LangGraph manages that State. To emphasize: **Nodes and Edges are nothing more than Python functions** - they can contain an LLM or just good Python code.

In short: nodes do the work, edges tell what to do next.

### Understand the Workflow Exectuion throught Graph

LangGraph's underlying graph algorithm uses **message passing** to define a general program. When a Node completes its operation, it sends messages along one or more edges to other node(s). These recipient nodes then execute their functions, pass the resulting messages to the next set of nodes, and the process continues. Inspired by Google's Pregel system, the program proceeds in discrete "super-steps."

A super-step can be considered a single iteration over the graph nodes. Nodes that run in parallel are part of the same super-step, while nodes that run sequentially belong to separate super-steps. At the start of graph execution, all nodes begin in an inactive state. A node becomes active when it receives a new message (state) on any of its incoming edges (or "channels"). The active node then runs its function and responds with updates. At the end of each super-step, nodes with no incoming messages vote to halt by marking themselves as inactive. The graph execution terminates when all nodes are inactive and no messages are in transit.

### Compiling your Graph

To build your graph, you first define the state, you then add nodes and edges, and then you compile it. What exactly is compiling your graph and why is it needed?

Compiling is a pretty simple step. It provides a few basic checks on the structure of your graph (no orphaned nodes, etc). It is also where you can specify runtime args like checkpointers and breakpoints. You compile your graph by just calling the `.compile` method:

graph = graph_builder.compile(...)

You **MUST** compile your graph before you can use it.

### State

The first thing you do when you define a graph is define the State of the graph. The State consists of the schema of the graph as well as reducer functions which specify how to apply updates to the state. The schema of the state will be the input schema to all Nodes and Edges in the graph, and can be either a TypedDict or a Pydantic model. All Nodes will emit updates to the State which are then applied using the specified reducer function.

### Working with Messages in Graph State

Most modern LLM providers have a chat model interface that accepts a list of messages as input. LangChain's `ChatModel` in particular accepts a list of Message objects as inputs. These messages come in a variety of forms such as HumanMessage (user input) or AIMessage (LLM response).

### Node

In LangGraph, nodes are typically python functions (sync or async) where the first positional argument is the state, and (optionally), the second positional argument is a "config", containing optional configurable parameters (such as a thread_id).

### Edges

 *Noted* edges are functions.

Edges define how the logic is routed and how the graph decides to stop. This is a big part of how your agents work and how different nodes communicate with each other. There are a few key types of edges:

* `Normal Edges`: Go directly from one node to the next.
* `Conditional Edges`: Call a function to determine which node(s) to go next.
* `Entry Point`: Which node to call first when user input arrives.
* `Conditional Entry Point`: Call a function to determine which node(s) to call first when user input arrives.

A node can have MULTIPLE outgoing edges. If a node has multiple out-going edges, all of those destination nodes will be executed in parallel as a part of the next superstep.

#### Normal Edges
If you always want to go from node A to node B, you can use the add_edge method directly.

graph.add_edge("node_a", "node_b")

#### Conditional Edges
If you want to optionally route to 1 or more edges (or optionally terminate), you can use the add_conditional_edges method. This method accepts the name of a node and a "routing function" to call after that node is executed:

graph.add_conditional_edges("node_a", routing_function)
Similar to nodes, the routing_function accepts the current state of the graph and returns a value.

By default, the return value routing_function is used as the name of the node (or list of nodes) to send the state to next. All those nodes will be run in parallel as a part of the next superstep.

You can optionally provide a dictionary that maps the routing_function's output to the name of the next node.

graph.add_conditional_edges("node_a", routing_function, {True: "node_b", False: "node_c"})

### Recursion Limit

The recursion limit sets the maximum number of super-steps the graph can execute during a single execution. Once the limit is reached, LangGraph will raise GraphRecursionError. By default this value is set to 25 steps.

## Reference

* https://www.anthropic.com/engineering/building-effective-agents
* https://langchain-ai.github.io/langgraph/concepts/low_level/
