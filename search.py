# <!--IMPORTS:[{"imported": "Tool", "source": "langchain_core.tools", "docs": "https://python.langchain.com/api_reference/core/tools/langchain_core.tools.simple.Tool.html", "title": "Google Search"}]-->
import os
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

search = GoogleSearchAPIWrapper(k=1)

tool = Tool(
    name="google_search",
    description="Search Google for recent results.",
    func=search.run,
    google_api_key=GOOGLE_API_KEY,
    google_cse_id=GOOGLE_CSE_ID,
)

tool.run("Obama's first name?")
