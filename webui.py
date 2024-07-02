import os
if os.environ.get("GenTTP", False):
    __import__("pysqlite3")
    import sys

    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")


import streamlit as st
from src.porvider import Provider


def main():
    config_page = st.Page(
        "src/webui_pages/config.py", title="Settings", icon=":material/settings:"
    )
    dialogue_page = st.Page(
        "src/webui_pages/dialogue.py", title="Dialogue", icon=":material/chat:"
    )

    pg = st.navigation([dialogue_page, config_page])
    st.set_page_config(page_title="GenTTP")

    pg.run()

    with st.sidebar:
        st.write("LLM: ", Provider.get_current_llm()[1])
        st.write("Embedding: ", Provider.get_current_embedding()[1])
        st.write("Collection: ", Provider.get_current_collection()[1])
        chat_option = st.selectbox("Chat Agent", ["dialogue", "query"], index=1)
        st.session_state.chat_option = chat_option
        if st.session_state.get("agent", None) is None:
            st.write("Agents: None")
        else:
            for agent in st.session_state.agent:
                st.write("Agent: ", agent)


if __name__ == "__main__":
    main()
