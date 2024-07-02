import streamlit as st
import pandas as pd
from src.porvider import Provider, llms_list, util_agents
import os


def update_options():
    if st.session_state.selected_option != st.session_state.llm_options[0]:
        st.session_state.llm_options.remove(st.session_state.selected_option)
        st.session_state.llm_options.insert(0, st.session_state.selected_option)


# LLM Config
with st.container():
    st.title("Configure")
    st.session_state.setdefault("llm_options", llms_list)
    series_option = st.selectbox(
        "LLM Series",
        options=st.session_state.llm_options,
        key="selected_option",
        on_change=update_options,
    )
    with st.empty():
        llm = Provider.get_llm(series_option)
        llm.config_ui()


def explore_file(dir_path_list, path_names):
    with st.empty():
        length = len(dir_path_list)
        cols = st.columns(length)
        for i in range(length):
            with cols[i]:
                df = pd.DataFrame(dir_path_list[i], columns=[path_names[i]])
                st.dataframe(df)


def explore_dir(dir_path_list):
    dirs = []
    path_names = []
    for dir_path in dir_path_list:
        if os.path.exists(dir_path):
            path_name = os.path.basename(dir_path)
            path_names.append(path_name)
            dirs.append(os.listdir(dir_path))
    explore_file(dirs, path_names)


with st.container(border=True):
    st.title("Knowledge Base")
    if not os.environ.get("GenTTP", False):
        with st.container():
            st.header("File Inspector")
            if st.button("Reload Agent"):
                progress_text = "Operation in progress. Please wait."
                bar = st.progress(0, text=progress_text)

                agents = list(util_agents.keys())
                for idx in range(len(agents)):
                    agent_name = agents[idx]
                    Provider.init_agent(agent_name)
                    bar.progress((idx + 1) / len(agents), text=progress_text)
                bar.empty()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                raw_file_path = st.text_input("Raw File Path", value="data/raw")
                inspect = st.button("Inspect")
            with col2:
                unzip_file_path = st.text_input("Unzip File Path", value="data/unzip")
                unzip = st.button("Unzip")
            with col3:
                analysis_file_path = st.text_input(
                    "Analysis File Path", value="data/analysis"
                )
                analysis_unzip = st.button("Analyze")
            with col4:
                vectorstore_path = st.text_input(
                    "Vectorstore Path", value="data/attack_vector.xlsx"
                )

            if unzip:
                if Provider.get_agent("unzip"):
                    llm_name = Provider.get_current_llm()[1]
                    if "gpt" not in llm_name:
                        st.error("Please select a GPT model to unzip.")
                    else:
                        try:
                            with st.spinner("Unzip..."):
                                Provider.get_agent("unzip").invoke(
                                    raw_file_path, unzip_file_path
                                )
                                explore_dir(
                                    [raw_file_path, unzip_file_path, analysis_file_path]
                                )
                        except Exception as e:
                            st.error(e)
                else:
                    st.write("Please configure the app first.")
            if inspect:
                explore_dir([raw_file_path, unzip_file_path, analysis_file_path])

            if analysis_unzip:
                if Provider.get_agent("analyze"):
                    analyze_progress_text = "Analyze..."
                    analyze_bar = st.progress(0, text=analyze_progress_text)

                    try:
                        for i, length in Provider.get_agent("analyze").invoke(
                            unzip_file_path, analysis_file_path
                        ):
                            analyze_bar.progress(i / length, text=analyze_progress_text)
                        explore_dir(
                            [raw_file_path, unzip_file_path, analysis_file_path]
                        )
                    except Exception as e:
                        st.error(e)
                    analyze_bar.empty()
                else:
                    st.write("Please configure the app first.")

    with st.container():
        st.header("Chromadb Inspector")
        if os.environ.get("GenTTP", False):
            st.write("Database Path: example/chroma_database")
            database_path = "example/chroma_database"
        else:
            database_path = st.text_input("Database Path", value="data/chroma_database")

        def inspect_collection(collection_name):
            collection = Provider.get_collection(collection_name)
            result = collection.get(include=["embeddings", "documents", "metadatas"])
            df = pd.DataFrame(
                {
                    "ids": result["ids"],
                    "embeddings": result["embeddings"],
                    "documents": result["documents"],
                    "metadatas": result["metadatas"],
                }
            )
            st.dataframe(df)

        if st.button("Reload Chromadb") or os.environ.get("GenTTP", False):
            Provider.init_database(database_path)

        if Provider.get_database():
            client = Provider.get_database()
            collection_names = [
                collection.name for collection in client.list_collections()
            ]
            collection_name = st.selectbox("Select Collection", collection_names)
            if not os.environ.get("GenTTP", False):
                with st.expander("Add Collection", expanded=False):
                    add_collection_name = st.text_input("Collection Name")
                    if st.button("Add Collection") and add_collection_name != "":
                        Provider.register_collection(add_collection_name)

        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            chromadb_inspect = st.button("Inspect", key="chromadb_inspect")
        with col2:
            load_collection = st.button("Load Collection")
        if not os.environ.get("GenTTP", False):
            with col3:
                import_btn = st.button("Import")
        else:
            import_btn = False

        if chromadb_inspect and collection_name:
            inspect_collection(collection_name)

        if (load_collection and collection_name) or os.environ.get("GenTTP", False):
            Provider.register_collection(collection_name)

        if import_btn and collection_name:
            from langchain_chroma import Chroma

            collection = Chroma(
                collection_name=collection_name,
                persist_directory=database_path,
                embedding_function=Provider.get_current_embedding()[0],
            )

            from src.utils.data import add_document

            import_progress_text = "Importing..."
            import_bar = st.progress(0, text=import_progress_text)
            for i, length in add_document(
                collection=collection,
                embedding=Provider.get_current_embedding()[0],
                input_dir=analysis_file_path,
            ):
                import_bar.progress(i / length, text=import_progress_text)
            import_bar.empty()
            inspect_collection(collection_name)
