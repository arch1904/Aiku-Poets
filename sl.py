import streamlit as st
from streamlit_chat import message
from Top_Applicant_SpeedPass import TASP

header = st.container()
upload = st.container()
textInput = st.container()
chatbot = st.container()

bot = TASP()

with header:
    st.title('Top Applicant Speedpass')

files = None
def file_list(count):
    l = []
    for i in range(count):
        l.append("R"+str(i+1)+".pdf")
    return l
with upload:
    st.header('1. Upload resumes')
    st.text('Select multiple PDFs for analysis')

    files = st.file_uploader("Select Files",'pdf', True)
    for i in range(len(files)):
        f = open("R" + str(i+1)+".pdf", "wb")
        for line in files[i]:
            f.write(line)
        f.close()
    resumes = file_list(len(files))




st.title("TAPS")

with textInput:
    st.header('2. What criteria would you like to assess on?')
    st.text('ie. "Can you assess which applicants have finance management expertise \n in the aviation industry?" ')

    def get_text():
        input_text = st.text_input("Your question", "Can you assess ", key="input")
        return input_text
    
    question = get_text()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if question:
    output = bot.assess_multiple_resumes(resumes, question)
    # store the output 
    st.session_state.past.append(question)
    st.session_state.generated.append(output)

for i in range(len(st.session_state['generated'])-1, -1 ,-1):
    message(st.session_state["generated"][i], key=str(i))
    message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')


