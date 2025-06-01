from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_openai import ChatOpenAI

inference_server_url = "http://localhost:8000/v1"

llm = ChatOpenAI(
    model="Qwen/Qwen3-4B",
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=32,
    temperature=0,
)


messages = [
    SystemMessage(
        content="You are a helpful assistant that translates English to Chinese."
    ),
    HumanMessage(
        content="Translate the following sentence from English to Chinese: I love programming."
    ),
]

ret=llm.invoke(messages)
print(ret)


'''
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(
    model="claude-3-7-sonnet-latest",
    temperature=0,
    max_tokens=2048
)

agent = create_react_agent(
    model=llm,
    # other parameters
)
'''
