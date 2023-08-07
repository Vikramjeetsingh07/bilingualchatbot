#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import openai

# This is the yellow title
st.markdown(
    """
    <h1 style="color: #FFD700; text-align: center; font-size: 48px; font-weight: bold; text-shadow: 2px 2px 4px #000000;">Hindi-English Bilingual ChatGPT</h1>
    """,
    unsafe_allow_html=True,
)


openai.api_key = db.secrets.get("OPENAI_API_KEY")
if not openai.api_key:  # Ask for key if we don't have one
    with st.chat_message("assistant"):
        st.write(
            """
        Hi there. You haven't provided me with an OpenAI API key that I can use. 
        Please provide a key in the box below so we can start chatting:
        """
        )
        api_key = st.text_input("Please type inn your API key", type="password")
        if api_key:
            db.secrets.put("OPENAI_API_KEY", api_key)
            st.experimental_rerun()
        st.stop()


# This is where we set the personality and style of our chatbot
prompt_template = """
        You are hindi tutor. you will answer everything in hindi and help in learning hindi. you can even answer messages given to you in hindi 
    """

# When calling ChatGPT, we  need to send the entire chat history together
# with the instructions. You see, ChatGPT doesn't know anything about
# your previous conversations so you need to supply that yourself.
# Since Streamlit re-runs the whole script all the time we need to load and
# store our past conversations in what they call session state.
prompt = st.session_state.get(
    "prompt", [{"role": "system", "content": prompt_template}]
)


for message in prompt:
    # If we have a message history, let's display it
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# This is where the user types a question
question = st.chat_input("Ask me anything")


if question:  # Someone have asked a question
    # First we add the question the question to our message history
    prompt.append({"role": "user", "content": question})

    # Let's post our question and a place holder for the bot answer
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        botmsg = st.empty()

    # Here we call ChatGPT with streaming
    response = []
    result = ""
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=prompt, stream=True
    ):
        text = chunk.choices[0].get("delta", {}).get("content")
        if text is not None:
            response.append(text)
            result = "".join(response).strip()

            # Let us update the Bot's answer with the new chunk
            botmsg.write(result)

    # When we get an answer back we add that to the message history
    prompt.append({"role": "assistant", "content": result})

    # Finally, we store it in the session state
    st.session_state["prompt"] = prompt

