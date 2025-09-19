from langgraph.func import entrypoint, task
from langgraph.types import Command, interrupt

@task
def step_1(input_query):
    """Append bar."""
    return f"{input_query} bar"

@task
def human_feedback(input_query):
    """Append user input."""
    feedback = interrupt(f"Please provide feedback: {input_query}")
    return f"{input_query} {feedback}"

@task
def step_3(input_query):
    """Append qux."""
    return f"{input_query} qux"

#We can now compose these tasks in an entrypoint:

from langgraph.checkpoint.memory import InMemorySaver

checkpointer = InMemorySaver()

@entrypoint(checkpointer=checkpointer)
def graph(input_query):
    result_1 = step_1(input_query).result()
    result_2 = human_feedback(result_1).result()
    result_3 = step_3(result_2).result()

    return result_3


config = {"configurable": {"thread_id": "1"}}

for event in graph.stream("foo", config):
    print(event)
    print("\n")


# Continue execution
events = graph.stream("foo", config)
for event in events:
    print(event)
    if "__interrupt__" in event:
        msg = event["__interrupt__"][0].value
        user_input = input(f"{msg} ")  # 真正阻塞等待用户输入
        # 恢复执行
        resume_events = graph.stream(Command(resume=user_input), config)
        for e in resume_events:
            print(e)
