import platform
from tempfile import TemporaryDirectory
from pathlib import Path
 
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

import sys
import concurrent.futures
import threading

import openai

with open('OPEN_AI_KEY.txt') as f:
    lines = f.readlines()
openai.api_key = lines[0]

def get_resume_text(resume_file):
    PDF_file = Path(resume_file)
    image_file_list = []
    
    with TemporaryDirectory() as tempdir: # Create a temporary directory to hold our temporary images.
        pdf_dpi = 500
        pdf_pages = convert_from_path(PDF_file, pdf_dpi) # Read in the PDF file at set DPI

        for page_enumeration, page in enumerate(pdf_pages, start=1): # Iterate through all the pages stored above
            # enumerate() "counts" the pages for us.
            # Create a file name to store the image
            filename = f"{tempdir}\page_{page_enumeration:03}.jpg"

            # Declaring filename for each page of PDF as JPG
            # For each page, filename will be:
            # PDF page 1 -> page_001.jpg
            # Save the image of the page in system
            page.save(filename, "JPEG")
            image_file_list.append(filename)
    resume_text = ""
    for image_file in image_file_list:

        text = str(((pytesseract.image_to_string(Image.open(image_file)))))

        text = text.replace("-\n", "")
        text= text.replace("\n\n", "----")
        resume_text += text
    return resume_text

# resumes = sys.argv[1:len(sys.argv)-1]
# question = sys.argv[len(sys.argv) - 1]
def parse_all_resumes(resumes):
    res_text_compiled = []
    for i in range(len(resumes)):
        resume = resumes[i]
        curr = get_resume_text(resume)
        if len(curr) == 0:
            continue #break
        # curr = "----Begin Candidate " + str(i+1) + ":" + curr + "End Candidate"+ str(i+1) +  "----\n    "
        # res_text_compiled += curr
        res_text_compiled.append(curr)
    return res_text_compiled

def make_prompt(resumes, question):
    res_text_compiled = parse_all_resumes(resumes)
    prompt = "Given all those resumes marked with ----Begin Candidate: and End Candidate----\n assess" + question
    return prompt


def summarize_resume(text_resume):
    model_engine_summary = "text-davinci-003"
    max_tokens = 1024
    prompt = "Summarize the following Text Resume: " + text_resume
    completion = openai.Completion.create(
        engine=model_engine_summary,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return completion.choices[0].text

def assess_single_resume(text_resume, question_completion):
    """
    Questions in the form of {Is this candidate a good fit for} user-input(for ex: a Marketing Manager Role? ***, given certain criteria*** optional)
    """
    model_engine_assessment = "gpt-3.5-turbo"
    summary = summarize_resume(text_resume)

    response = openai.ChatCompletion.create(
    model = model_engine_assessment,
    messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Consider the following text-resume from a Candidate: " + summary},
            {"role": "user", "content": "Is this candidate a good fit for " + question_completion}
        ]
    )
    return response['choices'][0]['message']['content']



def get_resume_summaries(textresumes):
    summaries = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        iterator = {executor.submit(summarize_resume, textresume): textresume for textresume in textresumes}
        for i in concurrent.futures.as_completed(iterator):
            original = iterator[i]
            summaries.append((original,i.result()))
    return summaries
    

def generate_resume_messages(textresumes):
    base_sys_msg = "You are a helpful assistant."
    messages=[{"role": "system", "content": base_sys_msg}]
    for i in range(len(textresumes)):
        res = textresumes[i]



    
def assess_multiple_resumes(text_resumes ,question_completion):
    pass


x = parse_all_resumes(["Resume.pdf", "Resume_Revised.pdf"])
print(get_resume_summaries(x))
    


# prompt = make_prompt(resumes, question)
# completion = openai.Completion.create(
#     engine=model_engine,
#     prompt=prompt,
#     max_tokens=max_tokens,
#     temperature=0.5,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0
# )

# print(completion.choices[0].text)
        


