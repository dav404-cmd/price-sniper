import streamlit as st
from ai_agents.suggestion_provider.suggester import DummyLLM, OpenRouterLLM, SalesAssistantAgent


def render():
    llm_mode = st.radio(
        "Run LLM by:",
        ["Api mode", "Local mode"],
        index=["Api mode", "Local mode"].index(st.session_state.get("llm_mode", "Api mode"))
    )

    # Only update agent if mode changed or agent not initialized
    if "agent" not in st.session_state or st.session_state.llm_mode != llm_mode:
        if llm_mode == "Api mode":
            llm = OpenRouterLLM()
            agent_info = {
                "name": "OpenRouterLLM",
                "description": "Running via OpenRouter API. Requires valid API key and credits."
            }
        else:
            llm = DummyLLM()
            agent_info = {
                "name": "DummyLLM (local)",
                "description": "Running locally. Requires llama3 installed on your machine."
            }

        st.session_state.agent = SalesAssistantAgent(llm)
        st.session_state.agent_info = agent_info
        st.session_state.llm_mode = llm_mode  # Update after agent setup

    agent = st.session_state.agent

    # Header + Mode Info
    st.header("🛍️ AI Sales Assistant")
    st.write(f"**Current LLM:** `{st.session_state.agent_info['name']}`")
    st.caption(st.session_state.agent_info["description"])

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
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
