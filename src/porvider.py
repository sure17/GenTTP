import streamlit as st
from src.agents.dialogue import DialogueAgent
from src.agents.query import QueryAgent
from src.agents.unzip import UnzipAgent
from src.agents.analyze import AnalysisAgent
import logging


class Dashscope:
    model_names = ["qwen-turbo", "qwen-plus"]
    embedding_names = ["text-embedding-v1", "text-embedding-v2"]
    url = "https://dashscope.console.aliyun.com/model"

    def config_ui(self):
        with st.container(border=True):
            st.subheader("Dashscope")
            st.write(self.url)
            api_key = st.text_input(
                "API Key", value=st.session_state.get("api_key", "")
            )
            st.session_state.api_key = api_key
            model_name = st.selectbox("Model Name", self.model_names, index=0)
            if st.button("Load LLM") and api_key != "":
                from langchain_community.llms import tongyi

                Provider.register_llm(
                    tongyi.Tongyi(dashscope_api_key=api_key, model_name=model_name),
                    model_name,
                )

            embedding_name = st.selectbox("Embedding Name", self.embedding_names)
            if st.button("Load embedding") and api_key != "":
                from langchain_community.embeddings import DashScopeEmbeddings

                Provider.register_embedding(
                    DashScopeEmbeddings(
                        dashscope_api_key=api_key, model=embedding_name
                    ),
                    embedding_name,
                )


class Qianfan:
    model_names = ["ERNIE-4.0-8K", "ERNIE-3.5-128K"]
    embedding_names = ["Embedding-V1"]
    url = "https://console.bce.baidu.com/qianfan/modelcenter/model/buildIn/list"

    def config_ui(self):
        with st.container(border=True):
            st.subheader("Qianfan")
            st.write(self.url)
            api_key = st.text_input(
                "API Key", value=st.session_state.get("api_key", "")
            )
            st.session_state.api_key = api_key
            secret_key = st.text_input(
                "Secret Key", value=st.session_state.get("secret_key", "")
            )
            st.session_state.secret_key = secret_key
            model_name = st.selectbox("Model Name", self.model_names)
            if st.button("Load LLM") and api_key != "" and secret_key != "":
                from langchain_community.llms import baidu_qianfan_endpoint

                Provider.register_llm(
                    baidu_qianfan_endpoint.QianfanLLMEndpoint(
                        model=model_name, qianfan_ak=api_key, qianfan_sk=secret_key
                    ),
                    model_name,
                )

            embedding_name = st.selectbox("Embedding Name", self.embedding_names)
            if st.button("Load embedding") and api_key != "" and secret_key != "":
                from langchain_community.embeddings import baidu_qianfan_endpoint

                Provider.register_embedding(
                    baidu_qianfan_endpoint.QianfanEmbeddingsEndpoint(
                        model=embedding_name, qianfan_ak=api_key, qianfan_sk=secret_key
                    ),
                    embedding_name,
                )


class Volcano:
    model_names = ["doubao-pro-32k", "doubao-lite-32k"]
    embedding_names = ["doubao-embedding"]

    url = "https://console.volcengine.com/ark/region:ark+cn-beijing/model"

    def config_ui(self):
        with st.container(border=True):
            st.subheader("Volcano")
            st.write(self.url)
            api_key = st.text_input(
                "API Key", value=st.session_state.get("api_key", "")
            )
            st.session_state.api_key = api_key
            secret_key = st.text_input(
                "Secret Key", value=st.session_state.get("secret_key", "")
            )
            st.session_state.secret_key = secret_key
            model_name = st.selectbox("Model Name", self.model_names)
            if st.button("Load LLM") and api_key != "" and secret_key != "":
                from langchain_community.llms import volcengine_maas

                Provider.register_llm(
                    volcengine_maas.VolcEngineMaasLLM(
                        model=model_name,
                        volc_engine_maas_ak=api_key,
                        volc_engine_maas_sk=secret_key,
                    ),
                    model_name,
                )

            embedding_name = st.selectbox("Embedding Name", self.embedding_names)
            if st.button("Load embedding") and api_key != "" and secret_key != "":
                from langchain_community.embeddings import volcengine

                Provider.register_embedding(
                    volcengine.VolcanoEmbeddings(
                        model=embedding_name,
                        volcano_ak=api_key,
                        volcano_sk=secret_key,
                    ),
                    embedding_name,
                )


class OpenAI:
    model_names = ["gpt-3.5-turbo"]
    embedding_names = ["text-embedding-ada-002"]
    url = "https://openai.com"

    def config_ui(self):
        with st.container(border=True):
            st.subheader("OpenAI")
            st.write(self.url)
            api_key = st.text_input(
                "API Key", value=st.session_state.get("api_key", "")
            )
            st.session_state.api_key = api_key
            model_name = st.selectbox("Model Name", self.model_names)
            if st.button("Load LLM") and api_key != "":
                from langchain_openai import ChatOpenAI

                Provider.register_llm(
                    ChatOpenAI(
                        openai_api_key=api_key,
                        model_name=model_name,
                        base_url="https://api.openai-hub.com/v1",
                    ),
                    model_name,
                )

            embedding_name = st.selectbox("Embedding Name", self.embedding_names)
            if st.button("Load embedding") and api_key != "":
                from langchain_openai import OpenAIEmbeddings

                Provider.register_embedding(
                    OpenAIEmbeddings(
                        openai_api_key=api_key,
                        model=embedding_name,
                        base_url="https://api.openai-hub.com/v1",
                    ),
                    embedding_name,
                )


llms = {
    "dashscope": Dashscope,
    "qianfan": Qianfan,
    "volcano": Volcano,
    "openai": OpenAI,
}

llms_list = list(llms.keys())

dialogue_agents = {"dialogue": DialogueAgent, "query": QueryAgent}

util_agents = {
    "unzip": UnzipAgent,
    "analyze": AnalysisAgent,
}

agents = {**dialogue_agents, **util_agents}


class Provider:
    @staticmethod
    def get_database():
        return st.session_state.get("database_client", None)

    @staticmethod
    def init_database(database_path):
        from chromadb import PersistentClient

        st.session_state.database_path = database_path
        st.session_state.database_client = PersistentClient(path=database_path)
        logging.info(f"Initialized database client")

    @staticmethod
    def get_collection(collection_name):
        return st.session_state.database_client.get_collection(collection_name)

    @staticmethod
    def register_collection(collection_name):
        st.session_state.current_collection = {}
        st.session_state.current_collection["name"] = collection_name
        st.session_state.current_collection["instance"] = (
            st.session_state.database_client.get_or_create_collection(collection_name)
        )
        logging.info(f"Registered collection {collection_name}")

    @staticmethod
    def get_current_collection():
        current_collection = st.session_state.get("current_collection", {})
        return current_collection.get("instance", None), current_collection.get(
            "name", None
        )

    @staticmethod
    def get_llm(llm_name):
        return llms[llm_name]()

    @staticmethod
    def register_llm(llm, name):
        st.session_state.llm = {}
        st.session_state.llm["instance"] = llm
        st.session_state.llm["name"] = name
        st.session_state.agent = None

    @staticmethod
    def register_embedding(embedding, name):
        st.session_state.embedding = {}
        st.session_state.embedding["instance"] = embedding
        st.session_state.embedding["name"] = name
        st.session_state.agent = None

    @staticmethod
    def get_current_llm():
        current_llm = st.session_state.get("llm", {})
        return current_llm.get("instance", None), current_llm.get("name", None)

    @staticmethod
    def get_current_embedding():
        current_embedding = st.session_state.get("embedding", {})
        return current_embedding.get("instance", None), current_embedding.get(
            "name", None
        )

    @staticmethod
    def get_agent(agent_name):
        if st.session_state.get("agent", None) is None:
            return None
        return st.session_state.agent.get(agent_name, None)

    @staticmethod
    def register_agent(agent_name, agent):
        if st.session_state.get("agent", None) is None:
            st.session_state.agent = {}
        st.session_state.agent[agent_name] = agent
        logging.info(f"Registered agent {agent_name}")

    @staticmethod
    def init_agent(agent_name):
        llm = st.session_state.get("llm", {}).get("instance", None)
        embedding = st.session_state.get("embedding", {}).get("instance", None)
        if llm and embedding:
            try:
                agent = agents[agent_name](llm, embedding)
                if hasattr(agent, "load_database"):
                    collection = Provider.get_current_collection()[1]
                    database_path = st.session_state.get("database_path", None)
                    if not collection or not database_path:
                        return None
                    agent.load_database(database_path, collection)
                if hasattr(agent, "load_vectorstore"):
                    agent.load_vectorstore(
                        st.session_state.get(
                            "vectorstore_path", "./data/attack_vector.xlsx"
                        )
                    )
                Provider.register_agent(agent_name, agent)
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                return None
        else:
            return None
