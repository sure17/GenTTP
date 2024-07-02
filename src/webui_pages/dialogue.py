import streamlit as st
from src.porvider import Provider


st.title("Chat")

with st.chat_message("assistant"):
    st.write("Hello 👋")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []


if Provider.get_agent(st.session_state.get("chat_option", "")) is None:
    Provider.init_agent(st.session_state.get("chat_option", ""))

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    if Provider.get_agent(st.session_state.get("chat_option", "")) is None:
        with st.chat_message("assistant"):
            st.write("You should configure the app first in the settings page.")
    else:
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            try:
                response = st.write_stream(
                    Provider.get_agent(st.session_state.get("chat_option", "")).stream(
                        prompt
                    )
                )
            except Exception as e:
                response = e
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
