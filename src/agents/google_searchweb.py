import os
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper

# Set environment variables
os.environ["GOOGLE_CSE_ID"] = ""  # enter your Google CSE ID
os.environ["GOOGLE_API_KEY"] = ""  # enter your Google API Key
os.environ["http_proxy"] = "http://127.0.0.1:7890" 
os.environ["https_proxy"] = "http://127.0.0.1:7890" 

# Create a Google search object
search = GoogleSearchAPIWrapper()

# Create a tool for Google search
tool = Tool(
    name="google_search",
    description="Search Google for results.",
    func=search.run,
)

# Run the tool with a search query
results = tool.run("site:sonatype.com/blog malware package")

# Print the search results
print(results)