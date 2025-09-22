from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import ChatOpenAI

from langgraph.graph import MessagesState

#urls = [
#    "https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/",
#]
#docs = [WebBaseLoader(url).load() for url in urls]
# convert [[doc00, doc01], [doc10, doc11]] to [doc00, doc01, doc10, doc11]
#docs_list = [item for sublist in docs for item in sublist]

# Read file into paragraphs
with open("ticket.txt", "r", encoding="utf-8") as file:
    content = file.read()

# Split by two or more newlines (paragraph separator)
paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
docs = [Document(page_content=item) for item in paragraphs]
#print(docs)

#text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
#    chunk_size=256, chunk_overlap=50)
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=512,  # 增大分块大小
    chunk_overlap=30,  # 减少重叠
    separators=["\n\n", "\n", "。", "！", "？", "；", "，", "、", ""]  # 明确指定分隔符
)
doc_splits = text_splitter.split_documents(docs)

result = doc_splits[0].page_content.strip()
#print(result)


from langchain_core.vectorstores import InMemoryVectorStore

embeddings = OllamaEmbeddings(model="nomic-embed-text")

vectorstore = InMemoryVectorStore.from_documents(
    documents=doc_splits, embedding=embeddings)

retriever = vectorstore.as_retriever(
    Dearch_type="similarity",
    search_kwargs={
        "k": 8,                 # 返回结果数量 (top-k)
        #"score_threshold": 0.2  # 相似度/距离阈值，0.0~1.0 之间，越高越严格
    })
#Create a retriever tool using LangChain's prebuilt create_retriever_tool:


from langchain.tools.retriever import create_retriever_tool

retriever_tool = create_retriever_tool(
    retriever,
    "检索铁路相关内容",
    "检索铁路部门，铁路运输的相关内容.包括且不限于:车票，列车信息，托运旅物资等游.",
)

#Test the tool:
'''
documents = retriever.get_relevant_documents("有哪些购买火车票的方式？")
print("返回文档数量:", len(documents))
for i, doc in enumerate(documents):
    print(f"文档{i+1}: {doc.page_content}")

result = retriever_tool.invoke({"query": "有哪些购买火车票的方式？"})
print("Query: 有哪些购买火车票的方式?, len", len(result), result)

result = retriever_tool.invoke({"query": "如何补票"})
print("Query: 如何补票, len: ", len(result), result)
'''

inference_server_url = "http://localhost:8000/v1"
model="Qwen/Qwen3-4B"

llm = ChatOpenAI(
    model=model,
    openai_api_key="EMPTY",
    openai_api_base=inference_server_url,
    max_tokens=2048,
    temperature=0.0,
)

import pdb
pdb.set_trace()

llm_with_tools = llm.bind_tools([retriever_tool])

def generate_query_or_respond(state: MessagesState):
    response = llm_with_tools.invoke(state["messages"]) 
    return {"messages": [response]}

input_d = { "messages" :[ {"role":"user", "content":"有哪些购买火车票的方式"}, 
                          {"role":"system", "content":"你是个有用的小帮手，请根据上下文类容回答用户问题。"}] }

output = generate_query_or_respond(input_d)
print(output["messages"][-1].pretty_print())
