import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.tools import ShellTool
from langchain_core.messages import SystemMessage


class UnzipAgent:
    """
    UnzipAgent is a class for unzipping all zip files at a specified path.
    Initialize UnzipAgent with a large language model and an embedding model.
    """

    def __init__(self, llm, embedding):
        self.llm = llm
        shell_tool = ShellTool()
        self.tools = [shell_tool]

        unzip_prompt_template = """
        Please decompress all the zip files from the given path: {raw_path} to {unzip_path}.

        Note that:
        1. Each extracted file should be stored in a new directory corresponding to the zip filename. This will prevent errors during future decompression of files with similar names.
        2. All paths should be processed using UTF-8 encoding.
        """

        system_prompt = """
        Please ensure that all tools and environment settings are properly set up. Follow these steps to decompress the zipfile:
        1. Set the working directory to the given raw path.
        2. Decompress all the zip files from the given raw directory path to the specified unzip path.
        You can use Python scripts or shell commands to complete these tasks. If errors occur, log them and try alternative methods.
        """

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder("chat_history", optional=True),
                ("human", unzip_prompt_template),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

    def invoke(self, zip_dir, unzip_dir):
        """
        Invokes the UnzipAgent to decompress all zip files at the specified path.
        """
        os.makedirs(unzip_dir, exist_ok=True)
        

        self.agent_executor.invoke(
            {
                "raw_path": zip_dir,
                "unzip_path": unzip_dir,
                "chat_history": [
                    SystemMessage(
                        content="Please ensure operations are always completed in the directories specified by the user."
                    ),
                ],
            }
        )
