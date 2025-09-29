import streamlit as st
from ai_agents.suggestion_provider.suggester import DummyLLM , SalesAssistantAgent

llm = DummyLLM()
agent = SalesAssistantAgent(llm)

def render():
    st.header("🛍️ AI Sales Assistant")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Create two containers: one for messages, one for input
    messages_container = st.container()
    input_container = st.container()

    # Chat input (always at bottom)
    with input_container:
        user_input = st.chat_input("Ask me about deals, products, or prices...")

    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = agent.run(user_input, st.session_state.chat_history)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

    # Display messages (latest at bottom)
    with messages_container:
        for msg in st.session_state.chat_history:
            st.chat_message(msg["role"]).markdown(msg["content"])
