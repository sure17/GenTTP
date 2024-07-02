from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


class QueryAgent:
    def __init__(self, llm, embedding):
        self.embeddings = embedding
        self.llm = llm
        template = """
        TTP (Tactics, Techniques, and Procedures) is used to describe the attack behaviors and sequences of open source software malware. Specifically, TTPs include strategies (tactics) for tricking users into installing malware, and specific techniques (technologies and procedures) for executing malicious activities. These represent attack patterns for malware packages. Each JSON file in the database contains information about a malware package, such as the package name, TTPs, and the analysis process of these TTPs.

        ########
        Guidelines:
        1. If the question is factual, provide a direct and concise answer.
        2. If the question is open-ended, offer a detailed and thoughtful response.
        3. If the information is insufficient, acknowledge it and suggest possible next steps.
        ########

        **User Question:** {question}
        **Relevant Information:** {context}
        You are a Malware Package Behavior Analysis Engineer working on software supply chain security. Your task is to generate a response based on the user's question and relevant information retrieved from the database. Provide a detailed and accurate response, referring to "analysis_process" in the database when explaining the TTP analysis process for a malware package, and use the "→" symbol to link the "TTP" in the database for a malware package.
        """

        self.prompt = ChatPromptTemplate.from_template(template)

    def load_database(self, database_path, collection_name):
        self.vectorstore = Chroma(
            collection_name=collection_name,
            persist_directory=database_path,
            embedding_function=self.embeddings,
        )
        self.retriever = self.vectorstore.as_retriever()

    def invoke(self, question):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10})
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        response = rag_chain.invoke(question)
        return response

    def stream(self, question):
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 10})
        rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        for response in rag_chain.stream(question):
            yield response
