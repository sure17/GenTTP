import os
import json
import pandas as pd
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough


def parse_json(str):
    # find json string
    start = str.find("{")
    end = str.rfind("}")
    if start == -1 or end == -1:
        return {}
    return json.loads(str[start : end + 1])


def format_malicious_behaviors_from_excel(excel_path):
    df = pd.read_excel(excel_path)
    formatted_behaviors = ""
    for _, row in df.iterrows():
        category = row["Category"]
        behavior = row["Name"]
        description = row["Description"]
        formatted_behaviors += (
            f"Category:{category} Name:{behavior} Description:{description} \n"
        )
    return formatted_behaviors


def get_file(target_path):
    code_content = ""
    all_files = []
    processed_files = set()
    for root, dirs, files in os.walk(target_path):
        for file in files:
            if "PKG-INFO" in file or file.endswith(".py"):
                all_files.append((root, file))
    all_files.sort(key=lambda x: (x[1].endswith(".py"), x[1]))

    for root, file in all_files:
        if file not in processed_files:
            processed_files.add(file)
            script_path = os.path.join(root, file)
            if os.path.isfile(script_path):
                with open(script_path, "r", encoding="utf-8") as file_content:
                    code_content += file + ":\n" + file_content.read() + "\n"
    return code_content


class AnalysisAgent:
    def __init__(self, llm, embedding):

        template = """
Task: Context-Based Analysis of Python Package for Security Threats

Objective: Perform a detailed, context-based analysis to identify potential security threats in a Python package, using user-provided {context} which includes names and descriptions of attack vectors.Let's think step by step.

Step 1: Information Collection and Preliminary Analysis
Input: User provides package information and Python code {file_content}.
Action: Identify and distinguish different Python files. Analyze the execution sequence of Python code.
Output: Catalog of Python files and their respective execution sequences.

Step 2: Detection of Deceiving AV Attack Vectors in pkg-info
Context: Utilize the user-provided context to identify specific deceiving attack vectors (names and descriptions).
Action: Examine pkg-info for characteristics matching the descriptions of deceiving attack vectors in the context,focuses on the information which is suspicious,unknown or uncertain.
Output: List of identified deceiving attack vectors based on context.

Step 3: Detection of Malicious AV Attack Vectors in Python Files
Context: Use the execution sequence from Step 1 and the context for targeted analysis.
Action: Scrutinize Python files for potential malicious attack vectors, focusing on their execution sequence and matching against context.
Output: List of identified malicious attack vectors based on context with the execution sequence.

Step 4:Report names of attack vectors
Action: Compile the findings from Steps 2 and 3. Focus on reporting the names of identified attack vectors.
Output: A list that includes:
Names of all identified vectors (deceiving and malicious).

Guidelines:
Progress through each step methodically, ensuring a thorough examination based on the provided context.
Document findings and observations systematically at each step.
Continuously cross-reference with context to ensure alignment with specified attack vector descriptions.
Provide regular summaries to maintain clarity and focus on the objectives.
You should output the results in a JSON format with the following structure:
```json
    "package_name": string // Name of the Python package
    "version": string // Version of the Python package
    "TTP": string // Tactics, Techniques, and Procedures
    "ecosystem": string // Software ecosystem
    "analysis_process": dict // Analysis process details
```

Example: notice the brackets should be placed in the right place, and \\n should be used to indicate a new line
```json
    "package_name": "bbeautifulsoup",
    "version": "0.1",
    "TTP": "Typosquatting\\nImitated description\\nEvasion\\ncmd",
    "ecosystem": "pypi",
    "analysis_process":
        "step_1":
            "description": "Catalog of Python Files and Their Respective Execution Sequences",
            "details": " 1: Catalog of Python Files and Their Respective Execution Sequences\\n\\nThe provided Python package contains two primary files of interest:\\n\\n1. **PKG-INFO**: Contains metadata about the package.\\n2. **setup.py**: A script used for installing the package, which includes suspicious obfuscated code.\n\n**Execution Sequence in setup.py**:\\n- The script checks the platform and then executes a block of obfuscated code that seems to conditionally import modules and perform operations based on complex conditions.\n- The obfuscated code and the use of direct system calls within a setup script are unusual and warrant further investigation.\\n\\n"
        ,
        "step_2": 
            "description": "Detection of Deceiving AV Attack Vectors in pkg-info",
            "details": " 2: Detection of Deceiving AV Attack Vectors in pkg-info\\n\\nBased on the provided context, let's examine the pkg-info for deceiving attack vectors:\\n\\n- **Name: bbeautifulsoup**: This closely mimics a well-known package named \"beautifulsoup4\", differing by one character. This matches the \"typosquatting\" deceiving AV vector.\\n- **Version: 0.1**: The version is suspiciously low for a well-known package, which might indicate an \"imitated version\" attack vector, although the description provided does not fully match this scenario.\\n- **Summary, Home-page, Author, Author-email, License, Description, Platform**: All are marked as UNKNOWN, which is suspicious and aligns with the \"imitated description\" vector, indicating an attempt to deceive by not providing legitimate information.\\n\\n"
        ,
        "step_3": 
            "description": "Detection of Malicious AV Attack Vectors in Python Files",
            "details": " 3: Detection of Malicious AV Attack Vectors in Python Files\\n\\nFocusing on the `setup.py` file:\n\n- The obfuscated code and conditional checks based on the system platform could be indicative of an \"evasion\" technique, designed to only execute malicious code under certain conditions.\\n- The use of direct system calls and attempts to import modules like `win32com` (which is unusual in a setup script) aligns with the \"cmd\" attack vector, indicating potential execution of malicious commands.\\n- The complex and obfuscated nature of the code itself could be considered a form of \"concealment\", making it difficult to understand the script's true purpose.\n\n"
        ,
        "step_4": 
            "description": "Report Names of Attack Vectors",
            "details": " 4: Report Names of Attack Vectors\n\nBased on the analysis, the identified attack vectors include:\n\n- **Deceiving AV Vectors**:\n  - Typosquatting (Name: bbeautifulsoup)\n  - Imitated description (Summary, Home-page, Author, Author-email, License, Description, Platform all UNKNOWN)\\n\\n- **Malicious AV Vectors**:\\n  - Evasion (Obfuscated code that checks the system platform)\n  - Cmd (Use of system calls and unusual imports)\\n\\nThis analysis highlights the importance of scrutinizing package metadata and the code within setup scripts for signs of malicious intent. The identified vectors suggest that the package is likely malicious, employing both deceiving and direct malicious techniques to potentially harm the user's system or environment."
        
    
```

YOUR RESPONSE:
"""
        self.prompt = ChatPromptTemplate.from_template(template)

        self.model = llm
        self.embeddings = embedding

    def load_vectorstore(self, vectorstore_path):
        formatted_behaviors = format_malicious_behaviors_from_excel(vectorstore_path)
        vectorstore = Chroma.from_texts(
            {formatted_behaviors},
            embedding=self.embeddings,
        )
        retriever = vectorstore.as_retriever()
        self.chain = (
            {"context": retriever, "file_content": RunnablePassthrough()}
            | self.prompt
            | self.model
            | StrOutputParser()
        )

    def process_subfolder(self, subfolder_path):
        try:
            file_content = get_file(subfolder_path)
            results = self.chain.invoke(file_content)
            return results
        except Exception as e:
            return {subfolder_path: {"result": str(e)}}

    def invoke(self, unzip_dir, result_dir):
        os.makedirs(result_dir, exist_ok=True)
        top_folder = unzip_dir
        subfolders = [
            os.path.join(top_folder, f)
            for f in os.listdir(top_folder)
            if os.path.isdir(os.path.join(top_folder, f))
        ]
        length = len(subfolders)
        for i in range(length):
            folder_path = subfolders[i]
       
            genavc_result = {}
            result = self.process_subfolder(folder_path)
            result = parse_json(result)
            genavc_result.update(result)
            folder_name = os.path.basename(folder_path)
            json_filename = os.path.join(result_dir, f"{folder_name}.json")
            with open(json_filename, "w") as json_file:
                json.dump(genavc_result, json_file, indent=4)
            yield i, length
