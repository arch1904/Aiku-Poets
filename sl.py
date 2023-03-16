import openai
import streamlit as st
# pip install streamlit-chat
from streamlit_chat import message
#/home/why/Desktop/Aiku-Poets/main.py

#openai.api_key = st.secrets["api_secret"]



header = st.container()
upload = st.container()
textInput = st.container()
chatbot = st.container()


with header:
    st.title('Top Applicant Speedpass')

l_col, r_col = st.columns(2)

with upload:
    st.header('1. Upload resumes')
    st.text('Select multiple PDFs for analysis')

    st.file_uploader("Select Files",'pdf', True)

#generating responses from ai
def generate_response(prompt):
    completions = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = prompt,
        max_tokens = 1024,
        n = 1,
        stop = None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message 

#Creating the chatbot interface
    st.title("chatBot : Streamlit + openAI")

# Storing the chat
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []

    if 'past' not in st.session_state:
        st.session_state['past'] = []

with textInput:
    st.header('2. Ask your Question(s)')
    st.text('ie. "Can you suggest which applicants have finance management expertise \n in the aviation industry?" ')

    def get_text():
        input_text = st.text_input("Your question", "Can you suggest ", key="input")
        return input_text
    
    user_input = get_text()


#display the chat history by iterating through the generated and past lists and using the message function from the streamlit_chat library to display each message.
if user_input:
    output = generate_response(user_input)
    # store the output 
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

#if st.session_state['generated']:
    
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')



